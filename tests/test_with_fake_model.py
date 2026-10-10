"""Runs the full analyze() flow with a fake model client (no network, no key)."""
import json
from pathlib import Path
from types import SimpleNamespace

import reportsamjho.pipeline as pl

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = json.loads((ROOT / "samples" / "sample_expected.json").read_text())


class FakeCompletions:
    def create(self, model, messages, **kw):
        system, user = messages[0]["content"], messages[1]["content"]
        if system.startswith("You extract"):
            body = {"tests": EXPECTED["simulated_extraction"]}
        else:
            items = json.loads(user.split("RESULTS:\n", 1)[1])
            body = {"explanations": [{"id": i["id"], "text": f"{i['test']} is {i['status']}."} for i in items]}
        msg = SimpleNamespace(content=json.dumps(body))
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def test_analyze_full_flow(monkeypatch):
    fake = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    monkeypatch.setattr(pl, "get_client", lambda: (fake, "fake-model", "fake"))
    text = pl.pdf_to_text(ROOT / "samples" / "sample_report.pdf")
    a = pl.analyze(text, "English")
    by = {r.name: r for r in a.results}
    assert by["Haemoglobin"].explanation == "Haemoglobin is low."
    assert by["C-Reactive Protein"].explanation is None      # not in KB -> no AI explanation
    assert a.results[0].status in ("far_high", "far_low")   # most urgent first
    assert len(a.dropped) == 1
