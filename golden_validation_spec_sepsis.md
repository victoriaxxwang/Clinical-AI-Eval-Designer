# Clinical AI Validation Specification — EHR-Based Sepsis Early-Warning Algorithm

**System under evaluation:** Algorithm that continuously analyzes routinely-collected structured EHR time-series (vital signs, labs, nursing assessments, demographics) to predict onset of sepsis / septic shock in hospitalized adults hours before clinical recognition; deployed as an inpatient early-warning / clinical decision support (CDS) tool that alerts clinicians to initiate sepsis workup and treatment. Input: structured EHR data only (no new sensor, image, or genomic assay).

**Grounding status:** Every identifier below was retrieved and resolved this session — PMIDs against PubMed E-utilities, DOIs against Crossref, FDA records/product codes against openFDA, trial IDs against the ClinicalTrials.gov v2 API. Identifiers that could not be resolved were dropped. Numbers are labeled **[retrieved-from-source]** or **[study-defined-placeholder]**; no numeric threshold is presented as an established regulatory standard unless retrieved from a source.

---

## 1. Study Design

**Recommendation.** Adopt a phased evaluation matching the maturity ladder that regulators and reporting bodies now expect for CDS algorithms: (a) retrospective internal + **geographically/temporally external** validation of discrimination and calibration; (b) **silent-mode prospective** deployment (algorithm runs, alerts suppressed) to confirm performance on the live data pipeline before any clinician sees output; (c) a **prospective interventional** study measuring the effect of alerting on process and patient outcomes, ideally cluster-randomized or stepped-wedge. Report per the TRIPOD+AI checklist for the predictive-model components and DECIDE-AI for the early-stage live-deployment/human-factors components.

**Rationale.** The EHR-time-series approach itself was established with an interpretable real-time score derived from routinely-collected data (TREWScore, PMID 26246167), which defines the phase-(a) modeling starting point. The single most instructive cautionary case for this device class is the Epic Sepsis Model: an external validation in ~27,000 patients found substantially worse discrimination than the vendor-reported figure, establishing that internal/vendor validation does not transfer (PMID 34152373; editorial PMID 34152360) — a gap that only a prospective multicenter validation can close (updated proprietary-model prospective validation, PMID 41758510). Prospective, multi-site outcome evaluation is achievable and is the current bar for credibility — demonstrated by the TREWS program's prospective multi-site study (PMID 35864252) and its companion adoption analysis (PMID 35864251), and by the COMPOSER deployment study reporting quality-of-care and survival endpoints (PMID 38263386). Silent-mode / simulated-prospective evaluation before go-live is an established de-risking step (PMID 33711001). Reporting standards: TRIPOD+AI (PMID 38626948 · DOI 10.1136/bmj-2023-078378) and DECIDE-AI (PMID 35585198 · DOI 10.1038/s41591-022-01772-9; BMJ version PMID 35584845 · DOI 10.1136/bmj-2022-070904).

**Confidence:** HIGH.
**Expert review needed:** Biostatistician + clinical trialist to fix the interventional design (cluster-RCT vs stepped-wedge) and the primary endpoint hierarchy.

---

## 2. Input / Signal Validation (pre-condition)

**Recommendation.** Before any output is interpreted, validate the **EHR data substrate itself**: (a) measurement-completeness and latency of each input stream (vitals, labs, nursing flowsheets) at prediction time; (b) agreement of ingested values against the source record (unit harmonization, timezone/timestamp integrity, mapping of local codes to the model's expected vocabulary); (c) missingness patterns and the behavior of imputation under real-world gaps; (d) confirmation that features are computable from data available *before* the label event (no leakage of order/result timing). Define minimum data-availability criteria below which the algorithm returns "insufficient data" rather than a score.

**Rationale.** For an EHR-only model the "signal" is the data pipeline, and its integrity is the dominant failure mode: the Epic external-validation experience shows that discrimination collapses when the deployment data environment differs from the development one (PMID 34152373). Systematic reviews of ML sepsis prediction repeatedly flag heterogeneous, incompletely reported input handling and leakage risk as core threats to validity (Fleuren meta-analysis PMID 31965266; Moor et al. review PMID 34124082). An explicit "abstain when uncertain / insufficient input" behavior has been implemented and evaluated for a deployed sepsis model (COMPOSER "I don't know" mechanism, PMID 34504260). Data-drift surveillance of the input distribution is a validated early indicator of downstream failure (PMID 41337748). The FDA classification for this device type (product code **SAK**, 21 CFR 880.6316) states the device is **adjunctive** and "not intended to be used as the sole determining factor" [retrieved-from-source, openFDA classification], which presupposes trustworthy inputs.

**Confidence:** HIGH.
**Expert review needed:** Clinical informatics / EHR-integration lead to specify per-feature completeness thresholds and the site-onboarding data-QC protocol.

---

## 3. Performance Benchmarks

**Recommendation.** Report discrimination (AUROC), and — because sepsis is low-prevalence and alerts drive workload — **AUPRC, sensitivity at a fixed alert rate, positive predictive value, number-needed-to-alert, and calibration (plot + slope/intercept)**, all stratified by lead time before clinical recognition. Do **not** adopt any single AUROC cut-off as a pass/fail standard; benchmark against the site's incumbent workflow (e.g., SIRS/Sepsis-3 criteria, existing EWS) as the comparator.

**Rationale.** No regulatory or literature source retrieved this session establishes a fixed numeric performance threshold that a sepsis EHR algorithm must exceed; the FDA pathway relies on special controls and clinical/analytical validation rather than a published minimum AUROC (openFDA product code **SAK**, De Novo **DEN230036**). Reported performance is highly heterogeneous and setting-dependent across the evidence base (Fleuren PMID 31965266; Moor PMID 34124082), and vendor-reported vs externally-validated AUROC can diverge sharply (Epic: PMID 34152373) — the AUROC/sensitivity-at-fixed-alert-rate metric set recommended here mirrors how EHR sepsis models have reported discrimination since TREWScore (PMID 26246167) and how a multicenter prospective validation reported updated-model performance (PMID 41758510). Prospective deployments have reported process/outcome effects (timeliness of antibiotics: PMID 38381351; care/survival: PMID 38263386) — these process and clinical endpoints, not a bare AUROC, are the meaningful benchmarks.

- **Any specific AUROC / sensitivity / alert-rate target = [study-defined-placeholder]** to be pre-registered by the sponsor; none is retrieved-from-source as an established standard.

**Confidence:** MEDIUM (metrics are well-established; specific target values are not standardized).
**Expert review needed:** Statistician to set the operating point and the non-inferiority/superiority margin vs the incumbent EWS.

---

## 4. Ground Truth Strategy

**Recommendation.** Anchor the sepsis label on the **Sepsis-3 clinical criteria** (suspected infection + acute SOFA increase ≥2; septic shock as the vasopressor + lactate subset), operationalized from structured EHR surrogates (culture orders + antibiotic administration windows for "suspected infection", organ-dysfunction from labs/vitals). Require an independent, blinded clinical adjudication of a sampled subset to estimate label noise, and pre-specify the timestamp definition of "onset" (this defines lead time). Report label prevalence and the sensitivity of conclusions to alternative label definitions (e.g., billing/ICD-based vs clinical).

**Rationale.** Sepsis-3 is the governing consensus definition (PMID 26903338 · DOI 10.1001/jama.2016.0287) and is the reference against which sepsis prediction labels are constructed. The reviews retrieved emphasize that label definition (clinical vs administrative, onset-time anchoring) is a primary driver of apparent performance and a major source of between-study heterogeneity (Fleuren PMID 31965266; Moor PMID 34124082). The FDA SAK definition frames the device around "prediction or diagnosis of sepsis" and explicitly excludes monitoring treatment response, which constrains what the ground-truth event may be [retrieved-from-source, openFDA classification, product code SAK].

**Confidence:** HIGH (definition anchor); MEDIUM (EHR operationalization varies by site).
**Expert review needed:** Infectious-disease / critical-care clinician to adjudicate the suspected-infection window and onset timestamp.

---

## 5. Sample Size

**Recommendation.** Power the study on the **event (sepsis case) count**, not total admissions, given low prevalence. Use TRIPOD+AI-aligned sample-size logic (adequate events-per-candidate-predictor for any refitting/recalibration; precision targets on AUROC/calibration for validation). For the interventional stage, power on the clinical/process primary endpoint (e.g., time-to-antibiotics, mortality, ICU transfer) with realistic effect sizes and clustering inflation if cluster-randomized.

**Rationale.** No source retrieved prescribes a fixed N for this device class; sizing is design- and prevalence-dependent. Enrollment in comparable registered evaluations spans a wide range [retrieved-from-source, ClinicalTrials.gov v2]: interventional sepsis-EWS trials include NCT02376842 (n≈1,149), NCT03235193 (n≈2,296), NCT05065333 (n≈1,345), and NCT04570618 (n≈320); large pragmatic/observational efforts reach the tens of thousands (e.g., NCT04005001, n≈37,986). These bracket realistic enrollment but do not substitute for a pre-specified power calculation.

- **Any specific N = [study-defined-placeholder]**, to be derived from the chosen primary endpoint and expected sepsis prevalence.

**Confidence:** MEDIUM.
**Expert review needed:** Statistician for the formal power calculation once prevalence and endpoint are fixed.

---

## 6. Subgroup Requirements

**Recommendation.** Pre-specify performance (discrimination **and** calibration) within subgroups: **sex, age bands, race/ethnicity, admitting service (medical vs surgical), care setting (ward vs ICU), and admission acuity**, plus key confounder strata (immunocompromise, chronic organ disease). Set a minimum event count per subgroup for reportable estimates and flag subgroups falling below it as under-powered rather than omitting them. Report subgroup calibration drift explicitly — miscalibration, not just AUROC gaps, drives inequitable alerting.

**Rationale.** The intended population spans sexes, ages, races/ethnicities, and admitting diagnoses, so subgroup validity is a claim-level requirement. Reviews of ML sepsis models note inconsistent subgroup reporting as a limitation of the current evidence base (Fleuren PMID 31965266; Moor PMID 34124082), and TRIPOD+AI specifically strengthens expectations for fairness/subgroup reporting in clinical prediction models (PMID 38626948). External-validation failure modes (PMID 34152373) frequently manifest unevenly across case-mix, making subgroup calibration a safety issue, not a secondary analysis.

**Confidence:** HIGH (requirement); MEDIUM (specific strata thresholds are site-dependent).
**Expert review needed:** Health-equity methodologist + clinician to finalize strata and minimum-event thresholds.

---

## 7. Regulatory Pathway

**Recommendation.** Treat the device as **FDA Class II software** under **21 CFR 880.6316**, product code **SAK** ("Software Device To Aid In The Prediction Or Diagnosis Of Sepsis"), General Hospital specialty. A purely-EHR sepsis prediction/diagnosis-aid device now has a **510(k) pathway with an existing predicate**, so pursue **510(k) clearance** citing the cleared predicate; a De Novo would be required only if the sponsor's intended use falls outside the established SAK classification and special controls. Design labeling to the SAK special controls: **adjunctive use, not the sole determining factor, not for monitoring treatment response.**

**Rationale.** openFDA classification confirms product code **SAK**, device class **2**, regulation **880.6316** [retrieved-from-source]. The classification was created by De Novo **DEN230036** — *Sepsis ImmunoScore* (Prenosis, Inc.), decision date **2024-04-02** [retrieved-from-source, openFDA]. **Caveat on DEN230036:** that granted device combines blood-biomarker measurements with clinical parameters, so it is not a pure EHR-time-series-only device; it is cited here as the **classification-defining record**, not as an identical predicate. The directly analogous EHR-based clearance retrieved is **K250680** — *Bayesian Health Sepsis Flagging Device* (Bayesian Health, Inc.), a **Traditional 510(k)**, decision **Substantially Equivalent**, decision date **2026-04-30**, product code **SAK** [retrieved-from-source, openFDA]. Together these establish both the class and an available predicate route for an EHR-based sepsis early-warning algorithm.

**Confidence:** HIGH (classification and records verified); MEDIUM (which specific device is the best predicate depends on the sponsor's exact intended-use statement).
**Expert review needed:** Regulatory affairs specialist to draft the intended-use statement and confirm substantial equivalence to K250680 vs a De Novo strategy.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Operate a continuous monitoring program covering: (a) **input data-drift** surveillance on each feature stream; (b) **performance drift** (rolling AUROC/AUPRC/calibration against adjudicated or proxy labels); (c) **alert burden / fatigue** metrics (alerts per patient-day, override/dismissal rates, PPV in production); (d) **subgroup performance** on the same cadence as launch; (e) a pre-specified **recalibration / retraining and rollback** trigger and change-control process consistent with an FDA Predetermined Change Control Plan. Track downstream process metrics (time-to-antibiotics, workup ordering) as leading indicators.

**Rationale.** Performance degradation after deployment is expected, not exceptional, and unsupervised characterization of temporal dataset shift is a validated early-warning method for it (PMID 41337748). Provider adoption and alert response are themselves determinants of benefit and must be monitored, not assumed (TREWS adoption analysis PMID 35864251; deployment/quality study PMID 38263386). Whether alerting actually changes care (e.g., antibiotic timeliness) is measurable in production and is the operational signal of value (PMID 38381351). The adjunctive, alarm-capable framing in the SAK special controls (openFDA product code SAK) makes alert-fatigue and override monitoring a labeling-relevant safety obligation.

**Confidence:** HIGH.
**Expert review needed:** MLOps/clinical-informatics team + regulatory to define drift thresholds and the change-control/rollback SOP.

---

# SOURCE INVENTORY

### Peer-reviewed literature (all resolved this session: PMID → PubMed, DOI → Crossref)

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| Sepsis-3: Third International Consensus Definitions for Sepsis and Septic Shock (JAMA 2016) | 26903338 · 10.1001/jama.2016.0287 | 4 |
| TREWScore: targeted real-time early warning score for septic shock from EHR (Sci Transl Med 2015) | 26246167 · 10.1126/scitranslmed.aab3719 | 1, 3 |
| TREWS prospective multi-site patient-outcome study after implementation (Nat Med 2022) | 35864252 · 10.1038/s41591-022-01894-0 | 1, 3 |
| TREWS provider-adoption factors and effect on sepsis treatment (Nat Med 2022) | 35864251 · 10.1038/s41591-022-01895-z | 1, 8 |
| External validation of a widely-implemented proprietary sepsis model (Epic) (JAMA Intern Med 2021) | 34152373 · 10.1001/jamainternmed.2021.2626 | 1, 2, 3, 4, 6 |
| Editorial: the Epic Sepsis Model falls short — importance of external validation (JAMA Intern Med 2021) | 34152360 · 10.1001/jamainternmed.2021.3333 | 1 |
| Multicenter prospective validation of an updated proprietary sepsis model (JAMA Netw Open 2026) | 41758510 · 10.1001/jamanetworkopen.2026.0181 | 1, 3 |
| Simulated-prospective evaluation of a deep-learning real-time deterioration model on wards (Crit Care Med 2021) | 33711001 · 10.1097/CCM.0000000000004966 | 1 |
| Machine learning for prediction of sepsis: systematic review & meta-analysis (Fleuren, Intensive Care Med 2020) | 31965266 · 10.1007/s00134-019-05872-y | 2, 3, 4, 5, 6 |
| Early prediction of sepsis in the ICU using ML: systematic review (Moor, Front Med 2021) | 34124082 · 10.3389/fmed.2021.607952 | 2, 3, 4, 5, 6 |
| COMPOSER deep-learning sepsis model: impact on quality of care and survival (npj Digit Med 2024) | 38263386 · 10.1038/s41746-023-00986-6 | 1, 3, 8 |
| COMPOSER sepsis model that abstains ("I don't know") (npj Digit Med 2021) | 34504260 · 10.1038/s41746-021-00504-6 | 2 |
| Real-time ML-assisted sepsis alert improves antibiotic-administration timeliness (Intern Emerg Med 2024) | 38381351 · 10.1007/s11739-024-03535-5 | 3, 8 |
| Unsupervised characterization of temporal dataset shift as early indicator of AI degradation (JMIR Med Inform 2025) | 41337748 · 10.2196/78309 | 2, 8 |
| TRIPOD+AI: updated reporting guidance for clinical prediction models using AI (BMJ 2024) | 38626948 · 10.1136/bmj-2023-078378 | 1, 5, 6 |
| DECIDE-AI: reporting guideline for early-stage clinical evaluation of decision-support AI (Nat Med 2022) | 35585198 · 10.1038/s41591-022-01772-9 | 1 |
| DECIDE-AI (BMJ version) | 35584845 · 10.1136/bmj-2022-070904 | 1 |

### FDA regulatory records (resolved this session via openFDA)

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| Device classification: "Software Device To Aid In The Prediction Or Diagnosis Of Sepsis", Class II, 21 CFR 880.6316, General Hospital | Product code **SAK** | 2, 3, 4, 7, 8 |
| De Novo that created product code SAK — *Sepsis ImmunoScore* (Prenosis, Inc.), granted 2024-04-02 (biomarker + clinical inputs; classification-defining, not a pure-EHR predicate) | **DEN230036** | 3, 7 |
| 510(k) clearance — *Bayesian Health Sepsis Flagging Device* (Bayesian Health, Inc.), Substantially Equivalent, 2026-04-30 (EHR-based; candidate predicate) | **K250680** | 7 |

*(Related sepsis product codes retrieved but NOT applicable — they cover in-vitro/biomarker assays, not EHR-only algorithms: QFS (Monocyte Distribution Width), NTM (inflammatory-marker antigen assay), SCX (host-biomarker immunoassay), QUT (deformability cytometry). Listed for completeness; not cited as grounding for an EHR-time-series device.)*

### Trial registry use (ClinicalTrials.gov v2 API, searched this session)

- Searches for *"sepsis prediction machine learning alert"*, *"sepsis early warning algorithm randomized"*, and *"sepsis clinical decision support electronic health record"* informed **Field 1 (Study Design)** and **Field 5 (Sample Size)** — establishing that both interventional and observational designs are registered and bracketing realistic enrollment.
- Enrollment figures cited in Field 5 come from these records [retrieved-from-source]: **NCT02376842** (EHR-embedded severe-sepsis EWS, interventional, n≈1,149); **NCT03235193** (PREVENT sepsis algorithm, n≈2,296); **NCT05065333** (predictive-modeling implementation trial, n≈1,345); **NCT04570618** (Early Prediction of Sepsis, n≈320); **NCT04005001** (ML sepsis alert using clinical data, n≈37,986). A "TREWS sepsis" query returned no registry records this session (registry coverage gap, not a claim that no such trial exists).

### Expected conclusions

- **Regulatory class/pathway:** FDA **Class II** software, **21 CFR 880.6316**, product code **SAK**. A pure-EHR sepsis prediction/diagnosis-aid device has an available **510(k)** route with a verified predicate (**K250680**, cleared 2026-04-30); De Novo (**DEN230036**, 2024-04-02) created the classification but its granted device is biomarker-inclusive.
- **Regulatory NULL result:** No PMA (premarket approval) pathway applies — this is not a Class III device; no PMA number exists or was found for this device type. The FDA has **not** published a fixed numeric performance threshold (minimum AUROC/sensitivity) that such a device must meet; authorization rests on special controls plus clinical/analytical validation.
- **Established numeric benchmark:** **None exists** as a retrieved standard. All specific performance targets and sample sizes in this spec are **[study-defined-placeholder]** and must be pre-registered by the sponsor.

### Sources I wanted but could not access (coverage gaps)

- **Drugs@FDA / drug labeling:** Not applicable to this device (no drug or biologic product); not queried. Stated explicitly per grounding rules — this is a scope exclusion, not an access failure.
- **Full 510(k) summary / De Novo decision-summary PDFs:** openFDA returns structured metadata for DEN230036 and K250680 but not the narrative decision summaries or the specific special-controls text and clinical-study design of each authorization; the detailed special controls and any device-specific performance data in those summaries were **not** retrievable through the openFDA JSON endpoints this session.
- **FDA device classification special-controls full text (21 CFR 880.6316 subpart):** the openFDA classification `definition` field was retrieved; the codified special-controls list was not available through the API and would need the eCFR/CFR text.
- **NCBI rate-limiting:** PubMed E-utilities returned HTTP 429 intermittently (no contact-email/API-key was available this session); queries were completed with backoff, but this constrained the breadth of literature retrieval.
- **Vendor technical dossiers / peer-reviewed head-to-head EHR-only algorithm comparisons** beyond those cited: not systematically retrievable through the open databases available here.
