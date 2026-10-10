# MLH submission (copy-paste)

**Title:** ReportSamjho

**Description:**
ReportSamjho helps patients in Pakistan understand their lab reports. Upload a report PDF and it shows which values are outside the normal range, explains what each test measures in simple English, Urdu or Roman Urdu, and lists questions to ask the doctor. An open-weight model (Llama 3.1 8B Instant via Groq, or Qwen3-8B fully offline via Ollama) extracts every test from any lab's layout and writes the explanations. To keep it safe, plain code checks that every value really exists in the report and decides high/low, and explanations come only from a verified list of 39 common tests. It never diagnoses. Domain: Health & Wellness.

**GitHub link:** https://github.com/<your-username>/reportsamjho

**Team:** Ali Rizwan (solo)

# 2-minute demo script
1. Problem (15s): "Lab reports are full of abbreviations. People panic-Google or wait days for a doctor."
2. Upload the sample report, choose Urdu, click Explain (30s). Point at the out-of-range values first.
3. Urine pH card (15s): "Same test name means different things. pH under urine is explained; pH under blood gases is never guessed."
4. CRP card (10s): "Not in our verified list, so we say ask your doctor instead of inventing."
5. Open "How we checked these results" (20s): grounding check, code decides high/low, model only rephrases verified facts.
6. Model (15s): "Llama 3.1 8B on Groq, or Qwen3-8B offline with Ollama so medical data never leaves the laptop."
7. Limitations (15s): scanned reports need OCR, 39 tests covered, not a diagnosis tool.
