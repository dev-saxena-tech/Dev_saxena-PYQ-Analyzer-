import streamlit as st
import os
import glob
import subprocess
import json

st.set_page_config(page_title="PYQ Analyzer", layout="centered", page_icon="📘", initial_sidebar_state="expanded")

# ── Enhanced Dark CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #0d0d0f !important;
    color: #c8c8d0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Subtle noise texture overlay on main */
[data-testid="stMain"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── Force sidebar always visible, hide collapse button ── */
[data-testid="stSidebar"] {
    background-color: #0b0f1a !important;
    border-right: 1px solid #141c2e !important;
    padding-top: 0 !important;
    min-width: 240px !important;
    max-width: 240px !important;
    transform: none !important;
    visibility: visible !important;
    display: block !important;
}

/* Hide the collapse/expand arrow button */
[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* Also hide any chevron/arrow that toggles sidebar */
section[data-testid="stSidebar"] > div:first-child > div > button,
.st-emotion-cache-1cypcdb,
[data-testid="baseButton-headerNoPadding"] {
    display: none !important;
}

[data-testid="stSidebarContent"] {
    padding: 0 !important;
}

/* Sidebar top accent bar */
[data-testid="stSidebar"]::before {
    content: '';
    display: block;
    height: 3px;
    width: 100%;
    background: linear-gradient(90deg, #1a3a6e, #2d6be4, #1a3a6e);
    background-size: 200% 100%;
    animation: shimmer 3s ease infinite;
}

@keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Sidebar title */
[data-testid="stSidebarContent"] h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.35rem !important;
    color: #e8e8f0 !important;
    letter-spacing: 0.01em !important;
    padding: 1.5rem 1.25rem 0.5rem !important;
    margin-bottom: 1rem !important;
    border-bottom: 1px solid #141c2e !important;
}

/* Sidebar label */
[data-testid="stSidebarContent"] label,
[data-testid="stSidebarContent"] p {
    color: #5a5a6e !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-weight: 600 !important;
}

/* Radio buttons */
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 0.6rem 1.25rem !important;
    color: #8888a0 !important;
    font-size: 0.875rem !important;
    text-transform: none !important;
    letter-spacing: 0.01em !important;
    font-weight: 400 !important;
    border-radius: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    border-left: 2px solid transparent !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #c8c8d8 !important;
    background: rgba(30, 79, 194, 0.06) !important;
    border-left-color: #1e4fc2 !important;
}

/* Active radio option */
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio input:checked ~ label {
    color: #e0e0f0 !important;
    border-left-color: #2a5dcc !important;
    background: rgba(30, 79, 194, 0.1) !important;
}

/* Hide radio circles */
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
}

/* ── Headings ── */
h1 {
    font-family: 'DM Serif Display', serif !important;
    color: #e8e8f0 !important;
    font-size: 2.6rem !important;
    letter-spacing: -0.02em !important;
    line-height: 1.15 !important;
    margin-bottom: 0.25rem !important;
}

h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    color: #d0d0e0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    color: #c8c8d8 !important;
    border: 1px solid #121e30 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(30,79,194,0.12), rgba(45,107,228,0.08));
    opacity: 0;
    transition: opacity 0.2s ease;
}

.stButton > button:hover {
    border-color: #1e4fc2 !important;
    color: #e8e8f8 !important;
    box-shadow: 0 0 18px rgba(30, 79, 194, 0.18) !important;
}

.stButton > button:hover::before {
    opacity: 1 !important;
}

/* Primary CTA button */
.stButton > button[kind="primary"],
.stButton > button:first-child {
    background: linear-gradient(135deg, #0f3580, #1a4caa) !important;
    border-color: transparent !important;
    color: #fff !important;
    box-shadow: 0 2px 20px rgba(15, 53, 128, 0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1845b8, #2255c8) !important;
    box-shadow: 0 4px 28px rgba(15, 53, 128, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Text inputs ── */
.stTextInput input {
    background-color: #0b0f1a !important;
    color: #d0d0e0 !important;
    border: 1px solid #12202e !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput input:focus {
    border-color: #1e4fc2 !important;
    box-shadow: 0 0 0 3px rgba(30, 79, 194, 0.12) !important;
    outline: none !important;
}

.stTextInput label {
    color: #5a5a70 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
    margin-bottom: 0.4rem !important;
}


/* Suppress native file input text bleed */
[data-testid="stFileUploader"] input[type="file"] {
    opacity: 0 !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background-color: #090d18 !important;
    border: 1px solid #0f1c2e !important;
    border-left: 3px solid #1e4fc2 !important;
    border-radius: 6px !important;
    color: #6a8fc8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Home page feature cards ── */
.feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin: 2rem 0;
}

.feature-card {
    background: #0b1020;
    border: 1px solid #101828;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
}

.feature-card:hover {
    border-color: #0f2040;
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.feature-card .icon {
    font-size: 1.5rem;
    margin-bottom: 0.6rem;
    display: block;
}

.feature-card .title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #d0d0e4;
    margin-bottom: 0.3rem;
}

.feature-card .desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    color: #55556a;
    line-height: 1.5;
}

.hero-badge {
    display: inline-block;
    background: rgba(30, 79, 194, 0.12);
    border: 1px solid rgba(30, 79, 194, 0.25);
    color: #4a82e8;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}

.hero-sub {
    color: #55556a !important;
    font-size: 0.95rem !important;
    line-height: 1.65 !important;
    margin-bottom: 2rem !important;
    max-width: 480px;
}

.divider {
    border: none;
    border-top: 1px solid #0e1828;
    margin: 2rem 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0d0f; }
::-webkit-scrollbar-thumb { background: #12202e; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #1a2e4a; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- Simple Login Authentication ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_form():
    st.title("🔒 Login to PYQ Analyzer")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "demo" and password == "pass123":
            # Delete all PDFs from Upload folder
            upload_dir = os.path.join(os.getcwd(), "Upload")
            if os.path.exists(upload_dir):
                for pdf_file in glob.glob(os.path.join(upload_dir, "*.pdf")):
                    os.remove(pdf_file)
            
            st.session_state.logged_in = True
            st.success("Login successful! Please wait...")
            st.rerun()
        else:
            st.error("Invalid username or password")

if not st.session_state.logged_in:
    login_form()
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📘 PYQ Analyzer")

if "navigate_to_upload" in st.session_state and st.session_state.navigate_to_upload:
    st.session_state["page"] = "📂 Upload PDFs"
    st.session_state.navigate_to_upload = False

if "navigate_to_analysis" in st.session_state and st.session_state.navigate_to_analysis:
    st.session_state["page"] = "📊 Analysis Results"
    st.session_state.navigate_to_analysis = False

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📂 Upload PDFs", "📊 Analysis Results"],
    key="page"
)

# ---------------- HOME PAGE ----------------
if page == "🏠 Home":

    st.markdown('<div class="hero-badge">✦ Smart Study Platform</div>', unsafe_allow_html=True)
    st.title("PYQ Analyzer")
    st.markdown('<p class="hero-sub">Stop wasting time on less-tested topics. Surface the questions that actually matter — powered by pattern analysis across multiple years.</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="icon">📄</span>
            <div class="title">Upload Papers</div>
            <div class="desc">Drag in multiple PDFs from any year, any subject.</div>
        </div>
        <div class="feature-card">
            <span class="icon">🔍</span>
            <div class="title">Extract Questions</div>
            <div class="desc">Automatic extraction and deduplication across papers.</div>
        </div>
        <div class="feature-card">
            <span class="icon">📊</span>
            <div class="title">Frequency Analysis</div>
            <div class="desc">See which topics repeat most — ranked by importance.</div>
        </div>
        <div class="feature-card">
            <span class="icon">🧠</span>
            <div class="title">Smart Focus</div>
            <div class="desc">Study what matters. Skip the noise.</div>
        </div>
    </div>
    <hr class="divider">
    """, unsafe_allow_html=True)

    if st.button("🚀 Get Started"):
        st.session_state.navigate_to_upload = True
        st.rerun()

# ---------------- UPLOAD PAGE ----------------
elif page == "📂 Upload PDFs":
    st.title("📂 Upload Question Papers")
    st.markdown("Upload multiple PDF files for analysis")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state["uploaded_files"] = [
            {"name": file.name, "data": file.getvalue()} for file in uploaded_files
        ]

    files_to_show = st.session_state.get("uploaded_files", [])
    if files_to_show:
        st.success(f"{len(files_to_show)} file(s) uploaded successfully!")

        upload_dir = os.path.join(os.getcwd(), "Upload")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file_info in files_to_show:
            st.write(f"📄 {file_info['name']}")
            file_path = os.path.join(upload_dir, file_info['name'])
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(file_info['data'])

    if st.button("🔍 Analyze PDFs"):
        if files_to_show:
            # Run extractor.py in backend
            try:
                result = subprocess.run(
                    ["python", "extractor.py"],
                    cwd=os.getcwd(),
                    capture_output=True,
                    text=True
                )
                st.session_state["extraction_success"] = True
                st.session_state["extraction_message"] = "PDFs extracted successfully! ✅"
                
                # Run parsing.py after successful extraction
                try:
                    parse_result = subprocess.run(
                        ["python", "parsing.py"],
                        cwd=os.getcwd(),
                        capture_output=True,
                        text=True
                    )
                    st.session_state["parsing_success"] = True
                    st.session_state["parsing_message"] = "Questions parsed successfully! ✅"
                    
                    # Run analysis.py after successful parsing
                    try:
                        analysis_result = subprocess.run(
                            ["python", "analysis.py"],
                            cwd=os.getcwd(),
                            capture_output=True,
                            text=True
                        )
                        st.session_state["analysis_success"] = True
                        st.session_state["analysis_message"] = "Questions clustered successfully! ✅"
                    except Exception as analysis_error:
                        st.session_state["analysis_success"] = False
                        st.session_state["analysis_message"] = f"Error clustering questions: {str(analysis_error)}"
                except Exception as parse_error:
                    st.session_state["parsing_success"] = False
                    st.session_state["parsing_message"] = f"Error parsing questions: {str(parse_error)}"
            except Exception as e:
                st.session_state["extraction_success"] = False
                st.session_state["extraction_message"] = f"Error running extraction: {str(e)}"
            
            st.session_state["navigate_to_analysis"] = True
            st.rerun()
        else:
            st.warning("Please upload at least one PDF")

elif page == "📊 Analysis Results":

    # ── CSS ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .metric-strip { display: flex; gap: 14px; flex-wrap: wrap; margin: 18px 0 24px; }
    .metric-card {
        flex: 1; min-width: 130px; background: white; border-radius: 14px;
        padding: 18px 20px; text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-top: 4px solid var(--accent);
    }
    .metric-card .num { font-size: 2em; font-weight: 800; color: var(--accent); }
    .metric-card .lbl { font-size: 0.78em; color: #888; margin-top: 4px; line-height: 1.3; }

    .cluster-card {
        background: white; border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        margin-bottom: 18px; overflow: hidden;
        border-left: 6px solid var(--border-color);
    }
    .cluster-head {
        background: #f8f9fb; padding: 12px 18px;
        display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
        border-bottom: 1px solid #eee;
    }
    .freq-badge {
        padding: 4px 14px; border-radius: 20px;
        font-weight: 700; font-size: 0.8em; color: white;
    }
    .cluster-num { color: #aaa; font-size: 0.83em; }

    .canonical-box {
        margin: 14px 18px 10px;
        background: linear-gradient(135deg, #eaf4ff, #dceefb);
        border-left: 4px solid #2980b9;
        border-radius: 0 10px 10px 0;
        padding: 12px 16px;
        font-size: 1em; font-weight: 600; color: #1a252f; line-height: 1.5;
    }
    .canonical-label {
        font-size: 0.72em; text-transform: uppercase;
        letter-spacing: 1px; color: #2980b9; margin-bottom: 4px;
    }
    .years-line { font-size: 0.8em; color: #999; margin: 6px 18px 10px; }

    .q-list { padding: 0 18px 14px; }
    .q-row {
        display: flex; align-items: flex-start; gap: 10px;
        padding: 9px 12px; border-radius: 8px;
        background: #f8f9fb; border: 1px solid #eee;
        margin-bottom: 6px; font-size: 0.9em; color: #2c3e50;
    }
    .ypill {
        display: inline-block; padding: 2px 9px; border-radius: 12px;
        font-size: 0.75em; font-weight: 700; color: white;
        white-space: nowrap; flex-shrink: 0; margin-top: 1px;
    }

    /* ── Question list (below cards) ── */
    .qlist-section {
        background: white; border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        padding: 0; margin-top: 28px; overflow: hidden;
    }
    .qlist-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #0f3460 100%);
        color: white; padding: 14px 22px;
        font-size: 1.05em; font-weight: 700; letter-spacing: 0.4px;
    }
    .qlist-body { padding: 16px 22px; }
    .qlist-item {
        display: flex; align-items: flex-start; gap: 12px;
        padding: 10px 0; border-bottom: 1px solid #f0f0f0;
        font-size: 0.93em; color: #2c3e50; line-height: 1.5;
    }
    .qlist-item:last-child { border-bottom: none; }
    .qnum {
        font-weight: 800; color: #0f3460; white-space: nowrap;
        min-width: 36px; font-size: 0.95em;
    }
    .qyear {
        font-size: 0.78em; font-weight: 700; color: #888;
        white-space: nowrap; flex-shrink: 0; margin-top: 2px;
    }

    .sec-banner {
        background: linear-gradient(90deg, #1a1a2e 0%, #0f3460 100%);
        color: white; padding: 13px 20px; border-radius: 10px;
        font-size: 1.05em; font-weight: 700;
        margin: 8px 0 16px; letter-spacing: 0.4px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 Analysis Results")

    # ── Guards ────────────────────────────────────────────────────────────────
    if "extraction_success" not in st.session_state:
        st.info("📂 Upload PDFs and click **Analyze PDFs** to see results here.")
        st.stop()
    if not st.session_state["extraction_success"]:
        st.error(st.session_state.get("extraction_message", "Analysis failed."))
        st.stop()

    clustered_file = os.path.join(os.getcwd(), "clustered_questions.json")
    if not os.path.exists(clustered_file):
        st.warning("⚠️ `clustered_questions.json` not found. Please run analysis first.")
        st.stop()

    with open(clustered_file, "r", encoding="utf-8") as f:
        clustered_data = json.load(f)

    summary      = clustered_data.get("summary", clustered_data.get("metadata", {}))
    clusters_2m  = clustered_data.get("SECTION_A_clusters",  [])
    clusters_10m = clustered_data.get("SECTION_BC_clusters", [])

    total_2m   = summary.get("total_section_a_questions",        0)
    total_10m  = summary.get("total_section_bc_questions",       0)
    repeat_2m  = summary.get("section_a_clusters_with_repeats",  0)
    repeat_10m = summary.get("section_bc_clusters_with_repeats", 0)
    total_repeat = repeat_2m + repeat_10m

    # ── Metrics ───────────────────────────────────────────────────────────────
    metrics = [
        ("2-Mark Questions",   total_2m,     "#e74c3c"),
        ("10-Mark Questions",  total_10m,    "#2980b9"),
        ("Repeated Questions", total_repeat, "#e67e22"),
    ]
    cards_html = "".join(
        f'<div class="metric-card" style="--accent:{acc};">'
        f'<div class="num">{num}</div><div class="lbl">{lbl}</div></div>'
        for lbl, num, acc in metrics
    )
    st.markdown(f'<div class="metric-strip">{cards_html}</div>', unsafe_allow_html=True)
    st.divider()

    # ── Helpers ───────────────────────────────────────────────────────────────
    YEAR_COLORS = {"2019": "#e74c3c", "2022": "#2980b9",
                   "2023": "#27ae60", "2024": "#8e44ad"}

    def ypill(year):
        c = YEAR_COLORS.get(str(year), "#7f8c8d")
        return f'<span class="ypill" style="background:{c};">{year}</span>'

    def freq_style(freq):
        if freq >= 4: return "#e74c3c", "🔥 Very High Priority"
        if freq == 3: return "#e67e22", "⚡ High Priority"
        if freq == 2: return "#27ae60", "📌 Repeated"
        return "#95a5a6", "Unique"

    def render_cluster_card(cluster, idx):
        freq      = cluster.get("frequency", 0)
        years     = cluster.get("years", [])
        canonical = cluster.get("canonical_question", "")
        
        color, priority_label = freq_style(freq)
        year_pills = " ".join(ypill(y) for y in years)
        
        st.markdown(f"""
        <div class="cluster-card" style="--border-color:{color};">
          <div class="cluster-head">
            <span class="freq-badge" style="background:{color};">Freq {freq} · {priority_label}</span>
            <span style="margin-left:auto;">{year_pills}</span>
          </div>
          <div class="canonical-box">
            <div class="canonical-label">🎯Question</div>
            {canonical}
          </div>
          <div class="years-line">Asked in: {" · ".join(str(y) for y in years)}</div>
        </div>""", unsafe_allow_html=True)

    def render_question_list(clusters, section_label):
        """Flat numbered list of canonical questions with year tags."""
        items_html = ""
        for i, cluster in enumerate(clusters, 1):
            canon = cluster.get("canonical_question", "")
            years = cluster.get("years", [])
            years_str = ", ".join(str(y) for y in sorted(set(years)))
            items_html += (
                f'<div class="qlist-item">'
                f'<span class="qnum">Q.{i}</span>'
                f'<span style="flex:1;">{canon}</span>'
                f'<span class="qyear">[{years_str}]</span>'
                f'</div>'
            )
        st.markdown(
            f'<div class="qlist-section">'
            f'<div class="qlist-header">{section_label}</div>'
            f'<div class="qlist-body">{items_html}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Combined PDF (2M + 10M in one file) ───────────────────────────────────
    def generate_combined_pdf(clusters_2m, clusters_10m):
        import io
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                 leftMargin=2*cm, rightMargin=2*cm,
                                 topMargin=2*cm,  bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "T", parent=styles["Title"], fontSize=20, spaceAfter=4,
            textColor=colors.HexColor("#0f3460")
        )
        sub_style = ParagraphStyle(
            "S", parent=styles["Normal"], fontSize=10,
            textColor=colors.HexColor("#888888"), spaceAfter=22
        )
        section_style = ParagraphStyle(
            "SEC", parent=styles["Heading1"], fontSize=13,
            spaceBefore=20, spaceAfter=12,
            textColor=colors.HexColor("#0f3460"),
            borderPad=0,
        )
        q_style = ParagraphStyle(
            "Q", parent=styles["Normal"], fontSize=10,
            leftIndent=0, spaceAfter=8, leading=16
        )

        story = [
            Paragraph("Computer Networks", title_style),
            Paragraph("Question Cluster Analysis — All Years", sub_style),
            HRFlowable(width="100%", thickness=1.5,
                       color=colors.HexColor("#0f3460"), spaceAfter=16),
        ]

        # ─ 2-Mark section ─────────────────────────────────────────────────────
        story.append(Paragraph("2-Mark Questions", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor("#cccccc"), spaceAfter=8))
        for idx, cluster in enumerate(clusters_2m, 1):
            canon = cluster.get("canonical_question", "")
            years = sorted(set(str(q.get("year", "")) for q in cluster.get("questions_in_cluster", [])))
            years_str = ", ".join(years)
            story.append(Paragraph(
                f'<b>Q.{idx}</b>&nbsp;&nbsp;{canon}&nbsp;&nbsp;'
                f'<font color="#888888" size="8">[{years_str}]</font>',
                q_style
            ))

        story.append(Spacer(1, 24))

        # ─ 10-Mark section ────────────────────────────────────────────────────
        story.append(Paragraph("10-Mark Questions", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor("#cccccc"), spaceAfter=8))
        for idx, cluster in enumerate(clusters_10m, 1):
            canon = cluster.get("canonical_question", "")
            years = sorted(set(str(q.get("year", "")) for q in cluster.get("questions_in_cluster", [])))
            years_str = ", ".join(years)
            story.append(Paragraph(
                f'<b>Q.{idx}</b>&nbsp;&nbsp;{canon}&nbsp;&nbsp;'
                f'<font color="#888888" size="8">[{years_str}]</font>',
                q_style
            ))

        doc.build(story)
        buf.seek(0)
        return buf.read()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_2m, tab_10m = st.tabs(["📘 2-Mark Questions", "📗 10-Mark Questions"])

    # ─── 2-Mark ───────────────────────────────────────────────────────────────
    with tab_2m:
        st.markdown('<div class="sec-banner">📘 2-Mark Questions — All Clusters</div>',
                    unsafe_allow_html=True)

        # Download combined PDF at the top
        if clusters_2m or clusters_10m:
            pdf_bytes = generate_combined_pdf(clusters_2m, clusters_10m)
            st.download_button(
                "⬇️ Download All Questions PDF (2-Mark + 10-Mark)",
                data=pdf_bytes,
                file_name="all_question_clusters.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)

        # Cluster cards
        if clusters_2m:
            for i, cluster in enumerate(clusters_2m, 1):
                render_cluster_card(cluster, i)
        else:
            st.info("No 2-mark question clusters found.")

        # Flat question list below cards
        if clusters_2m:
            render_question_list(clusters_2m, "📋 2-Mark Questions — Complete List")

    # ─── 10-Mark ──────────────────────────────────────────────────────────────
    with tab_10m:
        st.markdown('<div class="sec-banner">📗 10-Mark Questions — All Clusters</div>',
                    unsafe_allow_html=True)

        # Download combined PDF at the top
        if clusters_2m or clusters_10m:
            pdf_bytes = generate_combined_pdf(clusters_2m, clusters_10m)
            st.download_button(
                "⬇️ Download All Questions PDF (2-Mark + 10-Mark)",
                data=pdf_bytes,
                file_name="PYQ-All-Questions.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)

        # Cluster cards
        if clusters_10m:
            for i, cluster in enumerate(clusters_10m, 1):
                render_cluster_card(cluster, i)
        else:
            st.info("No 10-mark question clusters found.")

        # Flat question list below cards
        if clusters_10m:
            render_question_list(clusters_10m, "📋 10-Mark Questions — Complete List")