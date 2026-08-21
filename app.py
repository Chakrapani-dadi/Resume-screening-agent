"""
app.py
------
A web UI for the Resume Screening Agent, built with Streamlit.

This file does NOT contain any new AI logic - it's purely a frontend that
calls the same functions from parser.py and scorer.py that main.py (the
command-line version) uses. One single source of truth for how scoring
works, whether you run it from the terminal or the browser.

Visual concept: a "case file" / hiring dossier. Each candidate becomes a
case file entry with a stamped verdict, echoing how a recruiter actually
works through a stack of resumes.

Run with:  streamlit run app.py
"""

import os
import html
import tempfile
import pandas as pd
import streamlit as st

from parser import extract_text
from scorer import get_embedding, score_resume, generate_reasoning

st.set_page_config(page_title="Candidate Screening Dossier", page_icon=":file_folder:", layout="wide")


# ---------------------------------------------------------------------------
# DESIGN TOKENS
# Palette: manila / ledger-book, not the default cream+terracotta AI look.
#   paper        #EDE9DE  - main background (muted manila)
#   paper-card   #F8F6EF  - card surfaces, slightly lighter than paper
#   ink          #22261F  - primary text
#   ledger       #2F4A3D  - deep forest green, primary accent / actions
#   ledger-light #3E6350  - hover state for ledger
#   stamp        #B33B24  - rubber-stamp rust red, used sparingly for emphasis
#   tan          #C9AD82  - kraft-folder tan, dividers / tab markers
#   muted-line   #D8D0BC  - hairline borders
# Type:
#   display -> Zilla Slab (ledger/case-file authority)
#   body    -> IBM Plex Sans
#   data    -> IBM Plex Mono (scores, filenames, ranks - like a typed report)
# Signature element: the rotated "stamp" verdict badge on each case card.
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --paper: #EDE9DE;
            --paper-card: #F8F6EF;
            --ink: #22261F;
            --ledger: #2F4A3D;
            --ledger-light: #3E6350;
            --stamp: #B33B24;
            --tan: #C9AD82;
            --muted-line: #D8D0BC;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--paper) !important;
            color: var(--ink);
            font-family: 'IBM Plex Sans', sans-serif;
        }

        [data-testid="stHeader"] { background-color: transparent; }

        /* ---------- Case header banner ---------- */
        .case-header {
            background: var(--ledger);
            color: var(--paper-card);
            padding: 2.2rem 2.5rem 1.8rem 2.5rem;
            border-radius: 4px;
            margin-bottom: 1.75rem;
            border: 1px solid #1E3129;
            position: relative;
        }
        .case-header::after {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: repeating-linear-gradient(90deg, var(--stamp) 0 14px, transparent 14px 24px);
            border-radius: 4px 4px 0 0;
        }
        .case-header-eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #B7C9BE;
            margin-bottom: 0.5rem;
        }
        .case-header-title {
            font-family: 'Zilla Slab', serif;
            font-weight: 700;
            font-size: 2.3rem;
            margin: 0 0 0.5rem 0;
            color: #FBFAF6;
            line-height: 1.1;
        }
        .case-header-sub {
            font-size: 0.95rem;
            max-width: 640px;
            color: #DCE3DE;
            margin: 0;
            line-height: 1.5;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background-color: var(--tan) !important;
            border-right: 1px solid #B79A6E;
        }
        [data-testid="stSidebar"] * { color: var(--ink) !important; }
        [data-testid="stSidebar"] h2 {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.78rem !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border-bottom: 1.5px solid var(--ink);
            padding-bottom: 0.35rem;
            margin-top: 1.4rem !important;
        }
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stSlider label { font-weight: 500; }

        /* ---------- Buttons ---------- */
        .stButton > button {
            background-color: var(--ledger) !important;
            color: var(--paper-card) !important;
            border: 1px solid #1E3129 !important;
            border-radius: 3px !important;
            font-family: 'IBM Plex Mono', monospace !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            font-size: 0.8rem !important;
            padding: 0.6rem 1rem !important;
            transition: background-color 0.15s ease, transform 0.1s ease;
        }
        .stButton > button:hover {
            background-color: var(--ledger-light) !important;
            transform: translateY(-1px);
        }
        .stDownloadButton > button {
            background-color: var(--paper-card) !important;
            color: var(--ink) !important;
            border: 1.5px solid var(--ink) !important;
            border-radius: 3px !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.8rem !important;
        }

        /* ---------- File uploader ---------- */
        [data-testid="stFileUploaderDropzone"] {
            background-color: var(--paper-card) !important;
            border: 1.5px dashed #A18A5E !important;
            border-radius: 3px;
        }

        /* ---------- Progress bar ---------- */
        [data-testid="stProgress"] > div > div > div {
            background-color: var(--stamp) !important;
        }

        /* ---------- Section labels ---------- */
        .section-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--ledger);
            border-bottom: 1.5px solid var(--muted-line);
            padding-bottom: 0.4rem;
            margin: 1.6rem 0 1rem 0;
        }

        /* ---------- Summary ledger table ---------- */
        .ledger-table { width: 100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; }
        .ledger-table th {
            text-align: left; text-transform: uppercase; letter-spacing: 0.08em;
            font-size: 0.7rem; color: #5A5E52; border-bottom: 1.5px solid var(--ink);
            padding: 0.5rem 0.6rem;
        }
        .ledger-table td { padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--muted-line); }
        .ledger-table tr:hover td { background-color: rgba(47,74,61,0.06); }
        .verdict-pill {
            display: inline-block; padding: 0.1rem 0.5rem; border-radius: 2px;
            font-size: 0.68rem; letter-spacing: 0.06em; text-transform: uppercase;
            border: 1px solid currentColor;
        }
        .verdict-strong { color: var(--ledger); }
        .verdict-moderate { color: #8A6C1E; }
        .verdict-weak { color: #8C4436; }

        /* ---------- Case cards ---------- */
        .case-card {
            display: flex;
            background-color: var(--paper-card);
            border: 1px solid var(--muted-line);
            border-left: 5px solid var(--tan);
            border-radius: 3px;
            margin-bottom: 0.9rem;
            box-shadow: 1px 2px 0 rgba(34,38,31,0.05);
        }
        .case-card.tier-strong { border-left-color: var(--ledger); }
        .case-card.tier-moderate { border-left-color: #C79A2E; }
        .case-card.tier-weak { border-left-color: #A16656; }

        .case-card-tab {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: #7A7C6E;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            padding: 0.9rem 0.5rem;
            border-right: 1px dashed var(--muted-line);
            display: flex; align-items: center; justify-content: center;
            letter-spacing: 0.05em;
        }
        .case-card-main { padding: 1rem 1.2rem; flex: 1; }
        .case-card-row {
            display: flex; align-items: flex-start; justify-content: space-between;
            gap: 1rem; margin-bottom: 0.4rem;
        }
        .candidate-name {
            font-family: 'Zilla Slab', serif;
            font-weight: 600;
            font-size: 1.15rem;
            color: var(--ink);
        }
        .case-card-reasoning {
            font-size: 0.92rem;
            line-height: 1.5;
            color: #3A3D33;
            margin: 0.3rem 0 0 0;
        }

        /* Stamp badge - signature element */
        .stamp {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
            font-size: 0.68rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            text-align: center;
            padding: 0.35rem 0.6rem;
            border: 2px double currentColor;
            border-radius: 3px;
            transform: rotate(-3deg);
            white-space: nowrap;
            flex-shrink: 0;
        }
        .stamp-strong { color: var(--ledger); }
        .stamp-moderate { color: #8A6C1E; }
        .stamp-weak { color: #8C4436; }
        .stamp-score { display: block; font-size: 0.95rem; margin-top: 0.1rem; }

        /* ---------- Misc ---------- */
        [data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; color: var(--ledger); }
        hr { border-color: var(--muted-line) !important; }
    </style>
    """, unsafe_allow_html=True)


inject_css()


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown("""
<div class="case-header">
    <div class="case-header-eyebrow">Agent 04 - Resume Screening - Case File</div>
    <h1 class="case-header-title">Candidate Screening Dossier</h1>
    <p class="case-header-sub">
        Every resume is weighed against the job description by meaning, not
        keywords -- using embeddings and cosine similarity -- then the
        strongest matches get a written verdict.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SIDEBAR: INTAKE FORM
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1 - Job Description")
    jd_input_mode = st.radio("Provide JD as:", ["Paste text", "Upload file"], horizontal=True, label_visibility="collapsed")

    jd_text = ""
    if jd_input_mode == "Paste text":
        jd_text = st.text_area("Paste the job description here", height=200,
                                placeholder="Job Title: Backend Software Engineer\n\nResponsibilities:\n- ...",
                                label_visibility="collapsed")
    else:
        jd_file = st.file_uploader("Upload JD file", type=["txt", "pdf", "docx"], label_visibility="collapsed")
        if jd_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.name)[1]) as tmp:
                tmp.write(jd_file.read())
                tmp_path = tmp.name
            jd_text = extract_text(tmp_path)
            os.unlink(tmp_path)
            st.caption(f"[OK] Loaded {jd_file.name} ({len(jd_text)} characters)")

    st.header("2 - Resumes")
    resume_files = st.file_uploader(
        "Upload resumes (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if resume_files:
        st.caption(f"[OK] {len(resume_files)} resume(s) queued")

    st.header("3 - Options")
    top_n = st.slider("Generate AI reasoning for top N candidates", 1, 10, 5,
                       help="Reasoning uses an extra API call per candidate, so keep this small to save cost.")

    run_button = st.button("Open the Case ->", type="primary", use_container_width=True,
                            disabled=not (jd_text.strip() and resume_files))

if not jd_text.strip() or not resume_files:
    st.info("Add a job description and at least one resume in the sidebar to open a case.")
    st.stop()


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------
if run_button:
    progress = st.progress(0, text="Embedding job description...")

    jd_embedding = get_embedding(jd_text)
    progress.progress(15, text="Job description embedded. Scoring resumes...")

    results = []
    total = len(resume_files)
    for i, uploaded_file in enumerate(resume_files):
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            resume_text = extract_text(tmp_path)
        except Exception as e:
            st.warning(f"Could not read {uploaded_file.name}: {e}")
            os.unlink(tmp_path)
            continue
        os.unlink(tmp_path)

        if not resume_text.strip():
            st.warning(f"{uploaded_file.name} appears empty, skipping.")
            continue

        scored = score_resume(jd_embedding, resume_text)
        results.append({
            "filename": uploaded_file.name,
            "score": scored["score"],
            "resume_text": resume_text,
        })

        pct = 15 + int(((i + 1) / total) * 55)
        progress.progress(pct, text=f"Scored {i + 1}/{total} resumes...")

    results.sort(key=lambda r: r["score"], reverse=True)

    progress.progress(75, text=f"Generating verdicts for top {top_n} candidates...")
    for i, r in enumerate(results):
        r["rank"] = i + 1
        if i < top_n:
            r["reasoning"] = generate_reasoning(jd_text, r["resume_text"], r["filename"])
        else:
            r["reasoning"] = "(reasoning skipped past top N to save API calls)"

    progress.progress(100, text="Case closed.")
    progress.empty()

    st.session_state["results"] = results


# ---------------------------------------------------------------------------
# TIER LOGIC -- drives the stamp badge color/label (relative to top score)
# ---------------------------------------------------------------------------
def tier_for(score: float, max_score: float):
    ratio = (score / max_score) if max_score else 0
    if ratio >= 0.92:
        return "strong", "Strong Match"
    elif ratio >= 0.78:
        return "moderate", "Possible Match"
    else:
        return "weak", "Low Match"


# ---------------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------------
if "results" in st.session_state:
    results = st.session_state["results"]
    max_score = max((r["score"] for r in results), default=1.0)

    st.markdown(f'<div class="section-label">Case Summary -- {len(results)} candidates reviewed</div>', unsafe_allow_html=True)

    rows_html = ""
    for r in results:
        tier_key, tier_label = tier_for(r["score"], max_score)
        rows_html += f"""
        <tr>
            <td>{r['rank']:02d}</td>
            <td>{html.escape(r['filename'])}</td>
            <td>{r['score']:.4f}</td>
            <td><span class="verdict-pill verdict-{tier_key}">{tier_label}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="ledger-table">
        <thead><tr><th>File</th><th>Candidate</th><th>Score</th><th>Verdict</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Case Files -- Detailed Findings</div>', unsafe_allow_html=True)

    for r in results:
        tier_key, tier_label = tier_for(r["score"], max_score)
        st.markdown(f"""
        <div class="case-card tier-{tier_key}">
            <div class="case-card-tab">FILE No.{r['rank']:02d}</div>
            <div class="case-card-main">
                <div class="case-card-row">
                    <span class="candidate-name">{html.escape(r['filename'])}</span>
                    <span class="stamp stamp-{tier_key}">{tier_label}<span class="stamp-score">{r['score']:.4f}</span></span>
                </div>
                <p class="case-card-reasoning">{html.escape(r['reasoning'])}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
    csv_data = pd.DataFrame([
        {"Rank": r["rank"], "Candidate": r["filename"], "Score": r["score"], "Reasoning": r["reasoning"]}
        for r in results
    ]).to_csv(index=False).encode("utf-8")
    st.download_button("Download Case File (CSV)", csv_data, "ranked_candidates.csv", "text/csv")
