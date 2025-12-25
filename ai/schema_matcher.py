def apply_schema_mapping(df, ai_response):
    mapping = ai_response.get("column_mapping", {})
    missing = ai_response.get("missing_fields", [])

    df = df.rename(columns=mapping)

    for field in missing:
        if field not in df.columns:
            df[field] = None

    return df
