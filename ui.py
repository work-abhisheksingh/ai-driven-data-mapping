import streamlit as st
import pandas as pd
from io import StringIO
import json

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Lumber AI",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "hero"

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# --------------------------------------------------
# GLOBAL STYLES
# --------------------------------------------------
st.markdown("""
<style>
html, body, .stApp {
    background-color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
}
.hero {
    height: 100vh;
    background: linear-gradient(135deg, #063f3b 0%, #0f766e 45%, #5eead4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}
.hero-content {
    text-align: center;
    max-width: 900px;
}
.badge {
    padding: 6px 16px;
    border-radius: 999px;
    background: rgba(255,255,255,0.18);
    font-weight: 600;
    margin-bottom: 28px;
    display: inline-block;
}
.hero h1 {
    font-size: 56px;
    font-weight: 900;
}
.hero h1 span {
    color: #5eead4;
}
.hero p {
    font-size: 18px;
    opacity: 0.9;
    margin: 24px 0 40px;
}
.container {
    max-width: 1100px;
    margin: auto;
    padding: 60px 20px;
}
.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 28px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.title {
    font-size: 32px;
    font-weight: 800;
}
.subtitle {
    font-size: 16px;
    color: #374151;
    margin: 16px 0 30px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CANONICAL SCHEMA
# --------------------------------------------------
CANONICAL_SCHEMA = [
    "employee_id",
    "employee_name",
    "work_date",
    "regular_hours",
    "overtime_hours",
    "project_code",
    "client_name",
    "work_location",
    "pay_rate_usd",
    "approval_status"
]

# --------------------------------------------------
# LLM-STYLE SCHEMA MAPPING (SIMULATED)
# --------------------------------------------------
def llm_schema_mapping(client_columns):
    mappings = []
    for col in client_columns:
        c = col.lower()
        if "emp" in c or "id" in c:
            mappings.append((col, "employee_id", 0.92))
        elif "name" in c:
            mappings.append((col, "employee_name", 0.90))
        elif "date" in c:
            mappings.append((col, "work_date", 0.88))
        elif "hour" in c or "hrs" in c:
            mappings.append((col, "regular_hours", 0.85))
        elif "ot" in c:
            mappings.append((col, "overtime_hours", 0.83))
        elif "project" in c or "job" in c:
            mappings.append((col, "project_code", 0.80))
        else:
            mappings.append((col, None, 0.0))
    return mappings

# ==================================================
# HERO
# ==================================================
if st.session_state.step == "hero":
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <div class="badge">✨ AI-First Data Onboarding</div>
            <h1>
                Built for the <span>Back Office</span><br/>
                Trusted by the <span>Crew</span>
            </h1>
            <p>
                Convert arbitrary client timesheets into
                Lumber-ready canonical data with AI-driven mapping.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3,1,3])
    with col2:
        if st.button("Get Started"):
            st.session_state.step = "upload"
            st.rerun()

# ==================================================
# UPLOAD
# ==================================================
elif st.session_state.step == "upload":
    st.markdown('<div class="container"><div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="title">Client Data Upload</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">'
        'Upload any client Excel / CSV. '
        'AI will map it to Lumber canonical schema.'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader("Upload client file", type=["xlsx", "csv"])

    if uploaded:
        st.session_state.uploaded_file = uploaded
        st.success(f"Uploaded: {uploaded.name}")

        if st.button("Analyze & Map"):
            st.session_state.step = "analysis"
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

# ==================================================
# ANALYSIS + CORRECTED FILE + REPORT
# ==================================================
elif st.session_state.step == "analysis":

    uploaded_file = st.session_state.uploaded_file

    # Read file
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # LLM mapping
    mappings = llm_schema_mapping(df.columns)

    # Build canonical DF
    canonical_df = pd.DataFrame(columns=CANONICAL_SCHEMA)
    mapping_report = []

    for src, target, conf in mappings:
        if target:
            canonical_df[target] = df[src]
        mapping_report.append({
            "source_column": src,
            "mapped_to": target,
            "confidence": conf,
            "status": "Mapped" if target else "Unmapped"
        })

    for col in CANONICAL_SCHEMA:
        if col not in canonical_df.columns:
            canonical_df[col] = None

    # Risk
    mapped = len([m for m in mapping_report if m["status"] == "Mapped"])
    total = len(CANONICAL_SCHEMA)
    risk_pct = mapped / total

    st.markdown('<div class="container"><div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">AI Mapping & Risk Analysis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Schema Match", f"{int(risk_pct*100)}%")
    col2.metric("Mapped Fields", mapped)
    col3.metric("Unmapped Fields", total - mapped)

    st.progress(risk_pct)

    if risk_pct > 0.8:
        st.success("Low onboarding risk")
    elif risk_pct > 0.5:
        st.warning("Medium onboarding risk")
    else:
        st.error("High onboarding risk")

    st.subheader("Schema Mapping Report")
    st.dataframe(pd.DataFrame(mapping_report))

    # Downloads
    csv_buf = StringIO()
    canonical_df.to_csv(csv_buf, index=False)

    st.download_button(
        "⬇ Download Corrected (Mapped) File",
        csv_buf.getvalue(),
        file_name="canonical_mapped.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇ Download Mapping Report (JSON)",
        json.dumps(mapping_report, indent=2),
        file_name="mapping_report.json",
        mime="application/json"
    )

    if st.button("Upload Another File"):
        st.session_state.step = "upload"
        st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)
