import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/clinical_trials_demo.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinical_trials (
        trial_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trial_code TEXT,
        trial_title TEXT,
        cancer_type TEXT,
        trial_phase TEXT,
        recruitment_status TEXT,
        city TEXT,
        province TEXT,
        country TEXT,
        latitude REAL,
        longitude REAL,
        hospital_name TEXT,
        summary TEXT,
        eligibility_summary TEXT,
        trial_link TEXT
    )
    """)
    conn.commit()

    # Clear existing data just in case this is re-run
    cursor.execute("DELETE FROM clinical_trials")

    # Mock Data
    trials_data = [
        # Breast Cancer (Toronto, Montreal, Vancouver, Calgary, Ottawa, Quebec City)
        ("ONC-BC-001", "Phase II Immunotherapy Trial for Breast Cancer", "Breast Cancer", "Phase II", "Recruiting", "Toronto", "Ontario", "Canada", 43.6532, -79.3832, "Princess Margaret Cancer Centre", "Immunotherapy targeting HER2 positive tumors", "Adults aged 18-70 with stage II-III breast cancer", "https://www.cancertrialscanada.ca/trial/ONC-BC-001"),
        ("ONC-BC-002", "Phase III Novel Hormone Therapy", "Breast Cancer", "Phase III", "Recruiting", "Montreal", "Quebec", "Canada", 45.5017, -73.5673, "McGill University Health Centre", "Testing efficacy of novel hormone suppression therapy", "Post-menopausal women with ER+ breast cancer", "https://www.cancertrialscanada.ca/trial/ONC-BC-002"),
        ("ONC-BC-003", "Phase I CDK4/6 Inhibitor Combination", "Breast Cancer", "Phase I", "Not Recruiting", "Vancouver", "British Columbia", "Canada", 49.2827, -123.1207, "BC Cancer Agency", "Dose escalation study of inhibitor with endocrine therapy", "Advanced or metastatic HR+ breast cancer", "https://www.cancertrialscanada.ca/trial/ONC-BC-003"),
        ("ONC-BC-004", "Phase I Anti-HER2 Agent", "Breast Cancer", "Phase I", "Recruiting", "Calgary", "Alberta", "Canada", 51.0447, -114.0719, "Tom Baker Cancer Centre", "Evaluating safety of new targeted biologic for HER2+ disease", "Refractory HER2+ breast cancer adults", "https://www.cancertrialscanada.ca/trial/ONC-BC-004"),
        ("ONC-BC-005", "Phase II Adjuvant Therapy Study", "Breast Cancer", "Phase II", "Recruiting", "Ottawa", "Ontario", "Canada", 45.4215, -75.6972, "The Ottawa Hospital", "Adjuvant chemotherapy plus experimental antibody", "Stage I-II breast cancer patients", "https://www.cancertrialscanada.ca/trial/ONC-BC-005"),
        ("ONC-BC-006", "Phase III Radiation Techniques", "Breast Cancer", "Phase III", "Recruiting", "Quebec City", "Quebec", "Canada", 46.8139, -71.2080, "CHU de Québec", "Comparing modern radiation fractions for early breast cancer", "Early stage breast cancer requiring radiotherapy", "https://www.cancertrialscanada.ca/trial/ONC-BC-006"),

        # Lung Cancer
        ("ONC-LC-001", "Phase II ALK Inhibitor Trial", "Lung Cancer", "Phase II", "Recruiting", "Toronto", "Ontario", "Canada", 43.6611, -79.3958, "Mount Sinai Hospital", "Targeted therapy for non-small cell lung cancer", "NSCLC with ALK rearrangement", "https://www.cancertrialscanada.ca/trial/ONC-LC-001"),
        ("ONC-LC-002", "Phase III Pembrolizumab Study", "Lung Cancer", "Phase III", "Recruiting", "Montreal", "Quebec", "Canada", 45.5124, -73.5547, "CHUM", "Immunotherapy compared to traditional chemotherapy", "Stage 3/4 NSCLC, no prior systemic therapy", "https://www.cancertrialscanada.ca/trial/ONC-LC-002"),
        ("ONC-LC-003", "Phase I KRAS Inhibitor", "Lung Cancer", "Phase I", "Recruiting", "Vancouver", "British Columbia", "Canada", 49.2612, -123.1139, "Vancouver General Hospital", "Dose finding study for KRAS G12C mutated tumors", "Advanced NSCLC with KRAS G12C mutation", "https://www.cancertrialscanada.ca/trial/ONC-LC-003"),
        ("ONC-LC-004", "Phase II SCLC Experimental Chemo", "Lung Cancer", "Phase II", "Not Recruiting", "Calgary", "Alberta", "Canada", 51.0664, -114.0906, "Foothills Medical Centre", "New chemotherapy agent for small cell lung cancer", "Extensive stage SCLC", "https://www.cancertrialscanada.ca/trial/ONC-LC-004"),
        ("ONC-LC-005", "Phase III EGFR Mutation Targeted Therapy", "Lung Cancer", "Phase III", "Recruiting", "Ottawa", "Ontario", "Canada", 45.4010, -75.7061, "Queensway Carleton Hospital", "First-line treatment matching for EGFR mutations", "Treatment-naive advanced EGFR+ NSCLC", "https://www.cancertrialscanada.ca/trial/ONC-LC-005"),
        ("ONC-LC-006", "Phase I Double Immunotherapy", "Lung Cancer", "Phase I", "Recruiting", "Quebec City", "Quebec", "Canada", 46.7876, -71.2662, "IUCPQ", "Safety of dual checkpoint inhibition", "Refractory advanced lung cancer", "https://www.cancertrialscanada.ca/trial/ONC-LC-006"),

        # Melanoma
        ("ONC-ME-001", "Phase III BRAF/MEK Combo", "Melanoma", "Phase III", "Recruiting", "Vancouver", "British Columbia", "Canada", 49.2781, -123.1215, "St. Paul's Hospital", "Combination targeted therapy for advanced melanoma", "Unresectable Stage III or IV Melanoma with BRAF V600", "https://www.cancertrialscanada.ca/trial/ONC-ME-001"),
        ("ONC-ME-002", "Phase II Adoptive Cell Transfer", "Melanoma", "Phase II", "Recruiting", "Toronto", "Ontario", "Canada", 43.6558, -79.3871, "Toronto General Hospital", "TIL cell therapy for refractory melanoma", "Metastatic melanoma failed previous anti-PD1", "https://www.cancertrialscanada.ca/trial/ONC-ME-002"),
        ("ONC-ME-003", "Phase I Intralesional Therapy", "Melanoma", "Phase I", "Not Recruiting", "Montreal", "Quebec", "Canada", 45.4962, -73.6268, "Jewish General Hospital", "Oncolytic virus injected directly into lesions", "Stage III/IV with injectable cutaneous metastases", "https://www.cancertrialscanada.ca/trial/ONC-ME-003"),
        ("ONC-ME-004", "Phase II Neo-adjuvant Immunotherapy", "Melanoma", "Phase II", "Recruiting", "Calgary", "Alberta", "Canada", 51.0486, -114.0708, "Rockyview General Hospital", "Immunotherapy given before surgical resection", "Resectable stage III melanoma", "https://www.cancertrialscanada.ca/trial/ONC-ME-004"),
        ("ONC-ME-005", "Phase III Adjuvant Checkpoint Inhibitor", "Melanoma", "Phase III", "Recruiting", "Ottawa", "Ontario", "Canada", 45.3942, -75.7533, "Montfort Hospital", "Preventing recurrence after surgical clearing", "Completely resected high-risk melanoma", "https://www.cancertrialscanada.ca/trial/ONC-ME-005"),
        ("ONC-ME-006", "Phase I Combination Vaccine", "Melanoma", "Phase I", "Recruiting", "Quebec City", "Quebec", "Canada", 46.8041, -71.2407, "Hôpital de l'Enfant-Jésus", "Personalized mRNA cancer vaccine with standard of care", "Advanced melanoma post first line", "https://www.cancertrialscanada.ca/trial/ONC-ME-006"),

        # Leukemia
        ("ONC-LE-001", "Phase I CAR-T Cell Therapy for ALL", "Leukemia", "Phase I", "Recruiting", "Toronto", "Ontario", "Canada", 43.6576, -79.3838, "SickKids / Princess Margaret", "Chimeric Antigen Receptor T-cell therapy", "Relapsed/Refractory Acute Lymphoblastic Leukemia", "https://www.cancertrialscanada.ca/trial/ONC-LE-001"),
        ("ONC-LE-002", "Phase III Targeted FLT3 Inhibitor", "Leukemia", "Phase III", "Recruiting", "Montreal", "Quebec", "Canada", 45.5794, -73.5604, "Maisonneuve-Rosemont Hospital", "Inhibitor for newly diagnosed AML with mutation", "Newly diagnosed acute myeloid leukemia, FLT3 mutated", "https://www.cancertrialscanada.ca/trial/ONC-LE-002"),
        ("ONC-LE-003", "Phase II CLL Combination Study", "Leukemia", "Phase II", "Recruiting", "Vancouver", "British Columbia", "Canada", 49.2635, -123.1251, "Vancouver General Hospital", "BTK inhibitor combined with BCL2 inhibitor", "Chronic lymphocytic leukemia without standard options", "https://www.cancertrialscanada.ca/trial/ONC-LE-003"),
        ("ONC-LE-004", "Phase I Menin Inhibitor", "Leukemia", "Phase I", "Not Recruiting", "Calgary", "Alberta", "Canada", 50.9575, -114.1200, "Peter Lougheed Centre", "Safety profile of menin targeted suppression", "Refractory acute leukemias with specific gene fusions", "https://www.cancertrialscanada.ca/trial/ONC-LE-004"),
        ("ONC-LE-005", "Phase III Pediatric ALL Regimen", "Leukemia", "Phase III", "Recruiting", "Ottawa", "Ontario", "Canada", 45.3996, -75.6514, "CHEO", "Optimizing asparaginase doses in standard induction", "Pediatric patients 1-18 years with ALL", "https://www.cancertrialscanada.ca/trial/ONC-LE-005"),
        ("ONC-LE-006", "Phase II Maintenance CML", "Leukemia", "Phase II", "Recruiting", "Quebec City", "Quebec", "Canada", 46.7725, -71.2858, "Hôtel-Dieu de Québec", "Discontinuing TKI in deep molecular response", "CML patients taking TKI stably for 3+ years", "https://www.cancertrialscanada.ca/trial/ONC-LE-006"),

        # Prostate Cancer
        ("ONC-PR-001", "Phase III PARP Inhibitor Efficacy", "Prostate Cancer", "Phase III", "Recruiting", "Toronto", "Ontario", "Canada", 43.6897, -79.4005, "Sunnybrook Health Sciences", "Testing PARP inhibitors in mCRPC", "Metastatic castration-resistant prostate cancer, BRCA1/2 mutated", "https://www.cancertrialscanada.ca/trial/ONC-PR-001"),
        ("ONC-PR-002", "Phase II Lutetium-177 PSMA Radioligand", "Prostate Cancer", "Phase II", "Recruiting", "Montreal", "Quebec", "Canada", 45.4746, -73.6067, "CUSM - Glen Site", "Targeted radiation delivered to PSMA expressing cells", "mCRPC progressing on androgen axis inhibitors", "https://www.cancertrialscanada.ca/trial/ONC-PR-002"),
        ("ONC-PR-003", "Phase I Novel Androgen Receptor Degrader", "Prostate Cancer", "Phase I", "Not Recruiting", "Vancouver", "British Columbia", "Canada", 49.2276, -123.1378, "Richmond Hospital", "Safety of oral AR degrader", "Advanced prostate cancer failed standard ADT", "https://www.cancertrialscanada.ca/trial/ONC-PR-003"),
        ("ONC-PR-004", "Phase III Neoadjuvant ADT + Abi/Enza", "Prostate Cancer", "Phase III", "Recruiting", "Calgary", "Alberta", "Canada", 51.0426, -114.0792, "Sheldon M. Chumir Health Centre", "Hormonal therapy prior to definitive prostatectomy", "High-risk localized prostate cancer", "https://www.cancertrialscanada.ca/trial/ONC-PR-004"),
        ("ONC-PR-005", "Phase II Sipuleucel-T like Vaccine", "Prostate Cancer", "Phase II", "Recruiting", "Ottawa", "Ontario", "Canada", 45.4192, -75.6836, "Riverside Campus, TOH", "Autologous cellular immunotherapy variant", "Asymptomatic or minimally symptomatic mCRPC", "https://www.cancertrialscanada.ca/trial/ONC-PR-005"),
        ("ONC-PR-006", "Phase I Hypofractionated RT", "Prostate Cancer", "Phase I", "Recruiting", "Quebec City", "Quebec", "Canada", 46.8202, -71.2155, "Hôpital du Saint-Sacrement", "Ultra-high dose radiation over fewer days", "Low to intermediate risk prostate cancer", "https://www.cancertrialscanada.ca/trial/ONC-PR-006"),

        # Colon Cancer / Colorectal
        ("ONC-CO-001", "Phase III Liquid Biopsy Guided Adjuvant", "Colon Cancer", "Phase III", "Recruiting", "Toronto", "Ontario", "Canada", 43.6525, -79.3820, "St. Michael's Hospital", "Using ctDNA to determine need for adjuvant chemo", "Resected stage II colon cancer", "https://www.cancertrialscanada.ca/trial/ONC-CO-001"),
        ("ONC-CO-002", "Phase II Targeted BRAF Inhibitor", "Colon Cancer", "Phase II", "Recruiting", "Montreal", "Quebec", "Canada", 45.5298, -73.6231, "Hôpital Jean-Talon", "Combination therapy for BRAF mutated colorectal cancer", "Metastatic CRC with BRAF V600E mutation", "https://www.cancertrialscanada.ca/trial/ONC-CO-002"),
        ("ONC-CO-003", "Phase I Oncolytic Adenovirus", "Colon Cancer", "Phase I", "Not Recruiting", "Vancouver", "British Columbia", "Canada", 49.2559, -123.1706, "UBC Hospital", "Safety of liver-directed delivery of virus", "mCRC with liver prominent metastases", "https://www.cancertrialscanada.ca/trial/ONC-CO-003"),
        ("ONC-CO-004", "Phase II Anti-PD1 plus Investigational Agent", "Colon Cancer", "Phase II", "Recruiting", "Calgary", "Alberta", "Canada", 51.0435, -114.0701, "Tom Baker Cancer Centre", "Sensitizing MSS tumors to immunotherapy", "Microsatellite stable metastatic CRC", "https://www.cancertrialscanada.ca/trial/ONC-CO-004"),
        ("ONC-CO-005", "Phase III Hepatic Artery Infusion", "Colon Cancer", "Phase III", "Recruiting", "Ottawa", "Ontario", "Canada", 45.4215, -75.6972, "The Ottawa Hospital", "Chemotherapy pumped directly into liver", "Unresectable liver-only CRC metastases", "https://www.cancertrialscanada.ca/trial/ONC-CO-005"),
        ("ONC-CO-006", "Phase I Radiosensitizer Molecule", "Colon Cancer", "Phase I", "Recruiting", "Quebec City", "Quebec", "Canada", 46.7844, -71.2662, "CHU de Québec", "Novel oral agent taken with rectal cancer radiation", "Locally advanced rectal cancer", "https://www.cancertrialscanada.ca/trial/ONC-CO-006")
    ]

    cursor.executemany("""
    INSERT INTO clinical_trials (
        trial_code, trial_title, cancer_type, trial_phase, recruitment_status,
        city, province, country, latitude, longitude, hospital_name,
        summary, eligibility_summary, trial_link
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trials_data)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully with {len(trials_data)} records.")

if __name__ == "__main__":
    init_db()
