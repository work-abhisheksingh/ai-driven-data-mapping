import pandas as pd

def read_client_file(uploaded_file):
    if uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        raise ValueError("Unsupported file format")
