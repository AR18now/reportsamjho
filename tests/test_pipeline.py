"""Offline tests for the code-only parts of the pipeline (no API key needed).
The model's extraction output is simulated with what a correct extraction looks like."""
import json
from pathlib import Path

from reportsamjho.pipeline import (build_results, compute_status, load_kb, match_kb, tidy_extraction,
                                   parse_json_loose, pdf_to_text, value_in_report)

ROOT = Path(__file__).resolve().parent.parent
KB = load_kb()
REPORT = pdf_to_text(ROOT / "samples" / "sample_report.pdf")
EXPECTED = json.loads((ROOT / "samples" / "sample_expected.json").read_text())


def test_status_logic():
    assert compute_status("10.8", 12, 16) == "low"
    assert compute_status("13", 12, 16) == "normal"
    assert compute_status("236", None, 200) == "high"
    assert compute_status("38", 40, None) == "low"
    assert compute_status("64", 0, 40) == "high"
    assert compute_status("95", 0, 40) == "far_high"
    assert compute_status("8-10", 0, 5) == "far_high"
    assert compute_status("7", 0, 5) == "high"
    assert compute_status("Nil", None, None) == "text"
    assert compute_status("5", None, None) == "no_range"


def test_grounding_rejects_invented_values():
    assert value_in_report("10.8", REPORT)
    assert value_in_report("8-10", REPORT)
    assert not value_in_report("11.9", REPORT)       # number not in the report
    assert not value_in_report("Positive", REPORT)   # text not in the report


def test_panel_aware_matching():
    assert match_kb("Reaction (pH)", "URINE R/E (ROUTINE EXAMINATION)", KB)["id"] == "urine_ph"
    assert match_kb("pH", "Arterial Blood Gases", KB) is None   # never explain blood pH as urine pH
    assert match_kb("pH", None, KB) is None
    assert match_kb("RBC", "Complete Blood Count", KB)["id"] == "rbc"
    assert match_kb("RBC", "Urine R/E", KB)["id"] == "urine_rbc"
    assert match_kb("SGPT", "LFT", KB)["id"] == "alt"
    assert match_kb("C-Reactive Protein", "Inflammatory Markers", KB) is None  # not in KB -> safe fallback


def test_sample_report_end_to_end_offline():
    a = build_results(EXPECTED["simulated_extraction"], REPORT, KB)
    got = {r.name: r.status for r in a.results}
    assert got == EXPECTED["expected_status"]
    assert [d["name"] for d in a.dropped] == ["Fake Test"]  # hallucinated row removed
    kb_ids = {r.name: (r.kb or {}).get("id") for r in a.results}
    assert kb_ids["Reaction (pH)"] == "urine_ph"
    assert kb_ids["C-Reactive Protein"] is None


def test_json_parsing_tolerates_wrappers():
    assert parse_json_loose('```json\n{"tests": []}\n```') == {"tests": []}
    assert parse_json_loose('<think>hmm</think>{"a": 1}') == {"a": 1}


def test_tidy_extraction_fixes_small_model_slips():
    # Unit glued onto the value (seen live with LFM2.5-2.6B) is split off.
    t = tidy_extraction({"name": "Haemoglobin", "value": "10.8 g/dL", "unit": "g/dL",
                         "ref_low": 12.0, "ref_high": 16.0})
    assert t["value"] == "10.8"
    assert compute_status(t["value"], t["ref_low"], t["ref_high"]) == "low"
    # Missing numeric limits are read from the range text.
    t = tidy_extraction({"name": "x", "value": "236", "ref_text": "< 200", "ref_low": None, "ref_high": None})
    assert (t["ref_low"], t["ref_high"]) == (None, 200.0)
    t = tidy_extraction({"name": "x", "value": "71", "ref_text": "80 - 100"})
    assert (t["ref_low"], t["ref_high"]) == (80.0, 100.0)
    # Text values and values that already look right are left alone.
    assert tidy_extraction({"name": "x", "value": "Nil", "unit": None})["value"] == "Nil"
    assert tidy_extraction({"name": "x", "value": "8-10", "unit": "/HPF"})["value"] == "8-10"


def test_range_text_overrides_wrong_model_limits():
    # Seen live: model read "> 40" as an upper limit, so HDL 38 looked normal.
    t = tidy_extraction({"name": "HDL Cholesterol", "value": "38", "ref_text": "> 40",
                         "ref_low": None, "ref_high": 40})
    assert (t["ref_low"], t["ref_high"]) == (40.0, None)
    assert compute_status(t["value"], t["ref_low"], t["ref_high"]) == "low"
    # Unusual range text is left to the model's numbers.
    t = tidy_extraction({"name": "x", "value": "5", "ref_text": "Up to 6", "ref_low": None, "ref_high": 6})
    assert (t["ref_low"], t["ref_high"]) == (None, 6)
