# MLH submission (copy-paste)

**Title:** ReportSamjho

**Description:**
ReportSamjho helps patients in Pakistan understand their lab reports. Upload a report PDF (or paste the text) and it shows which values are outside the normal range, explains what each test measures in simple English, Urdu or Roman Urdu, and lists questions to take to the doctor. An open-weight model, LFM2.5-2.6B by Liquid AI (2.6B parameters, free via OpenRouter), reads any lab's layout into structured results and writes the explanations. To keep a small model safe, plain code cleans its output, checks that every value really exists in the report, decides high/low from the report's own ranges, and limits explanations to a checked list of 39 common tests. It never diagnoses. Domain: Health & Wellness. Live demo: https://reportsamjho-x4tk2a2kogtirwrzcjxh7b.streamlit.app

**GitHub link:** https://github.com/AR18now/reportsamjho

**Team:** Ali Rizwan (solo)

**Model disclosure:** LFM2.5-2.6B (Liquid AI, open-weight, 2.6B) via OpenRouter API; optional offline mode with any <=8B Ollama model.

# 2-minute demo script
1. Problem (15s): "Lab reports are full of abbreviations. People panic-Google or wait days for a doctor."
2. Upload the sample report, choose Urdu, click Explain (30s). Point at the out-of-range values first.
3. Urine pH card (15s): "Same test name means different things. pH under urine is explained; pH under blood gases is never guessed."
4. CRP card (10s): "Not in our verified list, so we say ask your doctor instead of inventing."
5. Open "How we checked these results" (20s): grounding check, code decides high/low, model only rephrases verified facts.
6. Model (15s): "LFM2.5-2.6B, an open-weight 2.6B model, free via OpenRouter. Code, not the model, decides high/low."
7. Limitations (15s): small model is slow on the free tier (1-3 min) and weak at Urdu; scanned reports need OCR; 39 tests covered; not a diagnosis tool.
