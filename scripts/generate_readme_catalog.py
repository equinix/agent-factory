import os
import re
import json
import script_constants as sc

TRIGGER_DISPLAY = {
    "on_event": "On Event Agents",
    "on_schedule": "On Schedule Agents",
}

def extract_md_sections(md_content, current_md_file):
    name = re.search(r'^#\s+(.+)', md_content, re.MULTILINE)
    overview = re.search(r'## Overview\s*\n(.*?)(?:\n##|\Z)', md_content, re.DOTALL)
    capabilities = re.search(r'## Capabilities\s*\n((?:-.*\n?)*)', md_content)
    tools = re.search(r'## Available Tools\s*\n(.*?)(?:\n##|\Z)', md_content, re.DOTALL)

    if name:
        base_url = "https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/"
        rel_path = os.path.relpath(current_md_file, os.path.dirname(__file__) + "/../")
        url = f"{base_url}{rel_path.replace(os.sep, '/')}"
        current_md_file_last_index = rel_path.rfind("/")
        md_file = rel_path[current_md_file_last_index + 1:]
        html_name = f'<a href="{url}">{name.group(1).strip()}<br>[{md_file}]</a>'
    else:
        html_name = ""

    if capabilities:
        bullets = [line for line in capabilities.group(1).splitlines() if line.strip().startswith('-')]
        html_capabilities = "<br>".join(bullets)
    else:
        html_capabilities = ""

    return {
        "name": html_name,
        "description": overview.group(1).strip() if overview else "--",
        "capabilities": html_capabilities,
        "agent_definition": tools.group(1).strip() if tools else "--",
    }

def find_md_files(root):
    md_files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(os.path.join(dirpath, f))
    return md_files

def catalog_schema_entry(schema):
    agentFactories = ""

    if "agentFactories" in schema:
        agentFactories = schema["agentFactories"]

    return f"""---
### {schema["domain"]}
### {schema["url"]}
### {schema["datatype"]}
### {schema["agentFactories"]}
"""

def extract_schema_factory_status(entry_name, catalog):
    for schema in catalog["schemas"]:
        for agent_factory in schema.get("agentFactories", []):
            catalog_agent_factory_uri = agent_factory.get("uri", "")
            if catalog_agent_factory_uri and catalog_agent_factory_uri in entry_name:
                return agent_factory.get("releaseStatus")
    return sc.PREVIEW

def create_table(entries):
    if not entries:
        return ""
    table = "<table>\n\t<tr>\n\t\t<th>Name</th>\n\t\t<th>Overview</th>\n\t\t<th>Capabilities</th>\n\t\t<th>Agent Tools</th>\n\t\t<th>Release Status</th>\n\t</tr>\n"
    for entry in entries:
        table += f"\t<tr>\n\t\t<td>{entry['name']}</td>\n\t\t<td>{entry['description']}</td>\n\t\t<td>{entry['capabilities']}</td>\n\t\t<td>{entry['agent_definition']}</td>\n\t\t<td>{entry['release_status']}\n\t</tr>\n"
    table += "</table>\n"
    return table

def format_title(name):
    return re.sub(r'-', ' ', name).title() + " Agents"

def replace_readme_catalog():
    root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"
    readme_path = os.path.dirname(os.path.abspath(__file__)) + "/../README.md"
    catalog_path = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema/catalog.json"

    with open(catalog_path, "r") as catalog_file:
        catalog = json.load(catalog_file)

    # Build trigger-type → schema description mapping
    trigger_description = {}
    for schema in catalog["schemas"]:
        datatype_suffix = schema["datatype"].rsplit(".", 1)[-1]
        if datatype_suffix in TRIGGER_DISPLAY and datatype_suffix not in trigger_description:
            trigger_description[datatype_suffix] = schema.get("description", "")

    # Create groups for displaying sub-directories under main categories (On Event or On Schedule) in the README.
    # groups: { (product_key, trigger_type): { subdir: [entries] } }
    # product_key is the path prefix before the trigger dir (e.g. "equinix/fabric/v1")
    groups = {}

    for dirpath, dirnames, filenames in os.walk(root):
        md_files = sorted([os.path.join(dirpath, f) for f in filenames if f.endswith('.md')])
        if not md_files:
            continue

        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        parts = rel_dir.split("/")

        # Find the trigger type component in the path
        trigger_type = None
        trigger_idx = None
        for i, part in enumerate(parts):
            if part in TRIGGER_DISPLAY:
                trigger_type = part
                trigger_idx = i
                break

        if trigger_type is None:
            continue

        product_key = "/".join(parts[:trigger_idx])
        subdir = "/".join(parts[trigger_idx + 1:]) if trigger_idx + 1 < len(parts) else ""

        entries = []
        for md_file in md_files:
            with open(md_file, "r") as f:
                content = f.read()
            entry = extract_md_sections(content, md_file)
            entry["release_status"] = extract_schema_factory_status(entry["name"], catalog)
            entries.append(entry)

        key = (product_key, trigger_type)
        if key not in groups:
            groups[key] = {}
        groups[key][subdir] = entries

    sections = []
    for (product_key, trigger_type) in sorted(groups.keys()):
        product_title = re.sub(r'[/_]|v\d+', ' ', product_key).title().strip()
        trigger_title = TRIGGER_DISPLAY[trigger_type]
        description = trigger_description.get(trigger_type, "")

        sections.append(f"\n---\n## {product_title} {trigger_title}\n")
        if description:
            sections.append(f"{description}\n")

        for subdir in sorted(groups[(product_key, trigger_type)].keys()):
            entries = groups[(product_key, trigger_type)][subdir]
            if subdir:
                sections.append(f"\n### {format_title(subdir)}\n\n<details>\n<summary>Show agents</summary>\n\n{create_table(entries)}\n</details>\n")
            else:
                sections.append(create_table(entries))

    schemas_str = "\n".join(sections)

    with open(readme_path, "r+") as readme_file:
        content = readme_file.read()
        readme_file.seek(0)
        generation_start = "<!-- CATALOG_GENERATION_START -->"
        generation_end = "<!-- CATALOG_GENERATION_END -->"
        catalog_pattern = rf"{generation_start}.*?{generation_end}"
        updated_content = re.sub(
            catalog_pattern,
            f"{generation_start}\n{schemas_str}\n{generation_end}",
            content,
            flags=re.DOTALL
        )
        readme_file.write(updated_content)
        readme_file.truncate()

if __name__ == "__main__":
    replace_readme_catalog()
