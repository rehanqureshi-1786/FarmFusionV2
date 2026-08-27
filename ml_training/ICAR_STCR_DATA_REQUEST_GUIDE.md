# Official Data Request Guide: ICAR-AICRP on STCR Microdata

**Governing Policy**: ICAR Research Data Management Policy (2025) & National Data Sharing and Accessibility Policy (NDSAP), Government of India  
**Target Organization**: ICAR - Indian Institute of Soil Science (IISS), Bhopal & AICRP-STCR Coordinating Cell  
**Purpose**: Academic / Student Research Requisition for Multilingual AI Agricultural Copilot (FarmFusion)

---

## 1. Verified Official Contacts & Institutional Directory

| Authority / Role | Official Name & Designation | Verified Contact Details |
| :--- | :--- | :--- |
| **Project In-charge (STCR)** | **Dr. Sanjay Srivastava**<br>Principal Scientist & I/c AICRP-STCR | **Email**: `sanjay.srivastava1@icar.org.in`<br>**Alt Email**: `sanjaysrivastava238@gmail.com`<br>**Phone**: `+91-755-2730970` (Ext. 210) |
| **Director, ICAR-IISS** | **Dr. M. Mohanty**<br>Director, ICAR-IISS Bhopal | **Email**: `director.iiss@icar.org.in`<br>**Phone**: `+91-755-2730946`<br>**Fax**: `+91-755-2733310` |
| **Senior Administrative Officer** | Saurabh Meena | **Email**: `saurabh.meena@icar.org.in`<br>**Phone**: `+91-755-2730970` (Ext. 101) |
| **Official Postal Address** | ICAR - Indian Institute of Soil Science | Nabibagh, Berasia Road, Bhopal – 462038, Madhya Pradesh, India |
| **ICAR-KRISHI Data Portal** | Agricultural Research Data Repository | [https://krishi.icar.gov.in/](https://krishi.icar.gov.in/) |

---

## 2. Dual Submission Protocol (Email + KRISHI Portal)

To ensure the fastest academic processing, submit the request through both official channels:

### Route A: Formal Email Submission (Direct to Project Coordinator & Director)
1. Print the requisition letter (template below in Section 3) on your **University / Department Letterhead**.
2. Have the letter signed and stamped by your **Faculty Project Advisor / Head of Department (HOD)**.
3. Scan the signed letter to PDF.
4. Send an email to:
   * **To**: `sanjay.srivastava1@icar.org.in`, `director.iiss@icar.org.in`
   * **Subject**: `Formal Request for AICRP-STCR Experimental Plot-Level Microdata for Academic B.Tech AI/ML Research (FarmFusion Project)`
   * **Attachment**: The signed PDF letter and a copy of your Student ID card.

### Route B: ICAR-KRISHI Portal Submission
1. Visit [https://krishi.icar.gov.in/](https://krishi.icar.gov.in/) and register using your university email (`.ac.in` / `.edu`).
2. Search for `Soil Test Crop Response` or `STCR` in the Data Repository.
3. Submit an online data access request attaching the signed requisition letter.

---

## 3. Formal Academic Requisition Letter Template

```text
[PRINT ON OFFICIAL UNIVERSITY / DEPARTMENT LETTERHEAD]

Date: [DD/MM/YYYY]
Reference No.: [Department Dispatch / Project Ref No., if applicable]

To,
The Project In-Charge (AICRP-STCR),
ICAR - Indian Institute of Soil Science (IISS),
Nabibagh, Berasia Road,
Bhopal – 462038, Madhya Pradesh, India.

Through:
The Director,
ICAR - Indian Institute of Soil Science, Bhopal.

Subject: Requisition for Plot-Level STCR Experimental Trial Microdata for Academic B.Tech (AI/ML) Research Project — "FarmFusion Multilingual Agricultural Copilot"

Respected Dr. Sanjay Srivastava and Respected Director Sir,

I am writing to formally request access to plot-level research trial datasets collected under the All India Coordinated Research Project on Soil Test Crop Response (AICRP-STCR) network. 

I am a 3rd-year B.Tech student in Artificial Intelligence & Machine Learning at [Department Name], [College / University Name], [City, State]. As part of our undergraduate capstone research, we are developing "FarmFusion" — a multilingual, open-source AI agricultural decision-support system designed to provide smallholder Indian farmers with scientifically defensible crop recommendations and soil health guidance.

1. Research Justification & The Real-Data Mandate:
Current machine learning models in public circulation frequently rely on synthetic or unverified datasets that do not reflect real-world Indian agricultural conditions. To build a genuinely scientifically sound advisory copilot, our project enforces a strict "Real-Data-Only" policy. We require authentic, laboratory-measured plot-level observations where initial soil chemical tests are directly paired with the ground-truth crop grown and harvested on that exact trial plot.

2. Specific Microdata Fields Requested:
We respectfully request historical, anonymized plot-level trial spreadsheets across participating AICRP-STCR centers covering major Agro-Ecological Zones (Vertisols, Inceptisols, Alfisols, Entisols) containing:
  a) Experimental Station Metadata: Center code/name, district, state, approximate latitude/longitude coordinates, season (Kharif/Rabi/Zaid), and experiment year.
  b) Initial Soil Chemical Test Values: Available Soil Nitrogen (kg/ha via alkaline permanganate method), Available Soil Phosphorus (kg/ha P2O5 via Olsen/Bray), Available Soil Potassium (kg/ha K2O via neutral normal ammonium acetate), and Soil Reaction (pH in 1:2.5 suspension).
  c) Plot Layout & Crop Information: Plot ID, treatment ID, crop species, variety/cultivar, and cropping season.
  d) Harvest Yield: Measured grain yield (q/ha) and straw yield (q/ha) under control and fertilizer treatment plots.

3. Academic Undertaking & Compliance with ICAR Data Policy:
In accordance with the ICAR Research Data Management Policy (2025) and Government of India NDSAP guidelines, we formally undertake that:
  - The requested data will be utilized strictly for non-commercial academic research and machine learning algorithm development.
  - No individual proprietary or sensitive farmer identity will be published or compromised.
  - Full formal attribution and citation will be prominently given to ICAR, ICAR-IISS Bhopal, and the AICRP-STCR network in all publications, technical reports, and open-source project documentation.
  - The raw dataset will be stored securely and will not be redistributed for commercial purposes.

We would be deeply grateful for your favorable consideration and approval of this academic requisition.

Thanking you,

Yours sincerely,

________________________________________
[Student Name]
B.Tech (AI & ML), 3rd Year
Roll No. / Enrollment ID: [Your Student ID]
Department of [Your Department Name]
[College / University Name], [City, State, PIN]
Email: [Your University / Student Email]
Phone / Mobile: +91-[Your Mobile Number]


FORWARDED & RECOMMENDED BY:

________________________________________
[Faculty Advisor / Project Guide Name]
[Designation, e.g., Assistant Professor / Associate Professor]
Department of [Department Name]
Email: [Advisor Email]


________________________________________
[Head of Department / Dean Name]
Head, Department of [Department Name]
[College / University Name]
[Official Department Seal & Stamp]
```

---

## 4. Ingestion Path When Data is Received

Once the official STCR microdata spreadsheets are received from ICAR-IISS:
1. Save the untouched raw CSV file to:
   ```
   FarmFusionFinal/ml_training/data/raw/stcr/stcr_raw_trials.csv
   ```
2. The automated ingestion module [`ml_training/stcr_pipeline.py`](file:///home/rdj/FarmFusionFinal/ml_training/stcr_pipeline.py) will automatically validate column schemas, check physical bounds, and assimilate seasonal climate from Open-Meteo ERA5-Land.
3. The master Google Colab notebook [`ml_training/notebooks/FarmFusion_Crop_Model_V2.ipynb`](file:///home/rdj/FarmFusionFinal/ml_training/notebooks/FarmFusion_Crop_Model_V2.ipynb) will unlock its pre-training stop gate and execute the full multi-model training, calibration, and artifact export suite.
