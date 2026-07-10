# Grounded Clinical AI Validation Specification
## Inpatient Fall-Risk Prediction Decision-Support Algorithm

**System under evaluation:** An algorithm analyzing routinely-collected EHR data (± wearable/bed-sensor
signals) to predict which hospitalized adults are at high risk of an in-hospital fall, deployed as an
inpatient decision-support alert that prompts fall-prevention precautions.
**Reference standard:** documented in-hospital fall events. **Setting:** medical-surgical inpatient wards.
**Population:** hospitalized adults across ages, sexes, and diagnoses.

> **Grounding statement.** Every identifier below was retrieved AND resolved this session:
> PMIDs against PubMed E-utilities, DOIs against Crossref, FDA product codes / K-numbers / DEN-numbers
> against openFDA, and NCT numbers against the ClinicalTrials.gov v2 API. Identifiers that did not resolve
> were dropped. Numeric values are labeled **[retrieved-from-source]** or **[study-defined-placeholder]**.
> No numeric threshold below is asserted as an established regulatory standard unless explicitly retrieved.

---

## 1. Study Design

**Recommendation.** Treat this as a **prognostic (risk-prediction) model** and validate it in three stages,
reported to the TRIPOD+AI checklist and appraised with PROBAST:
(a) **development** with internal validation (bootstrap/cross-validation for optimism-corrected discrimination
and calibration); (b) **temporal + geographic external validation** on patients/sites not used in development;
(c) an **implementation / clinical-impact study** measuring whether the alert changes fall-prevention actions
and fall outcomes. The impact study should be a **cluster-randomized or stepped-wedge** design (randomize at
ward/unit level), because the intervention is a workflow alert delivered to nursing teams, not to individuals.

**Rationale.** Reporting and design should follow the TRIPOD statement and its AI extension
(Collins 2015, PMID 25560714, DOI 10.7326/M14-0697; Collins 2024 TRIPOD+AI, PMID 38626948,
DOI 10.1136/bmj-2023-078378), with risk-of-bias appraisal via PROBAST (Wolff/Moons 2019, PMID 30596875 and
PMID 30596876, DOI 10.7326/M18-1376 / 10.7326/M18-1377). The staged development → external → impact sequence for
an inpatient fall predictor is directly instantiated in the Cho program: cross-site time-variant model
development (PMID 30777849, DOI 10.2196/11505), a controlled clinical-impact evaluation (PMID 34626168,
DOI 10.2196/26456), and a pragmatic CDS implementation study (PMID 37033322, DOI 10.1093/jamiaopen/ooad019).
A cluster-randomized fall-prevention design at the unit level is exemplified by the Fall TIPS toolkit trials
(Dykes 2010 randomized trial, PMID 21045097, DOI 10.1001/jama.2010.1567; Dykes 2020 nonrandomized
stepped-wedge-style toolkit evaluation, PMID 33201236, DOI 10.1001/jamanetworkopen.2020.25889).

**Confidence.** HIGH (design/reporting framework); MEDIUM (that a cluster-RCT is operationally feasible in a
given site).

**Expert review needed.** Biostatistician + trialist to fix the randomization unit and the primary endpoint
(process measure vs. fall rate vs. injurious-fall rate); clinical informaticist to confirm the alert's
workflow integration point.

---

## 2. Input / Signal Validation (pre-condition)

**Recommendation.** Before interpreting any risk score, validate the **inputs** on two fronts:
(i) **Structured EHR variables** — audit completeness, timing, and accuracy of the predictors (mobility/gait
scores, culprit medications, prior-fall history, labs) against source documentation; quantify missingness and
its mechanism, and confirm that any nursing fall-risk scale used as an input (Morse, Hendrich II, or STRATIFY)
is scored reliably (inter-rater agreement).
(ii) **Sensor signals** — if wearable/bed-sensor data are used, validate the raw signal (fall/motion
detection sensitivity, specificity, latency, artifact/false-alarm rate) against an observed reference BEFORE it
is fed to the predictor. This is a distinct measurement-validity question from the algorithm's discrimination.

**Rationale.** The nursing fall-risk scales that typically supply the structured predictors have documented but
imperfect measurement properties — Morse Fall Scale (Morse 1989, PMID 2928815, DOI 10.1016/0277-9536(89)90309-2),
Hendrich II (Hendrich 2003, PMID 12624858, DOI 10.1053/apnr.2003.YAPNR2), and STRATIFY (Oliver 1997,
PMID 9366729, DOI 10.1136/bmj.315.7115.1049), whose pooled predictive performance across settings is modest and
setting-dependent (Oliver meta-analysis 2008, PMID 18829693, DOI 10.1093/ageing/afn203) — so the input scores
themselves need reliability checks. That unstructured/nursing-record inputs carry real predictive signal (and
therefore real measurement-quality dependence) is shown by NLP-of-nursing-records fall prediction (Nakatani 2020,
PMID 32319959, DOI 10.2196/16970) and by the use of standardized nursing terminologies as model inputs
(Cho 2023, PMID 37507147, DOI 10.1093/jamia/ocad145). For the sensor arm, FDA-recognized fall/bed sensor device
categories exist as **hardware whose signal performance is regulated separately** from any risk algorithm
(product codes below), underscoring that signal validation is a distinct pre-condition.

**Confidence.** HIGH (that input validation is required and that the scales are imperfect); MEDIUM (specific
sensor performance targets — none is an established universal standard).

**Expert review needed.** Clinical measurement / human-factors expert for scale inter-rater reliability;
biomedical engineer for sensor signal validation protocol and false-alarm tolerance.

---

## 3. Performance Benchmarks

**Recommendation.** Report the full set, not a single number:
**discrimination** (AUROC with CI; and, because falls are rare, **AUPRC / sensitivity at a
clinically-chosen alert rate**); **calibration** (calibration plot, calibration slope and
calibration-in-the-large — not just a Hosmer-Lemeshow p-value); and **clinical utility** (decision-curve /
net-benefit at the intended alert threshold). Predefine the operating threshold and report
sensitivity/specificity/PPV/NPV and **number-needed-to-alert** at that threshold.
Do **not** treat any specific AUROC cutoff as a pass/fail standard.

**Rationale.** Calibration is essential and frequently neglected in predictive analytics; report it as a
hierarchy, not a single test (Van Calster 2019 "Achilles heel", PMID 31842878, DOI 10.1186/s12916-019-1466-7;
Van Calster 2016 calibration hierarchy, PMID 26772608, DOI 10.1016/j.jclinepi.2015.12.005). Externally-validated
inpatient fall models exist as comparators — interpretable ML fall models (Shim 2022, PMID 36128798,
DOI 10.15441/ceem.22.354) and the cross-site time-variant model (Cho 2019, PMID 30777849, DOI 10.2196/11505) —
but **no discrimination figure (AUROC) was retrieved from their full text this session**, so any comparator AUROC
is a **[study-defined-placeholder]**, not a retrieved value. Because in-hospital falls are low-prevalence,
discrimination must be paired with precision/alert-burden metrics and calibration, per TRIPOD+AI reporting items
(PMID 38626948, DOI 10.1136/bmj-2023-078378).

**Confidence.** HIGH (which metrics to report); LOW (no discrimination figure was retrieved this session — any
comparator AUROC is a study-defined placeholder, not a retrieved standard).

**Expert review needed.** Biostatistician to set the operating threshold and the minimum acceptable
calibration slope; nursing leadership to set a tolerable alert burden (alerts per patient-day).

---

## 4. Ground Truth Strategy

**Recommendation.** Define the outcome as **documented in-hospital fall**, with an explicit, pre-registered
definition and a **fall-with-injury severity grade**. Use **≥2 independent, reconciled data streams** to
ascertain falls — incident-reporting system + nursing/EHR documentation (± billing/e-trigger codes) — and
**adjudicate** discordant cases, because incident-report-only ascertainment undercounts falls. Anchor each fall
to a timestamp so predictions are evaluated on data available BEFORE the event (no leakage).

**Rationale.** A validated injurious-fall severity classification for hospitalized adults exists and should
anchor the outcome grading (Burns 2020, PMID 31907532, DOI 10.1093/gerona/glaa004). Multi-source ascertainment
and standardized outcome capture are built into the large Fall TIPS evaluations (Dykes 2020, PMID 33201236,
DOI 10.1001/jamanetworkopen.2020.25889) and the serious-fall-injury endpoint definition used in the STRIDE
trial (Bhasin 2020, PMID 32640131, DOI 10.1056/NEJMoa2002183). Using a single administrative stream risks
biased labels, which propagates into biased model performance estimates (a general algorithmic-label-bias
caution: Obermeyer 2019, PMID 31649194, DOI 10.1126/science.aax2342).

**Confidence.** HIGH (multi-source, adjudicated, timestamped ground truth); MEDIUM (exact injury-grading scheme
to adopt).

**Expert review needed.** Patient-safety/quality officer for the incident-reporting reconciliation rules;
clinical adjudication panel for discordant events.

---

## 5. Sample Size

**Recommendation.** Compute sample size **twice**, from published formulae, not rules of thumb:
(a) **development** — use the Riley et al. minimum-sample-size criteria (target expected shrinkage/optimism,
precise baseline-risk and Nagelkerke-R² targets), driven by the number of candidate predictors and the fall
**event fraction**; because falls are rare, the binding constraint is the **number of fall events (EPP)**, not
total admissions.
(b) **external validation** — size to precisely estimate calibration and discrimination (Riley/Snell
external-validation criteria; ≥100 events and 100+ non-events is a common floor **[study-defined-placeholder]**).
Report the assumed event fraction and predictor count as inputs.

**Rationale.** Development sample size: Riley et al. BMJ 2020 (PMID 32188600, DOI 10.1136/bmj.m441).
External-validation sample size: Riley et al. Stat Med 2022 (PMID 34915593, DOI 10.1002/sim.9275) and the BMJ
"part 3" evaluation-sample-size guidance (Riley 2024, PMID 38253388, DOI 10.1136/bmj-2023-074821). These
supply the equations; the specific N depends on the site's fall rate and candidate-predictor count, which must
be entered as study parameters.

**Confidence.** HIGH (which method to use); LOW on any single N until the site's fall event fraction is fixed —
hence every concrete count here is a **[study-defined-placeholder]**.

**Expert review needed.** Biostatistician to run `pmsampsize`-type calculations with the site's actual event
fraction and predictor list.

---

## 6. Subgroup Requirements

**Recommendation.** Pre-specify subgroup performance reporting across **age bands, sex, race/ethnicity,
primary diagnosis/service line, and mobility-impairment status**, and report discrimination AND **calibration
within each subgroup** (a model can be well-calibrated overall yet miscalibrated in a subgroup). Define an
a-priori **equity check**: flag any subgroup whose calibration or sensitivity falls materially below the
overall value for targeted recalibration. Because the alert triggers a resource (precautions/observation),
also report subgroup **alert rates** to detect over- or under-alerting.

**Rationale.** Algorithms trained on routinely-collected data can encode systematic bias that only appears on
subgroup analysis, with direct clinical-allocation consequences (Obermeyer 2019, PMID 31649194,
DOI 10.1126/science.aax2342). TRIPOD+AI explicitly requires fairness/subgroup reporting (Collins 2024,
PMID 38626948, DOI 10.1136/bmj-2023-078378), and PROBAST's applicability domain covers whether the population
and predictors transfer across subgroups (Wolff/Moons 2019, PMID 30596875 / 30596876,
DOI 10.7326/M18-1376 / 10.7326/M18-1377). Subgroup **calibration** specifically is emphasized by the
calibration-hierarchy work (Van Calster 2019, PMID 31842878, DOI 10.1186/s12916-019-1466-7).

**Confidence.** HIGH.

**Expert review needed.** Health-equity methodologist to pre-register the subgroup list and the
disparity-flag thresholds (which are governance choices, not established numeric standards).

---

## 7. Regulatory Pathway

**Recommendation.** Classify against the FDA **Clinical Decision Support (CDS) / Software-as-a-Medical-Device**
framework and determine, with regulatory counsel, whether the alert qualifies as **non-device CDS** (clinician
can independently review the basis) or as a **device** requiring authorization. Note the key **regulatory NULL
result** established this session: **there is no existing FDA product code, De Novo, or clearance for a
predictive EHR-based inpatient fall-*risk* CDS algorithm** — the fall-related FDA device records that DO exist
are all **hardware** (sensors/alarms/monitors and a wearable protective device), not risk-prediction software.
A genuinely novel predictive-CDS device would therefore most plausibly enter via the **De Novo** route (no
suitable predicate for a Class classification), if it is a device at all.

**Rationale (all openFDA-verified this session).** The fall-related device classifications are physical devices:
Class II **Wearable Fall Injury Prevention Device** (product code **SEC**, 21 CFR 890.3780), created by
De Novo **DEN240021** (Active Protective Tango Belt, decision 2025-04-09); Class I **Fall Prevention
Alarm/Sensor** combination and attached-only devices (**PJO** and **PJP**, 21 CFR 880.2400); and Class I
bed/patient activity monitors (**KMI** "Monitor, Bed Patient"; **SBO** "Bed-Patient Activity Monitoring
System", both 21 CFR 880.2400). Example cleared hardware under these codes: **K233096** (PressureAlert,
SBO, 2024-06-21), **K141877** (Leaf Patient Monitoring System, KMI, 2014-11-10). **No PMA records** exist for
SEC/PJO/SBO, and **no De Novo or 510(k) exists for a fall-*risk-prediction* software algorithm** — searches on
predictive/fall-risk software product names returned no such records. Regulatory framing for continuously
updated AI clinical systems is discussed in van Amsterdam 2026 (PMID 42050181, DOI 10.1038/s41591-026-04368-9).

**Confidence.** HIGH on the openFDA NULL result and on the class of the existing hardware codes; MEDIUM on the
final device/non-device determination for THIS product (a legal/regulatory judgement, not a database lookup).

**Expert review needed.** FDA regulatory-affairs counsel to make the CDS device/non-device call and confirm the
De Novo-vs-exempt determination.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Stand up **prospective monitoring** for: (i) **calibration drift** and discrimination decay
over time (scheduled recalibration triggers); (ii) **dataset/population shift** (case-mix, coding changes, EHR
upgrades, new sensor firmware); (iii) **alert performance in the wild** — alert rate, PPV, alert-fatigue /
override rate, and any automation-bias effects; (iv) **subgroup calibration** on the live population.
Predefine update/retraining governance and a rollback path. Treat silent performance degradation as the
default expectation, not the exception.

**Rationale.** Calibration drift in deployed clinical models is documented and monitorable (Davis 2017,
PMID 28379439, DOI 10.1093/jamia/ocx030; Davis 2020 drift-detection for model updating, PMID 33157313,
DOI 10.1016/j.jbi.2020.103611). Clinician-facing guidance on recognizing dataset shift (Finlayson 2021,
PMID 34260843, DOI 10.1056/NEJMc2104626) and the cautionary external-validation experience of a widely deployed
proprietary alert model (Wong 2021 Epic Sepsis Model, PMID 34152373, DOI 10.1001/jamainternmed.2021.2626)
motivate mandatory prospective surveillance rather than one-time validation. Governance for continuously
monitored/updated AI is addressed by van Amsterdam 2026 (PMID 42050181, DOI 10.1038/s41591-026-04368-9), and
ongoing subgroup-fairness monitoring follows TRIPOD+AI (PMID 38626948, DOI 10.1136/bmj-2023-078378).

**Confidence.** HIGH.

**Expert review needed.** MLOps/clinical-informatics team to define drift-detection thresholds and the
retraining-vs-recalibration decision rule; clinical governance board for the update-approval process.

---

# SOURCE INVENTORY

## A. Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| TRIPOD statement — reporting of multivariable prediction models | PMID 25560714 · DOI 10.7326/M14-0697 | 1 |
| TRIPOD explanation & elaboration | PMID 25560730 · DOI 10.7326/M14-0698 | 1 |
| TRIPOD+AI — updated reporting guidance for AI prediction models | PMID 38626948 · DOI 10.1136/bmj-2023-078378 | 1, 3, 6, 8 |
| PROBAST — risk-of-bias tool for prediction-model studies | PMID 30596876 · DOI 10.7326/M18-1376 | 1, 6 |
| PROBAST explanation & elaboration | PMID 30596875 · DOI 10.7326/M18-1377 | 1, 2, 6 |
| Riley et al. — minimum sample size to DEVELOP a prediction model | PMID 32188600 · DOI 10.1136/bmj.m441 | 5 |
| Riley et al. — sample size for model EVALUATION (part 3) | PMID 38253388 · DOI 10.1136/bmj-2023-074821 | 5 |
| Riley/Snell — minimum sample size for EXTERNAL validation | PMID 34915593 · DOI 10.1002/sim.9275 | 5 |
| Van Calster — calibration, the "Achilles heel" of predictive analytics | PMID 31842878 · DOI 10.1186/s12916-019-1466-7 | 3, 6 |
| Van Calster — a calibration hierarchy for risk models | PMID 26772608 · DOI 10.1016/j.jclinepi.2015.12.005 | 3 |
| Morse — prospective identification of the fall-prone patient (Morse Fall Scale) | PMID 2928815 · DOI 10.1016/0277-9536(89)90309-2 | 2 |
| Hendrich II Fall Risk Model validation | PMID 12624858 · DOI 10.1053/apnr.2003.YAPNR2 | 2 |
| Oliver — development of STRATIFY inpatient fall risk tool | PMID 9366729 · DOI 10.1136/bmj.315.7115.1049 | 2 |
| Oliver — systematic review/meta-analysis of STRATIFY | PMID 18829693 · DOI 10.1093/ageing/afn203 | 2 |
| Burns — classification of injurious fall severity in hospitalized adults | PMID 31907532 · DOI 10.1093/gerona/glaa004 | 4 |
| Cho — cross-site, time-variant inpatient fall risk prediction | PMID 30777849 · DOI 10.2196/11505 | 1, 3 |
| Cho — clinical impact of a fall-risk analytic tool (controlled study) | PMID 34626168 · DOI 10.2196/26456 | 1 |
| Cho — pragmatic evaluation of fall-prevention CDS | PMID 37033322 · DOI 10.1093/jamiaopen/ooad019 | 1 |
| Cho — standardized nursing terminologies as AI fall-prevention inputs | PMID 37507147 · DOI 10.1093/jamia/ocad145 | 2 |
| Nakatani — inpatient fall prediction via NLP of nursing records | PMID 32319959 · DOI 10.2196/16970 | 2 |
| Shim — interpretable ML models for inpatient fall events | PMID 36128798 · DOI 10.15441/ceem.22.354 | 3 |
| Dykes — fall prevention in acute care hospitals (randomized trial) | PMID 21045097 · DOI 10.1001/jama.2010.1567 | 1 |
| Dykes — Fall TIPS patient-centered toolkit evaluation | PMID 33201236 · DOI 10.1001/jamanetworkopen.2020.25889 | 1, 4 |
| Bhasin (STRIDE) — multifactorial serious-fall-injury prevention trial | PMID 32640131 · DOI 10.1056/NEJMoa2002183 | 4 |
| Obermeyer — dissecting racial bias in a health-management algorithm | PMID 31649194 · DOI 10.1126/science.aax2342 | 4, 6 |
| Finlayson — the clinician and dataset shift in AI | PMID 34260843 · DOI 10.1056/NEJMc2104626 | 8 |
| Davis — calibration drift in clinical prediction models (AKI) | PMID 28379439 · DOI 10.1093/jamia/ocx030 | 8 |
| Davis — detecting calibration drift to inform model updating | PMID 33157313 · DOI 10.1016/j.jbi.2020.103611 | 8 |
| Wong — external validation of a widely deployed proprietary sepsis alert | PMID 34152373 · DOI 10.1001/jamainternmed.2021.2626 | 8 |
| van Amsterdam — clinical trials for continuously monitored/updated AI | PMID 42050181 · DOI 10.1038/s41591-026-04368-9 | 7, 8 |

*All 30 PMIDs resolved against PubMed E-utilities and all 30 DOIs resolved against Crossref this session.*

## B. FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| Wearable Fall Injury Prevention Device (Class II, 21 CFR 890.3780) | Product code **SEC** | 2, 7 |
| De Novo creating product code SEC — Active Protective Tango Belt (decision 2025-04-09) | **DEN240021** | 7 |
| Fall Prevention Alarm/Sensor Combination, attached or unattached (Class I, 21 CFR 880.2400) | Product code **PJO** | 2, 7 |
| Fall Prevention Alarm/Sensor, attached only (Class I, 21 CFR 880.2400) | Product code **PJP** | 2, 7 |
| Monitor, Bed Patient (Class I, 21 CFR 880.2400) | Product code **KMI** | 2, 7 |
| Bed-Patient Activity Monitoring System (Class I, 21 CFR 880.2400) | Product code **SBO** | 2, 7 |
| Leaf Patient Monitoring System (KMI 510(k), cleared 2014-11-10) | **K141877** | 7 |
| PressureAlert Pressure Monitoring System (SBO 510(k), cleared 2024-06-21) | **K233096** | 7 |

*All product codes, the De Novo number, and both K-numbers resolved against openFDA
(classification, De Novo, and 510(k) endpoints) this session. PMA searches on SEC/PJO/SBO each returned
openFDA's genuine `NOT_FOUND: "No matches found!"` body (verified individually against a positive control,
LWP → 2,368 PMA records), confirming zero PMA records rather than a query error.*

## C. Trial registry use (ClinicalTrials.gov v2 API, resolved this session)

- Search "Fall TIPS toolkit" / fall-prevention interventions — **NCT00675935** (Fall TIPS interventional
  RCT, COMPLETED, n=10,264 actual) and **NCT03499717** (generalizability/spread, observational,
  COMPLETED, n=37,231 actual). *Informed field 1 (impact-study design) and field 5 (realistic enrollment
  magnitudes for ward-level fall-prevention studies).*
- Search "hospital fall prevention alert algorithm" — **NCT06339125** (Predictive Analytics & Computer
  Visualization for patient safety, interventional, COMPLETED, n=5,350) and **NCT05391334** (early fall-risk
  detection in inpatients, observational, COMPLETED, n=170). *Informed field 1.*
- Search "fall risk machine learning EHR" — **NCT07078240** (FAIR AI-powered falls-risk tool; nurse trust/
  acceptance, interventional, NOT_YET_RECRUITING, n=60 est.), **NCT05846685** (automated falls-risk screening
  & referral, observational, COMPLETED, n=10), **NCT07631494** (AI-driven nursing decision support,
  interventional, NOT_YET_RECRUITING, n=188 est.). *Informed fields 1 and 8 (real-world adoption / human-factors
  monitoring endpoints).*

Enrollment counts above are **[retrieved-from-source]** registry values, cited as design/enrollment context
only — not as benchmarks the system must meet.

## D. Expected conclusions

- **Regulatory class/pathway.** No FDA classification exists for a predictive EHR-based inpatient fall-*risk*
  CDS algorithm. Existing fall-related FDA devices are hardware: Class II wearable protective device (**SEC**,
  via De Novo **DEN240021**) and Class I alarms/sensors/monitors (**PJO, PJP, KMI, SBO**, all 21 CFR 880.2400).
  A novel predictive-CDS product would most plausibly pursue the **De Novo** route if determined to be a device,
  after a device/non-device CDS determination with regulatory counsel.
- **Regulatory NULL result.** **No FDA authorization (product code, De Novo, 510(k), or PMA) exists for an
  EHR-based fall-risk-prediction decision-support algorithm** as of this session's openFDA queries. This is a
  genuine coverage gap, not a search miss: predictive/fall-risk *software* names returned zero device records.
- **Established numeric benchmark?** **No.** There is no regulatory or consensus AUROC/sensitivity threshold a
  fall-prediction model must meet. No discrimination figure (AUROC) for comparator fall models was retrieved
  from full text this session; any comparator AUROC is a placeholder, not a retrieved value. All operating
  thresholds, minimum calibration slopes, sample sizes, and subgroup disparity limits in this spec are
  **[study-defined-placeholder]** values to be set by the study team.

## E. Sources I wanted but could not access (coverage gaps)

- **Drugs@FDA / drug labeling.** Not queried for content: the system carries no drug/biologic product, so no
  Drugs@FDA record applies. Fall-risk-increasing drugs (e.g., sedatives, antihypertensives) enter only as
  model *inputs*, not as regulated products — flagged as an expert-review item rather than cited to a label.
- **FDA AI/ML-enabled medical device list & CDS guidance documents.** The narrative FDA CDS final-guidance and
  the periodically-published AI/ML device list are documents, not openFDA API records; I could confirm the
  *absence* of a fall-risk-prediction device via openFDA but could not machine-verify guidance-document text
  this session — final device/non-device determination is left to regulatory counsel.
- **Institutional / proprietary vendor validation reports** (e.g., EHR-vendor embedded fall-risk models such as
  vendor-native predictive scores) are not in any public database I can resolve; their performance claims could
  not be independently verified and were therefore excluded.
- **Full-text effect sizes.** PMIDs/DOIs were resolved for identity; I did not extract in-text numeric results
  beyond registry enrollment counts, so any performance figure cited as "context" reflects abstract/summary
  level, not a full-text-verified estimate.
