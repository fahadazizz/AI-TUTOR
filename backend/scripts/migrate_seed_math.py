import json
import os
import re

def migrate_string(text: str, wrap: bool = False) -> str:
    if not text:
        return text
    
    # Replace unicode math with LaTeX equivalents
    replacements = {
        "×": r"\times",
        "÷": r"\div",
        "²": "^2",
        "³": "^3",
        "½": "1/2",
        "⅓": "1/3",
        "¼": "1/4",
        "¾": "3/4"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    if wrap:
        # Wrap in $ $ if not already wrapped
        text = text.strip()
        if not text.startswith("$"):
            text = f"${text}$"
            
    return text

def migrate_data(data, keys_to_wrap):
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if isinstance(v, str):
                if k in keys_to_wrap:
                    new_data[k] = migrate_string(v, wrap=True)
                else:
                    new_data[k] = migrate_string(v, wrap=False)
            elif isinstance(v, list) and k == "formulas":
                # Special case for formulas list
                new_data[k] = [migrate_string(f, wrap=True) for f in v if isinstance(f, str)]
            else:
                new_data[k] = migrate_data(v, keys_to_wrap)
        return new_data
    elif isinstance(data, list):
        return [migrate_data(item, keys_to_wrap) for item in data]
    else:
        return data

def main():
    base_dir = os.path.join(os.path.dirname(__file__), '../../data/curriculum/mathematics')
    
    files_to_migrate = [
        "concepts.json",
        "misconceptions.json",
        "prerequisites.json",
        "questions/ch02_quadratic_equations.json",
        "questions/initial_assessment.json"
    ]
    
    keys_to_wrap = {"math", "result", "expected_answer", "problem"}
    
    for relative_path in files_to_migrate:
        file_path = os.path.join(base_dir, relative_path)
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (not found)")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        migrated_data = migrate_data(data, keys_to_wrap)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(migrated_data, f, ensure_ascii=False, indent=2)
            
        print(f"Migrated {relative_path}")

if __name__ == "__main__":
    main()
