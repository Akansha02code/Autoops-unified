"""
Extraction agent - takes raw OCR text and asks Groq to turn it into
structured JSON matching our case schema.

Handles multi-item invoices (sums quantities across all line items)
and now also detects the invoice's currency, since source documents
are not always in INR.

Usage:
    python extract_text.py sample_docs/invoice1.jpg
"""
import sys
import os
import json
from groq import Groq
from dotenv import load_dotenv

from ocr_test import extract_text  # reuse the OCR function from step 3

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT_TEMPLATE = """You are extracting structured data from an invoice or purchase document.
Below is raw OCR text, which may contain minor OCR errors (misread characters, broken lines).

Numbers in this document may use a COMMA as the decimal separator (e.g. "22,45" means 22.45,
not 2245). Always convert such numbers to standard decimal format with a period.

This invoice may contain MULTIPLE line items. Extract ALL of them, not just the first.

Also identify the CURRENCY the amounts are stated in, based on symbols ($, EUR, GBP, INR) or
explicit currency codes/words in the text. Use a 3-letter ISO code: USD, EUR, GBP, or INR.
If genuinely no currency indicator is present, use null - do not assume INR by default.

Return ONLY a valid JSON object (no markdown fences, no explanation) with exactly these fields:
{{
  "vendor": "string or null",
  "currency": "string or null (USD, EUR, GBP, or INR)",
  "line_items": [
    {{ "description": "string", "quantity": "number" }}
  ],
  "price": "number or null (the invoice GRAND TOTAL / total amount due - i.e. 'Total Due', including tax and shipping if shown - digits only, decimal point, no currency symbol)",
  "date": "string or null",
  "invoice_number": "string or null"
}}

If a field isn't present in the text, use null. Do not guess values that aren't there.
If there are no clear line items, return an empty list for line_items.

OCR TEXT:
---
{ocr_text}
---
"""


def extract_structured(ocr_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print("WARNING: could not parse JSON. Raw model output was:")
        print(raw)
        return {}

    # Post-process: sum quantities across all line items, and build a
    # short summary string for the "item" field.
    line_items = result.get("line_items") or []
    total_quantity = sum(li.get("quantity") or 0 for li in line_items)

    descriptions = [li.get("description", "").split(",")[0].strip() for li in line_items if li.get("description")]
    if len(descriptions) > 2:
        item_summary = f"{descriptions[0]}, {descriptions[1]} + {len(descriptions) - 2} more items"
    else:
        item_summary = ", ".join(descriptions) if descriptions else None

    result["item"] = item_summary
    result["quantity"] = total_quantity if line_items else None

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <path_to_image>")
        sys.exit(1)

    path = sys.argv[1]
    text = extract_text(path)

    result = extract_structured(text)
    print(json.dumps(result, indent=2))