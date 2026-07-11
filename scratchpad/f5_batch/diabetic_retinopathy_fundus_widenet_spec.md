# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ web search where noted)

## Inputs
- **AI model:** EfficientNet-B4 ordinal-regression classifier on macula-centered color fundus photographs (456×456, CLAHE + circular FOV crop), with test-time augmentation, attention-gated lesion evidence maps (microaneurysms, hemorrhages, hard exudates), and an upstream quality-assessment sub-network that gates ungradable images.
- **Clinical use case:** Assigns a five-level DR severity grade and flags cases meeting the referable-DR threshold for specialist review.
- **Patient population:** Adults with diabetes mellitus in routine annual eye screening.
- **Healthcare setting:** Primary-care and community optometry screening with tele-ophthalmology over-read.
- **Intended clinical claim (inferred — team to confirm):** *"In adults with diabetes undergoing routine screening, this software identifies referable diabetic retinopathy (moderate NPDR or worse, and/or DME) from gradable macula-centered fundus photographs with sensitivity and specificity non-inferior to a defined human-grader reference, and correctly rejects ungradable images."* This is an inferred assistive/triage claim; whether it is positioned as **autonomous diagnosis** vs. **screening triage with mandatory tele-ophthalmology over-read** materially changes the regulatory burden and must be fixed before validation (see Field 7).

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Prospective, multi-site screening-population study; pre-registered; software output vs. adjudicated grader reference on consecutively enrolled patients. |
| 2. Sensor/Input Validation | Camera/model-agnostic acquisition validity + gradability sub-network must be validated FIRST; NAVIS-EX laterality-swap recall is a concrete failure mode. |
| 3. Performance Benchmarks | No FDA-cleared numeric threshold retrieved; literature figures are lab-set, not standards — team/expert must pre-specify referable-DR sensitivity/specificity floors. |
| 4. Ground Truth | Multi-grader adjudicated ICDR/ETDRS grading; reference-standard noise caps achievable performance. |
| 5. Sample Size | No powering precedent retrieved — must be pre-specified to bound sensitivity CI at the referable threshold; disease prevalence drives PPV. |
| 6. Subgroups | Skin/fundus pigmentation, cataract/media opacity, camera vendor, DME presence, image quality strata — pre-specified. |
| 7. Regulatory Pathway | Ophthalmic device space; retrieved 510(k)s are cameras/lenses, NOT AI graders. Autonomous DR-AI De Novo pathway exists but no such precedent was retrieved — regulatory counsel required. |
| 8. Post-Deployment Monitoring | MAUDE/recall precedent (laterality swap, image mis-save) → monitor gradability drift, camera-fleet shift, referral yield, over-read override rate. |

## 1. Study Design
**Recommendation:** Prospective, multi-site diagnostic-accuracy study enrolling consecutive adults with diabetes at primary-care/community optometry screening sites, with the software's referable-DR flag compared against an independent adjudicated reading-center reference on the same images. Pre-register the protocol and analysis plan (ClinicalTrials.gov) with the primary endpoint and referable threshold locked before data collection. Include a pre-specified analysis of ungradable-image rate as a co-primary operating characteristic. A retrospective enriched-dataset study can support development/tuning but is insufficient alone for a screening claim because it distorts prevalence and quality distribution.
**Rationale:** No pivotal DR-screening trial NCT was returned in this retrieval, and the literature layer is almost entirely retrospective algorithm-development work on curated datasets (e.g., PMID 42151890 EfficientNet+GradCAM pipeline, 2026; PMID 39695310 ensemble EfficientNet, 2024; W3033442124 / W3114803724 EfficientNet-B5, 2020). These establish technical feasibility, not screening-population accuracy. The systematic review PMID 40171193 (Front Endocrinol 2025) and survey W4226244379 (IEEE Access 2022) confirm the field is dominated by dataset-level benchmarks rather than prospective screening evidence — reinforcing the need for a prospective design here.
**Confidence:** MEDIUM (design principles are standard; no matching prospective screening trial retrieved to anchor specifics).
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Before any grading-accuracy claim, validate (a) the acquisition chain across every camera make/model in the intended fleet, and (b) the quality-assessment sub-network as a standalone gate. Specifically: characterize the gradability sub-network's sensitivity/specificity for "ungradable" against human quality assessment; report the ungradable rate per camera and per operator; verify image laterality/metadata integrity end-to-end; and confirm the CLAHE + circular-crop preprocessing behaves identically across vendor image formats and resolutions. The downstream grade is untrustworthy on any image the gate should have rejected.
**Rationale:** Retrieved post-market records show these are real, documented fundus-imaging failure modes: a Class II recall of NAVIS-EX filing software for the NIDEK AFC fundus camera where **the left-eye image could be saved as the right eye** (recall Z-2046-2013) — a laterality/metadata error that would silently corrupt any per-eye grade — and MAUDE injury reports involving fundus diagnostic hardware (report MW5105451, product code HJI). Fundus cameras themselves are long-established predicate devices (e.g., Canon CF-60UV, K901839, 1990). Media opacity/cataract and small pupils are physiologic degraders of gradability specific to this diabetic, often older population.
**Confidence:** HIGH (concrete retrieved recall/MAUDE evidence for the exact modality).
**Expert review:** Expert sign-off — output is well-grounded; expert confirms or adjusts.

## 3. Performance Benchmarks
**Recommendation:** Pre-specify, before enrollment, minimum acceptable **referable-DR sensitivity and specificity** with two-sided confidence intervals, plus a maximum acceptable ungradable rate. **No FDA-established numeric performance standard for DR-screening AI was retrieved in this pipeline** — therefore these thresholds must be set by the study team with clinical/regulatory experts (screening context typically prioritizes high sensitivity to avoid missed referable disease, accepting lower specificity). Report per-grade agreement (quadratic-weighted kappa against the reference) given the ordinal objective, and report operating characteristics separately for the gate and the grader.
**Rationale:** The retrieved literature reports high accuracy figures, but these are **lab-derived on curated datasets and are not regulatory benchmarks** — e.g., calibration-focused foundation-model benchmarking (PMID 42078464, 2026) and multiple EfficientNet accuracy papers (PMID 39695310; PMID 42151890; W3109350411 IEEE Access 2020). Notably PMID 42078464 emphasizes **calibration**, which matters here because an ordinal-regression threshold decision depends on well-calibrated grade probabilities. None of these supplies a threshold you may adopt as a target.
**Confidence:** MEDIUM (rich literature context, but no citable regulatory benchmark; numbers must be team-set).
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 4. Ground Truth Strategy
**Recommendation:** Establish the reference standard as multi-grader adjudicated grading on a validated ordinal scale (ICDR five-level or ETDRS), with ≥2 independent graders plus adjudication of disagreements by a senior reader/reading center, and pre-defined referable threshold (typically moderate NPDR or worse, and/or DME). Report inter-grader reliability; where feasible, incorporate OCT confirmation for DME, since fundus photos underdetect macular edema. Explicitly state that achievable model sensitivity/specificity is **capped by reference-standard noise** — DR grading has well-documented inter-observer variability.
**Rationale:** The model's five-level ordinal output presupposes a graded reference; the literature uses exactly these scales (fine-grained severity grading, PMID 42386883, 2026). The DME limitation is grounded in retrieved fusion work showing fundus-only grading is strengthened by OCT (PMID 42346900 Fundus-OCT fusion, 2026; PMID 40171193 OCT+retinal-image meta-analysis, 2025) — since this model is fundus-only, DME-driven referrals are a known blind spot to disclose.
**Confidence:** MEDIUM.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 5. Sample Size
**Recommendation:** Power the study to bound the lower confidence limit of **referable-DR sensitivity** (the safety-critical operating point) at the pre-specified floor, then confirm sufficient referable cases will be captured given screening-population prevalence — this typically requires enriching total enrollment because referable disease is a minority of screened patients. Pre-specify separate adequacy for each mandatory subgroup (Field 6) and for the ungradable stratum. **No sample-size precedent was retrieved from this pipeline** — the number must be computed by the team's statistician against the locked thresholds and expected prevalence.
**Rationale:** No prospective DR-screening trial with enrollment figures was returned; retrieved works are dataset-based and do not translate to a screening-population power calculation. Because PPV in deployment is prevalence-driven, the sizing must reflect true screening prevalence, not a balanced dataset.
**Confidence:** LOW (no retrieved anchor; entirely a statistical judgment call).
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 6. Subgroup Requirements
**Recommendation:** Pre-specify and independently power (or at minimum report with CIs) the following subgroups: **fundus/retinal pigmentation and race/ethnicity** (retinal background pigmentation and skin-tone-correlated fundus variation can shift model features); **media opacity / cataract** (physiologic image degradation common in diabetics); **camera make/model and image resolution** across the deployed fleet; **presence of DME** (fundus-only blind spot); **image-quality strata** (borderline-gradable images); and **age/diabetes type/duration**. Population-specific validity threats here are physiologic/optical — pigmentation and media opacity — not cosmetic, and must be tested as pre-specified subgroups, not post-hoc.
**Rationale:** Camera-vendor shift is a documented modality risk (multiple distinct fundus-camera predicates, e.g., K901839; software-level errors tied to a specific camera, recall Z-2046-2013). The fundus-only DME limitation is supported by the OCT-fusion literature (PMID 42346900; PMID 40171193). Pigmentation/media-opacity effects are physiology; no retrieved study stratified on these for this exact model, so they must be prospectively required.
**Confidence:** MEDIUM.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 7. Regulatory Pathway
**Recommendation:** Treat this as an ophthalmic diagnostic-software device. **The intended-use positioning must be fixed first:** an *autonomous* "detect referable DR without clinician interpretation" claim carries the highest evidentiary bar, whereas a *screening-triage-with-mandatory-tele-ophthalmology-over-read* claim (which matches the stated setting) is a computer-assisted workflow claim. Engage FDA (likely via a Pre-Submission) and confirm the applicable product code and pathway. **This retrieval returned NO AI-based DR-grading device precedent** — the returned ophthalmic records are physical cameras/lenses (Hruby fundus lens HJI, reg 886.1395, Class I; Canon CF-60UV K901839; Yannuzzi laser lens K864304), not software classifiers. A De Novo pathway for autonomous DR-screening AI is known to exist in the broader landscape, but no such record was retrieved here and its identifier must be independently verified — do not rely on it as retrieved. The "primary"/"community" product codes returned (JIS calibrator, K951771, K252637) are unrelated matches and are not predicates.
**Rationale:** Grounded in the openFDA device records above; the mismatch between retrieved predicates and this software is itself the key finding. Absence of an AI-grader record here is a retrieval gap (this pipeline did not query all endpoints), not proof none exists.
**Confidence:** LOW (no on-point software precedent retrieved).
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized.

## 8. Post-Deployment Monitoring
**Recommendation:** Deploy with a monitoring plan tracking: ungradable-image rate per site/camera/operator (drift signal); camera-fleet composition changes and any preprocessing/format mismatches; referral yield and downstream confirmed-referable rate; tele-ophthalmology over-read override rate (both directions); laterality/metadata integrity audits; and periodic recalibration checks of grade-probability calibration. Establish a complaint/adverse-event capture route aligned to MAUDE. Trigger revalidation on any camera change, software update, or drift in gradable-rate or referral yield.
**Rationale:** Retrieved post-market records show the concrete failure modes to watch: the laterality image-save error (recall Z-2046-2013) and fundus-hardware injury reports (MAUDE MW5105451, report 2955842-2022-15143). MAUDE/recall data are safety signals, not efficacy evidence, and are used here strictly for failure-mode monitoring. The calibration-drift concern is reinforced by PMID 42078464 (2026).
**Confidence:** MEDIUM.
**Expert review:** Expert sign-off — output is well-grounded; expert confirms or adjusts.

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** That, on gradable macula-centered color fundus photographs from adults in routine diabetes screening at the studied primary-care/optometry sites and camera fleet, the software flags referable diabetic retinopathy at the pre-specified sensitivity/specificity floors against an adjudicated human-grader reference, correctly rejects ungradable images at the specified rate, and holds within pre-specified pigmentation, media-opacity, camera, and DME subgroups.
**DOES NOT CERTIFY:**
- True ophthalmic ground truth or visual outcomes — only agreement with a noise-limited human-grader reference.
- Detection of DME or non-DR pathology not represented in the reference standard (fundus-only, no OCT).
- Performance on ungradable images, or on cameras/populations/sites outside the study.
- Autonomous diagnostic use if the study was run with mandatory tele-ophthalmology over-read (or vice versa).
- Any regulatory clearance or marketing claim — that requires FDA engagement (Field 7).
- Long-term real-world performance absent the monitoring in Field 8.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*