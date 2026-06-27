import streamlit as st
import re

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
[data-testid="stAppViewContainer"] { background-color: #080c16; }
[data-testid="stSidebar"]          { background-color: #0d1120; border-right: 1px solid #1e2540; }
.block-container                    { padding-top: 1.8rem; max-width: 1120px; }

/* ── Gradient title ── */
.brand-title {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    background: linear-gradient(120deg, #6366f1 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin: 0;
}
.brand-sub {
    color: #5a6384;
    font-size: 0.95rem;
    margin-top: 0.35rem;
    letter-spacing: 0.01em;
}

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, #6366f1 0%, #1e2540 60%, transparent 100%);
    margin: 1.5rem 0;
    border: none;
}

/* ── Sidebar pipeline steps ── */
.sb-step {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
    margin-bottom: 0.35rem;
    border: 1px solid transparent;
    transition: border-color 0.2s;
}
.sb-step:hover { border-color: #2a3060; background: #10152a; }
.sb-icon {
    font-size: 1.3rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
}
.sb-label   { font-size: 0.82rem; font-weight: 700; color: #c4c9e8; }
.sb-caption { font-size: 0.72rem; color: #4f5a80; line-height: 1.4; margin-top: 0.1rem; }
.sb-connector {
    width: 1px;
    height: 16px;
    background: linear-gradient(180deg, #6366f1, #1e2540);
    margin: 0 0 0 1.55rem;
}

/* ── Pill chips ── */
.pill-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.pill {
    display: inline-block;
    padding: 0.22rem 0.75rem;
    background: rgba(99,102,241,0.10);
    border: 1px solid rgba(99,102,241,0.28);
    border-radius: 999px;
    font-size: 0.75rem;
    color: #a78bfa;
    font-weight: 600;
    cursor: default;
}

/* ── Step status headers ── */
.step-label {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 0.25rem;
}
.step-num {
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    color: #fff;
    border-radius: 5px;
    padding: 0.05rem 0.45rem;
    font-size: 0.7rem;
}

/* ── Raw output areas ── */
.raw-box {
    background: #0a0e1a;
    border: 1px solid #1a2035;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.75rem;
    color: #7a8ab0;
    white-space: pre-wrap;
    line-height: 1.6;
    max-height: 220px;
    overflow-y: auto;
}

/* ── Report ── */
.report-wrap {
    background: #0d1120;
    border: 1px solid #1e2540;
    border-left: 3px solid #6366f1;
    border-radius: 10px;
    padding: 1.6rem 2rem;
    line-height: 1.85;
    color: #c4c9e8;
}

/* ── Score card ── */
.score-card {
    background: linear-gradient(145deg, rgba(99,102,241,0.12), rgba(167,139,250,0.07));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 14px;
    padding: 1.4rem 1rem;
    text-align: center;
}
.score-num {
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.score-denom { font-size: 1rem; color: #4f5a80; font-weight: 600; }
.score-tag   { font-size: 0.7rem; color: #5a6384; margin-top: 0.3rem; letter-spacing: 0.05em; text-transform: uppercase; }

/* ── Verdict box ── */
.verdict-box {
    background: rgba(56,189,248,0.07);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    color: #93c5fd;
    font-style: italic;
    font-size: 1.02rem;
    line-height: 1.65;
    height: 100%;
    display: flex;
    align-items: center;
}

/* ── Strength / Improvement panels ── */
.strength-panel {
    background: rgba(74,222,128,0.06);
    border: 1px solid rgba(74,222,128,0.2);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    color: #bbf7d0;
    font-size: 0.875rem;
    line-height: 1.7;
}
.improvement-panel {
    background: rgba(251,146,60,0.06);
    border: 1px solid rgba(251,146,60,0.2);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    color: #fed7aa;
    font-size: 0.875rem;
    line-height: 1.7;
}
.panel-heading {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

/* ── Progress bar override ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #a78bfa) !important;
    border-radius: 999px !important;
}

/* ── Run button ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #a78bfa) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.32) !important;
    transition: all 0.18s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 7px 22px rgba(99,102,241,0.45) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid #2a3060 !important;
    color: #a78bfa !important;
    border-radius: 7px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: #6366f1 !important;
}

/* ── Text input ── */
[data-testid="stTextInput"] input {
    background: #0d1120 !important;
    border: 1px solid #1e2540 !important;
    color: #c4c9e8 !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    outline: none !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0d1120 !important;
    border: 1px solid #1a2035 !important;
    border-radius: 8px !important;
}

/* ── Status widget ── */
[data-testid="stStatusWidget"] { border-radius: 8px; }

/* ── Success / Error banners ── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #2a3060; border-radius: 999px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_critic(text: str) -> dict:
    """Extract score, strengths, improvements and verdict from critic output."""
    score_m = re.search(r"Score:\s*([\d.]+)/10", text)
    str_m   = re.search(r"Strengths:(.*?)(?=Areas to Improve:|One line verdict:|$)", text, re.DOTALL | re.IGNORECASE)
    imp_m   = re.search(r"Areas to Improve:(.*?)(?=One line verdict:|$)", text, re.DOTALL | re.IGNORECASE)
    verd_m  = re.search(r"One line verdict:(.*?)$", text, re.DOTALL | re.IGNORECASE)
    raw_score = float(score_m.group(1)) if score_m else 5.0
    return {
        "score":        f"{score_m.group(1)}/10" if score_m else "N/A",
        "score_raw":    raw_score,
        "strengths":    str_m.group(1).strip()   if str_m   else text,
        "improvements": imp_m.group(1).strip()   if imp_m   else "",
        "verdict":      verd_m.group(1).strip()  if verd_m  else "",
    }


def step_label(num: int, icon: str, text: str):
    st.markdown(
        f'<div class="step-label">'
        f'<span class="step-num">{num}</span>{icon} {text}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Pipeline")
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    pipeline_steps = [
        ("🔍", "Search Agent",  "Tavily web search — finds fresh, reliable sources"),
        ("📖", "Reader Agent",  "Scrapes the top URL for deep page content"),
        ("✍️", "Writer Chain",  "Synthesises research into a structured report"),
        ("🎯", "Critic Chain",  "Reviews, scores and gives actionable feedback"),
    ]
    for i, (icon, label, caption) in enumerate(pipeline_steps):
        st.markdown(
            f'<div class="sb-step">'
            f'  <div class="sb-icon">{icon}</div>'
            f'  <div><div class="sb-label">Step {i+1} — {label}</div>'
            f'       <div class="sb-caption">{caption}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if i < len(pipeline_steps) - 1:
            st.markdown('<div class="sb-connector"></div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
    st.markdown("**🛠 Stack**", help="Libraries powering this system")

    stack = [
        ("🦙", "Groq",         "LLaMA 3.1 8B Instant"),
        ("🔗", "LangChain",    "Agent orchestration"),
        ("🌐", "Tavily",       "Real-time web search"),
        ("🍲", "BeautifulSoup","HTML scraping & cleaning"),
    ]
    for icon, name, detail in stack:
        st.markdown(
            f"<span style='color:#7a8ab0;font-size:0.78rem'>{icon} **{name}** — {detail}</span>",
            unsafe_allow_html=True,
        )
    st.markdown("")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="brand-title">Multi-Agent Research System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">'
    'Four specialised AI agents — search, read, write, critique — all in one automated pipeline.'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)


# ── Topic Input ───────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input(
        "_",
        placeholder="e.g.  The rise of neuromorphic computing in edge AI devices",
        label_visibility="collapsed",
    )
with col_btn:
    run_btn = st.button("🚀  Run", type="primary", use_container_width=True)

# Example topic chips (decorative)
st.markdown(
    '<div class="pill-row">'
    '<span class="pill">🧬 Gene editing</span>'
    '<span class="pill">⚛️ Quantum cryptography</span>'
    '<span class="pill">🌊 Ocean plastic solutions</span>'
    '<span class="pill">🤖 Agentic AI systems</span>'
    '<span class="pill">🔋 Solid-state batteries</span>'
    '<span class="pill">🧠 Neuromorphic chips</span>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Pipeline Execution ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.error("⚠️  Please enter a research topic before running.")
        st.stop()

    # Lazy import so page loads even without .env configured
    try:
        from agents import (
            build_search_agent,
            build_reader_agent,
            writer_chain,
            critic_chain,
        )
    except ImportError as e:
        st.error(f"Could not import agents module: {e}")
        st.stop()

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
    state: dict = {}

    # ── Step 1 — Search Agent ─────────────────────────────────────────────────
    step_label(1, "🔍", "Search Agent")
    with st.status("Querying Tavily for recent, reliable sources…", expanded=True) as s1:
        try:
            agent = build_search_agent()
            result = agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = result["messages"][-1].content
            s1.update(label="✅ Search Agent — complete", state="complete", expanded=False)
        except Exception as err:
            s1.update(label="❌ Search Agent failed", state="error")
            st.error(f"Error: {err}")
            st.stop()

    with st.expander("📋 Raw search results", expanded=False):
        st.text_area("Raw search results", state["search_results"], height=180, disabled=True, label_visibility="collapsed")

    st.markdown("")

    # ── Step 2 — Reader Agent ─────────────────────────────────────────────────
    step_label(2, "📖", "Reader Agent")
    with st.status("Picking the best URL and extracting deep content…", expanded=True) as s2:
        try:
            reader = build_reader_agent()
            res2 = reader.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            })
            state["scraped_content"] = res2["messages"][-1].content
            s2.update(label="✅ Reader Agent — complete", state="complete", expanded=False)
        except Exception as err:
            s2.update(label="❌ Reader Agent failed", state="error")
            st.error(f"Error: {err}")
            st.stop()

    with st.expander("🌐 Scraped page content", expanded=False):
        st.text_area("Scraped page content", state["scraped_content"], height=180, disabled=True, label_visibility="collapsed")

    st.markdown("")

    # ── Step 3 — Writer Chain ─────────────────────────────────────────────────
    step_label(3, "✍️", "Writer Chain")
    with st.status("Synthesising research into a structured report…", expanded=True) as s3:
        try:
            combined = (
                f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({"topic": topic, "research": combined})
            s3.update(label="✅ Writer Chain — report ready", state="complete", expanded=False)
        except Exception as err:
            s3.update(label="❌ Writer Chain failed", state="error")
            st.error(f"Error: {err}")
            st.stop()

    col_head, col_dl = st.columns([4, 1])
    with col_head:
        st.markdown("#### 📝 Research Report")
    with col_dl:
        st.download_button(
            "⬇️ Download .md",
            data=state["report"],
            file_name=f"report_{topic[:40].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown(state["report"])

    st.markdown("")

    # ── Step 4 — Critic Chain ─────────────────────────────────────────────────
    step_label(4, "🎯", "Critic Chain")
    with st.status("Evaluating quality, depth, accuracy and structure…", expanded=True) as s4:
        try:
            state["feedback"] = critic_chain.invoke({"report": state["report"]})
            s4.update(label="✅ Critic Chain — evaluation complete", state="complete", expanded=False)
        except Exception as err:
            s4.update(label="❌ Critic Chain failed", state="error")
            st.error(f"Error: {err}")
            st.stop()

    parsed = parse_critic(state["feedback"])

    st.markdown("#### 🎯 Critic's Evaluation")

    # Score + verdict row
    c_score, c_verdict = st.columns([1, 3])
    with c_score:
        st.markdown(
            f'<div class="score-card">'
            f'  <div class="score-num">{parsed["score"].split("/")[0]}</div>'
            f'  <div class="score-denom">/ 10</div>'
            f'  <div class="score-tag">Overall Score</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.progress(min(parsed["score_raw"] / 10.0, 1.0))

    with c_verdict:
        verdict_html = parsed["verdict"].replace("\n", "<br>") or "See full feedback below."
        st.markdown(
            f'<div class="verdict-box">💬 &nbsp;{verdict_html}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Strengths + Improvements
    c_str, c_imp = st.columns(2)
    with c_str:
        lines = parsed["strengths"].replace("\n", "<br>")
        st.markdown(
            f'<div class="strength-panel">'
            f'<div class="panel-heading" style="color:#4ade80;">✅ Strengths</div>'
            f'{lines}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c_imp:
        lines = parsed["improvements"].replace("\n", "<br>")
        st.markdown(
            f'<div class="improvement-panel">'
            f'<div class="panel-heading" style="color:#fb923c;">⚠️ Areas to Improve</div>'
            f'{lines}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with st.expander("📄 Full critic feedback (raw)", expanded=False):
        st.text_area("Full critic feedback", state["feedback"], height=200, disabled=True, label_visibility="collapsed")

    # ── Done ──────────────────────────────────────────────────────────────────
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
    st.success(f"🎉  Pipeline complete!  Topic: **{topic}**")