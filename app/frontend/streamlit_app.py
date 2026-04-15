import base64
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.backend.models import SearchRequest
from app.backend.service import get_bha_connections, get_filter_options, get_search_engine

st.set_page_config(page_title="DS-1 Standard Data Extractor", layout="wide")


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception:
        return None


current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "logo.png")
logo_b64 = get_base64_image(logo_path)

# --- START OF UI THEME ---
st.markdown("""
<style>
/* 1. Main Backgrounds */
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
.stApp { background: #152033; color: #FFFFFF; } 
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1300px; }

/* 2. Topbar */
.ds-topbar {
    background: #233453; 
    border: 1px solid #3b4e73;
    border-bottom: 4px solid transparent;
    border-image: linear-gradient(to right, #FFCC00, #22C55E) 1; 
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 18px;
}
.ds-brand { display: flex; align-items: center; gap: 14px; }
.ds-logo-fallback {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #FFCC00 0%, #22C55E 100%);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #152033; font-size: 18px;
}
.ds-logo-img { height: 50px; width: auto; object-fit: contain; border-radius: 8px; }
.ds-title { font-size: 28px; font-weight: 700; color: white; }
.ds-subtitle { color: #aab7d1; font-size: 14px; }

/* 3. Cards */
.card, .result-card {
    background: #233453 !important; 
    border: 1px solid #3b4e73 !important;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
}
.result-card { border-left: 4px solid #22C55E !important; } 
.ref-box {
    background-color: #1a273f;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #FFCC00; 
}

/* 4. Ensure button text is dark navy so it's readable on Yellow */
button[kind="primary"] p {
    color: #152033 !important;
    font-weight: 800 !important;
}

/* 5. Inputs / Dropdowns */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: #152033 !important;
    border: 1px solid #3b4e73 !important;
    color: white !important;
}
input, textarea { color: white !important; }
th { background-color: #1a273f !important; color: #FFCC00 !important; }
</style>
""", unsafe_allow_html=True)
# --- END OF UI THEME ---

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="ds-logo-img" alt="DS-1 Logo">'
else:
    logo_html = '<div class="ds-logo-fallback">DS</div>'

st.markdown(f"""
<div class="ds-topbar">
    <div class="ds-brand">
        {logo_html}
        <div>
            <div class="ds-title">DS-1 Standard Data Extractor</div>
            <div class="ds-subtitle">Component-specific search for DS-1 Volume 3 and Volume 4</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_filter_options():
    return get_filter_options()


@st.cache_data(show_spinner=False)
def load_bha_connections():
    return get_bha_connections()


@st.cache_resource(show_spinner="Loading DS-1 search engine...")
def load_search_engine():
    return get_search_engine()


def run_search(payload: dict):
    request = SearchRequest(**payload)
    return load_search_engine().search(request).model_dump()


def render_result(res: dict):
    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    st.markdown(f"### {res.get('heading') or 'Result'}")
    meta_cols = st.columns(5)
    meta_cols[0].write(f"**Type:** {res.get('result_type', '')}")
    meta_cols[1].write(f"**Volume:** {res.get('volume', '')}")
    meta_cols[2].write(f"**Page:** {res.get('page_number', '')}")
    meta_cols[3].write(f"**Clause:** {res.get('clause') or 'N/A'}")
    meta_cols[4].write(f"**Confidence:** {res.get('confidence', '')}")

    if res.get("result_type") == "table" and res.get("table"):
        df = pd.DataFrame(res["table"])
        st.dataframe(df, use_container_width=True)
        if res.get("markdown_table"):
            with st.expander("Show markdown table"):
                st.code(res["markdown_table"], language="markdown")

    elif res.get("result_type") == "text" and res.get("text"):
        st.text_area("Extracted text", res["text"], height=300)

    else:
        st.markdown(
            f"""
            <div class="ref-box">
                <b>Reference only:</b><br>
                Volume: {res.get('volume', '')}<br>
                Page: {res.get('page_number', '')}<br>
                Clause: {res.get('clause') or 'N/A'}
            </div>
            """,
            unsafe_allow_html=True
        )

    if res.get("page_ref"):
        st.caption(f"Page reference: {res.get('page_ref')}")
    if res.get("notes"):
        st.caption(res["notes"])

    st.markdown("</div>", unsafe_allow_html=True)


try:
    filter_options = load_filter_options()
    bha_connections = load_bha_connections()
except Exception as e:
    st.error(f"Could not load backend options: {e}")
    st.stop()

vol1, vol2, vol3 = st.columns([1, 1, 1])
with vol1:
    if st.button("DS-1 Volume 3", use_container_width=True, type="primary"):
        st.session_state["selected_volume"] = "vol3"
with vol2:
    if st.button("DS-1 Volume 4", use_container_width=True, type="primary"):
        st.session_state["selected_volume"] = "vol4"
with vol3:
    if st.button("Both Volumes", use_container_width=True, type="primary"):
        st.session_state["selected_volume"] = "all"

selected_volume = st.session_state.get("selected_volume", "all")
st.caption(f"Selected volume: {selected_volume.upper()}")

tabs = st.tabs(["Drill Pipe", "HWDP", "BHA", "Free Text"])

with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Drill Pipe")

    dp_size = st.selectbox("Size *", [""] + filter_options["sizes"], key="dp_size")
    dp_weight = st.selectbox("Weight (ppf)", [""] + filter_options["weights_ppf"], key="dp_weight")
    
    # Custom Grade Logic
    grade_options = [""] + filter_options["grades"] + ["Other (Type Custom)"]
    dp_grade_selection = st.selectbox("Grade", grade_options, key="dp_grade_selection")
    
    if dp_grade_selection == "Other (Type Custom)":
        dp_grade = st.text_input("Type Custom Grade (e.g. V150, Z140)", key="dp_grade_custom")
    else:
        dp_grade = dp_grade_selection

    dp_conn = st.selectbox("Connection Type *", [""] + filter_options["connection_types"], key="dp_conn")

    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        dp_reduced_tsr = st.checkbox("Premium Class-Reduced TSR (Clause 3.7.26)", key="dp_reduced_tsr")
    with col_cb2:
        dp_twdp = st.checkbox("TWDP - Thick Walled Drill Pipe (Clause 3.8)", key="dp_twdp")

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        dp_clause = st.text_input("Target Clause (e.g. 3.7.1) [Optional]", value="", key="dp_clause")
    with col_opt2:
        dp_query = st.text_input("Optional free-text", value="", key="dp_query")

    if st.button("Search Drill Pipe", key="btn_dp", type="primary"):
        missing = []
        if not dp_size:
            missing.append("Size")
        if not dp_conn:
            missing.append("Connection Type")

        if dp_reduced_tsr and dp_twdp:
            st.warning("Please select either Reduced TSR or TWDP, not both.")
        elif missing:
            st.warning(f"Please select: {', '.join(missing)}")
        else:
            payload = {
                "volume": selected_volume if selected_volume != "vol4" else "vol3",
                "search_mode": "drill_pipe_dimensional",
                "component_type": "drill pipe",
                "size": dp_size,
                "weight_ppf": dp_weight or None,
                "connection_type": dp_conn,
                "grade": dp_grade or None,
                "reduced_tsr": dp_reduced_tsr,
                "twdp": dp_twdp,
                "target_clause": dp_clause or None,
                "query": dp_query or None,
                "top_k": 5
            }
            try:
                data = run_search(payload)
                st.write(f"**Interpreted query:** {data.get('query_interpreted', '')}")
                if data.get("message"):
                    st.warning(data["message"])
                for r in data.get("results", []):
                    render_result(r)
            except Exception as e:
                st.error(f"Search failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("HWDP")

    hwdp_size = st.selectbox(
        "Size *",
        [""] + filter_options.get("hwdp_sizes", []),
        key="hwdp_size"
    )

    hwdp_conn = st.selectbox(
        "Connection Type *",
        [""] + filter_options.get("hwdp_connection_types", []),
        key="hwdp_conn"
    )

    hwdp_center_pad_map = filter_options.get("hwdp_center_pad_map", {})
    center_pad_options = hwdp_center_pad_map.get(hwdp_size, [])

    hwdp_center_pad_od = st.selectbox(
        "Center Pad / Center Upset OD *",
        [""] + center_pad_options,
        key="hwdp_cpod"
    )

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        hwdp_clause = st.text_input(
            "Target Clause (e.g. 3.10.1) [Optional]",
            value="",
            key="hwdp_clause"
        )
    with col_opt2:
        hwdp_query = st.text_input(
            "Optional free-text",
            value="",
            key="hwdp_query"
        )

    if st.button("Search HWDP", key="btn_hwdp", type="primary"):
        missing = []
        if not hwdp_size:
            missing.append("Size")
        if not hwdp_conn:
            missing.append("Connection Type")
        if not hwdp_center_pad_od:
            missing.append("Center Pad / Center Upset OD")

        if missing:
            st.warning(f"Please select: {', '.join(missing)}")
        else:
            payload = {
                "volume": selected_volume if selected_volume != "vol4" else "vol3",
                "search_mode": "hwdp_dimensional",
                "component_type": "hwdp",
                "size": hwdp_size,
                "connection_type": hwdp_conn,
                "center_pad_od": hwdp_center_pad_od,
                "target_clause": hwdp_clause or None,
                "query": hwdp_query or None,
                "top_k": 5
            }
            try:
                data = run_search(payload)
                st.write(f"**Interpreted query:** {data.get('query_interpreted', '')}")
                if data.get("message"):
                    st.warning(data["message"])
                for r in data.get("results", []):
                    render_result(r)
            except Exception as e:
                st.error(f"Search failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("BHA")

    bha_mode = st.radio(
        "Mode",
        ["Used BHA connection acceptance criteria", "General BHA search"],
        horizontal=True
    )
    bha_size = st.selectbox("OD / Size *", [""] + filter_options["sizes"], key="bha_size")
    bha_conn = st.selectbox("Connection Type *", [""] + bha_connections, key="bha_conn")

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        bha_clause = st.text_input("Target Clause (e.g. 3.9) [Optional]", value="", key="bha_clause")
    with col_opt2:
        bha_query = st.text_input("Optional free-text", value="", key="bha_query")

    if st.button("Search BHA", key="btn_bha", type="primary"):
        missing = []
        if not bha_size:
            missing.append("OD / Size")
        if not bha_conn:
            missing.append("Connection Type")

        if missing:
            st.warning(f"Please select: {', '.join(missing)}")
        else:
            payload = {
                "volume": selected_volume if selected_volume != "vol3" else "vol4",
                "search_mode": "bha_acceptance" if "Used" in bha_mode else "bha_general",
                "component_type": "bha",
                "size": bha_size,
                "connection_type": bha_conn,
                "target_clause": bha_clause or None,
                "query": bha_query or None,
                "used_bha_acceptance_only": ("Used" in bha_mode),
                "top_k": 5
            }
            try:
                data = run_search(payload)
                st.write(f"**Interpreted query:** {data.get('query_interpreted', '')}")
                if data.get("message"):
                    st.warning(data["message"])
                for r in data.get("results", []):
                    render_result(r)
            except Exception as e:
                st.error(f"Search failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Free Text / Procedures / Clauses")

    ft_query = st.text_input(
        "Search query",
        placeholder="e.g. stabilizer ring gauge inspection criteria",
        key="ft_query"
    )

    if st.button("Search Free Text", key="btn_ft", type="primary"):
        payload = {
            "volume": selected_volume,
            "search_mode": "free_text",
            "query": ft_query or None,
            "top_k": 5
        }
        try:
            data = run_search(payload)
            st.write(f"**Interpreted query:** {data.get('query_interpreted', '')}")
            if data.get("message"):
                st.warning(data["message"])
            for r in data.get("results", []):
                render_result(r)
        except Exception as e:
            st.error(f"Search failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
