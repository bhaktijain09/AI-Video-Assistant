import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
load_dotenv()
# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
    --page: #111318;
    --panel: #191c23;
    --panel-soft: #20242d;
    --ink: #edf0f6;
    --muted: #9aa3b2;
    --line: #2b303a;
    --brand: #7188f2;
    --brand-soft: #283251;
    --green: #64c79a;
    --green-soft: #20372e;
    --amber: #e1b56a;
    --amber-soft: #392f20;
    --rose: #e08b9b;
    --rose-soft: #3b252b;
    --shadow: 0 12px 32px rgba(0, 0, 0, .22);
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--page) !important;
    color: var(--ink) !important;
}
.stApp { background: var(--page) !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 1320px;
    padding: 2.1rem 3rem 4rem;
}
h1, h2, h3, h4, h5, h6 { font-family: 'Manrope', sans-serif !important; color: var(--ink) !important; }
[data-testid="stSidebar"] {
    background: #171a20 !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.7rem 1.15rem 2rem; }
[data-testid="stSidebar"] * { color: var(--ink); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted) !important; }
.brand-mark { font: 800 1.05rem 'Manrope',sans-serif; letter-spacing: -.035em; color: var(--ink); }
.sidebar-kicker, .eyebrow {
    color: #a5adba; font: 700 .68rem 'Manrope',sans-serif;
    letter-spacing: .11em; text-transform: uppercase;
}
.sidebar-kicker { margin: 1.4rem 0 .45rem; }
.sidebar-sub { color: var(--muted); font-size: .78rem; line-height: 1.5; margin-top: .25rem; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 2.8rem; background: #1d2129 !important; border: 1px solid #353b47 !important;
    border-radius: 10px !important; color: var(--ink) !important; font: 500 .9rem 'DM Sans',sans-serif !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
    border-color: #8297ff !important; box-shadow: 0 0 0 3px rgba(130,151,255,.16) !important;
}
[data-testid="stButton"] button {
    min-height: 2.75rem; border-radius: 10px !important; border: 1px solid transparent !important;
    background: var(--brand) !important; color: #fff !important; font: 700 .88rem 'Manrope',sans-serif !important;
    box-shadow: 0 5px 12px rgba(0,0,0,.24); transition: background .15s,transform .15s,box-shadow .15s;
}
[data-testid="stButton"] button:hover { background: #6d83ed !important; transform: translateY(-1px); box-shadow: 0 8px 18px rgba(0,0,0,.32); }
[data-testid="stButton"] button:focus-visible { outline: 3px solid rgba(130,151,255,.38); outline-offset: 2px; }
[data-testid="stButton"] button[kind="secondary"] { background: #222630 !important; color: #d6dbe5 !important; border-color: var(--line) !important; box-shadow: none; }
hr { border: 0 !important; border-top: 1px solid var(--line) !important; margin: 1.4rem 0 !important; }
.hero-shell { padding: .2rem 0 1.65rem; }
.eyebrow { display: flex; align-items: center; gap: .5rem; margin-bottom: .8rem; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: #64c79a; box-shadow: 0 0 0 4px #254333; }
.hero-title {
    display: flex;
    align-items: center;
    gap: .35rem;
    font: 800 clamp(1.65rem,3vw,2.25rem)/1.2 'Manrope',sans-serif;
    letter-spacing: -.055em;
    color: var(--ink);
     transform: translateY(5px);
}


.hero-title-emoji {
    display: inline-block;
    transform: translateY(4px);
}
.hero-lede { margin-top: .42rem; color: #cbd2df; font: 600 1.02rem 'Manrope',sans-serif; }
.hero-support { max-width: 720px; margin-top: .4rem; color: var(--muted); font-size: .9rem; line-height: 1.65; }
.analysis-heading { display:flex; justify-content:space-between; align-items:flex-end; gap:1rem; margin: .65rem 0 1.15rem; }
.analysis-heading h2 { margin:0; font:800 1.55rem 'Manrope',sans-serif; letter-spacing:-.04em; }
.analysis-heading p { margin:.32rem 0 0; color:var(--muted); font-size:.88rem; }
.badge { display:inline-flex; align-items:center; gap:.35rem; padding:.36rem .68rem; border-radius:999px; font-size:.72rem; font-weight:700; }
.badge-green { background:var(--green-soft); color:var(--green); }
.card {
    background:var(--panel); border:1px solid var(--line); border-radius:16px;
    padding:1.35rem 1.45rem; margin-bottom:1rem; box-shadow:var(--shadow);
}
.card-title { margin-bottom:.8rem; color:#a2abba; font:700 .69rem 'Manrope',sans-serif; letter-spacing:.1em; text-transform:uppercase; }
.card-content { color:#c7cfdb; font-size:.93rem; line-height:1.75; overflow-wrap:anywhere; }
.title-card { display:flex; align-items:center; gap:1rem; padding:1.2rem 1.45rem; background:linear-gradient(110deg,#1c2029,#22283a); }
.title-icon { display:grid; place-items:center; flex:0 0 42px; height:42px; border-radius:12px; background:var(--brand-soft); font-size:1.2rem; }
.title-value { color:var(--ink); font:700 1.15rem 'Manrope',sans-serif; letter-spacing:-.02em; }
.summary-card { min-height:100%; border-top:3px solid #7187e2; }
.summary-card .card-content { font-size:1rem; line-height:1.82; }
.task-card { border-top:3px solid #65a884; }
.decision-card { border-top:3px solid #8190bd; }
.question-card { border-top:3px solid #dcaa5c; }
.transcript-label { margin:.1rem 0 .6rem .15rem; color:#a2abba; font:700 .69rem 'Manrope',sans-serif; letter-spacing:.1em; text-transform:uppercase; }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:14px !important; background:#191c23 !important; box-shadow:var(--shadow); }
[data-testid="stExpander"] summary { min-height:3.1rem; color:#e2e7f0 !important; font-weight:600; }
.transcript-box { max-height:360px; overflow:auto; padding:1rem 1.1rem; border-radius:10px; background:#20242c; color:#c1c9d6; font-size:.88rem; line-height:1.8; white-space:pre-wrap; overflow-wrap:anywhere; }
.status-heading { margin:1.3rem 0 .5rem; color:#a2abba; font:700 .67rem 'Manrope',sans-serif; letter-spacing:.11em; }
.status-bar { display:flex; align-items:center; gap:.55rem; margin:.16rem 0; padding:.48rem .55rem; border-radius:8px; background:transparent; color:#c1c8d4; font-size:.78rem; }
.status-dot { width:17px; height:17px; flex:0 0 17px; border-radius:50%; background:var(--green-soft); position:relative; }
.status-dot:after { content:'✓'; position:absolute; inset:0; text-align:center; color:var(--green); font:700 11px/17px 'DM Sans',sans-serif; }
.dot-active { background:var(--brand-soft); }
.dot-active:after { content:'•'; color:var(--brand); font-size:17px; }
.dot-pending { background:#303540; }
.dot-pending:after { content:''; }
.qna-cta { display:flex; align-items:center; gap:1.1rem; padding:1.55rem 1.7rem; margin:1.7rem 0 1.25rem; border:1px solid #333c59; border-radius:18px; background:linear-gradient(110deg,#20263a,#191c23 68%); box-shadow:0 12px 30px rgba(0,0,0,.2); }
.qna-icon { display:grid; place-items:center; flex:0 0 52px; width:52px; height:52px; border-radius:15px; background:#2b3453; font-size:1.45rem; }
.qna-title { color:var(--ink); font:750 1.14rem 'Manrope',sans-serif; letter-spacing:-.025em; }
.qna-copy { margin-top:.34rem; color:var(--muted); font-size:.87rem; line-height:1.6; }
.chat-heading { margin:.5rem 0 1rem; }
.chat-heading h3 { margin:0; font:750 1.35rem 'Manrope',sans-serif; letter-spacing:-.035em; }
.chat-heading p { margin:.32rem 0 0; color:var(--muted); font-size:.86rem; }
.chat-container { padding:1.15rem; max-height:450px; overflow-y:auto; margin-bottom:1rem; border:1px solid var(--line); border-radius:16px; background:#191c23; box-shadow:var(--shadow); }
.chat-msg { display:flex; flex-direction:column; gap:.35rem; margin-bottom:1.05rem; }
.chat-label { color:#a1aaba; font-size:.68rem; font-weight:700; }
.chat-bubble { display:inline-block; max-width:88%; padding:.72rem .95rem; border-radius:14px; font-size:.9rem; line-height:1.65; overflow-wrap:anywhere; }
.user-label { color:var(--brand); }
.bot-label { color:var(--green); }
.user-bubble { align-self:flex-end; background:#29314a; color:#e1e7ff; border:1px solid #384365; border-bottom-right-radius:5px; }
.bot-bubble { align-self:flex-start; background:#252a33; color:#e2e7f0; border:1px solid #343a45; border-bottom-left-radius:5px; }
.empty-wrap { max-width:940px; margin:1.8rem auto 0; text-align:center; }
.empty-emoji { margin-bottom:.65rem; font-size:2.8rem; }
.empty-title { color:var(--ink); font:800 clamp(1.45rem,3vw,2rem) 'Manrope',sans-serif; letter-spacing:-.05em; }
.empty-copy { max-width:530px; margin:.5rem auto 1.6rem; color:var(--muted); font-size:.95rem; line-height:1.7; }
.feature-card { min-height:155px; padding:1.2rem; text-align:left; background:#191c23; border:1px solid var(--line); border-radius:15px; box-shadow:var(--shadow); }
.feature-icon { margin-bottom:.65rem; font-size:1.3rem; }
.feature-title { color:#e3e8f1; font:700 .91rem 'Manrope',sans-serif; }
.feature-copy { margin-top:.38rem; color:var(--muted); font-size:.8rem; line-height:1.55; }
[data-testid="stProgress"] > div > div > div { background:var(--brand) !important; }
[data-testid="stSpinner"] > div { border-top-color:var(--brand) !important; }
[data-testid="stAlert"] { border-radius:12px; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-thumb { border-radius:8px; background:#414854; }
::-webkit-scrollbar-track { background:transparent; }
@media (max-width:900px) {
    [data-testid="stMainBlockContainer"] { padding:1.6rem 1.5rem 3rem; }
}
@media (max-width:640px) {
    [data-testid="stMainBlockContainer"] { padding:1.15rem 1rem 2.3rem; }
    .analysis-heading { align-items:flex-start; flex-direction:column; }
    .card { padding:1.1rem; border-radius:14px; }
    .qna-cta { align-items:flex-start; padding:1.2rem; }
}

/* Premium, restrained motion: short, soft entrances and small hover feedback */
@keyframes softFadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes heroGlow {
    0%, 100% { box-shadow: 0 0 0 rgba(130,151,255,0); }
    50% { box-shadow: 0 12px 34px rgba(130,151,255,.055); }
}
@keyframes ctaBreath {
    0%, 100% { box-shadow: 0 12px 30px rgba(130,151,255,.055); }
    50% { box-shadow: 0 14px 34px rgba(130,151,255,.10); }
}
@keyframes statusPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(130,151,255,.18); }
    50% { box-shadow: 0 0 0 5px rgba(130,151,255,.055); }
}
.hero-shell {
    animation: softFadeUp .52s cubic-bezier(.2,.7,.25,1) both, heroGlow 5.5s ease-in-out 650ms infinite;
    border-radius: 18px;
}
.card, [data-testid="stExpander"], .feature-card {
    transition: transform .24s ease, box-shadow .24s ease, border-color .24s ease;
}
.card:hover, [data-testid="stExpander"]:hover, .feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 17px 38px rgba(0,0,0,.34);
}
.summary-card { animation: softFadeUp .46s cubic-bezier(.2,.7,.25,1) .10s both; }
.transcript-label, [data-testid="stExpander"] { animation: softFadeUp .46s cubic-bezier(.2,.7,.25,1) .19s both; }
.task-card { animation: softFadeUp .46s cubic-bezier(.2,.7,.25,1) .27s both; }
.decision-card { animation: softFadeUp .46s cubic-bezier(.2,.7,.25,1) .35s both; }
.question-card { animation: softFadeUp .46s cubic-bezier(.2,.7,.25,1) .43s both; }
.title-card { animation: softFadeUp .42s cubic-bezier(.2,.7,.25,1) .04s both; }
.analysis-heading { animation: softFadeUp .42s cubic-bezier(.2,.7,.25,1) both; }
.feature-card:nth-child(1) { animation: softFadeUp .46s ease .08s both; }
.feature-card:nth-child(2) { animation: softFadeUp .46s ease .16s both; }
.feature-card:nth-child(3) { animation: softFadeUp .46s ease .24s both; }
.qna-cta {
    animation: softFadeUp .48s cubic-bezier(.2,.7,.25,1) .48s both, ctaBreath 4.8s ease-in-out 1s infinite;
    transition: transform .24s ease, border-color .24s ease, box-shadow .24s ease;
}
.qna-cta:hover { transform: translateY(-2px); border-color: #485477; }
[data-testid="stButton"] button {
    transition: background .2s ease, transform .2s ease, box-shadow .2s ease, letter-spacing .2s ease;
}
[data-testid="stButton"] button:hover { transform: translateY(-2px); box-shadow: 0 9px 20px rgba(0,0,0,.34); letter-spacing: .012em; }
.status-dot, .status-dot:after {
    transition: background-color .36s ease, color .36s ease, box-shadow .36s ease, transform .36s ease;
}
.status-dot.dot-active { animation: statusPulse 1.8s ease-in-out infinite; }
.chat-heading, .chat-container, .chat-container + div, .chat-msg {
    animation: softFadeUp .42s cubic-bezier(.2,.7,.25,1) both;
}
.chat-msg:nth-child(1) { animation-delay: .04s; }
.chat-msg:nth-child(2) { animation-delay: .09s; }
.chat-msg:nth-child(3) { animation-delay: .14s; }
.chat-msg:nth-child(4) { animation-delay: .19s; }
.chat-msg:nth-child(n+5) { animation-delay: .23s; }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
    }
}


/* Dark-theme control surfaces and legibility refinements */
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background: #20242c !important;
    border-color: #353b47 !important;
}
[data-baseweb="menu"] *, [role="listbox"] * { color: #e5e9f1 !important; }
[data-testid="stTextInput"] input::placeholder { color: #8993a3 !important; opacity: 1; }
[data-testid="stSelectbox"] svg { fill: #b9c1ce !important; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary { color: #e2e7f0 !important; }
.title-card .card-title, .feature-copy { color: #aab3c2; }
.hero-support, .analysis-heading p, .qna-copy, .chat-heading p { color: #a7b0bf; }
.empty-copy { color: #aab3c2; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #edf0f6; }
[data-testid="stSidebar"] label { color: #b6bfcc !important; }

</style>
""", unsafe_allow_html=True)
# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "qna_enabled": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default
# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"
def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)
# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-mark">🎬 &nbsp;AI Video Assistant</div><div class="sidebar-sub">Your meeting workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-kicker">Video / Meeting Source</div>', unsafe_allow_html=True)
    source = st.text_input("YouTube URL or File Path", placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4")
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    run_btn = st.button("⚡  Analyse", use_container_width=True)
    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Ready"),
        ]:
            render_step_bar(label, step, icon)
# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-shell">
    <div class="eyebrow"><span class="live-dot"></span> AI Meeting Intelligence</div>
   <div class="hero-title">
    <span class="hero-title-emoji">🎬</span>
    <span>AI Video Assistant</span>
</div>
    <div class="hero-lede">Turn meetings into searchable knowledge.</div>
    <div class="hero-support">Transcribe, summarize, extract decisions and action items, then ask questions about your meeting.</div>
</div>
""", unsafe_allow_html=True)
# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.qna_enabled = False
        st.session_state.pipeline_steps = {}
        progress_placeholder = st.empty()
        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")
            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")
            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")
            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")
            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")
            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")
            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")
            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()
        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")
# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    st.markdown("""
    <div class="analysis-heading">
        <div>
            <h2>Analysis Results</h2>
            <p>Your meeting, organized into a clear and useful overview.</p>
        </div>
        <span class="badge badge-green">✓ Analysis complete</span>
    </div>
    """, unsafe_allow_html=True)
    # Title banner
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)
    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        st.markdown(f"""
        <div class="card summary-card">
            <div class="card-title">📋 SUMMARY</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="transcript-label">📝 TRANSCRIPT</div>', unsafe_allow_html=True)
        with st.expander("View full transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)
    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="card task-card">
            <div class="card-title">✅ ACTION ITEMS</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card decision-card">
            <div class="card-title">🔑 KEY DECISIONS</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="card question-card">
            <div class="card-title">❓ OPEN QUESTIONS</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    # ── Q&A Opt-In ────────────────────────────────────────────────────────────
    if not st.session_state.qna_enabled:
        st.markdown("""
        <div class="qna-cta">
            <div class="qna-icon">💬</div>
            <div>
                <div class="qna-title">Want to explore this meeting further?</div>
                <div class="qna-copy">Ask questions about the transcript and get AI-powered answers.</div>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("Opt to Proceed with Q&A →", use_container_width=True):
            st.session_state.qna_enabled = True
            st.rerun()
    else:
        st.markdown("""<div class="chat-heading"><h3>💬 Ask about your meeting</h3><p>Your AI assistant has access to the analyzed transcript.</p></div>""", unsafe_allow_html=True)
        if st.session_state.chat_history:
            chat_html = '<div class="chat-container">'
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_html += f"""
                    <div class="chat-msg" style="align-items:flex-end">
                        <span class="chat-label user-label">You</span>
                        <div class="chat-bubble user-bubble">{msg['content']}</div>
                    </div>"""
                else:
                    chat_html += f"""
                    <div class="chat-msg" style="align-items:flex-start">
                        <span class="chat-label bot-label">🤖 Assistant</span>
                        <div class="chat-bubble bot-bubble">{msg['content']}</div>
                    </div>"""
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:2rem">
                <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
                <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
            </div>""", unsafe_allow_html=True)
        chat_col1, chat_col2 = st.columns([5, 1], gap="small")
        with chat_col1:
            user_input = st.text_input("Your question", placeholder="Ask a question about this meeting…", label_visibility="collapsed")
        with chat_col2:
            send_btn = st.button("Send →", use_container_width=True)
        if send_btn and user_input.strip():
            with st.spinner("Thinking…"):
                answer = ask_question(r["rag_chain"], user_input.strip())
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
else:
    st.markdown("""
    <div class="empty-wrap">
        <div class="empty-emoji">🎬</div>
        <div class="empty-title">Your meeting intelligence workspace</div>
        <div class="empty-copy">Upload a meeting or paste a YouTube URL in the sidebar to get started. Turn conversations into clear, searchable outcomes.</div>
    </div>
    """, unsafe_allow_html=True)
    feature_cols = st.columns(3, gap="medium")
    for col, icon, title, description in zip(
        feature_cols,
        ["📝", "✨", "💬"],
        ["Transcription", "AI Analysis", "Ask Questions"],
        ["Convert meeting audio into searchable text.", "Get summaries, decisions and action items.", "Chat with your meeting after analysis."],
    ):
        with col:
            st.markdown(f'''<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-copy">{description}</div></div>''', unsafe_allow_html=True)