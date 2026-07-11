# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ web search where noted)

## Inputs
- **AI model:** EfficientNet-B4 ordinal-regression classifier on macula-centered color fundus photographs (456×456, CLAHE + circular FOV crop), with test-time augmentation, attention-gated lesion evidence maps (microaneurysms, hemorrhages, hard exudates), and an upstream quality-assessment gating sub-network that rejects ungradable images. Outputs a 5-level severity grade.
- **Clinical use case:** Automated grading of fundus photos on a 5-point DR severity scale, flagging cases at/above the referral threshold for specialist review.
- **Patient population:** Adults with diabetes mellitus in routine annual eye screening.
- **Healthcare setting:** Primary-care and community optometry screening with tele-ophthalmology review.
- **Intended clinical claim (INFERRED — team to confirm):** *"In adults with diabetes undergoing routine screening, this software identifies referable diabetic retinopathy (moderate NPDR or worse, and/or DME) from macula-centered fundus photographs, flagging cases for specialist referral, with a gradeable-image rate and sensitivity/specificity adequate to serve as an assistive triage tool under tele-ophthalmology review."* I assume an **assistive/triage** claim under human tele-ophthalmology review, NOT an autonomous diagnostic device, because the deployment context specifies tele-ophthalmology review. If the team wants an autonomous claim (no clinician in the loop), the regulatory bar and study design change materially — flag this now.

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Prospective, multi-site, masked comparison of model output vs. reference reading-center grading on consecutively enrolled screening patients; De Novo/PMA-style precedent exists for autonomous DR AI. |
| 2. Sensor / Input Validation | Camera/vendor generalization + quality-gate performance are pre-conditions; note MAUDE/recall signals on fundus imaging (laterality mislabel, ungradable capture). |
| 3. Performance Benchmarks | No regulatory threshold retrieved; literature benchmarks (DeepDRiD, DKD, DR-grading papers) exist but are not FDA standards — team/experts must pre-specify. |
| 4. Ground Truth | Multi-grader reading-center consensus against an ETDRS-based scale; label noise caps achievable sensitivity/specificity. |
| 5. Sample Size | No retrieved study fixes N for THIS model; must be powered on pre-specified sensitivity/specificity lower bounds — expert biostatistician required. |
| 6. Subgroups | Skin/fundus pigmentation, camera vendor, image quality strata, diabetes type/duration, DME co-presence pre-specified. |
| 7. Regulatory Pathway | Likely FDA De Novo/Class II (autonomous DR AI precedent exists) or 510(k) if predicate claimed; retrieved codes (HJI) are hardware lenses/cameras, NOT the software predicate — regulatory counsel required. |
| 8. Post-Deployment Monitoring | Track gradeable rate, referral rate drift, camera-fleet changes, missed-referral audit; MAUDE laterality/recall signals inform failure modes. |

---

## 1. Study Design
**Recommendation:** Run a **prospective, multi-site, reader-masked diagnostic-accuracy study** enrolling consecutive adults with diabetes at primary-care/community optometry screening sites. Freeze the model (locked algorithm) before enrollment. Each patient's macula-centered fundus images are (a) scored by the device and (b) independently graded by a masked reading center; compute sensitivity/specificity for "referable DR" against that reference, plus the gradeable-image rate as a co-primary operating characteristic. Pre-specify the referral threshold on the 5-level scale before unblinding. Include the full screening workflow (capture → quality gate → grade → tele-ophthalmology review) so the study reflects deployment, not a curated image set.

**Rationale:** Autonomous/assistive DR detection from fundus photos is an established regulatory and clinical category, and the literature retrieved is dominated by DR-grading model development on screening populations (PMID 35755875 DeepDRiD grading + image-quality challenge; PMID 42078464 calibration-focused DR grading benchmark; PMID 42346900 fundus-OCT fusion for DR/DME; PMID 42076618, PMID 38239623, PMID 41704302 DR grading/subtype methods). Critically, almost all retrieved literature is **retrospective model-development work on image archives**, not prospective screening-workflow validation — this is exactly the evidence gap your study must close. A prospective consecutive-enrollment design is required to estimate real-world gradeable rate and to avoid spectrum bias from curated datasets. No matching ClinicalTrials.gov record for THIS device was retrieved, so I cannot cite a directly analogous registered trial design — treat this as a gap to confirm against a manual ClinicalTrials.gov search.

**Confidence:** MEDIUM — design is well-grounded in established DR-screening validation practice and the retrieved development literature, but no prospective trial for this exact model was retrieved.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Before any accuracy claim, validate (1) **camera/vendor/resolution generalization** — the device must be tested on every fundus camera model and capture protocol used across the deployment fleet, not just the training camera; (2) **the quality-assessment gating sub-network** as a standalone classifier — report its gradeable/ungradable operating point, and critically report accuracy *conditioned on images the gate passes* AND the fraction gated out, because a gate that discards hard cases inflates apparent accuracy; (3) **preprocessing robustness** — CLAHE and circular-crop behavior must be stable across illumination, media opacity (cataract), and small pupils common in undilated community screening. Establish these as pass/fail pre-conditions.

**Rationale:** The retrieved post-market signals are concrete input-integrity failure modes for fundus imaging: a NIDEK fundus-camera image-filing software **recall for saving the left-eye image as the right eye** (recall Z-2046-2013, Class II) — a laterality/labeling failure that would silently corrupt per-eye grading; and MAUDE injury reports on fundus diagnostic hardware (report MW5105451, product code HJI; report 2955842-2022-15143). The DeepDRiD challenge explicitly paired grading with **image-quality estimation** (PMID 35755875), confirming that quality gating is treated as integral, not optional, in this field. Because the model consumes sensor/image data, measurement validity is a gating pre-condition, not a footnote: a device validated on one camera does not transfer to another without evidence.

**Confidence:** MEDIUM — camera-shift and quality-gate threats are well established and supported by retrieved recall/challenge records; exact fleet composition for this deployment is unknown.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 3. Performance Benchmarks
**Recommendation:** Pre-specify, with clinical experts, the **minimum acceptable sensitivity and specificity for referable DR** and a **maximum acceptable ungradable rate** BEFORE the study. Do NOT adopt any number from a development paper as a pass threshold. Report sensitivity, specificity, PPV/NPV at the screening prevalence, per-grade confusion matrix, quadratic-weighted kappa vs. reference, and calibration of the ordinal output.

**Rationale:** **No regulatory performance threshold was retrieved** for this device class in the grounded context — treat any specific target as "no established benchmark retrieved — must be set by the study team / expert." The retrieved literature reports strong development-set metrics for DR grading (e.g., PMID 35755875 DeepDRiD; PMID 42078464 calibration benchmark for DR grading; PMID 42076618; PMID 38165976 vision-threatening DR), but these are (a) non-regulatory, (b) largely retrospective, and (c) not measured in your population/workflow, so they are context only, not acceptance criteria. Calibration deserves explicit attention: PMID 42078464 specifically flags that frozen foundation models transfer with calibration problems in DR grading — a mis-calibrated ordinal output will mis-place the referral threshold.

**Confidence:** LOW — no regulatory benchmark retrieved; literature values are not applicable as pass/fail thresholds.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 4. Ground Truth Strategy
**Recommendation:** Use a **masked, multi-reader reading-center consensus** grade on a standardized DR severity scale (ETDRS-based / ICDR 5-level), with adjudication of disagreements by a senior grader, as the reference standard for "referable DR." Pre-define referable = moderate NPDR or worse and/or DME. Report inter-grader agreement (kappa); where feasible on a subset, anchor against a higher standard (e.g., OCT for DME, or wider-field/dilated imaging) to bound reference error.

**Rationale:** DR grading reference standards are inherently noisy — inter-grader variability on the 5-level scale is well documented, and the retrieved work repeatedly builds around graded fundus datasets and OCT fusion for DME (PMID 42346900 fundus-OCT fusion; PMID 41590921 OCT-to-fundus translation). **Label reliability is a ceiling:** if reading-center kappa is moderate, the device's achievable measured sensitivity/specificity is capped by reference-standard disagreement, and this must be stated in the report. DME detection from single fundus photos is a particular weakness — DME is often defined on OCT, so a fundus-only reference will misclassify some DME; anchor a subset against OCT to quantify this.

**Confidence:** MEDIUM — reading-center methodology is standard practice and supported by the retrieved DR/DME literature; exact grader panel and scale to be fixed by experts.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 5. Sample Size
**Recommendation:** Power the study on the **lower confidence bound of sensitivity and specificity** for referable DR at the expected screening prevalence, with enough referable-positive cases to bound sensitivity precisely (the rarer endpoint drives N). Enroll consecutively so prevalence is representative, and inflate for the expected ungradable fraction (removed by the quality gate). A biostatistician must compute N once the pre-specified sensitivity/specificity targets and expected prevalence are fixed.

**Rationale:** **No retrieved record fixes a sample size for THIS model or a directly analogous prospective trial** — I will not invent one. Retrieved literature reports development/validation cohort sizes that are not transferable as targets. The binding constraint is the number of true referable cases (prevalence-limited), not total enrollment; this is why consecutive prospective enrollment plus prevalence estimation must precede the N calculation.

**Confidence:** LOW — no sample-size precedent retrieved; entirely dependent on expert-set targets.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 6. Subgroup Requirements
**Recommendation:** Pre-specify subgroup analyses (not post-hoc) with adequate cases per stratum for: (1) **fundus/retinal pigmentation and race/ethnicity** — pigmentation alters image contrast and lesion visibility, the physiological analogue of the skin-tone threat in optical devices; (2) **camera vendor/model and resolution** — the concrete generalization threat for imaging AI; (3) **image-quality strata** (borderline-gradeable vs. clearly gradeable) — to detect whether accuracy collapses near the gate boundary; (4) **DME present vs. absent** (fundus-only detection weakness); (5) **diabetes type and duration**; (6) **media opacity / cataract / small pupil** common in older undilated screening. Report operating characteristics per subgroup, not just pooled.

**Rationale:** Population-specific validity threats for fundus AI are physics/physiology, not optics polish: retinal pigmentation and camera-vendor domain shift directly change pixel statistics that EfficientNet features depend on. The retrieved literature treats image quality as a first-class variable (PMID 35755875 pairs grading with quality estimation), and calibration/transfer degradation across data sources is documented (PMID 42078464). The NIDEK laterality recall (Z-2046-2013) also motivates per-eye reporting within subgroups. No retrieved record provides subgroup performance for this model — these must be generated.

**Confidence:** MEDIUM — subgroup threats are well supported by imaging-AI evidence and retrieved records; exact strata and minimum cell sizes need expert input.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 7. Regulatory Pathway
**Recommendation:** Engage regulatory counsel to determine pathway. The most likely US route for software that outputs a DR severity grade / referral flag is a **device pathway (De Novo → Class II with special controls, or 510(k) if a legitimate software predicate is claimed)** — the intended-use decision hinges on whether the claim is **assistive (clinician-in-the-loop tele-ophthalmology review)** or **autonomous**. An autonomous diagnostic claim raises the evidentiary bar substantially. Do NOT finalize any claims language until counsel confirms.

**Rationale:** The retrieved openFDA device records are **not** valid software predicates: product code **HJI (Lens, Fundus, Hruby, Diagnostic, Class 1, reg 886.1395)** and the 510(k)s **K864304** (fundus laser lens) and **K901839** (Canon fundus camera) are all **imaging hardware**, not AI grading software. The "primary/community" hits (JIS calibrator, K093746 knee system, K971293 IV set, K951771 balance monitor, K252637 containers) are irrelevant keyword matches — flag these explicitly as non-applicable. No software DR-detection predicate (e.g., the known autonomous DR AI De Novo class) was returned in this retrieval; that does not mean none exists — autonomous DR screening software has been FDA-authorized, and the correct predicate/De Novo precedent must be identified via a manual FDA database search. The pipeline also did NOT query Drugs@FDA/SPL/FAERS or non-US regulators (EMA/MHRA/PMDA) per the coverage note, so any ex-US strategy is out of scope here.

**Confidence:** LOW — no on-point software predicate was retrieved; retrieved device codes are hardware, not the correct class.
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized.

## 8. Post-Deployment Monitoring
**Recommendation:** Institute continuous monitoring of: (1) **gradeable/ungradable rate** per site and per camera — a rising ungradable rate signals capture or hardware drift; (2) **referral-rate drift** vs. baseline; (3) **camera-fleet change control** — any new camera model triggers re-validation before use; (4) **missed-referral audit** — periodic reading-center re-grading of a sample, especially of device-negative cases, to catch false negatives; (5) **per-eye laterality integrity checks** given the documented mislabel failure mode; (6) calibration drift of the ordinal output. Establish MAUDE reporting procedures for patient-harm events.

**Rationale:** Retrieved post-market signals define concrete real-world failure modes: the NIDEK fundus-camera software **left/right eye mislabel recall (Z-2046-2013)** shows silent laterality corruption is a real event in this workflow, and MAUDE injury reports on fundus diagnostic hardware (MW5105451, code HJI; 2955842-2022-15143) confirm ongoing device-safety reporting. These are **safety/failure-mode signals, not efficacy evidence.** Because deployment spans multiple community sites and cameras, domain shift over time is the dominant post-market risk — the same generalization threat from Field 2, now monitored longitudinally.

**Confidence:** MEDIUM — failure modes are grounded in retrieved recall/MAUDE records; specific monitoring thresholds must be set by the team.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

---

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** That, under the study's specified conditions, a passing result would establish that this locked EfficientNet-B4 grading software identifies referable diabetic retinopathy (moderate NPDR or worse and/or DME) from macula-centered fundus photographs in adults screened in primary-care/community optometry with tele-ophthalmology review, meeting pre-specified sensitivity, specificity, and gradeable-rate targets against a masked reading-center reference, across the tested camera fleet and pre-specified subgroups.

**DOES NOT CERTIFY:**
- Standalone/autonomous diagnosis without tele-ophthalmology review (unless the study is explicitly designed and powered for that claim).
- Accuracy on camera models, resolutions, or capture protocols not included in the study.
- Detection of ocular disease beyond referable DR (e.g., glaucoma, AMD, non-diabetic pathology).
- Reliable DME detection where the reference is fundus-only rather than OCT-anchored.
- Performance beyond the ceiling imposed by reading-center label reliability.
- Generalization to populations (pigmentation, diabetes type/duration, media opacity) not adequately represented in enrollment.
- Any regulatory clearance — pathway and claims require FDA counsel and are not established by this spec.
- Long-term clinical outcomes (e.g., reduced vision loss) — the study measures diagnostic accuracy, not downstream outcomes.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*