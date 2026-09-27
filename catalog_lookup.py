"""
Catalog Lookup - matches the item name from intent_parse.py against
docs/catalog.json and fills in a real price (unit_price * quantity),
instead of letting the LLM guess a number.

Usage:
    python catalog_lookup.py "5 laptops for new interns"

Chains: intent_parse.py -> catalog_lookup.py -> (next: policy_check.py)
"""
import sys
import json
import difflib

from intent_parse import parse_intent

CATALOG_PATH = "docs/catalog.json"


def load_catalog(path: str = CATALOG_PATH) -> list:
    with open(path, "r") as f:
        return json.load(f)


def lookup_price(item_name: str, catalog: list):
    """Fuzzy-matches item_name against catalog item names (handles
    'laptops' vs 'laptop', small typos, etc.). Returns the catalog
    entry dict, or None if nothing matches well enough."""
    if not item_name:
        return None

    names = [c["item"] for c in catalog]
    matches = difflib.get_close_matches(item_name.lower(), names, n=1, cutoff=0.5)
    if not matches:
        return None

    matched_name = matches[0]
    return next(c for c in catalog if c["item"] == matched_name)


def enrich_with_catalog(case: dict) -> dict:
    catalog = load_catalog()
    entry = lookup_price(case.get("item"), catalog)

    if entry is None:
        case["price"] = None
        case["catalog_match"] = None
    else:
        quantity = case.get("quantity") or 1
        case["price"] = entry["unit_price"] * quantity
        case["catalog_match"] = entry["item"]
        if not case.get("department"):
            case["department"] = entry["department"]

    return case


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python catalog_lookup.py "your request text here"')
        sys.exit(1)

    text = sys.argv[1]
    case = parse_intent(text)
    case = enrich_with_catalog(case)
    print(json.dumps(case, indent=2))