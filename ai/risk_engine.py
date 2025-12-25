from core.canonical_schema import LUMBER_SCHEMA

def calculate_risk(df):
    expected = set(LUMBER_SCHEMA.keys())
    actual = set(df.columns)

    missing = expected - actual
    extra = actual - expected
    null_pct = round(df.isnull().mean().mean() * 100, 2)

    risk_score = len(missing)*3 + len(extra)*2 + (null_pct/10)

    if risk_score < 5:
        level = "LOW"
    elif risk_score < 10:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "missing_columns": list(missing),
        "extra_columns": list(extra),
        "null_percentage": null_pct,
        "risk_level": level
    }
