import pandas as pd
from google import genai
from google.genai import types
import json
import os

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDFzCr5C_ZxK1VsOdktllqqzCHtTpq_zx0")
client = genai.Client(api_key=API_KEY)

LUMBER_SCHEMA = [
    "employee_id", "employee_name", "work_date", "regular_hours", 
    "overtime_hours", "project_code", "client_name", 
    "work_location", "pay_rate_usd", "approval_status"
]

# --------------------------------------------------
# AI LOGIC (FOR DROPDOWNS)
# --------------------------------------------------
def get_ai_suggestions(df):
    """
    AI Engine: Analyzes headers and sample rows to predict mapping.
    """
    model_id = "gemini-1.5-flash" 
    client_headers = df.columns.tolist()
    sample_data = df.head(5).to_dict(orient='records')

    response_schema = {
        "type": "OBJECT",
        "properties": {field: {"type": "STRING"} for field in LUMBER_SCHEMA},
        "required": LUMBER_SCHEMA
    }

    prompt = f"""
    ROLE: Lead Payroll Integration Engineer at LumberFi.
    TASK: Map client CSV headers to Lumber Canonical Schema.
    
    GUIDELINES:
    - regular_hours: Values near 40. Look for 'ST', 'Reg', 'Worked'.
    - overtime_hours: Smaller values. Look for 'OT', 'Premium'.
    - project_code: Look for 'Job', 'Phase', 'Cost Code'.
    
    INPUT:
    - Headers: {client_headers}
    - Sample Data: {sample_data}

    RULES:
    1. If a column name is generic (e.g. 'Col 1'), use Sample Data to identify it.
    2. If no match is found, return "null".
    3. Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=response_schema,
                temperature=0.0
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        # Fallback to manual if AI fails
        return apply_manual_logic(client_headers)

# --------------------------------------------------
# MANUAL LOGIC (FOR DROPDOWNS)
# --------------------------------------------------
def apply_manual_logic(client_headers):
    """
    Heuristic matching based on string similarity.
    """
    mapping = {}
    for field in LUMBER_SCHEMA:
        match = None
        clean_field = field.replace("_", "").lower()
        for col in client_headers:
            clean_col = str(col).replace(" ", "").replace("_", "").lower()
            if clean_field in clean_col or clean_col in clean_field:
                match = col
                break
        mapping[field] = match
    return mapping

# --------------------------------------------------
# DATA PROCESSING (FOR main.py)
# --------------------------------------------------
def apply_schema_mapping(df, mapping_payload):
    """
    REQUIRED BY main.py: Transforms raw data into the final 10-column schema.
    """
    final_df = pd.DataFrame(index=df.index, columns=LUMBER_SCHEMA)
    
    # Payload format expected: {"mappings": [{"source_column": "X", "target_column": "Y"}]}
    mappings = mapping_payload.get("mappings", [])
    
    for item in mappings:
        src = item.get("source_column")
        tgt = item.get("target_column")
        
        if src in df.columns and tgt in LUMBER_SCHEMA:
            final_df[tgt] = df[src]
            
    return final_df