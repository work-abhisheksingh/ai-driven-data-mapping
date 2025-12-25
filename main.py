import os
import sys
import json

# --------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH (VERY IMPORTANT)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# --------------------------------------------------
# INTERNAL IMPORTS
# --------------------------------------------------
from core.file_reader import read_client_file
from ai.prompt_builder import build_prompt
from ai.schema_matcher import apply_schema_mapping
from ai.risk_engine import calculate_risk

# --------------------------------------------------
# MAIN ORCHESTRATOR
# --------------------------------------------------
def process_uploaded_file(uploaded_file, ai_response=None):
    # 1. Read client file
    df = read_client_file(uploaded_file)

    # 2. Build AI prompt
    prompt = build_prompt(list(df.columns))

    # 3. DEMO MODE AI RESPONSE (replace with ChatGPT later)
    if ai_response is None:
        ai_response = {
            "column_mapping": {},
            "missing_fields": [],
            "extra_fields": [],
            "confidence_score": 0.0
        }

    # 4. Apply AI schema mapping
    canonical_df = apply_schema_mapping(df, ai_response)

    # 5. Save canonical output
    os.makedirs("data/canonical", exist_ok=True)
    base = os.path.splitext(uploaded_file.name)[0]
    canonical_path = f"data/canonical/canonical_{base}.csv"
    canonical_df.to_csv(canonical_path, index=False)

    # 6. Calculate risk
    risk = calculate_risk(canonical_df)

    return {
        "canonical_path": canonical_path,
        "risk": risk,
        "prompt": prompt
    }
