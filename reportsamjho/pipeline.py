"""ReportSamjho core pipeline.

Flow: PDF -> raw text -> LLM extraction (JSON) -> code validation & status
      -> knowledge-base match -> LLM plain-language explanation (grounded in KB).

Design rule: the model reads and explains; plain code decides whether a number
is low / normal / high and checks every number actually exists in the report.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "tests.json"
MAX_REPORT_CHARS = 12000

# --------------------------------------------------------------------------
# Model client (OpenRouter, Groq or Ollama, all OpenAI-compatible)
# --------------------------------------------------------------------------
PROVIDERS = {
    # Groq shut down llama-3.1-8b-instant on 2026-08-16 and has no <=8B
    # replacement, so OpenRouter's free <=8B model is the default.
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "liquid/lfm-2.5-2.6b:free",
        "key_env": "OPENROUTER_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
        "key_env": "GROQ_API_KEY",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "qwen3:8b",
        "key_env": None,
    },
}


def get_client():
    """Return (client, model_name, provider) from environment variables."""
    from openai import OpenAI

    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    if provider not in PROVIDERS:
        raise ValueError(f"LLM_PROVIDER must be one of {list(PROVIDERS)}")
    cfg = PROVIDERS[provider]
    base_url = os.getenv("LLM_BASE_URL", cfg["base_url"])
    model = os.getenv("LLM_MODEL", cfg["default_model"])
    if cfg["key_env"]:
        key = os.getenv(cfg["key_env"])
        if not key:
            raise RuntimeError(f"Set {cfg['key_env']} in your .env file.")
    else:
        key = "ollama"  # Ollama ignores the key but the client needs one
    # Fail with a clear message instead of spinning when a free tier is slow or queued.
    timeout = float(os.getenv("LLM_TIMEOUT", "240"))
    return OpenAI(base_url=base_url, api_key=key, timeout=timeout, max_retries=1), model, provider


def _chat_json(client, model: str, system: str, user: str) -> Any:
    """Call the model at temperature 0 and parse a JSON object from the reply."""
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
    )
    return parse_json_loose(resp.choices[0].message.content or "")


def parse_json_loose(text: str) -> Any:
    """Parse JSON even if the model wrapped it in fences or <think> tags."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            return json.loads(m.group(0))
        raise


# --------------------------------------------------------------------------
# Step 1: PDF -> text
# --------------------------------------------------------------------------
def pdf_to_text(file) -> str:
    import pdfplumber

    parts = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


# --------------------------------------------------------------------------
# Step 2: LLM extraction
# --------------------------------------------------------------------------
EXTRACT_SYSTEM = """You extract lab test results from the text of a medical lab report.
Return ONLY a JSON object: {"tests": [ ... ]}. Each item:
{
 "panel": section heading the test is under (e.g. "Complete Blood Count", "Urine R/E", "Lipid Profile"), or null,
 "name": test name exactly as written,
 "value": the result exactly as written, WITHOUT the unit (string, e.g. "13.2" or "8-10" or "Nil" or "Positive"),
 "unit": unit as written or null (e.g. "g/dL"),
 "ref_low": lower limit of the reference range as a number, or null,
 "ref_high": upper limit of the reference range as a number, or null,
 "ref_text": the reference range exactly as written, or null
}
Rules:
- Copy values only from the report. Never guess, calculate or invent a value.
- For ranges like "< 200" set ref_low null, ref_high 200. For "> 40" set ref_low 40, ref_high null.
- Skip patient details, doctor names, addresses and comments.
- If the report has no test results, return {"tests": []}."""


def extract_tests(client, model: str, report_text: str) -> list[dict]:
    data = _chat_json(client, model, EXTRACT_SYSTEM,
                      "LAB REPORT TEXT:\n" + report_text[:MAX_REPORT_CHARS])
    tests = data.get("tests", []) if isinstance(data, dict) else []
    return [tidy_extraction(t) for t in tests if isinstance(t, dict) and t.get("name")]


REF_RANGE_RE = re.compile(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*")
REF_BOUND_RE = re.compile(r"\s*([<>])=?\s*(\d+(?:\.\d+)?)\s*")


def tidy_extraction(t: dict) -> dict:
    """Undo common small-model formatting slips before validation runs.

    Only reshapes what the model returned; never adds a number that is not
    already in its output. Validation (grounding + status) is unchanged.
    """
    t = dict(t)
    value, unit = t.get("value"), t.get("unit")
    # "10.8 g/dL" with unit "g/dL" -> "10.8"
    if isinstance(value, str) and isinstance(unit, str) and unit.strip():
        v, u = value.strip(), unit.strip()
        if v.lower().endswith(u.lower()) and len(v) > len(u):
            t["value"] = v[: -len(u)].strip()
    # When the range text is a plain pattern, read the limits from it with code
    # instead of trusting the model's numbers: live runs showed a 2.6B model
    # turning "> 40" into an upper limit, which made a low HDL look normal.
    ref = t.get("ref_text")
    if isinstance(ref, str):
        if m := REF_RANGE_RE.fullmatch(ref):
            t["ref_low"], t["ref_high"] = float(m.group(1)), float(m.group(2))
        elif m := REF_BOUND_RE.fullmatch(ref):
            if m.group(1) == "<":
                t["ref_low"], t["ref_high"] = None, float(m.group(2))
            else:
                t["ref_low"], t["ref_high"] = float(m.group(2)), None
    return t


# --------------------------------------------------------------------------
# Step 3: validation and status (plain code, no AI)
# --------------------------------------------------------------------------
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def to_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    m = NUM_RE.fullmatch(value.strip().replace(",", ""))
    return float(m.group(0)) if m else None


def numbers_in_text(text: str) -> list[float]:
    # No minus sign here: in "4.5-8.0" the dash is a range separator.
    return [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))]


RANGE_VALUE_RE = re.compile(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*")


def value_for_status(value: Any) -> float | None:
    """Number used for the status check. '8-10' (common for urine cells) -> 10."""
    n = to_number(value)
    if n is not None:
        return n
    if isinstance(value, str):
        m = RANGE_VALUE_RE.fullmatch(value)
        if m:
            return max(float(m.group(1)), float(m.group(2)))
    return None


def value_in_report(value: Any, report_text: str) -> bool:
    """Grounding check: the extracted value must appear in the report text."""
    num = to_number(value)
    if num is not None:
        return any(abs(abs(num) - n) < 1e-9 for n in numbers_in_text(report_text))
    if isinstance(value, str) and value.strip():
        return value.strip().lower() in report_text.lower()
    return False


def compute_status(value: Any, low: Any, high: Any) -> str:
    """Return normal / low / high / far_low / far_high / no_range / text."""
    v = value_for_status(value)
    lo, hi = to_number(low), to_number(high)
    if v is None:
        return "text"
    if lo is None and hi is None:
        return "no_range"
    # "far" = at most half the lower limit, or at least double the upper limit.
    # Only used to show a stronger "talk to your doctor soon" note, never a diagnosis.
    if lo is not None and v < lo:
        return "far_low" if lo > 0 and v <= 0.5 * lo else "low"
    if hi is not None and v > hi:
        return "far_high" if hi > 0 and v >= 2 * hi else "high"
    return "normal"


# --------------------------------------------------------------------------
# Step 4: knowledge base matching
# --------------------------------------------------------------------------
def load_kb(path: Path = KB_PATH) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["tests"]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def match_kb(name: str, panel: str | None, kb: list[dict]) -> dict | None:
    """Find the verified explanation for a test, or None if unsure.

    Panel-aware: the same name can mean different things (urine pH vs blood pH),
    so panel-specific entries only match when the report section matches them,
    and a panel-specific name never falls back to a generic entry.
    """
    n, p = _norm(name), _norm(panel or "")

    def panel_ok(e: dict) -> bool | None:
        kws = e.get("panel_keywords") or []
        if not kws:
            return None  # generic entry
        return any(_norm(k) in p for k in kws) if p else False

    special_panel = bool(p) and any(panel_ok(e) for e in kb)
    allowed = [e for e in kb if panel_ok(e) or (panel_ok(e) is None and not special_panel)]

    exact = [e for e in allowed if n in {_norm(a) for a in e["aliases"]}]
    if exact:
        exact.sort(key=lambda e: 0 if panel_ok(e) else 1)
        return exact[0]
    best, score = None, 0.0
    for e in allowed:
        for a in e["aliases"]:
            r = SequenceMatcher(None, n, _norm(a)).ratio()
            if r > score:
                best, score = e, r
    return best if score >= 0.9 else None


# --------------------------------------------------------------------------
# Step 5: grounded explanation
# --------------------------------------------------------------------------
LANG_HINT = {
    "English": "simple English",
    "Urdu": "simple Urdu written in Urdu script",
    "Roman Urdu": "simple Roman Urdu (Urdu written in English letters)",
}
# One example sentence per language: small models follow an example far more
# reliably than an instruction alone (a live run returned English for Roman Urdu).
LANG_EXAMPLE = {
    "English": "Your haemoglobin is a little below the normal range.",
    "Urdu": "آپ کا ہیموگلوبن نارمل حد سے تھوڑا کم ہے۔ یہ خون میں آکسیجن لے جاتا ہے۔",
    "Roman Urdu": "Aap ka haemoglobin normal hadd se thora kam hai. Yeh khoon mein oxygen le jata hai.",
}

EXPLAIN_SYSTEM = """You explain lab results to a patient with no medical background.
You receive results that ALREADY have a verified status and a verified knowledge entry.
Rules:
- Use ONLY the facts in each knowledge entry. Do not add medical facts of your own.
- Never diagnose. Never say the person has a disease. Use "can be linked to".
- Do not change the status you are given.
- 2 to 3 short sentences per test. Warm, calm, plain words.
Return ONLY JSON: {"explanations": [{"id": <same id>, "text": "..."}]}"""


def explain(client, model: str, items: list[dict], language: str) -> dict[str, str]:
    """items: [{id, name, value, unit, status, kb}] -> {id: explanation}."""
    if not items:
        return {}
    payload = [{
        "id": it["id"], "test": it["name"], "value": it["value"], "unit": it.get("unit"),
        "status": it["status"],
        "knowledge": {k: it["kb"][k] for k in ("measures", "high_means", "low_means")},
    } for it in items]
    lang = language if language in LANG_HINT else "English"
    user = (f"Write EVERY explanation in {LANG_HINT[lang]}, not in any other language. "
            f'Example of the style: "{LANG_EXAMPLE[lang]}"\n'
            f"RESULTS:\n{json.dumps(payload, ensure_ascii=False)}")
    data = _chat_json(client, model, EXPLAIN_SYSTEM, user)
    out = {}
    for e in (data.get("explanations", []) if isinstance(data, dict) else []):
        if isinstance(e, dict) and e.get("id") is not None and e.get("text"):
            out[str(e["id"])] = str(e["text"]).strip()
    return out


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
@dataclass
class Result:
    id: str
    name: str
    panel: str | None
    value: Any
    unit: str | None
    ref_text: str | None
    status: str
    grounded: bool
    kb: dict | None = None
    explanation: str | None = None
    ref_low: Any = None   # passed through for the range bar in the UI
    ref_high: Any = None


@dataclass
class Analysis:
    results: list[Result] = field(default_factory=list)
    dropped: list[dict] = field(default_factory=list)  # values not found in report
    model: str = ""
    provider: str = ""

    def to_dict(self):
        return asdict(self)


STATUS_ORDER = {"far_high": 0, "far_low": 0, "high": 1, "low": 1,
                "text": 2, "no_range": 3, "normal": 4}


def build_results(raw_tests: list[dict], report_text: str, kb: list[dict]) -> Analysis:
    """Validation + status + KB match. Pure code, fully testable offline."""
    a = Analysis()
    for i, t in enumerate(raw_tests):
        if not value_in_report(t.get("value"), report_text):
            a.dropped.append(t)
            continue
        status = compute_status(t.get("value"), t.get("ref_low"), t.get("ref_high"))
        a.results.append(Result(
            id=str(i), name=str(t["name"]), panel=t.get("panel"), value=t.get("value"),
            unit=t.get("unit"), ref_text=t.get("ref_text"), status=status, grounded=True,
            ref_low=t.get("ref_low"), ref_high=t.get("ref_high"),
            kb=match_kb(str(t["name"]), t.get("panel"), kb),
        ))
    a.results.sort(key=lambda r: STATUS_ORDER.get(r.status, 5))
    return a


def analyze(report_text: str, language: str = "English") -> Analysis:
    client, model, provider = get_client()
    kb = load_kb()
    raw = extract_tests(client, model, report_text)
    a = build_results(raw, report_text, kb)
    a.model, a.provider = model, provider
    to_explain = [{"id": r.id, "name": r.name, "value": r.value, "unit": r.unit,
                   "status": r.status, "kb": r.kb}
                  for r in a.results if r.kb is not None]
    texts = explain(client, model, to_explain, language)
    for r in a.results:
        r.explanation = texts.get(r.id)
    return a
