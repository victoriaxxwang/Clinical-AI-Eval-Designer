# Clinical AI Validation Specification — Reference Answer Key

**System under evaluation:** An AI algorithm that analyzes color retinal fundus photographs to detect referable (more-than-mild) diabetic retinopathy (mtmDR) in adults with diabetes, deployed as an autonomous / point-of-care screening tool in primary-care and non-ophthalmology settings. Input: non-mydriatic fundus images with an image-quality/gradeability gate. Population: adults with type 1 or type 2 diabetes, across skin tones and camera models.

**Grounding statement.** Every identifier below was retrieved and resolved live this session: PMIDs against NCBI E-utilities/PubMed, DOIs against Crossref, FDA product code / K-number / DEN-number against openFDA (device classification and 510(k)/De Novo endpoints), and NCT numbers against the ClinicalTrials.gov v2 API. Numbers are labeled **[retrieved-from-source]** when copied from a resolved record, and **[study-defined-placeholder]** when they are a value an evaluator must set for their own protocol. No identifier appears here that did not resolve this session.

> *Independent verification (Clinical-AI-Eval-Designer, 2026-07-09): all 5 PMIDs re-resolved via E-utils and all 5 DOIs via Crossref with matching titles; FDA codes and NCTs confirmed against the raw openFDA / ClinicalTrials.gov v2 responses saved with this case. Answer key: `golden_expected_ids_DR.json`.*

---

## 1. Study Design

**Recommendation.** Validate on a **prospective, multicenter, non-interventional (diagnostic-accuracy) trial** in the intended-use setting (primary care / non-ophthalmology), enrolling adults with diabetes and *no prior diagnosis of the target condition in that eye*, with images acquired by the intended non-specialist operators after a standardized operator-training protocol, and each subject's index test (AI on non-mydriatic fundus photos) compared against a pre-registered reference standard read independently and masked. Pre-specify superiority (or non-inferiority) endpoints for sensitivity and specificity before enrollment.

**Rationale.** This is the design of the pivotal trial that supported the first FDA authorization of an autonomous AI diagnostic in this class: a prospective study of 900 subjects with no history of DR, enrolled at primary-care clinics, operators trained on a standardized protocol, index test compared to a reading-center reference standard, with pre-specified superiority endpoints (PMID 31304320; DOI 10.1038/s41746-018-0040-6; ClinicalTrials.gov NCT02963441). The second device in this class used the same architecture — a prospective, pivotal, multicenter trial of 893 completing subjects / 1786 eyes (PMID 34779843; DOI 10.1001/jamanetworkopen.2021.34254; NCT03112005). Randomized interventional designs are appropriate for *deployment/effectiveness* endpoints (screening uptake, follow-up completion) rather than diagnostic accuracy — see the ACCESS RCT (PMID 38212308; DOI 10.1038/s41467-023-44676-z; NCT05131451).

**Confidence.** HIGH.

**Expert review needed.** Biostatistician to fix the endpoint framing (superiority vs non-inferiority and the comparator); trialist/IRB to confirm the enrollment restriction (no prior target-condition diagnosis) and the operator-training protocol.

---

## 2. Input / Signal Validation

*The pre-condition: does the input measurement (here, the fundus image) meet a gradeability/quality standard before the algorithm's output is interpreted?*

**Recommendation.** Require an **explicit image-quality / gradeability gate** as part of the device, and report **imageability rate** (fraction of subjects/eyes yielding an interpretable AI output against reference-gradable images) as a primary operating characteristic alongside sensitivity/specificity. Pre-specify the protocol for ungradable images (e.g., repeat capture, pharmacologic dilation, or referral). Separately, qualify each **camera model** as an input source rather than assuming transportability.

**Rationale.** Imageability is treated as a headline endpoint in the pivotal literature. IDx-DR reported an imageability rate of **96.1% (95% CI 94.6–97.3%)** [retrieved-from-source] (PMID 31304320). EyeArt reported imageability of **87.4% (95% CI 85.2–89.6%) without dilation, improving to 97.4% (95% CI 96.4–98.5%) when ungradable eyes were dilated per protocol** [retrieved-from-source] (PMID 34779843) — direct evidence that the ungradable-image pathway materially changes the input-validation result and must be pre-specified. Camera-model dependence is handled as a distinct regulatory activity: a dedicated camera-qualification study exists (ClinicalTrials.gov NCT05808699, "Camera Qualification of an Additional Fundus Camera Paired With An Autonomous AI"), and real-world integration is reported for a specific camera (Topcon NW500) with a named device (AEYE-DS) (PMID 42373309; DOI 10.1136/bjo-2025-328991).

**Confidence.** HIGH (that a gradeability gate and imageability reporting are required); MEDIUM (on the exact ungradable-image handling, which is protocol-specific).

**Expert review needed.** Retinal imaging specialist to define gradeability criteria and the per-camera qualification protocol; the specific imageability threshold to *require* is a **[study-defined-placeholder]**.

---

## 3. Performance Benchmarks

**Recommendation.** Report **sensitivity and specificity for mtmDR** (and, if claimed, vision-threatening DR) with two-sided 95% confidence intervals, against pre-specified endpoints set *before* enrollment. Do not treat any single sensitivity/specificity pair as a universal pass mark; state the source of every target.

**Rationale.** The FDA-authorizing IDx-DR pivotal pre-specified **superiority endpoints of sensitivity > 85% and specificity > 82.5%** [retrieved-from-source: these are the pivotal trial's pre-specified thresholds, PMID 31304320], and reported achieved **sensitivity 87.2% (95% CI 81.8–91.2%)** and **specificity 90.7% (95% CI 88.3–92.7%)** [retrieved-from-source] (PMID 31304320). The EyeArt pivotal reported **mtmDR sensitivity 95.5% (95% CI 92.4–98.5%) and specificity 85.0% (95% CI 82.6–87.4%)**, and **vtDR sensitivity 95.1% and specificity 89.0%**, without dilation [retrieved-from-source] (PMID 34779843). A subgroup/comparator analysis reported the EyeArt system at **sensitivity 97% / specificity 88%** for mtmDR versus clinicians in the same eyes [retrieved-from-source] (PMID 36345378; DOI 10.1016/j.xops.2022.100228).

> **Benchmark caveat (per grounding rules).** The 85% / 82.5% pair is the *pre-specified endpoint of one pivotal trial* accepted in that device's authorization — it is **not** a codified, device-class-wide regulatory threshold. No universal numeric performance standard for this device class was retrieved this session. Evaluators should record their own targets as **[study-defined-placeholder]** and cite the pivotal values only as precedent.

**Confidence.** HIGH (on which metrics and CIs to report); MEDIUM (on any specific numeric target, because it is precedent, not a mandated standard).

**Expert review needed.** Biostatistician to set and justify the endpoint values and the CI/alpha framework for the specific claim.

---

## 4. Ground Truth Strategy

**Recommendation.** Use an **independent, masked reading-center reference standard** based on a recognized DR severity scale (ETDRS), with a pre-specified case definition of the target condition, and grade macular edema explicitly. The reference imaging protocol should exceed the index test (e.g., widefield stereoscopic photography ± OCT) rather than reuse the same single-field non-mydriatic images.

**Rationale.** The IDx-DR pivotal used the **Wisconsin Fundus Photograph Reading Center**, widefield stereoscopic photography plus macular OCT, with **ETDRS** grading, and defined mtmDR as **ETDRS level ≥ 35 and/or diabetic macular edema in at least one eye** [retrieved-from-source] (PMID 31304320). The EyeArt pivotal used a reading-center reference standard on 4-widefield stereoscopic dilated fundus photographs graded on the ETDRS severity scale (PMID 34779843), and the subgroup study benchmarked against reading-center grading of 4-widefield stereoscopic photographs and clinician dilated exams (PMID 36345378).

**Confidence.** HIGH.

**Expert review needed.** Reading-center director / retina grader to lock the grading protocol, adjudication of discordant reads, and the exact mtmDR/DME case definition.

---

## 5. Sample Size

**Recommendation.** Power the study to bound the 95% CI on **both** sensitivity and specificity for mtmDR, accounting for the prevalence of the target condition (which drives the number of true-positive cases) and for image-ungradable dropout. Report consented, completed, and analyzed counts separately.

**Rationale.** Enrollment in the two class-defining pivotal trials, retrieved from ClinicalTrials.gov: **900 subjects, actual** (NCT02963441; IDx-DR pivotal, with 198 (23.8%) having mtmDR, PMID 31304320) and **942 consenting → 893 completed / 1786 eyes** (NCT03112005; EyeArt pivotal, PMID 34779843). For deployment/uptake endpoints the ACCESS RCT enrolled **164 youth, actual** (NCT05131451; PMID 38212308). These are precedent enrollment sizes — the exact target N for a new evaluation is a **[study-defined-placeholder]** derived from the powering assumptions above.

**Confidence.** HIGH (that CI-width powering on both operating characteristics + prevalence is the right basis); the specific N is a **[study-defined-placeholder]**.

**Expert review needed.** Biostatistician for the formal power calculation and the prevalence/dropout assumptions.

---

## 6. Subgroup Requirements

**Recommendation.** Pre-specify subgroup analyses by **skin tone / race-ethnicity, diabetes type, age, sex, and camera model**, and enroll to permit them. Report operating characteristics (or at least imageability and referral rates) per subgroup, and treat camera model as a required subgroup because it is the input device.

**Rationale.** The pivotal trials reported demographic composition supporting subgroup reporting: IDx-DR reported **28.6% African American and 16.1% Hispanic** participants, 47.5% male, median age 59 (range 22–84) [retrieved-from-source] (PMID 31304320); EyeArt reported **73.3% White, 23.1% type 1 diabetes**, 50.3% men, mean age 53.9 (range 18–88) [retrieved-from-source] (PMID 34779843). A dedicated subgroup comparison of the EyeArt system versus clinicians was published (PMID 36345378). The ACCESS RCT was designed specifically to test performance in a **racially and ethnically diverse youth population** with type 1 and type 2 diabetes (PMID 38212308). Camera-model as a subgroup/qualification requirement is supported by the existence of a camera-qualification study (NCT05808699) and real-world evaluation tied to a specific camera (PMID 42373309).

**Confidence.** MEDIUM–HIGH. The *dimensions* to stratify are well-grounded; the enrollment quotas needed to power each subgroup are **[study-defined-placeholder]**.

**Expert review needed.** Health-equity / bias reviewer and biostatistician to set minimum subgroup cell sizes; note that no retrieved source this session established a *required* per-skin-tone accuracy floor.

---

## 7. Regulatory Pathway

**Recommendation.** In the U.S., this device type is **FDA Class II** under product code **PIB**, regulation **21 CFR 886.1100** ("Retinal diagnostic software device" / "Diabetic Retinopathy Detection Device," Ophthalmic panel). The classification was established by a **De Novo** request; subsequent devices clear via **510(k)** with a PIB predicate. A new entrant should plan for a 510(k) against a PIB predicate unless it lacks a suitable predicate (then De Novo).

**Rationale (all retrieved from openFDA this session).**
- Product code **PIB** resolves in the openFDA device-classification endpoint: device name "Diabetic Retinopathy Detection Device," **device class 2**, regulation number **886.1100**, Ophthalmic specialty.
- **DEN180001** (De Novo, "IDx-DR," Idx LLC, decision 2018-04-11, clearance type *Direct De Novo*, product code PIB) — the classification-establishing authorization.
- 510(k) clearances under PIB retrieved this session: **K200667** (EyeArt, Eyenuk, 2020-08-03), **K223357** (EyeArt v2.2.0, 2023-06-16), **K203629** (IDx-DR, Digital Diagnostics, 2021-06-10), **K213037** (IDx-DR v2.3, 2022-06-17), **K221183** (AEYE-DS, Aeye Health, 2022-11-10), **K240058** (AEYE-DS, 2024-04-23).

**Confidence.** HIGH.

**Expert review needed.** Regulatory-affairs specialist to confirm predicate selection and whether the specific claim (autonomous point-of-care use, camera set, population) is within the PIB indication or requires additional data.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Establish ongoing surveillance of **real-world imageability/gradeability, referral rates, and follow-through**, stratified by site, operator, camera model, and subgroup; monitor for input drift (new cameras, new operator populations) and for changes in the referable-case mix; and capture downstream eye-care follow-up completion as an outcome. Re-qualify on any new camera before clinical use.

**Rationale.** Real-world integration studies define the monitorable quantities: a real-world integration of AEYE-DS on the Topcon NW500 in an endocrinology clinic, with images taken by a novice non-ophthalmic operator, reports the deployment-setting metrics that a monitoring program should track (PMID 42373309; DOI 10.1136/bjo-2025-328991). The ACCESS RCT measured **diabetic eye-exam completion (100% intervention vs 22% control) and follow-through with an eye-care provider** [retrieved-from-source] (PMID 38212308; NCT05131451) — the downstream-outcome signals a monitoring program should sustain. Camera re-qualification as an ongoing obligation is evidenced by the dedicated camera-qualification study (NCT05808699).

**Confidence.** MEDIUM. The metrics are well-grounded; no retrieved source this session specified a mandated post-market surveillance cadence or thresholds for this class, so alerting thresholds are **[study-defined-placeholder]**.

**Expert review needed.** Quality/safety lead and regulatory-affairs specialist to define surveillance cadence, drift-detection thresholds, and the camera re-qualification trigger.

---

# SOURCE INVENTORY

## Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| IDx-DR pivotal trial: autonomous AI for mtmDR in primary care, N=900, reading-center reference standard, pre-specified superiority endpoints | PMID 31304320 · DOI 10.1038/s41746-018-0040-6 | 1 Study Design; 2 Input/Signal; 3 Performance; 4 Ground Truth; 5 Sample Size; 6 Subgroup; 7 Regulatory |
| EyeArt pivotal evaluation: autonomous detection of referable and vision-threatening DR, N=893 completed / 1786 eyes | PMID 34779843 · DOI 10.1001/jamanetworkopen.2021.34254 | 1 Study Design; 2 Input/Signal; 3 Performance; 4 Ground Truth; 5 Sample Size; 6 Subgroup |
| EyeArt subgroup comparison vs ophthalmologists' dilated exams, 521 participants / 999 eyes | PMID 36345378 · DOI 10.1016/j.xops.2022.100228 | 3 Performance; 4 Ground Truth; 6 Subgroup |
| ACCESS randomized controlled trial: autonomous AI increases screening/follow-up in youth | PMID 38212308 · DOI 10.1038/s41467-023-44676-z | 1 Study Design; 5 Sample Size; 6 Subgroup; 8 Post-Deployment |
| Real-world integration of an autonomous AI (AEYE-DS) with Topcon NW500 in an endocrinology clinic | PMID 42373309 · DOI 10.1136/bjo-2025-328991 | 2 Input/Signal; 8 Post-Deployment |

## FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| Device classification: "Diabetic Retinopathy Detection Device," Class II, 21 CFR 886.1100, Ophthalmic | Product code **PIB** | 7 Regulatory |
| De Novo authorization — IDx-DR (Idx LLC, 2018-04-11, Direct De Novo) — classification-establishing | **DEN180001** | 7 Regulatory; 1 Study Design |
| 510(k) — EyeArt (Eyenuk, 2020-08-03) | **K200667** | 7 Regulatory |
| 510(k) — EyeArt v2.2.0 (Eyenuk, 2023-06-16) | **K223357** | 7 Regulatory |
| 510(k) — IDx-DR (Digital Diagnostics, 2021-06-10) | **K203629** | 7 Regulatory |
| 510(k) — IDx-DR v2.3 (Digital Diagnostics, 2022-06-17) | **K213037** | 7 Regulatory |
| 510(k) — AEYE-DS (Aeye Health, 2022-11-10) | **K221183** | 7 Regulatory |
| 510(k) — AEYE-DS (Aeye Health, 2024-04-23) | **K240058** | 7 Regulatory |

*(No PMA number is listed because this device class is Class II — see Expected conclusions.)*

## Trial registry use (ClinicalTrials.gov)

All NCT records below were resolved this session against the ClinicalTrials.gov v2 API; enrollment counts are the registry's "actual" values.

- **NCT02963441** (IDx-DR pivotal; observational; enrollment 900, actual; completed) — informed **Study Design (1)**, **Sample Size (5)**, and cross-checked against PMID 31304320.
- **NCT03112005** (EyeArt pivotal, "Assessment of EyeArt as an Automated Diabetic Retinopathy Screening Tool"; observational; enrollment 942, actual; completed) — informed **Study Design (1)** and **Sample Size (5)**; matches the 942-consenting figure in PMID 34779843.
- **NCT05131451** (ACCESS, pediatric autonomous-AI RCT; interventional; enrollment 164, actual; completed) — informed **Study Design (1)**, **Sample Size (5)**, **Subgroup (6)**, and **Post-Deployment (8)**; matches PMID 38212308.
- **NCT05808699** ("Camera Qualification of an Additional Fundus Camera Paired With An Autonomous AI"; observational; enrollment 626, actual) — informed **Input/Signal Validation (2)**, **Subgroup (6, camera model)**, and **Post-Deployment (8, camera re-qualification)**.

## Expected conclusions

- **Regulatory class / pathway:** U.S. **FDA Class II**, product code **PIB**, regulation **21 CFR 886.1100**. Classification was established by **De Novo (DEN180001)**; current market entrants clear via **510(k)** against a PIB predicate (verified 510(k)s: K200667, K223357, K203629, K213037, K221183, K240058).
- **Regulatory NULL results:** **No PMA (Class III) authorization exists for this device type** — it is Class II, so no PMA number is applicable. No separately FDA-authorized standalone "image-quality gate" device was found distinct from the integrated autonomous screening systems; the gradeability gate is a component of the cleared devices, not its own record.
- **Established numeric benchmark:** **No universal, device-class-wide numeric performance standard was retrieved this session.** A concrete, source-retrieved *precedent* exists — the IDx-DR pivotal's pre-specified endpoints of **sensitivity > 85% and specificity > 82.5%** (PMID 31304320) — but this is a single trial's accepted endpoint, not a codified threshold binding all such devices. Any target used for a new evaluation should be labeled study-defined and justified by its own power/claim analysis.

## Sources I wanted but could not access (coverage gaps)

- **FDA De Novo decision summary / 510(k) Summary full-text PDFs.** openFDA returns the structured record (K/DEN number, dates, product code, applicant) but not the narrative decision summaries that would give the FDA-accepted operating-point and the exact indications wording. Those live on accessdata.fda.gov, which was not queried/accessible this session — the specific FDA-accepted acceptance criteria could not be read verbatim.
- **A verified per-skin-tone accuracy floor.** No retrieved source this session established a *required* minimum sensitivity/specificity stratified by skin tone; the subgroup requirement is grounded in demographic reporting and study design, not in a numeric equity threshold. This gap is flagged for expert review (Field 6).
- **Post-market surveillance cadence / drift thresholds for this device class.** No retrieved source specified a mandated monitoring frequency or alerting threshold; Field 8 thresholds remain study-defined placeholders.
- **Drugs@FDA / drug labeling** was **not applicable** — the system under evaluation is a software-as-a-medical-device diagnostic, not a drug or biologic, so no NDA/BLA/labeling record was sought.

---

*Verification log (Claude Science session): 5 PMIDs resolved in PubMed and their DOIs in Crossref; 1 product code + 7 K/DEN numbers resolved in openFDA (classification + 510(k)/De Novo endpoints); 4 NCT numbers resolved in the ClinicalTrials.gov v2 API. Independently re-verified 2026-07-09 by Clinical-AI-Eval-Designer. Every identifier in this document resolved live.*
