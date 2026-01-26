import os
import re
import json
import script_constants as sc

def extract_md_sections(md_content):
    name = re.search(r'^#\s+(.+)', md_content, re.MULTILINE)
    overview = re.search(r'## Overview\s*\n(.*?)(?:\n##|\Z)', md_content, re.DOTALL)
    capabilities_match = re.search(r'## Capabilities\s*\n((?:-.*\n?)*)', md_content)
    if capabilities_match:
        bullets = [line for line in capabilities_match.group(1).splitlines() if line.strip().startswith('-')]
        html_capabilities = "<br>".join(bullets)
    else:
        html_capabilities = ""
    tools = re.search(r'## Available Tools\s*\n(.*?)(?:\n##|\Z)', md_content, re.DOTALL)

    return {
        "name": name.group(1).strip() if name else "",
        "description": overview.group(1).strip() if overview else "",
        "capabilities": html_capabilities,
        "agent_definition": tools.group(1).strip() if tools else "",
    }

def find_md_files(root):
    md_files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.md'):
                md_files.append(os.path.join(dirpath, f))
    return md_files

def create_table(entries):
    if not entries:
        return ""
    table = "<table>\n\t<tr>\n\t\t<th>Name</th>\n\t\t<th>Overview</th>\n\t\t<th>Capabilities</th>\n\t\t<th>Agent Tools</th>\n\t</tr>\n"
    for entry in entries:
        table += f"\t<tr>\n\t\t<td>{entry['name']}</td>\n\t\t<td>{entry['description']}</td>\n\t\t<td>{entry['capabilities']}</td>\n\t\t<td>{entry['agent_definition']}\n\t</tr>\n"
    table += "</table>\n"
    return table

def replace_readme_catalog():
    root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"
    readme_path = os.path.dirname(os.path.abspath(__file__)) + "/../README.md"
    catalog_path = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema/catalog.json"

    sections = []
    for dirpath, dirnames, filenames in os.walk(root):
        # get md files in each directory starting at agent_factory_schema/equinix
        md_files = [os.path.join(dirpath, f) for f in filenames if f.endswith('.md')]
        if os.path.isdir(dirpath) and md_files:
            entries = []
            for md_file in md_files:
                with open(md_file, "r") as f:
                    content = f.read()
                    entry = extract_md_sections(content)
                    entries.append(entry)
            rel_dir = os.path.relpath(dirpath, root)
            formatted_section_dir = re.sub(r'[/]|v1', ' ', rel_dir, flags=re.IGNORECASE)
            formatted_section_dir = re.sub(r'_', '-', formatted_section_dir).title()
            sections.append(f"\n---\n### {formatted_section_dir}\n")
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
