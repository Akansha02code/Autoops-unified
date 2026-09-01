"""
Policy & Business Rule Agent - loads rules from docs/policy_rules.json
(data, not hardcoded Python) and checks an extracted case against them.

Usage:
    python policy_check.py sample_docs/batch1-1486.jpg
    (chains onto extract_text.py's output)

Or import check_policy(case_dict) directly once this is wired into the
main pipeline.
"""
import sys
import json

RULES_PATH = "docs/policy_rules.json"

CONDITIONS = {
    "greater_than": lambda field_value, rule_value: field_value is not None and field_value > rule_value,
    "less_than": lambda field_value, rule_value: field_value is not None and field_value < rule_value,
    "equals": lambda field_value, rule_value: field_value == rule_value,
}


def load_rules(path: str = RULES_PATH) -> list:
    with open(path, "r") as f:
        return json.load(f)


def check_policy(case: dict, rules_path: str = RULES_PATH) -> dict:
    """
    Takes an extracted case dict (like the output of extract_structured)
    and returns it with two new fields: policy_status and policy_flags.
    """
    rules = load_rules(rules_path)
    triggered = []

    for rule in rules:
        field_value = case.get(rule["field"])
        condition_fn = CONDITIONS.get(rule["condition"])
        if condition_fn and condition_fn(field_value, rule["value"]):
            triggered.append({"rule_id": rule["id"], "action": rule["action"]})

    case["policy_status"] = "flagged" if triggered else "ok"
    case["policy_flags"] = triggered
    return case


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python policy_check.py <path_to_image>")
        sys.exit(1)

    # Reuses the OCR + extraction pipeline from the previous step
    from ocr_test import extract_text
    from extract_test import extract_structured

    path = sys.argv[1]
    text = extract_text(path)
    case = extract_structured(text)
    case = check_policy(case)

    print(json.dumps(case, indent=2))