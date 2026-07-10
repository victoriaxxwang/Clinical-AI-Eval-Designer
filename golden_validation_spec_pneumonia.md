# Clinical AI Validation Specification — Chest-Radiograph Pneumonia Triage / CADe

**System under evaluation:** Software that analyzes frontal chest radiographs (DICOM) to detect
findings suspicious for pneumonia and either prioritize the study on the radiologist worklist
(computer-assisted triage, CADt) or flag the finding for reader attention (computer-assisted
detection, CADe). **Intended use claim:** shorten time-to-review for suspicious studies and/or
assist detection — *not* autonomous diagnosis. **Reference standard:** expert radiologist
adjudication ± follow-up imaging / clinical confirmation. **Setting:** high-volume hospital
radiology (ED + inpatient). **Population:** adults presenting for chest imaging.

All identifiers below were retrieved and resolved this session: PMIDs via PubMed, DOIs via
Crossref, FDA product codes / K-numbers via openFDA (`device/classification`, `device/510k`),
trial context via ClinicalTrials.gov. Every DOI resolved (26/26 selected; 39/39 across the
candidate pool, no retraction flags). Databases that were unreachable are listed at the end.

---

## 1. Study Design

**Recommendation.** Use a two-stage design matched to the intended-use claim. (a) A **retrospective
standalone** study establishing algorithm diagnostic performance against the reference standard on
a locked, representative test set. (b) A **clinical-effect** study for the workflow claim: for the
triage (CADt) claim, a study whose *primary* endpoint is **time-to-review / time-to-notification**
of suspicious studies (retrospective time-stamp simulation or, preferably, a prospective /
randomized comparison of worklist order with vs. without the algorithm); for the detection (CADe)
claim, a **multi-reader multi-case (MRMC)** study measuring reader sensitivity/specificity (and
reading time) with vs. without the aid. Do not substitute standalone accuracy for the clinical
claim — the claim is about review latency and reader detection, so the pivotal endpoint must
measure those directly.

**Rationale.** Triage-tool evidence centers on latency: an AI worklist-prioritization tool was
reported to reduce report turnaround/communication time for flagged studies
(PMID 37124638 · 10.1148/ryct.220163), an effect
corroborated by a systematic review of deep-learning worklist triage
(PMID 40397031 · 10.1007/s00330-025-11674-2) and an
earlier worklist-implementation study showing decreased time-to-read
(PMID 34201775 · 10.3390/brainsci11070832); a real-world
triage/notification validation for an analogous imaging finding shows the same endpoint structure
(PMID 37602253 · 10.3389/fneur.2023.1177723). For the
detection claim, the MRMC paradigm — readers interpreting cases with and without the aid — is the
established design and quantifies both accuracy and reading-time effects
(PMID 29064756 · 10.2214/AJR.17.18185), and a
standardized framework for premarket CADe/CADx evaluation formalizes the standalone-plus-reader
structure (PMID 32842797 · 10.1080/17434440.2020.1813566).

**Confidence:** HIGH (design paradigm well established for CADt/CADe; latency-endpoint literature is
smaller and heterogeneous).

**Expert review needed.** A biostatistician must fix the pivotal endpoint (time-to-notification vs.
MRMC accuracy) and whether the clinical-effect study is prospective/randomized or a retrospective
simulation; a radiology workflow lead must define "time-to-review" operationally against real
PACS/RIS timestamps.

---

## 2. Input / Signal Validation (image-adequacy gate)

**Recommendation.** Validate the **image-adequacy gate as its own pre-condition**, before any
downstream accuracy claim: (i) confirm the DICOM ingestion accepts only in-scope studies
(frontal projection, correct body part, adult), and (ii) validate the automated quality/adequacy
classifier (adequate vs. inadequate — e.g., rotation, exposure, collimation, lung-field coverage)
against a human quality reference on a dedicated adequacy dataset. Report the gate's own
sensitivity/specificity for rejecting inadequate images, and report downstream algorithm
performance **conditioned on "adequate"** so that failures of the gate are not silently attributed
to the detector.

**Rationale.** Automated CXR quality assessment is a validated, separable task — deep-learning
systems score overall radiograph quality against expert quality labels
(PMID 35420306 · 10.1007/s00330-022-08771-x), estimate
specific quality defects such as thoracic rotation
(PMID 39141433 · 10.1093/bjr/tqae149), and perform the
lung-field segmentation that underpins a coverage/positioning check
(PMID 35054267 · 10.3390/diagnostics12010101). Because the
detector's reported accuracy is only meaningful on images the gate admits, the gate is a genuine
input-signal validation step, not a UI nicety.

**Confidence:** MEDIUM (quality-assessment methods are well validated in isolation; there is no
single retrieved standard prescribing adequacy-gate acceptance thresholds — those are
study-defined).

**Expert review needed.** Radiologists must define what "adequate for pneumonia assessment" means
(minimum lung-field coverage, acceptable rotation/exposure ranges) and the disposition of
gate-rejected studies (route to human, request repeat). All acceptance thresholds are
**study-defined-placeholder** and must be set before the pivotal study locks.

---

## 3. Performance Benchmarks

**Recommendation.** Report **standalone** operating characteristics on the locked test set:
per-image sensitivity and specificity at the deployed operating point, ROC-AUC with 95% CIs, and —
for the triage claim — the time-to-notification distribution vs. the no-AI baseline. Do **not**
adopt any fixed numeric pass/fail threshold as an "established standard"; there is no retrieved
universal numeric benchmark for CXR pneumonia triage/CADe. Pre-specify the target operating point
and the non-inferiority / superiority margin as **study-defined placeholders** and justify them
clinically (a triage tool tolerates lower specificity than an autonomous diagnostic; a CADe aid
must not degrade reader specificity).

**Rationale.** Reported diagnostic accuracy for deep-learning pneumonia detection on chest
radiographs varies widely with dataset, reference standard, and operating point
(PMID 32768045 · 10.1016/j.compbiomed.2020.103898)(PMID 33861150 · 10.1259/bjr.20201263), which is
precisely why a single external numeric benchmark cannot be asserted. The appropriate benchmark is
task- and reader-referenced: multi-institution reader studies for chest-radiograph findings report
standalone AUC alongside reader sensitivity/specificity as the paired yardstick
(PMID 34350409 · 10.1148/ryai.2021200190), and
reader-performance CAD studies across multiple chest pathologies establish the reader-referenced
comparison this device needs (PMID 34706849 · 10.1016/j.acra.2021.09.016)(PMID 36121622 · 10.1007/s11604-022-01330-w).

**Confidence:** MEDIUM-HIGH for *which* metrics to report; LOW for any specific numeric target
(none is an established standard — all are study-defined).

**Expert review needed.** Clinical + regulatory reviewers must set the pre-specified operating
point, the CI width, and the non-inferiority margin, and decide whether reader-with-AI
non-inferiority in specificity is a gating criterion.

---

## 4. Ground Truth Strategy

**Recommendation.** Define the reference standard as **independent multi-reader adjudication**
(≥2–3 radiologists with a pre-specified tie-break / panel rule), strengthened where available by
follow-up imaging (CT) and/or microbiologic/clinical confirmation of pneumonia. Lock the
annotation protocol (finding definition, label granularity — image-level "suspicious for
pneumonia" vs. region-level localization — and blinding) before reading. Capture inter-reader
agreement and treat the reference standard's own limitations as a reported source of uncertainty.

**Rationale.** Reference-standard quality is a first-order determinant of apparent AI performance in
radiography, and improving/documenting it is a recognized validation problem in its own right
(PMID 34142868 · 10.1259/bjr.20210435). Label
granularity is not cosmetic: coarse image-level labels let models learn shortcuts that inflate
apparent accuracy, so annotation granularity must be chosen deliberately and reported
(PMID 36204545 · 10.1148/ryai.210299). The reference
standard, reader qualifications, and adjudication rule are core reportable items under the imaging-AI
reporting checklist (PMID 33937821 · 10.1148/ryai.2020200029).

**Confidence:** HIGH (multi-reader adjudication ± confirmatory imaging is the accepted reference for
CXR AI).

**Expert review needed.** Radiology + infectious-disease input on how much clinical/microbiologic
confirmation is feasible vs. imaging-only adjudication, and the exact panel/tie-break rule.

---

## 5. Sample Size

**Recommendation.** Power the **pivotal endpoint**, not the algorithm in the abstract. For the CADe
claim, size the **MRMC** study on the reader-averaged AUC (or sensitivity) difference using an
MRMC variance framework (readers × cases as crossed random effects), with disease-enriched case
sampling to obtain adequate positives. For the triage claim, size on the **time-to-notification**
effect (paired/between-arm comparison). Pre-specify the target effect size, positive:negative
case mix, and number of readers; all are **study-defined placeholders**, not retrieved standards.

**Rationale.** MRMC studies achieve statistical efficiency by crossing a modest number of readers
with an enriched case set — e.g., a reported CAD reading-time MRMC used 20 readers over 240
enriched cases (PMID 29064756 · 10.2214/AJR.17.18185),
and a standardized premarket-evaluation framework describes the reader/case sizing logic for
CADe/CADx (PMID 32842797 · 10.1080/17434440.2020.1813566).
Multi-institution chest-radiograph reader studies illustrate the enrichment-plus-multiple-readers
sizing in practice (PMID 34350409 · 10.1148/ryai.2021200190).

**Confidence:** MEDIUM (methodology is well established; there is no retrieved fixed minimum N — the
number follows from the pre-specified effect size and variance assumptions).

**Expert review needed.** A biostatistician must run the MRMC / time-to-event power calculation once
the effect size, case mix, and reader count are fixed; no number here should be treated as a
standard.

---

## 6. Subgroup Requirements

**Recommendation.** Pre-specify and power (or at minimum report with CIs) subgroup performance
across: **sex, age band, care setting (ED vs. inpatient), acquisition device/vendor and portable vs.
fixed, and site/institution.** Report per-subgroup sensitivity/specificity and flag material gaps.
Include an **external / multi-site** validation, because single-site performance does not transfer
automatically.

**Rationale.** Chest-radiograph models encode demographic signal — deep-learning models can predict
patient sex and age directly from the radiograph, the substrate for demographic shortcut learning
and subgroup bias (PMID 37529539 · 10.1177/20552076231191055),
and shortcut learning from label/dataset artifacts inflates in-distribution accuracy while degrading
it out-of-distribution (PMID 36204545 · 10.1148/ryai.210299).
Multi-institution evaluation is therefore necessary to expose site- and device-dependent performance
(PMID 34350409 · 10.1148/ryai.2021200190), and external
validation on independent infrastructure/data is a documented failure point for CXR models
Ardestani 2022 (PMID 35483438 · 10.1016/j.jacr.2022.03.013).

**Confidence:** HIGH (subgroup + external validation is a well-supported requirement).

**Expert review needed.** Decide which subgroups are *powered* vs. *descriptive*, define the
device/vendor strata that matter for the deployment fleet, and set minimum acceptable per-subgroup
performance (study-defined).

---

## 7. Regulatory Pathway

**Recommendation.** In the US, treat this as a **Class II, 510(k)** software device under the FDA
radiological computer-assisted software framework, with the product code determined by the claim:

- **Triage/notification (CADt) claim → product code `QFM`**, "Radiological Computer-Assisted
  Prioritization Software For Lesions," 21 CFR **892.2080**, Class II (retrieved from openFDA
  `device/classification`). The closely related triage code `QAS` ("Radiological Computer-Assisted
  Triage And Notification Software," also 892.2080, Class II) exists for the notification-only
  formulation.
- **Detection/diagnosis (CADe) claim → the 892.2090 family** ("Radiological Computer Assisted
  Detection/Diagnosis Software"), Class II — retrieved product codes in that regulation include
  `QDQ` (lesions suspicious for cancer) and `QBS` (fracture). **No retrieved product code is
  specific to pneumonia CXR CADe**, so the code would be assigned by analogy/De Novo at FDA's
  discretion (see NULL result below).

Numerous **CXR triage devices are already 510(k)-cleared under QFM** (all verified in openFDA
`device/510k` this session), e.g. Lunit INSIGHT CXR Triage (K211733, 2021-11-10), VUNO Med-Chest
X-ray Triage (K241439, 2024-11-15), Annalise Enterprise CXR Triage Trauma (K222179, 2023-03-28),
SmartChest (K232410, 2024-05-10), HealthCXR (K192320, 2019-11-26) — establishing QFM as the
operative pathway and a predicate pool.

**Rationale.** The QFM classification text itself limits the device to prioritization/notification
and explicitly states it "does not provide … information from the image analysis other than triage
and notification" (openFDA classification record) — directly matching the not-autonomous-diagnosis
claim. FDA's own regulatory-science literature describes the imaging-AI/ML device evaluation
framework and the CADt/CADe distinction
(PMID 37361549 · 10.1117/1.JMI.10.5.051804). Study
reporting should follow imaging-AI checklists — CLAIM
(PMID 33937821 · 10.1148/ryai.2020200029) — and the
diagnostic-accuracy reporting extension for AI, STARD-AI, whose development
(PMID 32514173 · 10.1038/s41591-020-0941-1) and
protocol (PMID 34183345 · 10.1136/bmjopen-2020-047709)
are published.

**Confidence:** HIGH for CADt = QFM / 892.2080 Class II 510(k) (directly retrieved and matches the
claim). MEDIUM for the CADe code assignment (no pneumonia-specific code retrieved).

**Expert review needed.** Regulatory affairs must confirm the specific predicate(s) and product code
with FDA, decide 510(k) vs. De Novo if no adequate predicate exists for a pneumonia-CADe claim, and
draft a Predetermined Change Control Plan (PCCP) for model updates.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Implement a monitoring program covering: (i) **dataset/population shift**
detection on incoming study characteristics and device output distributions; (ii) **standing
performance surveillance** against periodically adjudicated samples (not just input drift);
(iii) **workflow/effect monitoring** — confirm the time-to-notification benefit persists in
production and that flag rates and reader override rates stay in range; and (iv) a **change-control
(PCCP)** process governing retraining/threshold changes. Define trigger thresholds and cadence in
advance (study-defined placeholders).

**Rationale.** Dataset shift is the central post-deployment failure mode for clinical ML, and
concrete detection/mitigation strategies are documented
(PMID 40876698 · 10.1016/j.jbi.2025.104902); sustainable
deployment requires a lifecycle ("360°") monitoring approach rather than one-time validation
(PMID 38422379 · 10.1093/jamia/ocae036); and pragmatic
operational monitoring frameworks for ambient/deployed clinical AI describe the standing-evaluation
machinery (PMID 39763559 · 10.1101/2024.12.27.24319685)
(medRxiv preprint — flagged as not peer-reviewed). Regulatory expectations for lifecycle change
control (Good Machine Learning Practice / PCCP) are described in the imaging-AI regulatory literature
(PMID 37361549 · 10.1117/1.JMI.10.5.051804).

**Confidence:** MEDIUM-HIGH (monitoring necessity and categories are well supported; specific
trigger thresholds and cadence are study-defined).

**Expert review needed.** Define drift metrics, alert thresholds, re-adjudication sampling rate, and
the governance path for model updates under the PCCP; one monitoring citation is a preprint and
should be re-checked for a peer-reviewed version.

---

## SOURCE INVENTORY

### Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| AI worklist prioritization reduces communication/turnaround time for flagged CXR studies | PMID 37124638 · 10.1148/ryct.220163 | 1,3 |
| Systematic review: impact of deep-learning worklist triage on radiology workflow | PMID 40397031 · 10.1007/s00330-025-11674-2 | 1,3 |
| Worklist ML implementation decreases time-to-read | PMID 34201775 · 10.3390/brainsci11070832 | 1 |
| Real-world validation of an AI triage/notification detection tool (analogous finding) | PMID 37602253 · 10.3389/fneur.2023.1177723 | 1 |
| Deep-learning triage/detection of incidental findings on imaging | PMID 41058960 · 10.1093/radadv/umaf021 | 1 |
| MRMC reader study: concurrent CAD shortens reading time, maintains performance | PMID 29064756 · 10.2214/AJR.17.18185 | 1,5 |
| Standardized premarket evaluation framework for CADe/CADx | PMID 32842797 · 10.1080/17434440.2020.1813566 | 1,5 |
| Reader-performance CAD across seven chest pathologies on PA radiographs | PMID 34706849 · 10.1016/j.acra.2021.09.016 | 1,3 |
| Validation of deep-learning CAD software for chest radiograph reading | PMID 36121622 · 10.1007/s11604-022-01330-w | 1,3 |
| Multi-institution reader study, deep-learning pneumothorax detection on CXR | PMID 34350409 · 10.1148/ryai.2021200190 | 3,5,6 |
| Accuracy of deep learning for automated pneumonia detection on CXR | PMID 32768045 · 10.1016/j.compbiomed.2020.103898 | 3 |
| Automated pneumonia detection via deep transfer learning on CXR | PMID 33861150 · 10.1259/bjr.20201263 | 3 |
| Automated deep-learning quality assessment of chest radiographs | PMID 35420306 · 10.1007/s00330-022-08771-x | 2 |
| Automated estimation of thoracic rotation on CXR (quality defect) | PMID 39141433 · 10.1093/bjr/tqae149 | 2 |
| Deep-learning four-region lung segmentation for CXR (coverage check) | PMID 35054267 · 10.3390/diagnostics12010101 | 2 |
| Improving reference standards for validation of AI-based radiography | PMID 34142868 · 10.1259/bjr.20210435 | 4 |
| Annotation granularity to overcome shortcut learning in CXR deep learning | PMID 36204545 · 10.1148/ryai.210299 | 4,6 |
| Deep-learning model infers sex/age from CXR (demographic shortcut substrate) | PMID 37529539 · 10.1177/20552076231191055 | 6 |
| External validation of a COVID-19 CXR deep-learning model on independent infra (Ardestani 2022) | PMID 35483438 · 10.1016/j.jacr.2022.03.013 | 6 |
| CLAIM: Checklist for Artificial Intelligence in Medical Imaging | PMID 33937821 · 10.1148/ryai.2020200029 | 4,7 |
| STARD-AI: developing diagnostic-accuracy reporting guideline for AI | PMID 32514173 · 10.1038/s41591-020-0941-1 | 7 |
| STARD-AI protocol (reporting guideline development) | PMID 34183345 · 10.1136/bmjopen-2020-047709 | 7 |
| FDA regulatory considerations for medical imaging AI/ML devices (CADt/CADe, PCCP) | PMID 37361549 · 10.1117/1.JMI.10.5.051804 | 7,8 |
| Strategies for detecting/mitigating dataset shift in clinical ML | PMID 40876698 · 10.1016/j.jbi.2025.104902 | 8 |
| 360° lifecycle approach to sustainable deployment of clinical prediction tools | PMID 38422379 · 10.1093/jamia/ocae036 | 8 |
| Pragmatic operations playbook to monitor/evaluate deployed clinical AI (medRxiv preprint) | PMID 39763559 · 10.1101/2024.12.27.24319685 | 8 |

*All 26 DOIs were resolved against Crossref this session; none carried a retraction flag. Note:
PMID 39763559 is a medRxiv preprint (not peer-reviewed) and is flagged as such wherever cited.*

### FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| Product code — CADt triage/prioritization (frontal-CXR triage claim) | QFM (21 CFR 892.2080, Class II) | 7 |
| Product code — CADt triage & notification (notification-only variant) | QAS (21 CFR 892.2080, Class II) | 7 |
| Product code — CADe/CADx detection family (lesions susp. for cancer) | QDQ (21 CFR 892.2090, Class II) | 7 |
| Product code — CADe/CADx detection family (fracture) | QBS (21 CFR 892.2090, Class II) | 7 |
| Cleared CXR triage 510(k) — Lunit INSIGHT CXR Triage | K211733 (QFM, 2021-11-10) | 1,7 |
| Cleared CXR triage 510(k) — VUNO Med-Chest X-ray Triage | K241439 (QFM, 2024-11-15) | 1,7 |
| Cleared CXR triage 510(k) — Annalise Enterprise CXR Triage Trauma | K222179 (QFM, 2023-03-28) | 1,7 |
| Cleared CXR triage 510(k) — SmartChest (Milvue) | K232410 (QFM, 2024-05-10) | 1,7 |
| Cleared CXR triage 510(k) — HealthCXR (Zebra Medical Vision) | K192320 (QFM, 2019-11-26) | 1,7 |
| Cleared CXR triage 510(k) — AIMI-Triage CXR PTX (RadLogics) | K193300 (QFM, 2020-04-08) | 1,7 |

*Product codes verified via openFDA `device/classification`; K-numbers verified via openFDA
`device/510k` (all resolve to the named device, applicant, and decision date). **DEN-numbers and
PMA-numbers: none are cited** — see NULL result and coverage-gap notes below.*

### Trial registry use (ClinicalTrials.gov)

ClinicalTrials.gov searches ("AI/deep learning chest radiograph + pneumonia/triage/worklist";
"computer-aided detection chest radiograph") informed **Fields 1 (Study Design) and 5 (Sample
Size)** by confirming the range of real-world study designs and enrollment scales in this space
(all NCT IDs and enrollment figures retrieved this session):

- **NCT05117320** — *AI to Improve Chest X-ray Reading in Acute Dyspnoeic Patients* — RCT
  (INTERVENTIONAL), enrollment 33. Illustrates a randomized reader-effect design.
- **NCT06456203** — *AI for Chest Radiography: Impact on Economics, Patient Outcomes and Radiology
  Service Delivery* — INTERVENTIONAL, enrollment 10,000. Illustrates a large prospective
  effectiveness design.
- **NCT06075836** — *Utility of an AI-based CXR Interpretation Tool in Assisting Diagnostic
  Accuracy, Speed, and Confidence* — OBSERVATIONAL, enrollment 33. Reader-assist / speed endpoint.
- **NCT05963945** — *Multi-Reader Retrospective Study, Carebot AI CXR* — OBSERVATIONAL, enrollment
  956. Illustrates a multi-reader retrospective design and case-set scale.
- **NCT05594485** — *CXR Abnormality Detection Using AI (Carebot), retrospective* — OBSERVATIONAL,
  enrollment 127.

These trials were used **for design/enrollment context only** — not as performance-benchmark
sources and not as reference-standard authorities.

### Expected conclusions

- **Regulatory class / pathway:** US **Class II, 510(k)**. Triage (CADt) claim → product code
  **QFM**, 21 CFR **892.2080**; notification-only variant → **QAS** (same regulation). Detection
  (CADe) claim → the **892.2090** CADe/CADx family (Class II).
- **Regulatory NULL result:** **No FDA product code specific to *pneumonia* chest-radiograph
  CADe/CADt was found.** Cleared CXR triage devices under QFM target pneumothorax, pleural
  effusion, trauma, or general CXR triage — **no cleared 510(k) is named for pneumonia CXR
  triage** in the records retrieved. A pneumonia-CADe claim therefore has no exact predicate code
  and may require De Novo classification or predication by analogy — to be confirmed with FDA.
- **Established numeric benchmark:** **None exists.** There is no retrieved universal numeric
  sensitivity/specificity/AUC or time-to-notification threshold that constitutes an accepted
  standard for CXR pneumonia triage/CADe. All numeric targets in this spec are labeled
  **study-defined placeholders**; the only retrieved numbers are the descriptive
  enrollment figures above and reported (dataset-specific, non-standard) accuracies in the
  performance literature.

### Sources I wanted but could not access (coverage gaps)

- **openFDA De Novo endpoint** — `api.fda.gov/device/denovo.json` returns **404 (no such endpoint)**.
  De Novo (DEN-) numbers, including the founding grants that created the QFM/QAS/QDQ/QBS
  regulations, **could not be verified this session**, so none are cited. Verifying them requires the
  FDA De Novo database / device classification order pages directly.
- **FDA 510(k) summary PDFs / decision summaries** — openFDA returns structured metadata (device
  name, applicant, product code, dates) but **not** the free-text summary describing each device's
  specific target findings or reported test statistics. Confirming which cleared devices list
  *pneumonia/consolidation* as a target finding, and their reported operating points, requires the
  per-K 510(k) summary documents (not reachable via the API here).
- **FDA AI/ML-enabled device list & Predetermined Change Control Plan guidance** — narrative FDA
  guidance documents (GMLP, PCCP) were **not** retrieved as primary sources; regulatory framing
  rests on the peer-reviewed regulatory-science literature (PMID 37361549) rather than the guidance
  text itself.
- **EU MDR / CE-mark records** — no European regulatory database was queried; the pathway above is
  **US FDA only**.
- **Drugs@FDA / drug labeling** — not applicable (this is a software/imaging device, not a drug or
  biologic); intentionally not used.

---

*Grounding provenance: PubMed (PMIDs) + Crossref (DOI resolution, 26/26 selected resolved, 0
retractions); openFDA `device/classification` and `device/510k` (product codes + K-numbers);
ClinicalTrials.gov (design/enrollment context). Fields marked HIGH/MEDIUM/LOW reflect strength of
the retrieved evidence, not certainty about any individual deployment.*
