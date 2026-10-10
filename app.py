"""ReportSamjho: understand your lab report in plain Urdu or English."""
import html
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from reportsamjho.pipeline import analyze, pdf_to_text

load_dotenv()
SAMPLE = Path(__file__).parent / "samples" / "sample_report.pdf"

st.set_page_config(page_title="ReportSamjho", page_icon="🩺", layout="centered")

st.markdown("""
<style>
:root { --ink:#1E2B3C; --muted:#5B6878; --line:#E3E7EC;
        --ok:#2E7D5B; --low:#2F5DA8; --high:#B4462E; --info:#7A6A3A; }
.block-container { max-width: 760px; }
h1 { color: var(--ink); letter-spacing: -0.5px; margin-bottom: 0; }
.tagline { color: var(--muted); font-size: 1.05rem; margin-top: .2rem; }
.summary { border-left: 4px solid var(--ink); padding: .6rem 1rem; margin: 1rem 0;
           background: #F6F8FA; color: var(--ink); }
.card { border: 1px solid var(--line); border-left: 6px solid var(--c); border-radius: 6px;
        padding: .8rem 1rem; margin: .6rem 0; }
.card .top { display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.card .name { font-weight: 600; color: var(--ink); }
.card .val { font-weight: 700; color: var(--c); }
.card .meta { color: var(--muted); font-size: .85rem; }
.card .exp { margin-top: .45rem; color: var(--ink); line-height: 1.55; }
.card .note { margin-top: .45rem; font-size: .9rem; color: var(--high); font-weight: 600; }
.rtl { direction: rtl; text-align: right; font-size: 1.08rem; line-height: 1.9; }
</style>
""", unsafe_allow_html=True)

STATUS = {
    "far_high": ("Well above range", "var(--high)"),
    "high": ("Above range", "var(--high)"),
    "far_low": ("Well below range", "var(--low)"),
    "low": ("Below range", "var(--low)"),
    "normal": ("Within range", "var(--ok)"),
    "text": ("See report", "var(--info)"),
    "no_range": ("No range on report", "var(--info)"),
}

st.markdown("<h1>ReportSamjho</h1>", unsafe_allow_html=True)
st.markdown('<p class="tagline">Upload your lab report. See which values are outside the normal range, '
            "what each test means, and what to ask your doctor.</p>", unsafe_allow_html=True)

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

if st.button("Explain my report", type="primary", disabled=not report_text):
    with st.spinner("Reading your report…"):
        try:
            st.session_state["analysis"] = analyze(report_text, language)
            st.session_state["lang"] = language
        except Exception as e:  # show a clear message instead of a stack trace
            st.error(f"Could not analyze the report: {e}")

a = st.session_state.get("analysis")
if a:
    lang = st.session_state.get("lang", "English")
    attention = [r for r in a.results if r.status in ("high", "low", "far_high", "far_low")]
    if not a.results:
        st.info("No test results were found. Check that the PDF is a lab report, or paste the results text.")
    else:
        st.markdown(f'<div class="summary"><b>{len(a.results)}</b> results found. '
                    f'<b>{len(attention)}</b> outside the normal range.</div>', unsafe_allow_html=True)

    for r in a.results:
        label, color = STATUS.get(r.status, ("", "var(--muted)"))
        value = html.escape(f"{r.value} {r.unit or ''}".strip())
        ref = html.escape(r.ref_text or "not given")
        panel = html.escape(r.panel or "")
        if r.kb and r.explanation:
            cls = ' class="exp rtl"' if lang == "Urdu" else ' class="exp"'
            body = f"<div{cls}>{html.escape(r.explanation)}</div>"
        elif r.kb:
            body = f'<div class="exp">{html.escape(r.kb["measures"])}</div>'
        else:
            body = ('<div class="exp"><i>No verified explanation for this test yet. '
                    "Please ask your doctor what it means for you.</i></div>")
        note = ('<div class="note">This value is far from the normal range. '
                "Please show this report to a doctor soon.</div>"
                if r.status in ("far_high", "far_low") else "")
        st.markdown(f"""
<div class="card" style="--c:{color}">
  <div class="top"><span class="name">{html.escape(r.name)}</span>
       <span class="val">{value} · {label}</span></div>
  <div class="meta">{panel}{' · ' if panel else ''}Normal range: {ref}</div>
  {body}{note}
</div>""", unsafe_allow_html=True)

    if attention:
        st.subheader("Questions to ask your doctor")
        for r in attention:
            st.markdown(f"- My **{r.name}** is {STATUS[r.status][0].lower()}. "
                        "What could be causing this, and does it need a repeat test or treatment?")

    with st.expander("How we checked these results"):
        st.write(f"Model: `{a.model}` via {a.provider}. The model reads the report and writes the explanations. "
                 "Plain code checks that every value really appears in your report and decides "
                 "whether it is above or below the range. Explanations come only from a verified "
                 "list of common tests.")
        if a.dropped:
            st.write("These values were removed because they could not be found in the report text:")
            st.json(a.dropped)

    st.caption("ReportSamjho helps you understand your report. It does not diagnose and does not "
               "replace a doctor. Always discuss your results with a qualified doctor.")
