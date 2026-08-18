#!/usr/bin/env python3
"""
Phase 1 — Static template content evaluation for agent-factory.

Runs two tiers of checks on every agent-factory template markdown file:
  1. Deterministic structural checks (fast, no LLM — the hard gate):
       - All required sections present
       - Frontmatter fields (name, description) present
       - At least one well-formed tool declared under ## Available Tools
       - ## Configuration section, if non-empty, contains at least one parseable parameter
       - ## Instructions section is non-empty
       - Declared tools exist in the known tool corpus (warning, non-blocking)
  2. LLM judge (Claude on AWS Bedrock via agent-eval-service, 0-1 per dimension):
       - clarity, nonContradiction, scope, completeness, instructionToolAlignment

Overall pass = all deterministic checks pass AND min judge score >= threshold.
Exit code 1 if any template fails, 0 if all pass.

Usage:
    python scripts/template_content_eval.py [options]

Options:
    --changed=a.md,b.md       Comma-separated list of files to evaluate
    --templates-dir=<dir>     Evaluate every *.md under this directory (recursive)
    --threshold=0.6           Minimum judge score to pass (default: 0.6)
    --dataset=<name>          LangSmith dataset name (optional)
    --experiment=<name>       LangSmith experiment name (optional)
    --skip-llm                Run deterministic checks only (no LLM judge)

Environment variables:
    APIGEE_TOKEN_URL           OAuth2 token endpoint (grant_type=password)
    AGENT_EVAL_SERVICE_URL     Base URL of agent-eval-service's external Apigee route
    APIGEE_CLIENT_ID           OAuth2 client_id
    APIGEE_CLIENT_SECRET       OAuth2 client_secret
    APIGEE_SERVICE_USERNAME    Service account username (grant_type=password)
    APIGEE_SERVICE_PASSWORD    Service account password (grant_type=password)
    LANGSMITH_API_KEY          LangSmith API key (optional — disables LangSmith if absent)
"""

from __future__ import annotations

import argparse
import httpx
import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger("template_content_eval")
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

# ---------------------------------------------------------------------------
# Constants — mirrors TemplateContentEvalService.REQUIRED_SECTIONS
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = [
    "## Overview",
    "## Prerequisites",
    "## Capabilities",
    "## Instructions",
    "## Available Tools",
    "## Guidelines",
    "## Configuration",
]

JUDGE_DIMENSIONS = [
    "clarity",
    "nonContradiction",
    "scope",
    "completeness",
    "instructionToolAlignment",
]

DEFAULT_THRESHOLD = 0.6
# Scores below this are surfaced as advisory warnings even when the template passes the gate.
SOFT_THRESHOLD = 0.8
# Scores that fail the gate but sit in this band are noted as borderline — the judge is
# non-deterministic near its rubric anchors, so a re-run may land on either side of the gate.
BORDERLINE_FLOOR = 0.5
DEFAULT_DATASET = "Agent Factory Template Content Eval"

# Backtick-quoted token, e.g. `search_routers`
_BACKTICK = re.compile(r"`([^`]+)`")
# A valid snake_case tool/param identifier
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
# Section header: exactly two hashes
_SECTION_HEADER = re.compile(r"^##\s+(\S.*)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ConfigParam:
    name: str
    required: bool


@dataclass
class TemplateSpec:
    source_path: str
    name: Optional[str]
    description: Optional[str]
    sections: dict[str, str]          # "## Header" -> body text
    declared_tools: list[str]
    config_params: list[ConfigParam]
    raw_markdown: str
    malformed_tool_tokens: list[str]  # backtick tokens that look like tools but failed _IDENTIFIER

    def section(self, header: str) -> str:
        return self.sections.get(header, "")


@dataclass
class JudgeScore:
    score: float
    comment: str


@dataclass
class EvalResult:
    source_path: str
    template_name: Optional[str]
    passed: bool
    deterministic_checks: dict[str, bool]
    issues: list[str]
    warnings: list[str]
    judge_scores: dict[str, JudgeScore]
    judge_min_score: float
    threshold: float
    judge_ran: bool = True  # False when judge failed open on every dimension


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

class TemplateMarkdownParser:

    def parse(self, path: str, markdown: str) -> TemplateSpec:
        content = (markdown or "").replace("\r\n", "\n")
        name, description, body = self._extract_frontmatter(content)
        sections = self._extract_sections(body)
        declared_tools, malformed_tokens = self._extract_identifiers(
            sections.get("## Available Tools", "")
        )
        config_params = self._extract_config_params(sections.get("## Configuration", ""))
        return TemplateSpec(
            source_path=path,
            name=name,
            description=description,
            sections=sections,
            declared_tools=declared_tools,
            config_params=config_params,
            raw_markdown=content,
            malformed_tool_tokens=malformed_tokens,
        )

    # ---- frontmatter -------------------------------------------------------

    def _extract_frontmatter(self, content: str) -> tuple[Optional[str], Optional[str], str]:
        stripped = content.lstrip()
        if not stripped.startswith("---"):
            return None, None, content
        first_nl = stripped.find("\n")
        if first_nl < 0:
            return None, None, content
        closing = stripped.find("\n---", first_nl)
        if closing < 0:
            return None, None, content
        block = stripped[first_nl + 1 : closing]
        after_close = stripped.find("\n", closing + 1)
        body = "" if after_close < 0 else stripped[after_close + 1 :]

        name = description = None
        for line in block.split("\n"):
            v = self._frontmatter_value(line, "name")
            if v:
                name = v
                continue
            v = self._frontmatter_value(line, "description")
            if v:
                description = v
        return name, description, body

    @staticmethod
    def _frontmatter_value(line: str, key: str) -> Optional[str]:
        stripped = line.strip()
        prefix = key + ":"
        if not stripped.startswith(prefix):
            return None
        value = stripped[len(prefix):].strip()
        return value if value else None

    # ---- sections ----------------------------------------------------------

    def _extract_sections(self, body: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current_header: Optional[str] = None
        current_lines: list[str] = []

        for line in body.split("\n"):
            m = re.match(r"^##\s+(\S.*)$", line)
            if m:
                if current_header is not None:
                    sections[current_header] = "\n".join(current_lines).strip()
                current_header = "## " + m.group(1).strip()
                current_lines = []
            elif current_header is not None:
                current_lines.append(line)

        if current_header is not None:
            sections[current_header] = "\n".join(current_lines).strip()

        return sections

    # ---- tools & config ----------------------------------------------------

    def _extract_identifiers(self, section_body: str) -> tuple[list[str], list[str]]:
        seen: dict[str, None] = {}  # ordered set via dict
        malformed: list[str] = []
        for m in _BACKTICK.finditer(section_body):
            token = m.group(1).strip()
            if _IDENTIFIER.match(token):
                if token not in seen:
                    seen[token] = None
            elif token and "_" in token:
                # Looks like it was meant to be a tool name but failed (e.g. trailing space)
                malformed.append(token)
        return list(seen), malformed

    def _extract_config_params(self, section_body: str) -> list[ConfigParam]:
        params: list[ConfigParam] = []
        seen: set[str] = set()
        for line in section_body.split("\n"):
            m = _BACKTICK.search(line)
            if not m:
                continue
            name = m.group(1).strip()
            if not _IDENTIFIER.match(name) or name in seen:
                continue
            seen.add(name)
            required = "required" in line.lower()
            params.append(ConfigParam(name=name, required=required))
        return params


# ---------------------------------------------------------------------------
# Tool corpus builder — builds known tool set from all existing templates
# ---------------------------------------------------------------------------

def build_tool_corpus(templates_root: Optional[str], exclude: Optional[Path] = None) -> set[str]:
    """Collect all tool identifiers declared across all .md templates as the known corpus.

    exclude: if provided, skip this path so a template is not validated against itself.
    """
    if not templates_root:
        return set()
    root = Path(templates_root)
    if not root.is_dir():
        return set()
    parser = TemplateMarkdownParser()
    corpus: set[str] = set()
    for md_path in root.rglob("*.md"):
        if exclude and md_path.resolve() == exclude.resolve():
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
            spec = parser.parse(str(md_path), text)
            corpus.update(spec.declared_tools)
        except Exception:
            pass
    return corpus


# ---------------------------------------------------------------------------
# LLM judge
# ---------------------------------------------------------------------------

class AgentEvalServiceJudge:
    """
    Scores a template on five semantic dimensions by calling agent-eval-service's
    POST /fabric/v4/eval/template-content endpoint through the external Apigee gateway.

    agent-eval-service runs in-cluster and calls AWS Bedrock Runtime (Claude) internally.
    GitHub Actions runners cannot reach Bedrock — or the internal /fabric/i4/* route —
    directly (VPC-only), so they authenticate with an OAuth2 Bearer token (obtained via
    the platform's grant_type=password token endpoint) and call the external v4 route
    through Apigee instead. Runs on a normal ubuntu-latest runner; no self-hosted/in-network
    runner needed.

    Fails open (all dimensions 1.0) on any error so a flaky network call never blocks a PR.
    """

    _FAIL_OPEN_COMMENT = "judge unavailable — failed open"

    def __init__(
        self,
        token_url: str,
        eval_service_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        timeout: float = 30.0,
    ):
        self._enabled = False
        self._eval_service_url = (eval_service_url or "").rstrip("/")
        self._username = username
        self._timeout = timeout
        if not all([token_url, eval_service_url, client_id, client_secret, username, password]):
            log.warning("LLM judge disabled (missing Apigee credentials/config)")
            return
        self._access_token = self._fetch_token(token_url, client_id, client_secret, username, password)
        if not self._access_token:
            log.warning("LLM judge disabled (could not obtain Apigee access token)")
            return
        self._enabled = True
        log.info("LLM judge: using agent-eval-service via external Apigee (%s)", self._eval_service_url)

    def _fetch_token(self, token_url: str, client_id: str, client_secret: str,
                      username: str, password: str) -> Optional[str]:
        """
        Exchanges service-account credentials for a short-lived Bearer token via the
        platform's OAuth2 grant_type=password flow. One token is fetched per script run
        (not cached/persisted across runs) and reused for every template judged in this run —
        its ~3599s TTL comfortably covers a single CI run.
        """
        body = {
            "grant_type": "password",
            "user_name": username,
            "user_password": password,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CORRELATION-ID": str(uuid.uuid4()),
        }
        for attempt in range(2):
            try:
                response = httpx.post(token_url, json=body, headers=headers, timeout=self._timeout)
                response.raise_for_status()
                token = response.json().get("access_token")
                if not token:
                    raise ValueError("token response missing access_token")
                return token
            except Exception as e:
                if attempt == 0:
                    log.debug("Apigee token fetch attempt 1 failed, retrying in 2s: %s", e)
                    time.sleep(2)
                    continue
                log.warning("Apigee token fetch failed after retry: %s", e)
                return None
        return None

    def judge(self, spec: TemplateSpec) -> dict[str, JudgeScore]:
        if not self._enabled:
            return self._fail_open()
        for attempt in range(2):
            try:
                resp = httpx.post(
                    f"{self._eval_service_url}/fabric/v4/eval/template-content",
                    json={
                        "templateMarkdown": spec.raw_markdown,
                        "templatePath": spec.source_path,
                    },
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "X-AUTH-USER-NAME": self._username,
                        "X-CORRELATION-ID": str(uuid.uuid4()),
                    },
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                return self._parse(resp.json(), spec.source_path)
            except Exception as e:
                if attempt == 0:
                    log.debug("Judge attempt 1 failed, retrying in 2s: %s", e)
                    time.sleep(2)
                    continue
                log.warning(
                    "Template judge failed after retry (failing open) path=%s: %s",
                    spec.source_path, e,
                )
                return self._fail_open()
        return self._fail_open()

    def _parse(self, body: dict, source_path: str) -> dict[str, JudgeScore]:
        if body.get("failedOpen"):
            log.warning(
                "agent-eval-service reported failedOpen=true for path=%s — treating as fail-open",
                source_path,
            )
            return self._fail_open()
        scores: dict[str, JudgeScore] = {}
        for dim in JUDGE_DIMENSIONS:
            entry = (body.get("scores") or {}).get(dim, {})
            score = max(0.0, min(1.0, float(entry.get("score", 1.0))))
            scores[dim] = JudgeScore(score=score, comment=entry.get("comment", ""))
        return scores

    @staticmethod
    def _fail_open() -> dict[str, JudgeScore]:
        return {dim: JudgeScore(score=1.0, comment=AgentEvalServiceJudge._FAIL_OPEN_COMMENT)
                for dim in JUDGE_DIMENSIONS}

    @staticmethod
    def scores_are_fail_open(scores: dict[str, JudgeScore]) -> bool:
        """True when every dimension carries the fail-open sentinel comment."""
        return bool(scores) and all(
            s.comment == AgentEvalServiceJudge._FAIL_OPEN_COMMENT
            for s in scores.values()
        )


# ---------------------------------------------------------------------------
# Eval service
# ---------------------------------------------------------------------------

class TemplateContentEvalService:

    def __init__(self, judge: AgentEvalServiceJudge, tool_corpus: set[str] | None = None):
        self._parser = TemplateMarkdownParser()
        self._judge = judge
        self._tool_corpus = tool_corpus or set()

    def evaluate(self, path: str, markdown: str, threshold: float,
                 skip_llm: bool = False, tool_corpus: set[str] | None = None) -> EvalResult:
        spec = self._parser.parse(path, markdown)
        active_corpus = tool_corpus if tool_corpus is not None else self._tool_corpus
        checks: dict[str, bool] = {}
        issues: list[str] = []
        warnings: list[str] = []

        # 1. Required sections
        missing = [s for s in REQUIRED_SECTIONS if s not in spec.sections]
        checks["sectionsPresent"] = not missing
        for s in missing:
            issues.append(f"Missing required section: {s}")

        # 2. Frontmatter
        fm_ok = True
        if not spec.name:
            fm_ok = False
            issues.append("Missing frontmatter field: name")
        if not spec.description:
            fm_ok = False
            issues.append("Missing frontmatter field: description")
        checks["frontmatterPresent"] = fm_ok

        # 3. Tools declared
        checks["toolsDeclared"] = bool(spec.declared_tools)
        if not spec.declared_tools:
            issues.append("No tools declared under ## Available Tools")

        # 4. Config section parseable if non-empty
        config_body = spec.section("## Configuration")
        config_ok = not config_body.strip() or bool(spec.config_params)
        checks["configParsed"] = config_ok
        if not config_ok:
            issues.append("## Configuration present but no parameters could be parsed")

        # 5. Instructions non-empty
        instructions_ok = bool(spec.section("## Instructions").strip())
        checks["instructionsNonEmpty"] = instructions_ok
        if not instructions_ok:
            issues.append("## Instructions section is empty")

        # 6. Malformed tool tokens (warning, non-blocking)
        if spec.malformed_tool_tokens:
            warnings.append(
                f"Possibly malformed tool names in ## Available Tools: "
                f"{', '.join(repr(t) for t in spec.malformed_tool_tokens)}"
            )

        # 7. Unknown tools check (warning, non-blocking) — only when corpus is available
        if active_corpus and spec.declared_tools:
            unknown = [t for t in spec.declared_tools if t not in active_corpus]
            if unknown:
                warnings.append(
                    f"Tools not seen in any other template (may be new or mistyped): "
                    f"{', '.join(unknown)}"
                )

        deterministic_passed = all(checks.values())

        # 8. LLM judge
        if skip_llm:
            judge_scores: dict[str, JudgeScore] = {}
            judge_min = 1.0
            judge_ran = False
        else:
            judge_scores = self._judge.judge(spec)
            judge_ran = not AgentEvalServiceJudge.scores_are_fail_open(judge_scores)
            judge_min = min((s.score for s in judge_scores.values()), default=1.0)
            if not judge_ran:
                log.warning("path=%s  LLM judge failed open — scores are unreliable", path)
            for dim, score in judge_scores.items():
                if score.score < threshold and judge_ran:
                    note = ""
                    if score.score >= BORDERLINE_FLOOR:
                        note = " ⚠️ borderline — score may vary run-to-run"
                    issues.append(
                        f"Judge dimension below threshold: {dim}={score.score:.2f} (< {threshold:.2f}) — {score.comment}{note}"
                    )
                elif score.score < SOFT_THRESHOLD and judge_ran:
                    warnings.append(
                        f"Judge advisory ({dim}={score.score:.2f}, below ideal {SOFT_THRESHOLD:.2f}): {score.comment}"
                    )

        passed = deterministic_passed and (not judge_ran or judge_min >= threshold)

        log.info("path=%s  passed=%s  deterministic=%s  judgeMin=%.2f  judgeRan=%s",
                 path, passed, deterministic_passed, judge_min, judge_ran)
        return EvalResult(
            source_path=path,
            template_name=spec.name,
            passed=passed,
            deterministic_checks=checks,
            issues=issues,
            warnings=warnings,
            judge_scores=judge_scores,
            judge_min_score=judge_min,
            threshold=threshold,
            judge_ran=judge_ran,
        )


# ---------------------------------------------------------------------------
# LangSmith logger (uses official Python SDK)
# ---------------------------------------------------------------------------

class LangSmithLogger:
    """
    Optional best-effort LangSmith integration.
    Never raises — LangSmith is observability, not the gate.
    """

    def __init__(self, api_key: str):
        self._enabled = bool(api_key and api_key.strip())
        self._client = None
        if not self._enabled:
            log.info("LangSmith disabled (no api-key) — skipping experiment logging")
            return
        try:
            from langsmith import Client
            self._client = Client(api_key=api_key)
        except ImportError:
            log.warning("langsmith package not installed — skipping LangSmith logging")
            self._enabled = False
        except Exception as e:
            log.warning("LangSmith init failed (ignored): %s", e)
            self._enabled = False

    def get_client(self):
        """Return the underlying LangSmith client for wrap_openai tracing."""
        return self._client if self._enabled else None

    def log_experiment(self, dataset_name: str, experiment_name: str, results: list[EvalResult]) -> None:
        if not self._enabled:
            return
        try:
            self._ensure_dataset(dataset_name)
            for result in results:
                self._log_one(dataset_name, experiment_name, result)
            log.info("LangSmith experiment '%s' logged %d results to dataset '%s'",
                     experiment_name, len(results), dataset_name)
        except Exception as e:
            log.warning("LangSmith logging failed (ignored — observability only): %s", e)

    def _ensure_dataset(self, name: str) -> None:
        try:
            if not self._client.has_dataset(dataset_name=name):
                self._client.create_dataset(
                    dataset_name=name,
                    description="Agent Factory template Phase 1 content evaluation",
                )
        except Exception as e:
            log.debug("LangSmith dataset ensure failed: %s", e)

    def _log_one(self, dataset_name: str, experiment_name: str, result: EvalResult) -> None:
        inputs = {"path": result.source_path or "", "templateName": result.template_name or ""}
        outputs = {
            "passed": result.passed,
            "judgeMinScore": result.judge_min_score,
            "deterministicChecks": result.deterministic_checks,
            "issues": result.issues,
        }

        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Upsert example — idempotent across PRs (keyed on source_path via inputs)
        example_id: Optional[str] = None
        try:
            example = self._client.upsert_example(
                dataset_name=dataset_name,
                inputs=inputs,
                outputs=outputs,
            )
            example_id = str(example.id)
        except AttributeError:
            # Older SDK versions may not have upsert_example — fall back to create_example
            try:
                example = self._client.create_example(
                    dataset_name=dataset_name,
                    inputs=inputs,
                    outputs=outputs,
                )
                example_id = str(example.id)
            except Exception as e:
                log.debug("LangSmith example create (fallback) failed: %s", e)
        except Exception as e:
            log.debug("LangSmith example upsert failed: %s", e)

        try:
            self._client.create_run(
                id=run_id,
                name="template-content-eval",
                run_type="chain",
                inputs=inputs,
                outputs=outputs,
                project_name=experiment_name,
                reference_example_id=example_id,
                start_time=now,
                end_time=now,
            )
            # Feedback: overall gate + per judge dimension
            self._client.create_feedback(run_id, key="passed",
                                          score=1.0 if result.passed else 0.0,
                                          comment="Overall Phase 1 gate")
            for dim, score in result.judge_scores.items():
                self._client.create_feedback(run_id, key=dim,
                                              score=score.score, comment=score.comment)
        except Exception as e:
            log.debug("LangSmith run/feedback post failed: %s", e)


# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------

def _resolve_templates(args: argparse.Namespace) -> list[Path]:
    resolved: list[Path] = []

    if args.changed:
        for entry in args.changed.split(","):
            entry = entry.strip()
            if not entry or not entry.endswith(".md"):
                continue
            p = Path(entry)
            if p.is_file():
                resolved.append(p)
            else:
                log.warning("Skipping non-existent changed file: %s", p)
        return resolved

    if args.templates_dir:
        root = Path(args.templates_dir)
        resolved = sorted(root.rglob("*.md"))

    return resolved


def _print_summary(results: list[EvalResult], threshold: float) -> None:
    passed = sum(1 for r in results if r.passed)
    lines = [
        "",
        "======= Template Spec Check (static, not execution-tested) =======",
        f"Threshold: {threshold}",
    ]
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        lines.append(f"{verdict}  judgeMin={r.judge_min_score:.2f}  {r.source_path}")
        if r.warnings:
            for w in r.warnings:
                lines.append(f"       WARN: {w}")
        if not r.passed:
            for issue in r.issues:
                lines.append(f"       - {issue}")
    lines += [
        "------------------------------------------------------",
        f"Result: {passed}/{len(results)} passed",
        "======================================================",
    ]
    log.info("\n".join(lines))


def _write_report_md(results: list[EvalResult], threshold: float, output_path: str = "eval_report.md") -> None:
    """Write a markdown report suitable for posting as a GitHub PR comment."""
    passed_count = sum(1 for r in results if r.passed)
    overall = "✅ All templates passed" if passed_count == len(results) else f"❌ {len(results) - passed_count} template(s) failed"

    judge_skipped = any(not r.judge_ran for r in results)

    lines = [
        "<!-- template-content-eval-report -->",
        "## 🧪 Template Spec Check (static — not execution-tested)",
        "",
        "_Grades the template **text** only: structure + an LLM judge on spec quality. "
        "No agent was run and no tools were executed — a pass does not mean the agent works._",
        "",
    ]
    if judge_skipped:
        lines += [
            "> ⚠️ **LLM judge could not reach agent-eval-service via Apigee** (network error, timeout, or service unavailable). "
            "Deterministic checks ran; judge scores are skipped. "
            "Templates passed on deterministic checks alone — spec quality was NOT graded.",
            "",
        ]
    lines += [
        f"**{overall}** &nbsp;·&nbsp; {passed_count}/{len(results)} passed &nbsp;·&nbsp; threshold: `{threshold}`",
        "",
        "| Template | Result | Judge Min | Issues |",
        "|---|---|---|---|",
    ]
    for r in results:
        verdict = "✅ PASS" if r.passed else "❌ FAIL"
        template_name = Path(r.source_path).name
        issue_text = "<br>".join(r.issues) if r.issues else "—"
        judge_cell = "⚠️ skipped" if not r.judge_ran else f"`{r.judge_min_score:.2f}`"
        lines.append(f"| `{template_name}` | {verdict} | {judge_cell} | {issue_text} |")

    # Warnings section (non-blocking)
    all_warnings = [(Path(r.source_path).name, w) for r in results for w in r.warnings]
    if all_warnings:
        lines += ["", "### ⚠️ Warnings (non-blocking)", ""]
        for tname, w in all_warnings:
            lines.append(f"- **`{tname}`**: {w}")

    # Detailed judge scores for all evaluated templates
    judged = [r for r in results if r.judge_ran and r.judge_scores]
    if judged:
        lines += ["", "### Judge Scores", ""]
        for r in judged:
            verdict_icon = "✅" if r.passed else "❌"
            lines.append(f"**`{Path(r.source_path).name}`** {verdict_icon}")
            lines.append("")
            lines.append("| Dimension | Score | Comment |")
            lines.append("|---|---|---|")
            for dim, score in r.judge_scores.items():
                flag = " ⚠️" if score.score < SOFT_THRESHOLD else ""
                lines.append(f"| {dim} | `{score.score:.2f}`{flag} | {score.comment} |")
            lines.append("")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("Eval report written to %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 template content evaluation")
    parser.add_argument("--changed", help="Comma-separated list of changed .md files")
    parser.add_argument("--templates-dir", dest="templates_dir",
                        help="Directory to scan recursively for *.md files")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Minimum LLM judge score to pass (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--dataset", default=DEFAULT_DATASET,
                        help="LangSmith dataset name")
    parser.add_argument("--experiment", default=f"template-content-eval-{int(time.time())}",
                        help="LangSmith experiment name")
    parser.add_argument("--skip-llm", dest="skip_llm", action="store_true",
                        help="Run deterministic checks only, skip LLM judge")
    args = parser.parse_args()

    templates = _resolve_templates(args)
    if not templates:
        log.warning("No templates to evaluate. Provide --changed=<files> or --templates-dir=<dir>.")
        sys.exit(0)

    # LangSmith (observability only — no longer wired to the judge client)
    langsmith = LangSmithLogger(api_key=os.environ.get("LANGSMITH_API_KEY", ""))

    # Build judge — calls agent-eval-service via the external Apigee /fabric/v4 route,
    # which calls AWS Bedrock internally. Bedrock (and the internal /fabric/i4 route) are
    # VPC-only and not reachable from ubuntu-latest runners; the external v4 route is.
    judge = AgentEvalServiceJudge(
        token_url=os.environ.get("APIGEE_TOKEN_URL", ""),
        eval_service_url=os.environ.get("AGENT_EVAL_SERVICE_URL", ""),
        client_id=os.environ.get("APIGEE_CLIENT_ID", ""),
        client_secret=os.environ.get("APIGEE_CLIENT_SECRET", ""),
        username=os.environ.get("APIGEE_SERVICE_USERNAME", ""),
        password=os.environ.get("APIGEE_SERVICE_PASSWORD", ""),
    )

    corpus_root = args.templates_dir or "agent_factory_schema"
    service = TemplateContentEvalService(judge=judge)

    results: list[EvalResult] = []
    failures = 0
    for template in templates:
        try:
            markdown = template.read_text(encoding="utf-8")
            # Build corpus excluding the current template so tools unique to it are flagged as unknown
            per_template_corpus = build_tool_corpus(corpus_root, exclude=template)
            if per_template_corpus:
                log.debug("path=%s  corpus=%d tools (excluding self)", template, len(per_template_corpus))
            result = service.evaluate(str(template), markdown, args.threshold,
                                      skip_llm=args.skip_llm, tool_corpus=per_template_corpus)
            results.append(result)
            if not result.passed:
                failures += 1
        except OSError as e:
            failures += 1
            log.error("Failed to read template %s: %s", template, e)

    _print_summary(results, args.threshold)
    _write_report_md(results, args.threshold)

    langsmith.log_experiment(args.dataset, args.experiment, results)

    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
