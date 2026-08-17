"""
Standalone extraction test - takes the raw OCR text from ocr_test.py and
asks Gemini to turn it into structured JSON matching our case schema.

Run this by itself first, same as ocr_test.py, before wiring it into the
pipeline.

Usage:
    python extract_test.py sample_docs/invoice1.jpg
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

Return ONLY a valid JSON object (no markdown fences, no explanation) with exactly these fields:
{{
  "vendor": "string or null",
  "item": "string or null (main item/product description - if there are multiple line items, use the first one)",
  "quantity": "number or null (quantity of the main item above)",
  "price": "number or null (the invoice GRAND TOTAL / total amount due, not a single line item price - digits only, decimal point, no currency symbol)",
  "date": "string or null",
  "invoice_number": "string or null"
}}

If a field isn't present in the text, use null. Do not guess values that aren't there.

OCR TEXT:
---
{ocr_text}
---
"""


def extract_structured(ocr_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    # Gemini sometimes wraps output in ```json fences despite instructions - strip them
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("WARNING: could not parse JSON. Raw model output was:")
        print(raw)
        return {}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_test.py <path_to_image>")
        sys.exit(1)

    path = sys.argv[1]
    text = extract_text(path)

    result = extract_structured(text)
    print(json.dumps(result, indent=2))