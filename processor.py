import pandas as pd
import os
from validator import validate_file

def process_file(input_path, output_dir, canonical_dir):
    validation = validate_file(input_path)
    if not validation["valid"]:
        return f"Validation failed: {validation['reason']}"

    df = pd.read_excel(input_path)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(canonical_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(input_path))[0]

    output_path = f"{output_dir}/processed_{base}.csv"
    canonical_path = f"{canonical_dir}/canonical_{base}.csv"

    df.to_csv(output_path, index=False)
    df.to_csv(canonical_path, index=False)

    return f"Processing complete. Output generated successfully."
