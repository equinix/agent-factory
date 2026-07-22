import os
import re
import json
import script_constants as sc

BASE_URL = "https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/"


def read_md(uri):
    schema_root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"
    rel_path = uri.replace(BASE_URL + "agent_factory_schema/", "")
    local_path = os.path.join(schema_root, rel_path)
    if not os.path.exists(local_path):
        return ""
    with open(local_path, "r") as f:
        return f.read()


def extract_md_overview(content):
    match = re.search(r'## Overview\s*\n(.+)', content)
    return match.group(1).strip() if match else ""


def extract_md_title(content):
    match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def main():
    json_schemas = retrieve_json_schemas()
    write_json_schemas_to_catalog_file(json_schemas)


def sortedRemoveDuplicates(listOfDict):
    filtered_List = [d for d in listOfDict if isinstance(d, dict) and "name" in d]
    seen = set()
    unique = []
    for d in filtered_List:
        key = (d["name"], d.get("uri", ""))
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return sorted(unique, key=lambda x: x["name"])


def retrieve_json_schemas():
    directory = os.path.dirname(os.path.abspath(__file__)) + '/../agent_factory_schema'
    json_schemas = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and os.path.basename(root) != "agent_factory_schema":
                with open(root + "/" + file, "r") as jsonFiles:
                    data = json.load(jsonFiles)
                    for factory in data.get("agentFactories", []):
                        content = read_md(factory.get("uri", ""))
                        if content:
                            factory["description"] = extract_md_overview(content)
                            factory["name"] = extract_md_title(content)
                    agentFactories = sortedRemoveDuplicates(data.get("agentFactories", []))
                    newItem = {
                        "url": data["$id"],
                        "domain": data["domain"],
                        "title": data["name"],
                        "description": data["definitions"]["Data"]["description"],
                        "datatype": data["datatype"],
                        "agentFactories": agentFactories
                    }
                    json_schemas.append(newItem)
    json_schemas.sort(key=lambda x: x["url"])
    return json_schemas


def write_json_schemas_to_catalog_file(json_schemas):
    catalog = {
        "$schema": 'https://json.schemastore.org/schema-catalog',
        "version": 1,
        "schemas": json_schemas
    }
    with open(os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema/catalog.json", "w") as catalogFile:
        catalogFile.write(json.dumps(catalog, indent=4))
        catalogFile.write("\n")


if __name__ == "__main__":
    main()