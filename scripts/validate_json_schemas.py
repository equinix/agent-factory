import os
from jsonschema import validate
import json

def validate_json_schemas():
    validationSchemaFile = os.path.dirname(os.path.abspath(__file__)) + "/jsonschema-org-schema.json"
    root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"

    with open(validationSchemaFile, "r") as schemaFile:
        schema = json.load(schemaFile)

    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith('.json') and os.path.basename(root) != "agent_factory_schema":
                with open(root + "/" + file, "r") as jsonFile:
                    data = json.load(jsonFile)
                    validate(instance=data, schema=schema)

if __name__ == "__main__":
    validate_json_schemas()
