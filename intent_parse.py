"""
Intent Parsing Agent - the request-path equivalent of extract_test.py.
Takes a plain-language request and returns the same structured shape,
so it can flow through the same policy_check.py / run_pipeline.py code
already built for the document path.

Usage:
    python intent_parse.py "5 laptops for new interns"

Note: price is left null here - the next step (catalog lookup) will
fill it in from real item prices instead of letting the LLM guess.
"""
import sys
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT_TEMPLATE = """You are parsing a plain-language business message for an automation system.

First, decide: is this a NEW REQUEST asking for something to be done (e.g. ordering
items, raising an approval, asking for an action)? Or is it something else - a
statement about something already completed/approved, a status update, a question,
or unrelated text? Only genuine new requests should be processed further.

Return ONLY a valid JSON object (no markdown fences, no explanation) with exactly these fields:
{{
  "is_new_request": "true or false",
  "reason": "one short sentence explaining the classification",
  "item": "string or null (the item/product being requested - null if not a new request)",
  "quantity": "number or null",
  "department": "string or null (if mentioned or clearly implied, e.g. 'IT' for laptops)",
  "requester": "string or null (if mentioned)",
  "notes": "string or null (any other relevant detail, e.g. destination, urgency)"
}}

Do not guess a price - that will be looked up separately from a catalog.
If a field isn't present or implied in the text, use null.

MESSAGE TEXT:
---
{request_text}
---
"""


def parse_intent(request_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(request_text=request_text)
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

    result["source_type"] = "request"
    if not result.get("is_new_request"):
        print(f"NOTE: classified as NOT a new request - {result.get('reason')}")
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python intent_parse.py "your request text here"')
        sys.exit(1)

    text = sys.argv[1]
    result = parse_intent(text)
    print(json.dumps(result, indent=2))