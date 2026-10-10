"""ReportSamjho: understand your lab report in plain Urdu or English."""
import html
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from reportsamjho.pipeline import PROVIDERS, analyze, pdf_to_text, to_number, value_for_status

load_dotenv()
SAMPLE = Path(__file__).parent / "samples" / "sample_report.pdf"

st.set_page_config(page_title="ReportSamjho · رپورٹ سمجھو", page_icon="🩺", layout="centered")

# Look and feel: a printed lab report, annotated for the patient.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');
:root { --paper:#FBF8F2; --sheet:#FFFDF9; --ink:#1D2430; --muted:#6B6457; --rule:#E2D9C8;
        --green:#0F5C4D; --red:#B23A2B; --blue:#2C4F8C; --ochre:#8A6A1F; }
html, body, [data-testid="stAppViewContainer"], .stMarkdown, .stRadio, .stTabs, .stCheckbox, button, input, textarea {
  font-family: 'IBM Plex Sans', system-ui, sans-serif; }
.block-container { max-width: 760px; padding-top: 3.6rem; }
.mono { font-family: 'IBM Plex Mono', ui-monospace, monospace; }

/* letterhead */
.mast { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; flex-wrap: wrap; }
.mast .kicker { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.mast h1 { font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; color: var(--ink);
           font-size: 2.6rem; line-height: 1; margin: .25rem 0 0; padding: 0; letter-spacing: -.02em; }
.mast .ur { font-family: 'Noto Nastaliq Urdu', serif; font-size: 1.7rem; color: var(--green); line-height: 1.6; }
.rule2 { border-top: 2px solid var(--ink); border-bottom: 1px solid var(--ink); height: 4px; margin: .5rem 0 .9rem; }
.lede { color: var(--ink); font-size: 1.02rem; line-height: 1.6; margin: 0 0 .3rem; }
.byline { color: var(--muted); font-size: .82rem; margin-bottom: 1.2rem; }
.byline b { color: var(--ink); font-weight: 600; }

/* summary slip */
.slip { display: flex; flex-wrap: wrap; border: 1px solid var(--rule); background: var(--sheet); margin: 1.2rem 0 .4rem; }
.slip > div { flex: 1 1 140px; padding: .65rem .9rem; border-right: 1px solid var(--rule); }
.slip > div:last-child { border-right: 0; }
.slip .n { font-family: 'IBM Plex Mono', monospace; font-size: 1.7rem; font-weight: 600; line-height: 1.1; }
.slip .l { font-size: .74rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }

.sect { display: flex; align-items: center; gap: .7rem; margin: 1.6rem 0 .2rem;
        font-size: .76rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.sect::after { content: ""; flex: 1; border-top: 1px solid var(--rule); }

/* one result = one line of the report, annotated */
.row { background: var(--sheet); border: 1px solid var(--rule); border-top: 3px solid var(--c);
       padding: .85rem 1rem .9rem; margin: .55rem 0; }
.row .top { display: flex; justify-content: space-between; align-items: flex-start; gap: .8rem; flex-wrap: wrap; }
.row .name { font-weight: 600; color: var(--ink); font-size: 1.02rem; }
.row .panel { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-top: .1rem; }
.row .val { font-family: 'IBM Plex Mono', monospace; font-weight: 600; color: var(--c); font-size: 1.15rem; text-align: right; }
.row .ref { font-family: 'IBM Plex Mono', monospace; font-size: .76rem; color: var(--muted); text-align: right; }
.stamp { display: inline-block; font-size: .66rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase;
         color: var(--c); border: 1.5px solid var(--c); border-radius: 3px; padding: .05rem .4rem;
         transform: rotate(-3deg); margin-top: .3rem; opacity: .9; }
.scale { position: relative; height: 6px; background: repeating-linear-gradient(90deg, #EDE6D8 0 2px, transparent 2px 10px);
         border-bottom: 1px solid var(--rule); margin: .7rem 0 .3rem; }
.scale .zone { position: absolute; top: 0; bottom: -1px; background: #CFE3DA; border-bottom: 1px solid var(--green); }
.scale .mark { position: absolute; top: -5px; width: 3px; height: 16px; background: var(--c); transform: translateX(-50%); }
.row .exp { margin-top: .55rem; color: var(--ink); line-height: 1.65; font-size: .97rem; }
.row .exp.missing { color: var(--muted); font-style: italic; }
.row .urgent { margin-top: .55rem; font-size: .88rem; color: var(--red); font-weight: 600;
               border-left: 3px solid var(--red); padding-left: .6rem; }
.rtl { direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif !important; font-size: 1.05rem; line-height: 2.3 !important; }

/* tear-off note for the doctor visit */
.note { margin: 1.6rem 0 .4rem; background: #FFF8E6; border: 1px dashed #C9B27A; padding: .9rem 1.1rem; position: relative; }
.note::before { content: "✂"; position: absolute; top: -.75rem; left: .8rem; background: var(--paper); color: #C9B27A; padding: 0 .25rem; }
.note h4 { font-family: 'Source Serif 4', Georgia, serif; margin: 0 0 .4rem; padding: 0; color: var(--ink); font-size: 1.1rem; }
.note ol { margin: 0; padding-left: 1.2rem; color: var(--ink); line-height: 1.6; }
.fine { color: var(--muted); font-size: .8rem; line-height: 1.5; border-top: 1px solid var(--rule); padding-top: .7rem; margin-top: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# label, colour, sort section
STATUS = {
    "far_high": ("Well above range", "var(--red)"),
    "high": ("Above range", "var(--red)"),
    "far_low": ("Well below range", "var(--blue)"),
    "low": ("Below range", "var(--blue)"),
    "normal": ("Within range", "var(--green)"),
    "text": ("Read on report", "var(--ochre)"),
    "no_range": ("No range given", "var(--ochre)"),
}
ATTENTION = ("far_high", "far_low", "high", "low")


def model_label() -> str:
    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    cfg = PROVIDERS.get(provider, {})
    return os.getenv("LLM_MODEL", cfg.get("default_model", ""))


def scale(r) -> str:
    """Where the value sits against the report's own normal range."""
    v = value_for_status(r.value)
    lo, hi = to_number(r.ref_low), to_number(r.ref_high)
    if v is None or (lo is None and hi is None):
        return ""
    if lo is not None and hi is not None and hi > lo:
        pad = (hi - lo) * 0.5
        start, end = lo - pad, hi + pad
    elif hi is not None:
        start, end = 0.0, hi * 1.5
    else:
        start, end = 0.0, lo * 2
    span = (end - start) or 1.0
    pct = lambda x: max(0.0, min(100.0, (x - start) / span * 100))
    z0 = pct(lo) if lo is not None else 0.0
    z1 = pct(hi) if hi is not None else 100.0
    return (f'<div class="scale"><div class="zone" style="left:{z0:.1f}%;width:{z1 - z0:.1f}%"></div>'
            f'<div class="mark" style="left:{pct(v):.1f}%"></div></div>')


def row(r, lang: str) -> str:
    label, color = STATUS.get(r.status, ("", "var(--muted)"))
    value = html.escape(f"{r.value} {r.unit or ''}".strip())
    ref = html.escape(r.ref_text or "—")
    panel = html.escape(r.panel or "")
    if r.kb and r.explanation:
        cls = "exp rtl" if lang == "Urdu" else "exp"
        body = f'<div class="{cls}">{html.escape(r.explanation)}</div>'
    elif r.kb:
        body = f'<div class="exp">{html.escape(r.kb["measures"])}</div>'
    else:
        body = ('<div class="exp missing">This test is not in our checked list yet, so we will not guess. '
                "Please ask your doctor what it means for you.</div>")
    urgent = ('<div class="urgent">Far from the normal range. Please show this report to a doctor soon.</div>'
              if r.status in ("far_high", "far_low") else "")
    return (f'<div class="row" style="--c:{color}"><div class="top">'
            f'<div><div class="name">{html.escape(r.name)}</div><div class="panel">{panel}</div></div>'
            f'<div><div class="val">{value}</div><div class="ref">normal {ref}</div></div></div>'
            f'<span class="stamp">{label}</span>{scale(r)}{body}{urgent}</div>')


# ---------------------------------------------------------------- letterhead
st.markdown(f"""<div class="mast">
<div><div class="kicker">Your lab report, in words you understand</div><h1>ReportSamjho</h1></div>
<div class="ur">رپورٹ سمجھو</div></div>
<div class="rule2"></div>
<p class="lede">Upload a lab report and see which values are outside the normal range, what each test
measures, and what to ask your doctor, in English, Urdu or Roman Urdu.</p>
<div class="byline">Read by the open-weight model <b class="mono">{html.escape(model_label())}</b>.
High / low decided by plain code from your report's own ranges. Never a diagnosis.</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- input
language = st.radio("Explain in", ["English", "Urdu", "Roman Urdu"], horizontal=True)

tab_pdf, tab_text = st.tabs(["Upload PDF", "Paste report text"])
report_text = ""
with tab_pdf:
    up = st.file_uploader("Lab report (PDF)", type=["pdf"])
    use_sample = st.checkbox("Use the sample report (synthetic, not a real patient)")
    if up is not None:
        report_text = pdf_to_text(up)
    elif use_sample:
        report_text = pdf_to_text(SAMPLE)
    if (up is not None or use_sample) and not report_text:
        st.warning("No text found in this PDF. It may be a scanned photo. "
                   "Paste the report text in the other tab instead.")
with tab_text:
    pasted = st.text_area("Report text", height=180,
                          placeholder="Copy the results section of your report here")
    if pasted.strip():
        report_text = pasted.strip()

if st.button("Explain my report", type="primary", disabled=not report_text, use_container_width=True):
    with st.spinner("Reading your report… on the free model this can take 1–3 minutes."):
        try:
            st.session_state["analysis"] = analyze(report_text, language)
            st.session_state["lang"] = language
        except Exception as e:  # show a clear message instead of a stack trace
            st.error(f"Could not analyze the report: {e}")

# ---------------------------------------------------------------- results
a = st.session_state.get("analysis")
if a:
    lang = st.session_state.get("lang", "English")
    attention = [r for r in a.results if r.status in ATTENTION]
    normal = [r for r in a.results if r.status == "normal"]
    other = [r for r in a.results if r.status not in ATTENTION and r.status != "normal"]
    unexplained = sum(1 for r in a.results if not r.kb)

    if not a.results:
        st.info("No test results were found. Check that the PDF is a lab report, or paste the results text.")
    else:
        st.markdown(f"""<div class="slip">
<div><div class="n">{len(a.results)}</div><div class="l">Results read</div></div>
<div><div class="n" style="color:var(--red)">{len(attention)}</div><div class="l">Outside range</div></div>
<div><div class="n" style="color:var(--green)">{len(normal)}</div><div class="l">Within range</div></div>
<div><div class="n" style="color:var(--ochre)">{unexplained}</div><div class="l">Ask your doctor</div></div>
</div>""", unsafe_allow_html=True)

    for title, group in (("Outside the normal range", attention), ("Within the normal range", normal),
                         ("Other results", other)):
        if group:
            st.markdown(f'<div class="sect">{title}</div>', unsafe_allow_html=True)
            for r in group:
                st.markdown(row(r, lang), unsafe_allow_html=True)

    if attention:
        items = "".join(
            f"<li>My <b>{html.escape(r.name)}</b> is {STATUS[r.status][0].lower()}. "
            "What could be causing this, and does it need a repeat test or treatment?</li>"
            for r in attention)
        st.markdown(f'<div class="note"><h4>Take these questions to your doctor</h4><ol>{items}</ol></div>',
                    unsafe_allow_html=True)

    with st.expander("How we checked these results"):
        st.write(f"Model: `{a.model}` via {a.provider}. The model reads the report and writes the explanations. "
                 "Plain code checks that every value really appears in your report and decides "
                 "whether it is above or below the range. Explanations come only from a checked "
                 "list of 39 common tests.")
        if a.dropped:
            st.write("These values were removed because they could not be found in the report text:")
            st.json(a.dropped)
        else:
            st.write("Every value the model extracted was found in your report.")

st.markdown('<div class="fine">ReportSamjho helps you understand your report. It does not diagnose and does '
            "not replace a doctor. Always discuss your results with a qualified doctor. Your report is not "
            'stored. Open source (MIT) · <a href="https://github.com/AR18now/reportsamjho">source code</a></div>',
            unsafe_allow_html=True)
