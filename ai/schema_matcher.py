import pandas as pd
from google import genai
from google.genai import types
import json
import os

# --------------------------------------------------
# CONFIGURATION & MEMORY PATH
# --------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDFzCr5C_ZxK1VsOdktllqqzCHtTpq_zx0")
client = genai.Client(api_key=API_KEY)
MEMORY_FILE = "mapping_memory.json"

LUMBER_SCHEMA = [
    "employee_id", "employee_name", "work_date", "regular_hours", 
    "overtime_hours", "project_code", "client_name", 
    "work_location", "pay_rate_usd", "approval_status"
]

# --------------------------------------------------
# MEMORY HELPERS (The "Learning" Part)
# --------------------------------------------------
def load_memory():
    """Loads previously learned mappings from a local JSON file."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_to_memory(source_col, target_field):
    """Saves a new learned rule to the local memory."""
    if source_col == "-- Skip / Null --":
        return
        
    memory = load_memory()
    # Normalize key to lowercase for robust matching
    memory[source_col.lower().strip()] = target_field
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

# --------------------------------------------------
# AI LOGIC (FOR DROPDOWNS)
# --------------------------------------------------
def get_ai_suggestions(df):
    """
    AI Engine: Analyzes headers and sample rows to predict mapping.
    Uses 'Few-Shot Learning' by injecting past memory into the prompt.
    """
    model_id = "gemini-1.5-flash" 
    client_headers = df.columns.tolist()
    # Analyzing 10 rows provides better pattern recognition for data types
    sample_data = df.head(10).to_dict(orient='records')
    past_knowledge = load_memory()

    response_schema = {
        "type": "OBJECT",
        "properties": {field: {"type": "STRING"} for field in LUMBER_SCHEMA},
        "required": LUMBER_SCHEMA
    }

    prompt = f"""
    ROLE: Senior Payroll Integration Engineer at LumberFi.
    TASK: Map client CSV headers to Lumber Canonical Schema.
    
    KNOWLEDGE FROM PAST SESSIONS (LEARNED RULES):
    {json.dumps(past_knowledge, indent=2)}

    GUIDELINES:
    - employee_id: Look for 'ID', 'Emp #', 'Employee Number', 'Clock No'.
    - regular_hours: Numerical values usually <= 40. Look for 'ST', 'Reg', 'Worked'.
    - overtime_hours: Smaller values. Look for 'OT', 'Premium', '1.5x'.
    - project_code: Look for 'Job', 'Phase', 'Cost Code', 'Project'.
    
    INPUT:
    - Headers: {client_headers}
    - Sample Data: {sample_data}

    RULES:
    1. PRIORITIZE "Learned Rules" provided above. If a header matches a learned rule, use it.
    2. ANALYZE sample data values if header is generic (e.g., 'Col 1', 'Data').
    3. If no match is found for a field, return "null".
    4. Return ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=response_schema,
                temperature=0.1 # Low temperature ensures consistency
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        return apply_manual_logic(client_headers)

# --------------------------------------------------
# MANUAL LOGIC (FOR DROPDOWNS)
# --------------------------------------------------
def apply_manual_logic(client_headers):
    """Heuristic matching based on string similarity and memory."""
    mapping = {}
    memory = load_memory()
    
    for field in LUMBER_SCHEMA:
        match = None
        clean_field = field.replace("_", "").lower()
        
        for col in client_headers:
            clean_col = str(col).lower().strip()
            
            # 1. Check Memory first
            if memory.get(clean_col) == field:
                match = col
                break
            
            # 2. Check String similarity fallback
            clean_col_no_space = clean_col.replace(" ", "").replace("_", "")
            if clean_field in clean_col_no_space or clean_col_no_space in clean_field:
                match = col
                break
                
        mapping[field] = match
    return mapping

# --------------------------------------------------
# DATA PROCESSING (FOR main.py)
# --------------------------------------------------
def apply_schema_mapping(df, mapping_payload):
    """Final transformation of source data into Lumber schema."""
    final_df = pd.DataFrame(index=df.index, columns=LUMBER_SCHEMA)
    mappings = mapping_payload.get("mappings", [])
    
    for item in mappings:
        src = item.get("source_column")
        tgt = item.get("target_column")
        
        if src in df.columns and tgt in LUMBER_SCHEMA:
            final_df[tgt] = df[src]
            
    return final_df