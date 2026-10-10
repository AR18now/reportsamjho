"""Builds knowledge/tests.json. Explanations written by the team in plain words,
checked against MedlinePlus (medlineplus.gov/lab-tests). Edit here, then re-run."""
import json, pathlib
M = "MedlinePlus Lab Tests (medlineplus.gov/lab-tests)"
T = []
def add(i, aliases, measures, high, low, kw=None):
    T.append({"id": i, "aliases": aliases, "panel_keywords": kw or [], "measures": measures,
              "high_means": high, "low_means": low, "source": M})

# Complete blood count
add("hemoglobin", ["Hemoglobin","Haemoglobin","Hb","HGB","Hb%"],
    "The protein in red blood cells that carries oxygen around the body.",
    "Can be linked to dehydration, smoking, living at high altitude, or some lung, heart or blood conditions.",
    "Can be linked to anemia, often from low iron, vitamin B12 or folate, or from blood loss. Low levels can cause tiredness and weakness.")
add("rbc", ["RBC","Red Blood Cells","RBC Count","Red Cell Count","Total RBC"],
    "The number of red blood cells, which carry oxygen.",
    "Can be linked to dehydration, smoking, or some heart, lung or bone marrow conditions.",
    "Can be linked to anemia, blood loss, or nutritional deficiencies.")
add("wbc", ["WBC","TLC","Total Leucocyte Count","Total Leukocyte Count","White Blood Cells","WBC Count","White Cell Count"],
    "The number of white blood cells, which fight infection.",
    "Can be linked to infection, inflammation, stress, some medicines, or less commonly blood disorders.",
    "Can be linked to some viral infections, certain medicines, or bone marrow problems, and can lower the body's ability to fight infection.")
add("platelets", ["Platelets","Platelet Count","PLT"],
    "Small blood cells that help blood clot and stop bleeding.",
    "Can be linked to infection, inflammation, iron deficiency, or some bone marrow conditions.",
    "Can be linked to viral infections such as dengue, some medicines, or bone marrow problems, and can increase bleeding or bruising.")
add("hct", ["HCT","Hematocrit","Haematocrit","PCV","Packed Cell Volume"],
    "The share of your blood made up of red blood cells.",
    "Can be linked to dehydration or conditions that increase red blood cells.",
    "Can be linked to anemia or blood loss.")
add("mcv", ["MCV","Mean Corpuscular Volume","Mean Cell Volume"],
    "The average size of your red blood cells.",
    "Larger cells can be linked to low vitamin B12 or folate, liver conditions, or alcohol use.",
    "Smaller cells are often linked to iron deficiency or inherited conditions such as thalassemia trait.")
add("mch", ["MCH","Mean Corpuscular Hemoglobin","Mean Corpuscular Haemoglobin"],
    "The average amount of hemoglobin inside each red blood cell.",
    "Can be linked to larger red cells, for example from low vitamin B12 or folate.",
    "Can be linked to iron deficiency or thalassemia trait.")
add("mchc", ["MCHC","Mean Corpuscular Hemoglobin Concentration"],
    "How concentrated hemoglobin is inside red blood cells.",
    "Can be linked to some inherited red cell conditions, or can be a measurement effect.",
    "Can be linked to iron deficiency anemia.")
add("rdw", ["RDW","RDW-CV","Red Cell Distribution Width"],
    "How much your red blood cells vary in size.",
    "Can be linked to mixed or changing causes of anemia, such as iron or vitamin deficiency.",
    "A low value is usually not a concern.")
add("neutrophils", ["Neutrophils","Neutrophil","Polymorphs"],
    "The most common type of white blood cell, the first responders to bacterial infection.",
    "Can be linked to bacterial infection, inflammation, stress, or steroid medicines.",
    "Can be linked to some viral infections, certain medicines, or bone marrow problems.")
add("lymphocytes", ["Lymphocytes","Lymphocyte"],
    "White blood cells that fight viral infections and make antibodies.",
    "Can be linked to viral infections or, less commonly, some blood disorders.",
    "Can be linked to some infections, steroid medicines, or immune system problems.")
add("eosinophils", ["Eosinophils","Eosinophil"],
    "White blood cells involved in allergies and fighting parasites.",
    "Can be linked to allergies, asthma, or parasitic (worm) infections.",
    "A low value is usually not a concern.")
add("esr", ["ESR","Erythrocyte Sedimentation Rate"],
    "A general marker of inflammation in the body.",
    "Can be linked to infection, inflammation, or some chronic conditions. It does not point to one specific cause.",
    "A low value is usually not a concern.")
# Sugar
add("fbs", ["Fasting Blood Sugar","FBS","Fasting Glucose","Glucose Fasting","Fasting Plasma Glucose","Blood Sugar Fasting","Blood Glucose Fasting"],
    "The sugar level in your blood after not eating for 8 or more hours.",
    "Can be linked to prediabetes or diabetes, stress, or some medicines.",
    "Can be linked to long fasting, some diabetes medicines, or less commonly other conditions. Very low sugar can cause shakiness, sweating or confusion.")
add("rbs", ["Random Blood Sugar","RBS","Random Glucose","Blood Sugar Random","Glucose Random"],
    "The sugar level in your blood at any time of day, regardless of meals.",
    "Can be linked to diabetes, a recent meal, stress, or some medicines.",
    "Can be linked to not eating for a long time or some diabetes medicines.")
add("hba1c", ["HbA1c","HBA1C","Glycated Hemoglobin","Glycosylated Hemoglobin","A1c","Hemoglobin A1c"],
    "Your average blood sugar over roughly the past 2 to 3 months.",
    "Can be linked to prediabetes or diabetes, or to diabetes that is not well controlled.",
    "A low value is usually not a concern, though some blood conditions can affect the result.")
# Lipids
add("cholesterol", ["Total Cholesterol","Cholesterol","Serum Cholesterol","Cholesterol Total"],
    "The total amount of cholesterol, a type of fat, in your blood.",
    "Can be linked to diet, genetics, low activity, or thyroid problems, and raises the long-term risk of heart disease.",
    "A low value is usually not a concern.")
add("ldl", ["LDL","LDL Cholesterol","LDL-C","Low Density Lipoprotein"],
    "The 'bad' cholesterol that can build up in blood vessel walls.",
    "Higher levels raise the long-term risk of heart disease and stroke.",
    "A low value is generally considered favorable.")
add("hdl", ["HDL","HDL Cholesterol","HDL-C","High Density Lipoprotein"],
    "The 'good' cholesterol that helps remove other cholesterol from the blood.",
    "Higher levels are generally considered protective.",
    "Low levels can be linked to low activity, smoking or excess weight, and raise heart disease risk.")
add("triglycerides", ["Triglycerides","TG","Serum Triglycerides"],
    "A type of fat in the blood that comes largely from food.",
    "Can be linked to diet high in sugar or fat, excess weight, alcohol, or diabetes, and raises heart disease risk.",
    "A low value is usually not a concern.")
# Liver
add("alt", ["ALT","SGPT","ALT (SGPT)","SGPT (ALT)","Alanine Aminotransferase"],
    "An enzyme found mainly in the liver. It rises when liver cells are irritated or damaged.",
    "Can be linked to fatty liver, hepatitis, some medicines, or alcohol use.",
    "A low value is usually not a concern.")
add("ast", ["AST","SGOT","AST (SGOT)","SGOT (AST)","Aspartate Aminotransferase"],
    "An enzyme found in the liver, heart and muscles.",
    "Can be linked to liver irritation, recent heavy exercise, or muscle injury.",
    "A low value is usually not a concern.")
add("alp", ["ALP","Alkaline Phosphatase","Alk Phos"],
    "An enzyme found mainly in the liver and bones.",
    "Can be linked to liver or bile duct problems or bone conditions. It is normally higher in growing children and in pregnancy.",
    "Can be linked to low zinc or poor nutrition, though often not a concern.")
add("bilirubin", ["Total Bilirubin","Bilirubin Total","Bilirubin","Serum Bilirubin","S. Bilirubin"],
    "A yellow substance made when old red blood cells break down, cleared by the liver.",
    "Can be linked to liver problems, blocked bile flow, or faster breakdown of red cells, and can cause yellow skin or eyes (jaundice).",
    "A low value is usually not a concern.")
add("albumin", ["Albumin","Serum Albumin","S. Albumin"],
    "The main protein in blood, made by the liver.",
    "Can be linked to dehydration.",
    "Can be linked to poor nutrition, liver problems, or kidney problems that leak protein.")
# Kidney
add("creatinine", ["Creatinine","Serum Creatinine","S. Creatinine","Creatinine Serum"],
    "A waste product from muscles, removed by the kidneys. It shows how well the kidneys filter.",
    "Can be linked to reduced kidney function, dehydration, high muscle mass, or some medicines.",
    "Can be linked to low muscle mass, and is usually not a concern.")
add("urea", ["Urea","Blood Urea","Serum Urea","BUN","Blood Urea Nitrogen"],
    "A waste product from breaking down protein, removed by the kidneys.",
    "Can be linked to dehydration, reduced kidney function, or a high-protein diet.",
    "Can be linked to a low-protein diet or liver problems, and is often not a concern.")
add("uric_acid", ["Uric Acid","Serum Uric Acid","S. Uric Acid"],
    "A waste product from breaking down purines, found in some foods like red meat.",
    "Can be linked to gout, kidney stones, diet, or reduced kidney function.",
    "A low value is usually not a concern.")
add("egfr", ["eGFR","Estimated GFR","GFR"],
    "An estimate of how well your kidneys filter blood, calculated from creatinine.",
    "A higher value is usually not a concern.",
    "Can be linked to reduced kidney function. Your doctor will look at it alongside other results.")
# Thyroid
add("tsh", ["TSH","Thyroid Stimulating Hormone"],
    "A hormone from the brain that tells the thyroid gland how much hormone to make.",
    "Can be linked to an underactive thyroid (hypothyroidism), which can cause tiredness, weight gain and feeling cold.",
    "Can be linked to an overactive thyroid (hyperthyroidism), which can cause a fast heartbeat, weight loss and anxiety.")
add("t4", ["Free T4","FT4","T4","Thyroxine"],
    "The main hormone made by the thyroid gland, which controls metabolism.",
    "Can be linked to an overactive thyroid.",
    "Can be linked to an underactive thyroid.")
add("t3", ["Free T3","FT3","T3","Triiodothyronine"],
    "An active thyroid hormone that controls metabolism.",
    "Can be linked to an overactive thyroid.",
    "Can be linked to an underactive thyroid or illness.")
# Vitamins / iron
add("vit_d", ["Vitamin D","25-OH Vitamin D","25 Hydroxy Vitamin D","Vit D","25(OH)D","Vitamin D3"],
    "The vitamin that helps the body absorb calcium for strong bones.",
    "Very high levels are usually from taking too many supplements.",
    "Can be linked to little sun exposure or diet, and to bone pain, weakness or tiredness.")
add("vit_b12", ["Vitamin B12","B12","Vit B12","Cobalamin"],
    "A vitamin needed for nerves and for making red blood cells.",
    "A high value is usually not a concern, often from supplements.",
    "Can be linked to diet, absorption problems, or some medicines, and can cause tiredness, numbness or anemia.")
add("ferritin", ["Ferritin","Serum Ferritin"],
    "A protein that stores iron. It shows your body's iron reserves.",
    "Can be linked to inflammation, infection, liver conditions, or iron overload.",
    "Can be linked to low iron stores, a common cause of anemia.")
# Urine R/E (panel-aware)
U = ["urine","r e","routine","urinalysis","complete examination"]
add("urine_ph", ["pH","Reaction","Reaction (pH)","Urine pH"],
    "How acidic or alkaline your urine is. It changes with diet and fluids.",
    "More alkaline urine can be linked to diet (e.g. lots of vegetables), some urinary infections, or kidney conditions.",
    "More acidic urine can be linked to diet (e.g. high protein), dehydration, or some metabolic conditions.", U)
add("urine_sg", ["Specific Gravity","Sp. Gravity","SG","Specific Gravity (urine)"],
    "How concentrated your urine is.",
    "Can be linked to not drinking enough water.",
    "Can be linked to drinking a lot of water, or some kidney or hormone conditions.", U)
add("urine_pus", ["Pus Cells","Pus cells","WBC","WBCs","WBC (urine)","Leucocytes"],
    "White blood cells in urine.",
    "Can be linked to a urinary tract infection or inflammation.",
    "A low or nil value is normal.", U)
add("urine_rbc", ["Red Cells","RBCs","RBC","Red Blood Cells","Red Blood Cells (urine)"],
    "Red blood cells in urine.",
    "Can be linked to infection, kidney stones, recent heavy exercise, or menstruation. Persistent blood in urine should be checked by a doctor.",
    "A low or nil value is normal.", U)

out = pathlib.Path(__file__).resolve().parent.parent / "knowledge" / "tests.json"
out.write_text(json.dumps({"version": 1, "source_note": "Plain-language summaries written by the team, checked against MedlinePlus. Not medical advice.", "tests": T}, indent=2, ensure_ascii=False), encoding="utf-8")
print(len(T), "tests written to", out)
