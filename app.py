import html
import time
from datetime import datetime

import streamlit as st

from agent import diagnose, record_outcome, record_incident, memory_client, BANK

st.set_page_config(page_title="Incident Response Agent", page_icon="🚨", layout="wide")

# ---------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #0a0f1c;
    --panel: #111a2b;
    --border: #263650;
    --text: #edf2fb;
    --muted: #91a0ba;
    --accent: #ffb020;
}

.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(255,176,32,.07), transparent 28rem),
        radial-gradient(circle at 90% 10%, rgba(70,120,255,.06), transparent 30rem),
        var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
}

.block-container {
    max-width: 1220px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.stApp p, .stApp li, .stApp label {
    color: inherit;
    font-family: 'IBM Plex Sans', sans-serif;
}

.hero {
    padding: 1.6rem 0 1.4rem;
}

.hero-kicker {
    display: inline-block;
    padding: .35rem .7rem;
    border: 1px solid rgba(255,176,32,.35);
    background: rgba(255,176,32,.08);
    color: var(--accent);
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: .8rem;
}

.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 3.15rem;
    line-height: 1;
    letter-spacing: -.035em;
    margin: 0 0 .7rem;
    color: var(--text);
}

.hero p {
    color: var(--muted);
    max-width: 700px;
    font-size: 1.03rem;
    line-height: 1.55;
    margin: 0;
}

.hero-flow {
    color: #b8c4d8;
    margin-top: .8rem;
    font-size: .86rem;
}

.stTextArea div[data-baseweb="textarea"],
.stTextInput div[data-baseweb="input"] {
    background: rgba(17,26,43,.96);
    border: 1px solid var(--border);
    border-radius: 12px;
}

.stTextArea textarea,
.stTextInput input {
    background: transparent;
    color: var(--text);
    font-size: 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

.stTextArea div[data-baseweb="textarea"]:focus-within,
.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent);
}

.stTextArea label, .stTextInput label {
    color: #c9d2e6;
}

button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #ffb020, #ffc64d);
    border: 0;
    border-radius: 10px;
    padding: .58rem 1.5rem;
    box-shadow: 0 8px 24px rgba(255,176,32,.15);
}

button[data-testid="stBaseButton-primary"] p {
    color: #1a1305;
    font-weight: 700;
}

button[data-testid="stBaseButton-primary"]:hover {
    background: #ffd064;
}

button[data-testid="stBaseButton-secondary"] {
    background: rgba(17,26,43,.72);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: .35rem 1rem;
}

button[data-testid="stBaseButton-secondary"] p {
    color: #c9d2e6;
    font-size: .88rem;
}

button[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--accent);
}

.hint {
    color: var(--muted);
    font-size: .86rem;
    margin: 1.25rem 0 .55rem;
}

.st-key-plain_card,
.st-key-mem_card {
    min-height: 100%;
    border-radius: 16px;
    padding: 1.25rem 1.35rem;
}

.st-key-plain_card {
    background: rgba(13,21,36,.72);
    border: 1px solid var(--border);
}

.st-key-mem_card {
    background: linear-gradient(180deg, rgba(18,29,48,.98), rgba(13,21,36,.98));
    border: 1px solid #35445f;
    border-top: 3px solid var(--accent);
    box-shadow: 0 14px 42px rgba(0,0,0,.18);
}

.card-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: .18rem;
}

.card-note {
    color: var(--muted);
    font-size: .86rem;
    margin-bottom: .9rem;
}

.st-key-plain_card p, .st-key-plain_card li {
    color: #aebbd0;
    font-size: .95rem;
    line-height: 1.55;
}

.st-key-mem_card p, .st-key-mem_card li {
    color: #edf2fb;
    font-size: .96rem;
    line-height: 1.58;
}

.memory-evidence {
    margin: .8rem 0 1.1rem;
    padding: .9rem 1rem;
    background: rgba(8,15,27,.72);
    border: 1px solid #2a3a55;
    border-radius: 12px;
}

.memory-evidence-title {
    color: var(--accent);
    font-size: .76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-bottom: .55rem;
}

.memory-evidence-item {
    padding: .65rem 0;
    border-bottom: 1px solid #1e2a3f;
}

.memory-evidence-item:last-child {
    border-bottom: 0;
}

.memory-evidence-date {
    color: var(--accent);
    font-size: .76rem;
    font-weight: 700;
    margin-bottom: .18rem;
}

.memory-evidence-text {
    color: #cbd6e7;
    font-size: .86rem;
    line-height: 1.45;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(13,21,36,.45);
    margin-top: 1rem;
}

div[data-testid="stExpander"] summary p {
    color: #d4ddec;
    font-weight: 600;
}

.logbook {
    border-left: 2px solid #2a3a55;
    margin-left: .3rem;
}

.entry {
    display: flex;
    gap: 1rem;
    padding: .65rem 0 .65rem 1rem;
    border-bottom: 1px solid #1b273b;
}

.entry:last-child {
    border-bottom: 0;
}

.when {
    flex: 0 0 6.6rem;
    color: var(--accent);
    font-weight: 700;
    font-size: .78rem;
}

.when.none {
    color: #56627c;
    font-weight: 400;
}

.what {
    color: #cbd6e7;
    font-size: .88rem;
    line-height: 1.48;
}

.st-key-teach_card {
    background: rgba(17,26,43,.52);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-top: 1.4rem;
    padding: 1.2rem 1.35rem;
}

.feedback-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
}

.elapsed {
    color: #66758e;
    font-size: .78rem;
    margin-top: .7rem;
}

@media (max-width: 760px) {
    .hero h1 { font-size: 2.2rem; }
    .entry { flex-direction: column; gap: .1rem; }
    .when { flex-basis: auto; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- helpers
EXAMPLES = [
    ("Payments API · 504", "payments-api is timing out and returning 504 errors"),
    ("Checkout · Redis 502", "checkout page returning 502 errors after redis failover"),
    ("Auth · Random logout", "auth-service users are randomly getting logged out"),
    ("Inventory · Kafka lag", "inventory-service stock counts are stale and Kafka consumer lag keeps growing"),
    ("Search · High latency", "search-api latency has increased to 8 seconds"),
]

TOP_MEMORIES = 12


def pretty_date(raw: str) -> str:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return raw.strip()


def log_row(text: str) -> str:
    parts = [p.strip() for p in text.split("|")]
    body = html.escape(parts[0])
    when = ""
    for p in parts[1:]:
        if p.startswith("When:"):
            when = pretty_date(p.replace("When:", "", 1))
    when_html = (
        f'<div class="when">{html.escape(when)}</div>' if when else '<div class="when none">undated</div>'
    )
    return f'<div class="entry">{when_html}<div class="what">{body}</div></div>'

def memory_evidence(texts, limit=4):
    items = []

    for text in texts[:limit]:
        parts = [p.strip() for p in text.split("|")]

        body = html.escape(parts[0])
        when = ""

        for p in parts[1:]:
            if p.startswith("When:"):
                when = pretty_date(p.replace("When:", "", 1))

        date_html = (
            f'<div class="memory-evidence-date">{html.escape(when)}</div>'
            if when
            else ""
        )

        items.append(
            '<div class="memory-evidence-item">'
            + date_html
            + f'<div class="memory-evidence-text">{body}</div>'
            + '</div>'
        )

    if not items:
        return (
            '<div class="memory-evidence">'
            '<div class="memory-evidence-title">🧠 Hindsight evidence</div>'
            '<div class="memory-evidence-text">'
            'No relevant memory was recalled.'
            '</div>'
            '</div>'
        )

    return (
        '<div class="memory-evidence">'
        '<div class="memory-evidence-title">🧠 Hindsight evidence</div>'
        + ''.join(items)
        + '</div>'
    )

def pick_example(text: str):
    st.session_state["alert_text"] = text
    st.session_state["auto_run"] = True


# ---------------------------------------------------------------- page
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">AI Incident Response · Hindsight Memory</div>
        <h1>Incident Response Agent</h1>
        <p>Diagnose production alerts using your team's previous incidents, successful fixes, and failed fixes — then close the loop so the agent gets better for the next similar alert.</p>
        <div class="hero-flow">Alert → Recall → Diagnose → Fix → Learn</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "alert_text" not in st.session_state:
    st.session_state["alert_text"] = ""

st.markdown(
    '<div class="card-note" style="margin: .5rem 0 .35rem;">CURRENT INCIDENT ALERT</div>',
    unsafe_allow_html=True,
)

st.text_area(
    "Alert",
    key="alert_text",
    placeholder="payments-api is timing out and returning 504 errors",
    height=105,
    label_visibility="collapsed",
)

run_clicked = st.button("Diagnose alert  →", type="primary")

st.markdown('<div class="hint">Quick test scenarios</div>', unsafe_allow_html=True)
cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES):
    col.button(label, key=f"ex_{label}", on_click=pick_example, args=(text,), use_container_width=True)

auto_run = st.session_state.pop("auto_run", False)

if run_clicked or auto_run:
    alert = st.session_state["alert_text"].strip()
    if not alert:
        st.warning("Paste an alert first, or pick an example.")
    else:
        with st.spinner("Searching past incidents and drafting an answer..."):
            started = time.time()
            st.session_state["alert"] = alert
            st.session_state["plain"] = diagnose(alert, use_memory=False)
            st.session_state["with_mem"] = diagnose(alert, use_memory=True)
            try:
                with memory_client() as m:
                    res = m.recall(bank_id=BANK, query=alert)
                    st.session_state["recalled"] = [r.text for r in res.results[:TOP_MEMORIES]]
            except Exception:
                st.session_state["recalled"] = []
            st.session_state["elapsed"] = time.time() - started
            st.session_state.pop("saved", None)

if "plain" in st.session_state:
    recalled = st.session_state.get("recalled", [])
    st.write("")

    st.markdown(
        f'<div class="card-note">CURRENT ALERT · MEMORY RECALL {len(recalled)} entries · RESPONSE {st.session_state.get("elapsed", 0):.1f}s</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([5, 7], gap="large")

    with left:
        with st.container(key="plain_card"):
            st.markdown(
                '<div class="card-title">Without memory</div>'
                '<div class="card-note">Generic advice. This model has never seen your incidents.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state["plain"])

    with right:
        with st.container(key="mem_card"):
            st.markdown(
                '<div class="card-title">With memory</div>'
                f'<div class="card-note">Hindsight recalled {len(recalled)} relevant memory entries</div>',
                unsafe_allow_html=True,
            )

            # Show the actual memories before the AI diagnosis
            st.markdown(
                memory_evidence(recalled, limit=4),
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="card-note">AI diagnosis using the recalled history</div>',
                unsafe_allow_html=True,
            )

            st.markdown(st.session_state["with_mem"])

    with st.expander(f"Incident log Hindsight recalled ({len(recalled)})"):
        if recalled:
            rows = "".join(log_row(t) for t in recalled)
            st.markdown(f'<div class="logbook">{rows}</div>', unsafe_allow_html=True)
        else:
            st.write("Nothing was recalled for this alert.")

    st.markdown(
        f'<div class="elapsed">Both answers took {st.session_state.get("elapsed", 0):.1f} seconds.</div>',
        unsafe_allow_html=True,
    )

    with st.container(key="teach_card"):
        st.markdown(
            '<div class="card-title">Close the loop</div>'
            '<div class="card-note">Tell the agent how your fix went. It uses this the next time a similar alert fires.</div>',
            unsafe_allow_html=True,
        )
        fix = st.text_input(
            "Fix you tried",
            key="fix_input",
            placeholder="e.g. enabled pgbouncer in transaction mode",
            label_visibility="collapsed",
        )
        b1, b2, _ = st.columns([1, 1, 4])
        worked = b1.button("Fix worked", key="btn_yes")
        failed = b2.button("Fix failed", key="btn_no")

        if worked or failed:
            if not fix.strip():
                st.info("Describe the fix you tried first.")
            else:
                record_outcome(st.session_state["alert"], fix.strip(), worked)
                st.session_state["saved"] = (
                    ("ok", "Saved. The agent will prefer this fix next time.")
                    if worked
                    else ("bad", "Saved. The agent will avoid this fix next time.")
                )

        saved = st.session_state.get("saved")
        if saved:
            (st.success if saved[0] == "ok" else st.warning)(saved[1])

with st.expander("Log a resolved incident"):
    svc = st.text_input("Service", key="li_svc", placeholder="storage-service")
    sym = st.text_input("What was happening", key="li_sym", placeholder="uploads failing with 403 signature errors")
    cause = st.text_input("Root cause", key="li_cause", placeholder="clock drift on the upload workers")
    fixed = st.text_input("Fix", key="li_fix", placeholder="synced NTP and restarted workers")
    mins = st.number_input("Minutes to resolve", min_value=1, value=30, key="li_min")
    if st.button("Save to memory", key="li_save"):
        if all(v.strip() for v in (svc, sym, cause, fixed)):
            record_incident(svc.strip(), sym.strip(), cause.strip(), fixed.strip(), int(mins))
            st.success("Saved. It can be recalled within a minute or so.")
        else:
            st.info("Fill in every field first.")