import streamlit as st
import pandas as pd
import os
import io
import time  # Added for progress bar timing
from main import process_uploaded_file
# Added save_to_memory to the imports
from ai.schema_matcher import get_ai_suggestions, apply_manual_logic, save_to_memory

# --------------------------------------------------
# CONFIG & THEME LOADING
# --------------------------------------------------
st.set_page_config(page_title="Lumber AI | Mapping", page_icon="🏗️", layout="wide")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

LUMBER_SCHEMA = [
    "employee_id", "employee_name", "work_date", "regular_hours", 
    "overtime_hours", "project_code", "client_name", 
    "work_location", "pay_rate_usd", "approval_status"
]

# --------------------------------------------------
# NAVIGATION HELPERS
# --------------------------------------------------
def move_to(step_name):
    st.session_state.step = step_name
    st.rerun()

# --------------------------------------------------
# STATE INITIALIZATION
# --------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "hero"
if "client_df" not in st.session_state:
    st.session_state.client_df = None
if "final_result" not in st.session_state:
    st.session_state.final_result = None
if "ai_results" not in st.session_state:
    st.session_state.ai_results = {}
if "manual_results" not in st.session_state:
    st.session_state.manual_results = {}

# --------------------------------------------------
# SCREENS
# --------------------------------------------------

# SCREEN 1: HERO
if st.session_state.step == "hero":
    st.markdown('<div class="hero-section"><h1>Lumber AI <span>Mapping</span></h1><p>Intelligent Construction Payroll Alignment</p></div>', unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.write("")
        if st.button("🚀 Start Onboarding", width="stretch", key="btn_start"):
            move_to("upload")

# SCREEN 2: UPLOAD
elif st.session_state.step == "upload":
    cols = st.columns([1, 8, 1])
    with cols[0]:
        if st.button("⬅️ Back", key="back_hero"): move_to("hero")
    
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.title("📁 Step 1: Upload File")
    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], label_visibility="collapsed", key="file_loader")
    
    if file:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, quotechar="'", skipinitialspace=True)
        else:
            df = pd.read_excel(file)
            
        st.session_state.client_df = df
        st.session_state.ai_results = {} 
        st.session_state.manual_results = {}
        
        st.success(f"Success! Detected **{len(df.columns)}** columns and **{len(df)}** rows.")
        if st.button("Proceed to Mapping →", width="stretch", key="btn_to_map"):
            move_to("mapping")
    st.markdown('</div>', unsafe_allow_html=True)

# SCREEN 3: INTERACTIVE MAPPING
elif st.session_state.step == "mapping":
    cols = st.columns([1, 8, 1])
    with cols[0]:
        if st.button("⬅️ Back", key="back_upload"): move_to("upload")
        
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.title("🎯 Step 2: Configure Mapping")
    
    mode = st.radio("Choose Mapping Engine:", ["AI Suggestion (Gemini)", "Manual Heuristic (String Match)"], horizontal=True, key="engine_mode")
    
    df = st.session_state.client_df
    client_cols = ["-- Skip / Null --"] + df.columns.tolist()
    
    if "AI Suggestion" in mode:
        if not st.session_state.ai_results:
            # PROGRESS BAR IMPLEMENTATION
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
                if percent_complete == 20: status_text.text("🔍 Analyzing headers...")
                if percent_complete == 50: status_text.text("🧠 Consulting Gemini AI...")
                if percent_complete == 80: status_text.text("💾 Applying learned rules...")
            
            st.session_state.ai_results = get_ai_suggestions(df)
            progress_bar.empty()
            status_text.empty()
            
        current_suggestions = st.session_state.ai_results
    else:
        if not st.session_state.manual_results:
            st.session_state.manual_results = apply_manual_logic(df.columns.tolist())
        current_suggestions = st.session_state.manual_results

    user_selections = {}
    c1, c2 = st.columns(2)
    for i, field in enumerate(LUMBER_SCHEMA):
        with (c1 if i % 2 == 0 else c2):
            suggested_col = current_suggestions.get(field)
            idx = client_cols.index(suggested_col) if suggested_col in client_cols else 0
            user_selections[field] = st.selectbox(f"Lumber Field: {field}", options=client_cols, index=idx, key=f"f_{field}_{mode}")

    st.divider()
    if st.button("Confirm Mapping & Process File", width="stretch", key="btn_process"):
        with st.spinner("Learning preferences and processing dataset..."):
            # SELF-LEARNING TRIGGER
            for target, source in user_selections.items():
                if source and source != "-- Skip / Null --":
                    save_to_memory(source, target)

            mapping_payload = {"mappings": [{"source_column": src, "target_column": tgt} for tgt, src in user_selections.items() if src != "-- Skip / Null --"]}
            res = process_uploaded_file(df, manual_mapping=mapping_payload)
            st.session_state.final_result = res
            move_to("analysis")
    st.markdown('</div>', unsafe_allow_html=True)

# SCREEN 4: PREVIEW & EXPORT
elif st.session_state.step == "analysis":
    cols = st.columns([1, 8, 1])
    with cols[0]:
        if st.button("⬅️ Back", key="back_mapping"): 
            move_to("mapping")

    res = st.session_state.final_result
    
    df_display = res['df'].copy()
    if 'S.No' not in df_display.columns:
        df_display.insert(0, 'S.No', range(1, len(df_display) + 1))

    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.title("📊 Step 3: Final Review")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Level", res['risk']['risk_level'])
    m2.metric("Fill Rate", f"{100 - res['risk']['null_percentage']}%")
    m3.metric("Processed Rows", len(res['df']))

    st.write("### Mapped Data Preview")
    
    st.dataframe(
        df_display, 
        width="stretch", 
        hide_index=True, 
        use_container_width=True,
        column_config={
            "S.No": st.column_config.Column("S.No", width="small")
        }
    )

    st.divider()
    col_ex, col_csv = st.columns(2)
    with col_ex:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine='xlsxwriter') as writer:
            df_display.to_excel(writer, index=False)
        st.download_button("⬇️ Excel Export", excel_buf.getvalue(), "mapped.xlsx", width="stretch", key="dl_excel")
        
    with col_csv:
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button("📑 CSV Export", csv_data, "mapped.csv", width="stretch", key="dl_csv")

    if st.button("🔄 Start New Mapping", width="stretch", key="btn_reset"):
        st.session_state.clear() 
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)