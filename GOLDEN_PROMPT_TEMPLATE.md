# Golden-Case Prompt Template (Claude Science)

Purpose: generate each **golden reference spec** in the SAME format as
`golden_validation_spec_HRV.md`, so the ablation harness can score every case
consistently. Run each case in a **fresh Claude Science conversation**. Copy the
**entire** output back and save it as `golden_validation_spec_<CASE>.md`.
Victoria provides the prose + source inventory; Claude builds the
`golden_expected_ids_<CASE>.json` answer key from it.

---

## THE PROMPT (paste this whole block, then fill in ONE "System under evaluation")

You are helping build a **grounded clinical AI validation specification** that will be used as a
reference answer key. I will describe a clinical AI system under evaluation. Produce a structured
8-field validation specification in which **every citation is a real, verifiable identifier**.
Accuracy of identifiers matters more than breadth — a wrong or unverifiable identifier is worse
than a missing one.

**System under evaluation:** <<DROP IN ONE OF THE CASE DESCRIPTIONS BELOW>>

**Grounding rules (strict):**
- Ground every recommendation in real sources retrieved and verified THIS session: PubMed (PMID)
  and Crossref-resolved DOIs for literature; openFDA for FDA records (product codes, 510(k)
  K-numbers, De Novo DEN-numbers, PMA numbers); ClinicalTrials.gov for trial / enrollment context;
  Drugs@FDA / drug labeling for drug or biologic products.
- **Verify every identifier resolves before including it** (PMID → PubMed; DOI → Crossref;
  K/DEN/PMA → openFDA; product code → openFDA classification). If an identifier cannot be verified,
  DROP it. Do not include any citation you did not resolve this session.
- Do **not** invent numeric thresholds as established standards. Label every number as either
  *retrieved-from-source* or *study-defined-placeholder*.
- Where a relevant database is not accessible to you, say so explicitly rather than guessing.

**Output format — follow exactly.** First, the 8 numbered fields. Each field has:
**Recommendation**, **Rationale** (with inline citations), **Confidence** (HIGH / MEDIUM / LOW),
and **Expert review needed**. The 8 fields are:

1. Study Design
2. Input / Signal Validation — the pre-condition: does the input measurement itself (sensor signal,
   image quality, lab assay, genotype call, etc.) agree with a reference standard before the
   algorithm's output is interpreted?
3. Performance Benchmarks
4. Ground Truth Strategy
5. Sample Size
6. Subgroup Requirements
7. Regulatory Pathway
8. Post-Deployment Monitoring

Then end with a **SOURCE INVENTORY** — this section is the most important part. It must contain:

- A table of **peer-reviewed literature**, columns exactly:
  `| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |`
- A table of **FDA regulatory records**, columns exactly:
  `| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |`
- A short note on **Trial registry** use (which ClinicalTrials.gov searches informed which fields).
- An **Expected conclusions** list: the regulatory class/pathway; any regulatory NULL result
  (e.g. "no FDA authorization exists for X"); and whether an established numeric benchmark exists.
- A **Sources I wanted but could not access** list (databases you could not reach — the coverage gaps).

Use the exact table columns above so the output is machine-parseable.

---

## CASE DESCRIPTIONS — drop ONE into "System under evaluation" per run

### Case 1 — HRV stress detection (ALREADY DONE — do not re-run)
Existing golden: `golden_validation_spec_HRV.md`. Listed here only as the format anchor.

### Case 2 — Diabetic-retinopathy screening (imaging device) — DONE
Golden: `golden_validation_spec_DR.md` + `golden_expected_ids_DR.json` (regulatory *positive*).
An AI algorithm that analyzes color retinal fundus photographs to detect **referable
(more-than-mild) diabetic retinopathy** in adults with diabetes, deployed as an autonomous /
point-of-care screening tool in primary-care and non-ophthalmology settings. Intended claim:
flag patients who should be referred to an eye-care professional. Input: fundus images from a
non-mydriatic retinal camera, with an image-quality/gradeability gate. Population: adults with
type 1 or type 2 diabetes, across skin tones and camera models.

### Case 3 — Warfarin dosing (drug / pharmacogenomics) — DONE
Golden: `golden_validation_spec_warfarin.md` + `golden_expected_ids_warfarin.json` (regulatory
*null*, first drug case).
An algorithm that recommends an **initial warfarin dose (and early dose adjustment)** to reach and
maintain therapeutic anticoagulation (target INR), using clinical variables (age, weight, height,
concomitant medications, indication) and optionally pharmacogenomic inputs (CYP2C9, VKORC1
genotype). Intended claim: decision support to help clinicians reach stable INR faster and reduce
out-of-range time. Setting: inpatient initiation and outpatient anticoagulation-clinic management.
Population: adults starting warfarin, spanning genotypes and ancestries.

---

**PILOT-3 SLATE LOCKED 2026-07-09.** Cases 1–3 span the three retrieval paths
(wellness-sensor null / imaging-device positive / drug null). The cases below are the
expansion toward the full 10; run them only as the harness needs more coverage. Case 4 (sepsis)
is queued to keep Claude Science warm while the harness is built.

### Case 4 — Sepsis early-warning prediction (EHR-based predictive SaMD)
An algorithm that continuously analyzes routinely-collected electronic health record data (vital
signs, laboratory results, nursing assessments, demographics) to **predict the onset of sepsis (or
septic shock) in hospitalized adults hours before clinical recognition**, deployed as an inpatient
early-warning / clinical decision support tool that alerts clinicians to initiate sepsis workup and
treatment. Intended claim: earlier identification of patients at high risk of sepsis to prompt
timely intervention. Input: structured EHR time-series data only (no new sensor, image, or genomic
assay). Setting: inpatient medical-surgical wards and ICUs. Population: hospitalized adults across
care settings, sexes, ages, races/ethnicities, and admitting diagnoses. *(Opens a new axis: a
predictive model on EHR data, with the Epic Sepsis Model external-validation failure as a rich
Input-Validation + Post-Deployment-Monitoring test.)*

### Case 5 — Atrial-fibrillation detection from single-lead / wearable ECG
An algorithm that analyzes a **single-lead ECG recorded on a consumer wearable** (e.g. a
smartwatch or patch) to **detect atrial fibrillation** and notify the wearer, deployed as an
over-the-counter / direct-to-consumer screening and notification feature. Intended claim: flag
possible AFib so the user can seek clinical confirmation (it does not replace a 12-lead ECG or a
clinician diagnosis). Input: a single-lead ECG waveform plus a photoplethysmography (PPG)
irregular-rhythm signal, with a signal-quality/wear-detection gate. Setting: ambulatory,
unsupervised consumer use. Population: adults without a prior AFib diagnosis, across ages, skin
tones, wrist sizes, and activity states. *(A consumer wearable that IS a regulated device via the
De Novo pathway — a live test of the classification / `submission_type_id:3` De Novo check on a
real granted De Novo, and of signal-quality Input Validation against a 12-lead reference.)*

### Case 6 — Melanoma / malignant skin-lesion classification from images
An algorithm that analyzes **dermoscopic and/or clinical photographs of a skin lesion** to
estimate the **risk that the lesion is malignant (melanoma or other skin cancer)** and guide the
biopsy / refer-to-dermatology decision, deployed as decision support in primary-care and
dermatology settings. Intended claim: help non-specialists decide which lesions need biopsy or
specialist referral. Input: dermoscopic or standardized clinical images, with an image-quality
gate; histopathology is the reference standard. Setting: primary care and dermatology clinics.
Population: adults with a lesion of concern, spanning the full range of skin tones (Fitzpatrick
I–VI) and body sites. *(An imaging device where **skin-tone subgroup performance is the
load-bearing fairness axis**, and the regulatory pathway is a recent De Novo / PMA — the imaging
mirror of DR but with a harder equity question and histopathology ground truth.)*

### Case 7 — Depression screening / detection
An algorithm that estimates the **likelihood that an adult has a depressive disorder** from
patient-reported responses and/or passively-collected behavioral or speech signals, deployed as a
screening / triage aid in primary care or behavioral-health settings. Intended claim: flag
patients who should receive a full clinical assessment (it does not diagnose). Input: structured
questionnaire responses and/or behavioral/voice features; the reference standard is a validated
instrument (e.g. PHQ-9) and/or a structured clinical interview by a clinician. Setting: primary
care and telehealth. Population: adults across ages, sexes, and race/ethnicity. *(A behavioral-
health case where **ground truth is a subjective, rating-scale / clinical-interview standard**
rather than a biomarker or histopathology — a hard test for the Ground-Truth Strategy and
Performance-Benchmark fields, and a regulatory pathway that is often Class II or an unsettled
null.)*

### Case 8 — Pneumonia detection / triage from chest X-ray
An algorithm that analyzes **frontal chest radiographs** to **detect findings suspicious for
pneumonia** and prioritize (triage) or flag (CADe) those studies for radiologist review, deployed
in emergency-department and inpatient radiology workflows. Intended claim: shorten time-to-review
for suspicious studies and/or assist detection — NOT to make an autonomous diagnosis. Input: DICOM
chest radiographs, with an image-adequacy gate; the reference standard is expert radiologist
adjudication (± follow-up imaging / clinical confirmation). Setting: hospital radiology, high study
volume. Population: adults presenting for chest imaging across care settings. *(A high-volume
radiology CAD case that tests the **triage (CADt) vs detection (CADe) vs diagnosis** distinction —
a regulatory space with many cleared 510(k)s and De Novo triage clearances, so the FDA-record
retrieval and the exact product-code match are heavily exercised.)*

### Case 9 — Response prediction / companion diagnostic for pembrolizumab
An algorithm-plus-assay that estimates whether a cancer patient is **likely to benefit from
pembrolizumab (an anti-PD-1 immunotherapy)** — for example by scoring **PD-L1 expression, tumor
mutational burden, or microsatellite-instability status** from tumor tissue or images — deployed as
a **companion diagnostic** that selects patients for the drug. Intended claim: identify patients
whose tumors are likely to respond, to guide treatment selection. Input: a tumor-tissue assay
readout and/or digital-pathology image, with an assay/specimen-adequacy gate; the reference
standard is the validated companion-diagnostic assay and clinical outcome. Setting: oncology, at
treatment-selection. Population: patients with the relevant tumor types, across ancestries.
*(The **drug-POSITIVE** mirror of warfarin's drug-null: pembrolizumab has a real biologic approval
(BLA125514) AND an FDA-approved companion diagnostic on the PMA pathway (e.g. PD-L1 IHC 22C3
pharmDx) — a case where `is_drug_case` co-exists with a device PMA, testing the Drugs@FDA/BLA +
companion-diagnostic-PMA retrieval together.)*

### Case 10 — Inpatient fall-risk prediction
An algorithm that analyzes **routinely-collected EHR data (and optionally wearable/bed-sensor
signals)** to **predict which hospitalized patients are at high risk of a fall**, deployed as an
inpatient decision-support alert that prompts fall-prevention precautions. Intended claim: earlier,
better-targeted fall-prevention for high-risk patients. Input: structured EHR variables (mobility
scores, medications, prior falls, labs) ± sensor signals; the reference standard is documented
in-hospital fall events. Setting: inpatient medical-surgical wards. Population: hospitalized adults
across ages, sexes, and diagnoses. *(The **predictive-NULL** mirror of sepsis: a risk-prediction
model whose regulatory status often turns on the **21st Century Cures §520(o) non-device-CDS**
determination — the load-bearing residual caveat from the warfarin De Novo analysis, here made the
central Regulatory-Pathway question.)*

---

## What to copy back for each case
1. Save the **entire** Claude Science output as `golden_validation_spec_<CASE>.md`
   (e.g. `golden_validation_spec_DR.md`, `golden_validation_spec_warfarin.md`).
2. Paste it back to Claude in the app-building session. Claude converts the SOURCE INVENTORY into
   `golden_expected_ids_<CASE>.json` (the scored answer key) and confirms every identifier resolves.
3. Do **not** hand-build the JSON — that is Claude's step, so the answer key can't drift from the spec.
