import pandas as pd

def read_client_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".xlsx"):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            # Encoding handling for messy client files
            return pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")