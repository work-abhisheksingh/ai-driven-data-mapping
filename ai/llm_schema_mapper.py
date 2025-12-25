def map_schema_with_llm(client_columns, canonical_columns):
    """
    DEMO MODE: Simulated LLM response
    """

    mappings = []

    for col in client_columns:
        col_lower = col.lower()

        if "emp" in col_lower:
            mappings.append((col, "employee_id", 0.92))
        elif "name" in col_lower:
            mappings.append((col, "employee_name", 0.90))
        elif "date" in col_lower:
            mappings.append((col, "work_date", 0.88))
        elif "hour" in col_lower or "hrs" in col_lower:
            mappings.append((col, "regular_hours", 0.85))
        elif "ot" in col_lower:
            mappings.append((col, "overtime_hours", 0.83))
        elif "project" in col_lower or "job" in col_lower:
            mappings.append((col, "project_code", 0.80))
        else:
            mappings.append((col, None, 0.0))

    return mappings
