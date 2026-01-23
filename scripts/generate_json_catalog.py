import os
import json
import script_constants as sc


def main():
    json_schemas = retrieve_json_schemas()
    write_json_schemas_to_catalog_file(json_schemas)


def sortedRemoveDuplicates(listOfDict):
    filtered_List = [d for d in listOfDict if isinstance(d, dict) and "name" in d]

    return sorted({d["name"]: d for d in filtered_List}.values(), key=lambda x: x["name"])


def retrieve_json_schemas():
    directory = os.path.dirname(os.path.abspath(__file__)) + '/../agent_factory_schema'
    json_schemas = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and os.path.basename(root) != "agent_factory_schema":
                with open(root + "/" + file, "r") as eventFile:
                    data = json.load(eventFile)
                    eventDriven = sortedRemoveDuplicates(data.get(sc.EVENT_DRIVEN, []))
                    runOnceTypes = sortedRemoveDuplicates(data.get(sc.RUN_ONCE, []))
                    scheduledTypes = sortedRemoveDuplicates(data.get(sc.SCHEDULED, []))
                    newItem = {
                        "url": data["$id"],
                        "domain": data["domain"],
                        "name": data["name"],
                        "description": data["definitions"]["description"],
                        "datatype": data["datatype"],
                        "eventDrivenTypes": eventDriven,
                        "runOnceTypes": runOnceTypes,
                        "scheduledTypes": scheduledTypes
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