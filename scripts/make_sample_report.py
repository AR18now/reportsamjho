"""Generates samples/sample_report.pdf: a SYNTHETIC lab report (fake patient)
so the repo never contains real medical data."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "samples" / "sample_report.pdf"
PANELS = [
    ("COMPLETE BLOOD COUNT", [
        ("Haemoglobin", "10.8", "g/dL", "12.0 - 16.0"),
        ("Total Leucocyte Count", "7.2", "x10^9/L", "4.0 - 11.0"),
        ("Platelet Count", "245", "x10^9/L", "150 - 400"),
        ("MCV", "71", "fL", "80 - 100"),
    ]),
    ("LIPID PROFILE", [
        ("Total Cholesterol", "236", "mg/dL", "< 200"),
        ("HDL Cholesterol", "38", "mg/dL", "> 40"),
        ("Triglycerides", "142", "mg/dL", "< 150"),
    ]),
    ("LIVER FUNCTION TESTS", [
        ("ALT (SGPT)", "64", "U/L", "0 - 40"),
        ("Total Bilirubin", "0.7", "mg/dL", "0.2 - 1.2"),
    ]),
    ("VITAMINS", [
        ("25-OH Vitamin D", "14", "ng/mL", "30 - 100"),
    ]),
    ("INFLAMMATORY MARKERS", [
        ("C-Reactive Protein", "3.1", "mg/L", "0 - 5"),
    ]),
    ("URINE R/E (ROUTINE EXAMINATION)", [
        ("Reaction (pH)", "7.0", "", "4.5 - 8.0"),
        ("Specific Gravity", "1.020", "", "1.005 - 1.030"),
        ("Pus Cells", "8-10", "/HPF", "0 - 5"),
    ]),
]

def main():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 14); c.drawString(40, y, "DEMO DIAGNOSTIC LAB (SYNTHETIC SAMPLE - NOT A REAL PATIENT)"); y -= 22
    c.setFont("Helvetica", 9)
    c.drawString(40, y, "Patient: Test Patient   Age/Sex: 34 Y / F   Report Date: 10-Oct-2026"); y -= 26
    for title, rows in PANELS:
        c.setFont("Helvetica-Bold", 10); c.drawString(40, y, title); y -= 14
        c.setFont("Helvetica-Bold", 8)
        for x, t in ((40, "Test"), (240, "Result"), (320, "Unit"), (400, "Reference Range")):
            c.drawString(x, y, t)
        y -= 12; c.setFont("Helvetica", 9)
        for name, val, unit, ref in rows:
            for x, t in ((40, name), (240, val), (320, unit), (400, ref)):
                c.drawString(x, y, t)
            y -= 13
        y -= 10
    c.setFont("Helvetica-Oblique", 8); c.drawString(40, 40, "This is a synthetic report generated for testing ReportSamjho.")
    c.save(); print("wrote", OUT)

if __name__ == "__main__":
    main()
