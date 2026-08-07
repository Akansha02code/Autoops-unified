# Shared case schema

Every case - whether it started as a document or a natural-language request -
gets normalized into this shape before it reaches the Policy Agent.
Fill this in properly before writing agent code; every agent downstream
reads and writes this shape.

```json
{
  "case_id": "string (uuid)",
  "source_type": "document | request",
  "item": "string",
  "quantity": "number",
  "department": "string",
  "destination": "string (optional, logistics only)",
  "price": "number",
  "requester": "string",
  "status": "pending_extraction | pending_policy_check | pending_approval | approved | rejected | executed",
  "policy_flags": ["string"],
  "created_at": "timestamp",
  "approved_by": "string (optional)"
}
```

## Policy rules (data, not code)

Store as `docs/policy_rules.json` so the Policy Agent just reads a file/table
instead of having rules hardcoded in Python. Start with 3-5 rules, not all 20:

```json
[
  { "id": "cfo_threshold", "condition": "price > 50000", "action": "require_cfo_approval" },
  { "id": "air_cargo_weight", "condition": "transport_mode == 'air' && weight_kg > 3000", "action": "suggest_rail" }
]
```
