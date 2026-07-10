#!/usr/bin/env python3
"""
Phase 1 — Static template content evaluation for agent-factory.

Runs two tiers of checks on every agent-factory template markdown file:
  1. Deterministic structural checks (fast, no LLM — the hard gate):
       - All required sections present
       - Frontmatter fields (name, description) present
       - At least one well-formed tool declared under ## Available Tools
       - ## Configuration section, if non-empty, contains at least one parseable parameter
  2. LLM judge (Azure OpenAI gpt-4o-mini, 0-1 per dimension):
       - clarity, nonContradiction, scope, completeness, instructionToolAlignment

Overall pass = all deterministic checks pass AND min judge score >= threshold.
Exit code 1 if any template fails, 0 if all pass.

Usage:
    python scripts/template_content_eval.py [options]

Options:
    --changed=a.md,b.md       Comma-separated list of files to evaluate
    --templates-dir=<dir>     Evaluate every *.md under this directory (recursive)
    --threshold=0.8           Minimum judge score to pass (default: 0.8)
    --dataset=<name>          LangSmith dataset name (optional)
    --experiment=<name>       LangSmith experiment name (optional)

Environment variables:
    AZURE_OPENAI_API_KEY      Azure OpenAI API key (required for LLM judge)
    AZURE_OPENAI_ENDPOINT     Azure OpenAI endpoint URL
    LANGSMITH_API_KEY         LangSmith API key (optional — disables LangSmith if absent)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
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

DEFAULT_THRESHOLD = 0.8
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
    sections: dict[str, str]          # "## Header" → body text
    declared_tools: list[str]
    config_params: list[ConfigParam]
    raw_markdown: str

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
    judge_scores: dict[str, JudgeScore]
    judge_min_score: float
    threshold: float


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

class TemplateMarkdownParser:

    def parse(self, path: str, markdown: str) -> TemplateSpec:
        content = (markdown or "").replace("\r\n", "\n")
        name, description, body = self._extract_frontmatter(content)
        sections = self._extract_sections(body)
        declared_tools = self._extract_identifiers(sections.get("## Available Tools", ""))
        config_params = self._extract_config_params(sections.get("## Configuration", ""))
        return TemplateSpec(
            source_path=path,
            name=name,
            description=description,
            sections=sections,
            declared_tools=declared_tools,
            config_params=config_params,
            raw_markdown=content,
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

    def _extract_identifiers(self, section_body: str) -> list[str]:
        seen: dict[str, None] = {}  # ordered set via dict
        for m in _BACKTICK.finditer(section_body):
            token = m.group(1).strip()
            if _IDENTIFIER.match(token) and token not in seen:
                seen[token] = None
        return list(seen)

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
# LLM judge
# ---------------------------------------------------------------------------

class TemplateContentJudge:
    """
    Scores a template on five semantic dimensions using Azure OpenAI gpt-4o-mini.
    Fails open (all dimensions 1.0) on any error so a flaky LLM call never blocks a PR.
    """

    def __init__(self, api_key: str, endpoint: str, deployment: str = "gpt-4o-mini"):
        try:
            from openai import AzureOpenAI
            self._client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2024-02-01",
            )
            self._deployment = deployment
            self._enabled = True
        except Exception as e:
            log.warning("LLM judge unavailable (will fail open): %s", e)
            self._enabled = False

    def judge(self, spec: TemplateSpec) -> dict[str, JudgeScore]:
        if not self._enabled:
            return self._fail_open()
        try:
            prompt = self._build_prompt(spec)
            response = self._client.chat.completions.create(
                model=self._deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=30,
            )
            raw = response.choices[0].message.content or ""
            return self._parse(raw)
        except Exception as e:
            log.warning("Template content judge failed (failing open) path=%s: %s", spec.source_path, e)
            return self._fail_open()

    def _build_prompt(self, spec: TemplateSpec) -> str:
        declared = ", ".join(spec.declared_tools) if spec.declared_tools else "none declared"
        return f"""You are evaluating an Equinix agent-factory template for production readiness.
A template is a natural-language agent specification. Its "## Instructions" describe the
workflow in prose and deliberately do NOT repeat the snake_case tool names, so judge tool
alignment by MEANING, not by literal string match.

Declared tools: {declared}

Full template markdown:
---
{spec.raw_markdown}
---

Score these five dimensions from 0.0 (broken/absent) to 1.0 (excellent) and respond with
ONLY valid JSON, no prose, no code fences:
{{
  "clarity":                  {{"score": <0.0-1.0>, "comment": "<brief reason>"}},
  "nonContradiction":         {{"score": <0.0-1.0>, "comment": "<brief reason>"}},
  "scope":                    {{"score": <0.0-1.0>, "comment": "<brief reason>"}},
  "completeness":             {{"score": <0.0-1.0>, "comment": "<brief reason>"}},
  "instructionToolAlignment": {{"score": <0.0-1.0>, "comment": "<brief reason>"}}
}}

Dimension guide:
- clarity:                  Are the objective and steps unambiguous and easy to follow?
- nonContradiction:         1.0 = no conflicting or circular instructions; lower if any conflict.
- scope:                    Is the agent's goal specific and bounded (not open-ended)?
- completeness:             Are prerequisites, termination/success criteria, and failure handling present?
- instructionToolAlignment: Does every instruction step map to a declared tool, and is every
                            declared tool actually used by a step? Penalize unused or missing tools.
"""

    def _parse(self, raw: str) -> dict[str, JudgeScore]:
        if not raw or not raw.strip():
            return self._fail_open()
        try:
            text = raw.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text).strip()
            node = json.loads(text)
            scores: dict[str, JudgeScore] = {}
            for dim in JUDGE_DIMENSIONS:
                entry = node.get(dim, {})
                score = max(0.0, min(1.0, float(entry.get("score", 1.0))))
                comment = entry.get("comment", "")
                scores[dim] = JudgeScore(score=score, comment=comment)
            return scores
        except Exception as e:
            log.warning("Failed to parse judge response (failing open): %s", e)
            return self._fail_open()

    @staticmethod
    def _fail_open() -> dict[str, JudgeScore]:
        return {dim: JudgeScore(score=1.0, comment="judge unavailable — failed open")
                for dim in JUDGE_DIMENSIONS}


# ---------------------------------------------------------------------------
# Eval service
# ---------------------------------------------------------------------------

class TemplateContentEvalService:

    def __init__(self, judge: TemplateContentJudge):
        self._parser = TemplateMarkdownParser()
        self._judge = judge

    def evaluate(self, path: str, markdown: str, threshold: float) -> EvalResult:
        spec = self._parser.parse(path, markdown)
        checks: dict[str, bool] = {}
        issues: list[str] = []

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

        deterministic_passed = all(checks.values())

        # 5. LLM judge
        judge_scores = self._judge.judge(spec)
        judge_min = min((s.score for s in judge_scores.values()), default=1.0)
        for dim, score in judge_scores.items():
            if score.score < threshold:
                issues.append(
                    f"Judge dimension below threshold: {dim}={score.score:.2f} (< {threshold:.2f}) — {score.comment}"
                )

        passed = deterministic_passed and judge_min >= threshold

        log.info("path=%s  passed=%s  deterministic=%s  judgeMin=%.2f",
                 path, passed, deterministic_passed, judge_min)
        return EvalResult(
            source_path=path,
            template_name=spec.name,
            passed=passed,
            deterministic_checks=checks,
            issues=issues,
            judge_scores=judge_scores,
            judge_min_score=judge_min,
            threshold=threshold,
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
        try:
            example = self._client.create_example(
                dataset_name=dataset_name,
                inputs=inputs,
                outputs=outputs,
            )
            example_id = str(example.id)
        except Exception:
            example_id = None

        run_id = str(uuid.uuid4())
        now_ms = int(time.time() * 1000)
        try:
            self._client.create_run(
                id=run_id,
                name="template-content-eval",
                run_type="chain",
                inputs=inputs,
                outputs=outputs,
                session_name=experiment_name,
                reference_example_id=example_id,
                start_time=now_ms,
                end_time=now_ms,
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
        "================ Template Content Eval ================",
        f"Threshold: {threshold}",
    ]
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        lines.append(f"{verdict}  judgeMin={r.judge_min_score:.2f}  {r.source_path}")
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

    lines = [
        "## 🧪 Template Content Eval Report",
        "",
        f"**{overall}** &nbsp;·&nbsp; {passed_count}/{len(results)} passed &nbsp;·&nbsp; threshold: `{threshold}`",
        "",
        "| Template | Result | Judge Min | Issues |",
        "|---|---|---|---|",
    ]
    for r in results:
        verdict = "✅ PASS" if r.passed else "❌ FAIL"
        template_name = Path(r.source_path).name
        issue_text = "<br>".join(r.issues) if r.issues else "—"
        lines.append(f"| `{template_name}` | {verdict} | `{r.judge_min_score:.2f}` | {issue_text} |")

    # Detailed judge scores for failed templates
    failed = [r for r in results if not r.passed]
    if failed:
        lines += ["", "### Judge Scores (failed templates)", ""]
        for r in failed:
            lines.append(f"**`{Path(r.source_path).name}`**")
            lines.append("")
            lines.append("| Dimension | Score | Comment |")
            lines.append("|---|---|---|")
            for dim, score in r.judge_scores.items():
                flag = " ⚠️" if score.score < threshold else ""
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
    parser.add_argument("--experiment", default=f"template-content-eval-{int(time.time() * 1000)}",
                        help="LangSmith experiment name")
    args = parser.parse_args()

    templates = _resolve_templates(args)
    if not templates:
        log.warning("No templates to evaluate. Provide --changed=<files> or --templates-dir=<dir>.")
        sys.exit(0)

    # Build judge (requires AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT)
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    judge = TemplateContentJudge(api_key=api_key, endpoint=endpoint)
    service = TemplateContentEvalService(judge=judge)

    results: list[EvalResult] = []
    failures = 0
    for template in templates:
        try:
            markdown = template.read_text(encoding="utf-8")
            result = service.evaluate(str(template), markdown, args.threshold)
            results.append(result)
            if not result.passed:
                failures += 1
        except OSError as e:
            failures += 1
            log.error("Failed to read template %s: %s", template, e)

    _print_summary(results, args.threshold)
    _write_report_md(results, args.threshold)

    langsmith = LangSmithLogger(api_key=os.environ.get("LANGSMITH_API_KEY", ""))
    langsmith.log_experiment(args.dataset, args.experiment, results)

    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
