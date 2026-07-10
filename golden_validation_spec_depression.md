# Clinical AI Validation Specification — Depression Screening / Triage Algorithm

**System under evaluation:** An algorithm estimating the likelihood of a depressive disorder in adults from patient-reported questionnaire responses and/or passively collected behavioral/speech signals, deployed as a screening/triage aid (flags patients for full clinical assessment; does not diagnose). Reference standard: validated instrument (e.g. PHQ-9) and/or structured clinical interview. Setting: primary care and telehealth. Population: adults across ages, sexes, race/ethnicity.

**Grounding status:** Every identifier below was retrieved and resolved this session — 15 literature records (PMID → PubMed efetch; DOI → Crossref), FDA records (K/DEN numbers and product codes → openFDA), and ClinicalTrials.gov v2 API queries. Numeric values are labeled `[retrieved-from-source]` or `[study-defined-placeholder]`.

---

## 1. Study Design

**Recommendation:** Conduct a prospective, multi-site diagnostic-accuracy study in the intended primary-care/telehealth settings, comparing the algorithm's screen-positive flag against a clinician-administered reference standard applied to *all* enrolled patients (avoiding partial/differential verification bias). Report per STARD 2015 and, because the system is an AI prediction model, per TRIPOD+AI; appraise risk of bias with QUADAS-2. Because this is a decision-support system entering clinical use, add an early-stage live-clinical-evaluation phase per DECIDE-AI before any effectiveness claim.

**Rationale:** STARD 2015 is the reporting standard for diagnostic-accuracy studies (PMID 28137831 · DOI 10.1136/bmjopen-2016-012799). TRIPOD+AI is the current reporting guideline for clinical prediction models including AI (PMID 38626949 · DOI 10.1136/bmj.q824), developed alongside the TRIPOD-AI/PROBAST-AI protocol (PMID 34244270 · DOI 10.1136/bmjopen-2020-048008). QUADAS-2 is the validated risk-of-bias tool for diagnostic-accuracy studies (PMID 22007046 · DOI 10.7326/0003-4819-155-8-201110180-00009). DECIDE-AI covers early-stage live clinical evaluation of AI decision-support systems (PMID 35584845 · DOI 10.1136/bmj-2022-070904; PMID 36639172 · DOI 10.1016/j.crad.2022.09.131).

**Confidence:** HIGH — the reporting/appraisal framework is established and directly on point.

**Expert review needed:** A biostatistician and clinical-trial methodologist should fix the enrollment flow (consecutive vs. convenience sampling), the verification protocol, and whether a paired within-patient design against PHQ-9 is feasible in telehealth.

---

## 2. Input / Signal Validation

**Recommendation:** Before interpreting any algorithm output, validate the *input signal itself*. For questionnaire inputs, confirm the digital PHQ-9 administration reproduces the validated paper instrument (item wording, scoring, response completeness). For passively collected behavioral/speech inputs, validate signal acquisition and feature extraction against a documented reference: device/microphone specification, sampling rate, minimum usable-signal thresholds, and a defined data-sufficiency (missingness/quality) gate that rejects unusable captures *before* scoring. This precondition is separate from — and prior to — output accuracy.

**Rationale:** The PHQ-9 as a measurement instrument has documented validity as a depression severity measure (PMID 11556941 · DOI 10.1046/j.1525-1497.2001.016009606.x); a digital re-implementation must be shown to preserve that instrument, not silently alter it. For speech-based inputs, the evidence base is a systematic review of automated psychiatric assessment from speech, which documents heterogeneity in acquisition and feature pipelines (PMID 32128436 · DOI 10.1002/lio2.354). For passive-sensing inputs, symptom-level passive-sensing work illustrates the dependence of downstream prediction on sensing-signal quality (PMID 37960563 · DOI 10.3390/s23218866). **No numeric signal-quality threshold is an established standard**; any minimum-signal cutoff is `[study-defined-placeholder]`.

**Confidence:** MEDIUM — the principle is well supported, but there is no consensus quantitative acceptance criterion for behavioral/speech signal quality in this domain.

**Expert review needed:** A speech/sensor-processing engineer and a psychometrician should define the concrete signal-acceptance thresholds and confirm digital-PHQ-9 equivalence testing.

---

## 3. Performance Benchmarks

**Recommendation:** Report sensitivity and specificity (with 95% CIs) at a pre-specified operating threshold, plus AUROC, PPV/NPV at the expected local prevalence, and calibration. Because the intended use is *triage* (flag for assessment), prioritize sensitivity and NPV, and pre-register the operating point. Anchor the target to the reference instrument's own screening accuracy rather than to an invented cutoff.

**Rationale:** In the PHQ-9 individual-participant-data meta-analysis (data obtained for 58 of 72 studies; overall total n=17,357, 2,312 major-depression cases), the operating point of cut-off ≥10 against semistructured clinical interviews — estimated from the **semistructured-interview subgroup of 29 studies / 6,725 participants** — gave pooled **sensitivity 0.88 (95% CI 0.83–0.92) and specificity 0.85 (0.82–0.88)** `[retrieved-from-source]` (PMID 30967483 · DOI 10.1136/bmj.l1476) — these figures describe the *reference instrument*, providing a realistic performance envelope. (The n=17,357 total describes the overall meta-analysis and is cited for §5 sample-size magnitude only, not bundled with the subgroup accuracy estimate.) **There is no FDA-cleared or guideline-established numeric accuracy benchmark for a depression-screening algorithm** (see §7 and Source Inventory); any minimum sensitivity/specificity the sponsor sets is `[study-defined-placeholder]`.

**Confidence:** MEDIUM — the reference-instrument benchmark is HIGH-confidence and source-grounded, but the absence of a device-specific regulatory benchmark means the acceptance target itself is a placeholder requiring justification.

**Expert review needed:** Clinical leads must set the pre-specified operating threshold and the minimum acceptable sensitivity/NPV given local prevalence and the cost of missed cases.

---

## 4. Ground Truth Strategy

**Recommendation:** Use a two-tier reference standard: a validated instrument (PHQ-9) as the screening comparator and a clinician-administered *structured/semistructured diagnostic interview* as the definitive reference for the presence of major depression. Apply the definitive reference to all enrollees where feasible; where a two-stage design is used, model verification bias explicitly. Record interviewer training and blinding to the algorithm output.

**Rationale:** The PHQ-9 IPD meta-analysis shows the reference standard's *type* materially changes measured accuracy — sensitivity against semistructured interviews was 5–22% higher than against fully structured lay-administered interviews (PMID 30967483 · DOI 10.1136/bmj.l1476). The instrument's original validation against clinician diagnosis anchors PHQ-9 as an acceptable comparator (PMID 11556941). The USPSTF adult-depression recommendation frames screening as valid only when coupled to adequate diagnosis and follow-up (PMID 26813211 · DOI 10.1001/jama.2015.18392), and a critical companion editorial cautions on the strength of that evidence base (PMID 26815331 · DOI 10.1001/jamapsychiatry.2015.3281). QUADAS-2 formalizes reference-standard bias domains (PMID 22007046).

**Confidence:** HIGH — reference-standard choice is well-characterized in the source literature.

**Expert review needed:** A psychiatrist should specify which structured interview (e.g. SCID vs. MINI) is the definitive reference and the acceptable inter-rater reliability floor.

---

## 5. Sample Size

**Recommendation:** Power the validation study using established minimum-sample-size methods for *external validation* of a binary-outcome prediction model — targeting precise estimation of sensitivity/specificity/calibration at the expected prevalence, not a generic rule of thumb. Compute the target from the pre-specified operating characteristics and event fraction.

**Rationale:** Riley et al. give the criteria and formulae for the minimum sample size to externally validate a clinical prediction model with a binary outcome (PMID 34031906 · DOI 10.1002/sim.9025); the companion paper covers continuous outcomes, relevant if a severity score is also validated (PMID 33150684 · DOI 10.1002/sim.8766). For enrollment-magnitude context, ClinicalTrials.gov shows on-topic studies span small pilot to large cohorts — e.g. a psychosocial digital-phenotyping screening study enrolling 25 (NCT07220343) versus a neurodevelopmental/mental-health detection study enrolling 500 (NCT06792175). The overall PHQ-9 IPD dataset (n=17,357) illustrates the magnitude of a pooled screening-accuracy evidence base (PMID 30967483). **Any specific N is `[study-defined-placeholder]`** until the operating point and prevalence are fixed.

**Confidence:** HIGH for the method; the numeric target is deliberately left as a placeholder pending §3 inputs.

**Expert review needed:** A statistician must run the Riley calculation once the operating threshold, anticipated sensitivity/specificity, and local prevalence are set, and inflate for expected subgroup analyses (§6).

---

## 6. Subgroup Requirements

**Recommendation:** Pre-specify and power (or at minimum adequately sample) subgroup analyses across age, sex, and race/ethnicity, reporting per-subgroup sensitivity/specificity and calibration with explicit fairness metrics. Test the input instrument for measurement invariance across subgroups, since a screening flag that is systematically less accurate in a subgroup produces inequitable triage. Report subgroup results per TRIPOD+AI.

**Rationale:** Obermeyer et al. demonstrated that a widely deployed health-management algorithm exhibited substantial racial bias, exposing how label/proxy choices propagate inequity into deployed tools (PMID 31649194 · DOI 10.1126/science.aax2342) — a direct cautionary precedent for a triage algorithm. The PHQ-9 IPD meta-analysis explicitly examined accuracy across participant subgroups via meta-regression, establishing subgroup accuracy variation as an expected, measurable phenomenon for depression screening (PMID 30967483 · DOI 10.1136/bmj.l1476). TRIPOD+AI requires reporting of fairness and subgroup performance (PMID 38626949).

**Confidence:** HIGH — subgroup/fairness evaluation is a well-established requirement with a strong precedent.

**Expert review needed:** A health-equity methodologist should choose the fairness metrics (e.g. equalized sensitivity vs. calibration parity) and set minimum per-subgroup sample sizes; note these decisions feed back into §5.

---

## 7. Regulatory Pathway

**Recommendation:** Treat this as a **Software as a Medical Device diagnostic/assessment aid** for which **no existing FDA product code or authorization covers a depression *screening/detection* algorithm** — meaning the likely U.S. pathway is **De Novo classification** (a novel low-to-moderate-risk device type without a predicate), *not* 510(k) clearance against an existing depression-screening predicate. Engage FDA via a pre-submission (Q-Sub) early. Do not assume a 510(k) predicate exists.

**Rationale (all openFDA-verified this session):**
- A direct openFDA classification search for depression-named devices returns only **treatment** devices — product code JXK (cranial electrotherapy stimulator to treat depression, class 3) and MUZ (implanted stimulator, depression, class 3) — not screening software.
- The only depression-*specific* software product code is **SAP — "Computerized Behavioral Therapy Device For Depressive Disorders," class 2, regulation 882.5801** — a *therapeutic* digital device, not a screening aid; its clearances are therapeutics (K231209 Rejoyn / Otsuka, 2024-03-30; and MamaLift Plus, product code SAP).
- Product code **SIE ("Tempo Pilot Bh: Behavioral Health," class N)** is a pilot/placeholder classification with **no regulation number** — it does not constitute a screening-device authorization.
- The **relevant precedent pathway is De Novo for a psychiatric diagnostic aid**: **DEN200069 — Cognoa ASD Diagnosis Aid** (2021-06-02), which *created* product code **QPF** (Pediatric Autism Spectrum Disorder Diagnosis Aid, class 2, reg 882.1491); and **DEN110019 — NEBA System** (2013-07-15), product code **NCG** (Neuropsychiatric Interpretative EEG Assessment Aid, class 2, reg 882.1440). These show FDA authorizes novel psychiatric assessment/diagnosis aids via De Novo, then subsequent devices clear via 510(k) against the new code (e.g. K243558 Canvas Dx under QPF).

**Regulatory NULL result (verified):** As of this session's openFDA queries, **there is no FDA product code, 510(k) clearance, De Novo grant, or PMA for a depression-screening/detection algorithm.** The nearest depression-specific code (SAP) is for therapy, not screening.

**Confidence:** MEDIUM-HIGH — the null result and the De Novo analogue pathway are directly verified in openFDA; the *precise* device classification FDA would assign is a regulatory judgment, not a database fact.

**Expert review needed:** A regulatory-affairs specialist should confirm the De Novo vs. 510(k) determination through a formal FDA pre-submission and assess whether the passive behavioral/speech modality raises the risk classification.

---

## 8. Post-Deployment Monitoring

**Recommendation:** Implement a Predetermined Change Control Plan-style monitoring program: continuous tracking of screen-positive rate, calibration drift, and *per-subgroup* performance against periodically sampled reference-standard confirmations; define trigger thresholds for re-validation; monitor input-signal quality drift (§2) as a leading indicator; and capture real-world outcomes (did flagged patients receive assessment). Report the live-evaluation phase per DECIDE-AI.

**Rationale:** DECIDE-AI specifically addresses the early live-clinical-evaluation stage where deployment behavior of an AI decision-support system is first observed (PMID 35584845 · DOI 10.1136/bmj-2022-070904; PMID 36639172 · DOI 10.1016/j.crad.2022.09.131). The Obermeyer precedent shows bias can be invisible pre-deployment and surface only in real-world use, motivating ongoing subgroup surveillance (PMID 31649194). USPSTF framing ties screening value to downstream follow-up, so monitoring must track whether flags translate into assessment, not just flag counts (PMID 26813211). **All monitoring trigger thresholds (drift %, recalibration cadence) are `[study-defined-placeholder]`** — no established numeric standard exists.

**Confidence:** MEDIUM — the framework is supported, but specific drift thresholds and re-validation cadence are not standardized and must be justified locally.

**Expert review needed:** A regulatory/quality lead should define the change-control triggers and the reference-standard re-sampling cadence for ongoing calibration checks.

---

# SOURCE INVENTORY

## Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| PHQ-9: validity of a brief depression severity measure (Kroenke, JGIM 2001) | PMID 11556941 · DOI 10.1046/j.1525-1497.2001.016009606.x | 2, 4 |
| USPSTF Recommendation Statement: Screening for Depression in Adults (JAMA 2016) | PMID 26813211 · DOI 10.1001/jama.2015.18392 | 4, 8 |
| Critical editorial on USPSTF depression-screening recommendation (JAMA Psychiatry 2016) | PMID 26815331 · DOI 10.1001/jamapsychiatry.2015.3281 | 4 |
| PHQ-9 screening accuracy — individual participant data meta-analysis (Levis, BMJ 2019) | PMID 30967483 · DOI 10.1136/bmj.l1476 | 3, 4, 5, 6 |
| Minimum sample size for external validation, binary outcome (Riley, Stat Med 2021) | PMID 34031906 · DOI 10.1002/sim.9025 | 5 |
| Minimum sample size for external validation, continuous outcome (Riley, Stat Med 2020/21) | PMID 33150684 · DOI 10.1002/sim.8766 | 5 |
| Dissecting racial bias in a health-management algorithm (Obermeyer, Science 2019) | PMID 31649194 · DOI 10.1126/science.aax2342 | 6, 8 |
| QUADAS-2 risk-of-bias tool for diagnostic-accuracy studies (Whiting, Ann Intern Med 2011) | PMID 22007046 · DOI 10.7326/0003-4819-155-8-201110180-00009 | 1, 4 |
| TRIPOD-AI / PROBAST-AI development protocol (Collins, BMJ Open 2021) | PMID 34244270 · DOI 10.1136/bmjopen-2020-048008 | 1 |
| DECIDE-AI reporting guideline, early clinical evaluation of AI DSS (Nat Med / BMJ 2022) | PMID 35584845 · DOI 10.1136/bmj-2022-070904 | 1, 8 |
| DECIDE-AI relevance to AI studies (Clinical Radiology 2023) | PMID 36639172 · DOI 10.1016/j.crad.2022.09.131 | 1, 8 |
| STARD 2015 diagnostic-accuracy reporting guideline, explanation & elaboration (BMJ Open 2016) | PMID 28137831 · DOI 10.1136/bmjopen-2016-012799 | 1 |
| Automated assessment of psychiatric disorders using speech — systematic review (2020) | PMID 32128436 · DOI 10.1002/lio2.354 | 2 |
| Depression-severity prediction from passive sensing — symptom-profiling (Sensors 2023) | PMID 37960563 · DOI 10.3390/s23218866 | 2 |
| TRIPOD+AI updated reporting guideline for clinical prediction models (Collins, BMJ 2024) | PMID 38626949 · DOI 10.1136/bmj.q824 | 1, 3, 6 |

*All 15: PMID confirmed via PubMed efetch (record returned); DOI confirmed to resolve via Crossref `/works/{DOI}` (HTTP 200, matching title) this session.*

## FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| Cranial electrotherapy stimulator to treat depression (class 3; treatment, not screening) | Product code **JXK** | 7 |
| Implanted autonomic nerve stimulator, depression (class 3; treatment) | Product code **MUZ** | 7 |
| Computerized Behavioral Therapy Device for Depressive Disorders (class 2, reg 882.5801; *therapy*, not screening) | Product code **SAP** | 7 |
| Rejoyn — depression digital therapeutic cleared under SAP (Otsuka, 2024-03-30) | **K231209** (product code SAP) | 7 |
| Behavioral-health pilot placeholder classification (class N, no regulation number) | Product code **SIE** | 7 |
| Cognoa ASD Diagnosis Aid — De Novo, created psychiatric diagnostic-aid code (2021-06-02) | **DEN200069** (product code QPF) | 7 |
| Pediatric Autism Spectrum Disorder Diagnosis Aid classification (class 2, reg 882.1491) | Product code **QPF** | 7 |
| Canvas Dx — subsequent 510(k) clearance under QPF (Cognoa, 2025) | **K243558** (product code QPF) | 7 |
| NEBA System — De Novo, neuropsychiatric EEG assessment aid (2013-07-15) | **DEN110019** (product code NCG) | 7 |
| Neuropsychiatric Interpretative EEG Assessment Aid classification (class 2, reg 882.1440) | Product code **NCG** | 7 |

*All records confirmed via openFDA `device/classification` and `device/510k` endpoints this session (K/DEN numbers and product codes returned matching device names, applicants, and decision dates). De Novo grants (DEN…) are surfaced through openFDA's `device/510k` endpoint.*

## Trial registry use (ClinicalTrials.gov v2 API)

- Query `"depression screening artificial intelligence"` → **76** studies (total count returned) — informed §1 (study-design landscape) and §7 (activity context).
- Query `"speech biomarker depression"` → **118** studies — informed §2 (speech-input validation).
- Query `"digital phenotyping depression"` → **33** studies — informed §2 and §5.
- Enrollment-magnitude anchors verified by direct ID lookup (§5): **NCT07220343** (digital-phenotyping psychosocial screening, n=25, recruiting) and **NCT06792175** (mental-health/neurodevelopmental detection, n=500, enrolling by invitation). ClinicalTrials.gov keyword matching is broad; these counts are contextual, not a curated cohort.

## Expected conclusions

1. **Regulatory class/pathway:** A depression screening/triage algorithm is a Software-as-a-Medical-Device assessment/diagnostic aid; the anchored precedent pathway is **De Novo classification** (novel device type, class II expected), as demonstrated by the Cognoa ASD (DEN200069→QPF) and NEBA (DEN110019→NCG) psychiatric-aid precedents — **not** a 510(k) against an existing depression-screening predicate.
2. **Regulatory NULL result (verified):** **No FDA product code, 510(k), De Novo, or PMA exists for a depression *screening/detection* algorithm.** The only depression-specific software code (SAP) is for *therapy*; depression-named cleared devices are treatment stimulators (JXK, MUZ).
3. **Established numeric benchmark:** **No FDA- or guideline-established accuracy benchmark exists for a depression-screening algorithm.** The only source-grounded performance reference is the *instrument's* accuracy — PHQ-9 at cut-off ≥10 vs. semistructured interview: sensitivity 0.88 (0.83–0.92), specificity 0.85 (0.82–0.88) `[retrieved-from-source]`, PMID 30967483 (semistructured-interview subgroup, 29 studies / 6,725 participants). All device acceptance thresholds, sample sizes, and monitoring triggers are `[study-defined-placeholder]`.

## Sources I wanted but could not access (coverage gaps)

- **openFDA dedicated De Novo endpoint** (`device/de_novo`) — **does not exist in openFDA** (404). De Novo grants were recoverable only because openFDA files DEN numbers within the `device/510k` endpoint; a purpose-built De Novo query surface was not available, so De Novo coverage is indirect.
- **openFDA `device/udi`, `device/registrationlisting`, `device/event` (MAUDE), and `enforcement` endpoints** returned 404 in this session's environment — I could not cross-check unique device identifiers, registration/listing, or adverse-event reports.
- **FDA Drugs@FDA / drug labeling** — not queried: this system is a device/SaMD, not a drug or biologic, so no drug identifier applies (stated explicitly rather than fabricating one).
- **Full-text of the cited articles** — only PubMed metadata/abstracts and Crossref records were verified; I confirmed the PHQ-9 accuracy figures directly from the Levis 2019 abstract, but did not retrieve full texts for the methodological guidelines (their content is cited from title/scope, not verified line-by-line).
- **A definitive FDA classification determination** for *this* device — this is a regulatory judgment obtainable only through an FDA pre-submission, not from any database queried here.
- **No contact email was configured**, so all NCBI/Crossref/openFDA calls used the anonymous (rate-limited) pools; this constrained batch size but not identifier verification.

---

*This is a research/informational validation reference, not regulatory or clinical advice — the "Expert review needed" lines flag decisions that require a qualified regulatory, statistical, or clinical professional. All identifiers resolved against their source databases during the generating session; where a database or record type was unreachable, it is listed as a coverage gap rather than filled with an unverified value.*
