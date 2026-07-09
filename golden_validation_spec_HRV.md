# Clinical Validation Specification — HRV-Based Stress Detection on a Consumer Wearable

*Grounded reference output. Every identifier below was verified this session (PubMed metadata, Crossref DOI resolution, openFDA device databases). Numeric thresholds are labelled either as retrieved-from-source or as study-defined-placeholder; none are invented as established standards.*

**System under evaluation:** Algorithm inferring psychological stress from HRV (RMSSD) derived from wrist PPG on a consumer wearable. Intended claim: notify the user when sustained physiological stress is detected, to prompt self-directed stress management. Setting: remote/at-home consumer wellness. Population: general adults, Fitzpatrick I–VI, across activity levels.

**Threshold finding that shapes the whole spec:** the intended claim as written — "notify to prompt self-directed stress management," no disease claim — is a **general-wellness claim, not a medical-device claim**. This is stated plainly here because it determines the regulatory pathway (Field 7) and the meaning of every benchmark below. If the sponsor adds any claim to detect, diagnose, or mitigate a stress/anxiety *condition*, the system crosses into device territory and the pathway changes.

---

## 1. Study Design

**Recommendation.** Prospective, decentralized (no-site-visit) observational cohort in free living, with a nested supervised sensor-validation sub-study. Reference standard = ecological momentary assessment (EMA) of momentary perceived stress. Primary analysis = discrimination of EMA-labelled stress epochs (ROC/AUC), evaluated **subject-independently** (held-out participants). One supervised session per sub-study participant for simultaneous wearable-vs-ECG capture.

**Rationale.** Consumer digital-health measures are expected to follow the V3 evidentiary chain — verification, analytical validation, clinical validation (Goldsack et al. 2020, DOI 10.1038/s41746-020-0260-4; Coravos et al. 2019, DOI 10.1038/s41746-019-0090-4). A free-living design is required because HRV–stress relationships measured in lab conditions do not transfer to daily-life motion and context (Smets et al. 2018, DOI 10.1038/s41746-018-0074-9). Comparable decentralized wearable cohorts on ClinicalTrials.gov informed the design (see inventory).

**Confidence: MEDIUM.** The V3 chain is well-established; the specific free-living + EMA + subject-independent combination is defensible but not a codified standard.

**Expert review needed.** Biostatistician (analysis-model lock), clinical-operations lead (decentralized logistics of the supervised sub-study), and an IRB for the EMA burden schedule.

---

## 2. Sensor / Input Validation *(pre-condition, not a footnote)*

**Recommendation.** Before any classifier ROC is interpreted, establish that wearable-derived RMSSD agrees with an ECG reference **on each device model, under motion**. Bland-Altman limits of agreement + concordance correlation coefficient (CCC) + mean absolute percentage error (MAPE), reported per device per activity condition (rest, paced breathing, postural change, ambulation, desk micro-motion, recovery). This gates the clinical analysis: conditions where RMSSD fails a pre-set agreement margin are where downstream output is uninterpretable.

**Rationale.** Wrist PPG recovers heart rate well but HRV poorly, and accuracy degrades with motion; consumer devices carry the largest HRV-validity concerns (Bent et al. 2020, DOI 10.1038/s41746-020-0226-6; Sinichi et al. 2025, DOI 10.1111/psyp.70004). Even research-grade wrist sensors show only moderate HRV agreement in dynamic conditions — an Empatica E4 driving-validation study reported time-domain HRV correlations of roughly r > 0.67–0.72 and weaker frequency-domain agreement (PMID 37896517, DOI 10.3390/s23208423). HRV feature methodology follows Shaffer & Ginsberg 2017, DOI 10.3389/fpubh.2017.00258 and Laborde et al. 2017, DOI 10.3389/fpsyg.2017.00213.

**Confidence: HIGH** (that this pre-condition is necessary). **The specific acceptance margins are MEDIUM/placeholder.**

**Expert review needed.** Signal-processing/biomedical-engineering review of the artifact-rejection pipeline and the per-device optical front-end differences; agreement on MAPE/CCC margins with clinical stakeholders.

---

## 3. Performance Benchmarks

**Recommendation.** Pre-register acceptance criteria **conditioned on the operating regime** (subject-independent, free-living, consumer-PPG, EMA-referenced). Illustrative anchors — **not** established standards: AUC point estimate ≥ 0.72 with lower 95% CI bound > 0.65; sensitivity ≥ 0.70 and specificity ≥ 0.70 at a pre-specified operating point, each with CIs. Contextualize against the published field range, not a single number.

**Rationale.** A systematic review of HRV-based stress/fatigue detection found sensitivity spanning **47.1–95%**, specificity **74.6–98%**, and accuracy **56.6–95%** across 19 studies (PMID 34565082, DOI 10.31083/j.rcm2203090) — a ~50-point spread driven mainly by evaluation regime, not algorithm quality. Three regime axes explain it: (a) **reference standard** (self-report vs lab stressor vs cortisol); (b) **generalization** — one architecture scored ~95% accuracy personalized but ~67% generalized to held-out subjects (PMID 38875573, DOI 10.2196/52171), and nonlinear models reached AUC 0.96–0.99 on curated lab data vs 0.70–0.73 for linear models (PMID 41825135, DOI 10.1088/1361-6579/ae520c); (c) **device/condition** — the closest analog to this regime, stress detection amid everyday activity on held-out subjects, reported **AUROC 0.741** (PMID 41945645, DOI 10.2196/80450). Lab SVM on HRV features reached 82.4% accuracy (PMID 39996980, DOI 10.3390/bios15020078) but under controlled conditions. The defensible expectation for *this* regime is therefore AUC ≈ 0.70–0.75, not the 0.90s that headline the field.

**Confidence: HIGH** (on the field range and why one number is meaningless). **The specific ≥0.72 anchor is a study-defined placeholder — explicitly NOT an established or regulatory benchmark.**

**Expert review needed.** Biostatistician + clinical stakeholders to finalize the operating point and anchors; the number must be fixed before unblinding.

---

## 4. Ground Truth Strategy

**Recommendation.** EMA momentary perceived-stress rating as primary reference. Reframe the endpoint as **agreement with self-perceived stress**, not physiological stress. Measure and report EMA label quality: compliance (answered/delivered) overall and by subgroup; within-person test–retest reliability of the stress item; a pre-specified stress-positive threshold with sensitivity analysis across adjacent cut points. Define the HRV window relative to each prompt a priori; include an activity covariate.

**Rationale.** EMA is the ecologically appropriate reference when the target construct is perceived stress (Smets et al. 2018, DOI 10.1038/s41746-018-0074-9). But cortisol/HPA-axis reactivity remains the physiological gold standard the field benchmarks against (Vos et al. 2023, DOI 10.1016/j.ijmedinf.2023.105026), and the HRV–stress association is real but modest (Kim et al. 2018, DOI 10.30773/pi.2017.08.17); classifier performance is bounded above by label reliability. Not collecting cortisol is a deliberate trade to preserve the decentralized design and must be stated as a limitation.

**Confidence: HIGH** (EMA is a defensible, correctly-scoped reference).

**Expert review needed.** Psychometrician / behavioral scientist on the EMA instrument and reliability estimation — flagged because PsycINFO-indexed measurement literature was not accessible in this session (see inventory).

---

## 5. Sample Size

**Recommendation.** Two distinct calculations. (a) **Primary benchmark** (does sensitivity clear a goal): a one-sample test distinguishing Se 0.75 from 0.70 at one-sided α=0.05, 80% power needs ≈ 501 stress-positive units — easily met by a 500-participant cohort contributing many epochs each. (b) **Sensor sub-study** (Field 2): sized for LoA precision, ~45 evaluable / ~50 enrolled per device (LoA 95% CI half-width ≈ 1.71·SD/√n → ~±0.4 SD). Subgroup disparity sizing is treated in Field 6.

**Rationale.** Enrollment magnitudes cross-checked against comparable decentralized wearable cohorts on ClinicalTrials.gov (see inventory). The one-sample benchmark figure is a reproducible power calculation, not a retrieved standard.

**Confidence: MEDIUM.** Calculations are sound; inputs (target Se, prevalence ~25%) are assumptions requiring stakeholder confirmation.

**Expert review needed.** Biostatistician to lock effect sizes, prevalence, and the epoch-level variance assumptions.

---

## 6. Subgroup Requirements

**Recommendation.** Add **Fitzpatrick skin tone (I–VI)** as a pre-specified stratum — grouped I–II / III–IV / V–VI — analyzed at the **epoch level with a generalized linear mixed model** (skin-tone fixed effect, participant random intercept, activity covariate). Recruitment floor **≥150 in the darkest stratum (V–VI)**. Report per-stratum sensitivity *and* specificity with CIs as a primary output. Pre-register the minimum detectable disparity given realized cluster sizes.

**Rationale.** Melanin absorbs the LED wavelengths PPG depends on, and this bias stays hidden when cohorts skew light-skinned — the pulse-oximetry precedent (Sjoding et al. 2020, DOI 10.1056/nejmc2029240; Koerber et al. 2023, DOI 10.1007/s40615-022-01446-9). Consensus wearable-research guidance now expects deliberate recruitment across skin tones and powered subgroup reporting (de Zambotti et al. 2023, DOI 10.1093/sleep/zsad325). A participant-level disparity test would need ~1,251/stratum to detect a 5pp gap; the epoch-level GLMM (design effect DEFF=1+(m−1)·ICC; ~37 epochs/person, ICC 0.1–0.2 → ~4.5–8 effective units/person) restores ~5pp detectability at feasible recruitment. **Fitzpatrick, not race**, because the confound is optical, not social.

**Confidence: HIGH** (skin tone is the mechanistically correct stratum and must be powered). Effective-N depends on the realized ICC — report and re-derive.

**Expert review needed.** Biostatistician (GLMM + ICC), DEI/recruitment lead (feasibility of the V–VI floor).

---

## 7. Regulatory Pathway

**Recommendation.** As currently claimed (wellness notification, no disease claim), this is a **General Wellness product — FDA product code PWC, unclassified, GMP-exempt — not regulated as a medical device**, provided labeling makes no diagnose/treat/cure/mitigate claim. If a medical-device claim is intended, the pathway is almost certainly **De Novo** (no predicate exists for HRV stress detection), with the study designed as De Novo-ready special-controls evidence.

**Rationale.** A direct openFDA query returns **no product code, 510(k), or De Novo for an HRV-based stress-detection algorithm on a consumer wearable**. Adjacent authorizations, none of which is a stress detector: biofeedback *treatment* for stress/anxiety symptoms (code **SEN**, Class II, 21 CFR 882.5050; e.g. **K233337**, Freespira 2025); the consumer-PPG code **QDB**, whose authorized use is irregular-rhythm notification (**DEN180042**, Apple 2018; **K212372**, Fitbit 2022); OTC ECG software **QDA** (**DEN180044** Apple 2018; **K221774** Garmin 2023; **K240909** Samsung 2024); Samsung's sleep-apnea feature (**DEN230041**, 2024, code **QZW**) — the clearest template for a consumer-wearable physiological-detection feature reaching De Novo; and camera-based vitals **QME** (**DEN200019**, Oxehealth 2021). The pattern: rhythm/ECG/SpO2/sleep-apnea have crossed into De Novo/510(k); **stress has not**. No regulator has published a numeric performance floor for this device class. Framing follows the V3 / digital-measure evidentiary approach (Goldsack et al. 2020, DOI 10.1038/s41746-020-0260-4).

**Confidence: HIGH** (wellness-vs-device boundary and the absence of an HRV-stress authorization are directly evidenced by openFDA).

**Expert review needed.** FDA regulatory counsel — especially a Q-Submission/pre-submission if the device framing is pursued.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Pre-specify real-world performance surveillance: drift monitoring of RMSSD-input quality and classifier output distribution by device model, OS/firmware version, and skin-tone stratum; a user-facing false-alarm feedback channel; periodic re-validation against fresh EMA. Define escalation thresholds for performance decay and a labelling-update trigger.

**Rationale.** Free-living consumer deployment introduces drift sources absent in validation — firmware changes to the optical pipeline, population shift, seasonal/behavioral change. General-wellness status does not remove the reputational/safety need to detect degradation, and if a device claim is later pursued, real-world performance monitoring is a predictable special control. Monitoring precedent and drift framing drawn from the digital-measure literature (Coravos et al. 2019, DOI 10.1038/s41746-019-0090-4; Goldsack et al. 2020, DOI 10.1038/s41746-020-0260-4).

**Confidence: MEDIUM.** The need is clear; specific drift metrics/thresholds are not standardized for this class and are study-defined.

**Expert review needed.** MLOps/quality lead + regulatory (for the device-claim scenario) to set drift thresholds and the re-validation cadence.

---

# CRITICAL — SOURCE INVENTORY

Every source consulted to build this spec, grouped by type, with the identifiers pulled and the field(s) each grounded.

## Peer-reviewed literature (PubMed / Crossref-verified DOIs)

| Source | Identifier | Grounded field(s) |
|---|---|---|
| Systematic review, HRV stress/fatigue detection (19 studies; Se 47.1–95%, Sp 74.6–98%, Acc 56.6–95%) | PMID 34565082 · DOI 10.31083/j.rcm2203090 | 3 (Performance Benchmarks) |
| Personalized vs generalized stress models (~95% vs ~67%) | PMID 38875573 · DOI 10.2196/52171 | 3 |
| Nonlinear vs linear models (AUC 0.96–0.99 vs 0.70–0.73, LOSO) | PMID 41825135 · DOI 10.1088/1361-6579/ae520c | 3 |
| Stress detection amid everyday activity (AUROC 0.741, held-out) | PMID 41945645 · DOI 10.2196/80450 | 3 |
| Cold-stress cognitive test, SVM on HRV (Acc 82.4%) | PMID 39996980 · DOI 10.3390/bios15020078 | 3 |
| Empatica E4 wrist HRV validation, driving (r>0.67–0.72) | PMID 37896517 · DOI 10.3390/s23208423 | 2 (Sensor Validation) |
| V3 framework (verification/analytical/clinical validation) | DOI 10.1038/s41746-020-0260-4 (Goldsack 2020) | 1, 3, 7, 8 |
| Developing measures / digital biomarkers | DOI 10.1038/s41746-019-0090-4 (Coravos 2019) | 1, 8 |
| Wearable HR/HRV accuracy & limitations | DOI 10.1038/s41746-020-0226-6 (Bent 2020) | 2 |
| Consumer wearable HRV validity | DOI 10.1111/psyp.70004 (Sinichi 2025) | 2 |
| HRV metrics norms/standards | DOI 10.3389/fpubh.2017.00258 (Shaffer & Ginsberg 2017) | 2 |
| HRV methodology in psychophysiology | DOI 10.3389/fpsyg.2017.00213 (Laborde 2017) | 2, 4 |
| EMA / ambulatory stress reference | DOI 10.1038/s41746-018-0074-9 (Smets 2018) | 1, 4 |
| Cortisol/physiological stress benchmark | DOI 10.1016/j.ijmedinf.2023.105026 (Vos 2023) | 4 |
| HRV–stress association (modest) | DOI 10.30773/pi.2017.08.17 (Kim 2018) | 4 |
| Pulse-oximetry racial bias (NEJM) | DOI 10.1056/nejmc2029240 (Sjoding 2020) | 6 (Subgroup) |
| Skin-tone bias in pulse oximetry | DOI 10.1007/s40615-022-01446-9 (Koerber 2023) | 6 |
| Wearable-research skin-tone recruitment guidance | DOI 10.1093/sleep/zsad325 (de Zambotti 2023) | 6 |

## FDA regulatory records (openFDA device databases)

| Record | Identifier | Grounded field(s) |
|---|---|---|
| General Wellness Product | product code PWC (unclassified, GMP-exempt) | 7 |
| Biofeedback for stress/anxiety symptoms (treatment) | product code SEN, 21 CFR 882.5050; K233337 (Freespira 2025) | 7 |
| Biofeedback device (general) | product code HCC | 7 |
| Photoplethysmograph analysis software, OTC | product code QDB; DEN180042 (Apple 2018), K212372 (Fitbit 2022) | 7 |
| ECG software, OTC | product code QDA; DEN180044 (Apple 2018), K221774 (Garmin 2023), K240909 (Samsung 2024) | 7 |
| Sleep apnea feature (De Novo template) | product code QZW; DEN230041 (Samsung 2024) | 7 |
| Camera-based vital-signs software | product code QME; DEN200019 (Oxehealth 2021) | 7 |

## Trial registry
- **ClinicalTrials.gov API v2** — consulted for comparable decentralized wearable-cohort designs and enrollment magnitudes informing Fields 1 and 5. (Design/enrollment context; no single NCT is load-bearing for a numeric claim in this spec.)

## Verification tooling
- **Crossref** (api.crossref.org) — every DOI above resolved to its registered title/authors/year before inclusion. Grounds the integrity of all fields.

## Databases indexed for regulatory nulls
- **openFDA device/classification.json** and **device/510k.json** — queried across stress, heart rate variability, biofeedback, psychophysiological, autonomic, photoplethysmograph, wellness terms; the **null result** (no HRV stress-detection authorization) is itself the Field-7 finding.

---

## Sources I wanted but could not fully access

- **PsycINFO / APA PsycNet** — the primary psychology/behavioral-measurement index. Directly relevant to the EMA construct and stress-measurement reliability (Field 4) and to Field 6's behavioral confounds. No free, no-auth API; not queryable in this environment. **This is the most consequential gap for a psychological-construct system.**
- **Cochrane Library (CENTRAL/CDSR)** — RCT evidence and existing systematic reviews; would strengthen Fields 1, 3. Subscription only.
- **Embase** — broader drug/device and conference coverage than MEDLINE; Fields 3, 7. Subscription only.
- **Web of Science / Scopus** — citation-completeness cross-check. Subscription only.
- **CINAHL** — nursing/allied-health, patient-reported-outcome and EMA-adjacent literature (Field 4). Subscription only.
- **openFDA device/pma.json, device/event.json (MAUDE), device/recall.json** — not queried this session; would strengthen Field 8 (real-world safety signals) and the Class III scenario in Field 7.
- **Ex-US regulators** — EU EUDAMED/EMA, UK MHRA, Japan PMDA, Australia TGA. No clean free APIs; relevant only if multi-market claims are intended (Field 7).
- **FDA guidance PDFs** — the General Wellness guidance and De Novo special-controls documents were referenced by name/regulation number via the classification records, not fetched as full text; a full-text read would sharpen Field 7 language.
- **medRxiv/bioRxiv preprints** — not swept this session; would address recency/publication-bias blind spots in Fields 2, 3.

*Note on method: this reference output was synthesized from sources retrieved and verified during the discovery session. An automated pipeline reproducing it should re-retrieve each identifier live and re-run the Crossref/openFDA resolution pass, treating any identifier that fails to resolve as a drop, not a synthesis.*
