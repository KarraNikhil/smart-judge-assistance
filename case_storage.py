import json
import os

# ✅ Case Storage File
CASE_FILE = "case_data.json"

def load_cases():
    """Load existing cases from JSON."""
    if os.path.exists(CASE_FILE):
        with open(CASE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_case(case_data):
    """Save a new case to JSON."""
    cases = load_cases()
    case_data["case_id"] = len(cases) + 1  # Auto-increment case ID
    cases.append(case_data)

    with open(CASE_FILE, "w", encoding="utf-8") as file:
        json.dump(cases, file, indent=4)

    print("✅ Case saved successfully!")
