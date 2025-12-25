def build_schema_mapping_prompt(client_columns, canonical_columns):
    return f"""
You are a data schema expert.

Your task is to map client data columns to Lumber's canonical schema.

Client columns:
{client_columns}

Canonical schema:
{canonical_columns}

Rules:
- One client column can map to only one canonical column
- If no suitable mapping exists, return null
- Return confidence score (0 to 1)

Return output strictly in JSON:

{{
  "mappings": [
    {{
      "source_column": "...",
      "target_column": "...",
      "confidence": 0.0
    }}
  ]
}}
"""
