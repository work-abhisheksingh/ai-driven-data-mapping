import google.generativeai as genai
import json

# Yahan apni Gemini API Key daalein
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def build_prompt(client_columns):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    canonical_columns = [
        "employee_id", "employee_name", "work_date", "regular_hours", 
        "overtime_hours", "project_code", "client_name", 
        "work_location", "pay_rate_usd", "approval_status"
    ]

    prompt = f"""
    You are a data mapping expert. Map these client headers to Lumber's canonical schema.
    Client Headers: {client_columns}
    Lumber Schema: {canonical_columns}

    Return ONLY a JSON object with this structure:
    {{
      "mappings": [
        {{"source_column": "actual_header", "target_column": "lumber_header", "confidence": 0.95}}
      ]
    }}
    """
    
    response = model.generate_content(prompt)
    # Safely parse JSON from response
    try:
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return {"mappings": []}