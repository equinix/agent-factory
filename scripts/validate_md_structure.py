import os

REQUIRED_SECTIONS = [
    "## Overview",
    "## Prerequisites",
    "## Capabilities",
    "## Follow the action step by step below",
    "## Available Tools",
    "## Guidelines",
]

def validate_md_sections(root_dir):
    root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"

    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(dirpath, file)
                with open(file_path, "r") as f:
                    content = f.read()
                missing = [section for section in REQUIRED_SECTIONS if section not in content]
                if missing:
                    raise ValueError(f"{file_path} is missing sections: {', '.join(missing)}")
                else:
                    print(f"{file_path} is valid.")

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__)) + "/../agent_factory_schema"
    validate_md_sections(root)
