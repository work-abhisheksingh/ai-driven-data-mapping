import os
import pandas as pd
from ai.schema_matcher import apply_schema_mapping
from ai.risk_engine import calculate_risk

def process_uploaded_file(df, manual_mapping=None):
    """
    Processes the entire dataframe based on user-selected manual mappings.
    This function ensures that the final output follows the 10-column 
    canonical schema without any static or mock data.
    """
    
    # 1. Capture the manual mapping provided by the UI dropdowns
    if manual_mapping:
        ai_response = manual_mapping
    else:
        # Fallback to empty mappings if none provided
        ai_response = {"mappings": []}

    # 2. Transform the data
    # The matcher uses the uploaded dataframe's index to process ALL rows
    canonical_df = apply_schema_mapping(df, ai_response)

    # 3. Ensure the output directory exists
    output_dir = "data/canonical"
    os.makedirs(output_dir, exist_ok=True)
    
    # 4. Save the full mapped dataset to a CSV file
    path = os.path.join(output_dir, "lumber_final_export.csv")
    canonical_df.to_csv(path, index=False)

    # 5. Calculate data health metrics (Fill Rate and Risk Level)
    risk_metrics = calculate_risk(canonical_df)

    # 6. Return the path for download, metrics for UI, and the dataframe for preview
    return {
        "canonical_path": path,
        "risk": risk_metrics,
        "df": canonical_df
    }