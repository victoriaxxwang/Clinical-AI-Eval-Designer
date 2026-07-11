# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ web search where noted)

## Inputs
- **AI model:** Dual-branch nodule-characterization system — inflated 3D ResNet-50 on 64³ voxel patches (1 mm isotropic) + hand-crafted radiomics branch (wavelet first-order, GLCM, GLRLM texture), U-Net candidate detector upstream, gated multi-instance attention pooling to a scan-level malignancy probability plus auxiliary doubling-time regression.
- **Clinical use case:** Assigns each screen-detected pulmonary nodule a calibrated malignancy-risk score and growth-rate estimate to triage biopsy vs. surveillance.
- **Patient population:** Adults 50–80, ≥20 pack-year smoking history, indeterminate pulmonary nodules on low-dose screening CT (LDCT).
- **Healthcare setting:** Outpatient lung cancer screening programs at tertiary imaging centers.
- **Intended clinical claim (INFERRED — team to confirm):** "In the LDCT screening population above, the model stratifies indeterminate pulmonary nodules by malignancy risk with performance non-inferior to (or additive to) an established clinical risk model (e.g., Brock/PanCan, Lung-RADS), functioning as a *concurrent-read decision-support / triage aid* — not an autonomous diagnostic and not a replacement for tissue diagnosis." This is the most defensible framing given the use case; a stronger autonomous-diagnosis claim is not supportable by the retrieved evidence.

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Multi-reader multi-center retrospective enrichment study + prospective observational validation nested in a screening cohort; concurrent-read design comparing model-aided vs. unaided nodule triage against biopsy/follow-up truth. |
| 2. Sensor / Input Validation | LDCT acquisition is the pre-condition: scanner vendor, slice thickness, dose, reconstruction kernel, and 1 mm resampling must be validated before any risk claim. No benchmark retrieved. |
| 3. Performance Benchmarks | Primary: AUROC for malignancy + calibration; comparator = Brock/PanCan and Lung-RADS. No regulatory benchmark retrieved; team must pre-specify against a named clinical model. |
| 4. Ground Truth | Composite reference: histopathology where available + ≥24-month imaging follow-up / NLST-style adjudication for non-biopsied nodules. Label noise caps achievable performance. |
| 5. Sample Size | Must be powered on events (malignant nodules), not patients. No retrieved study is a size precedent; statistician must set. |
| 6. Subgroups | Pre-specified: scanner vendor/kernel/slice-thickness, nodule type (solid/part-solid/GGN), size strata, sex, age; subsolid-nodule threat is central. |
| 7. Regulatory Pathway | Class II CADx software, product code POK, 21 CFR 892.2060, 510(k) most likely; De Novo if no predicate for the specific claim. Regulatory counsel required. |
| 8. Post-Deployment Monitoring | Drift monitoring on scanner mix + calibration, MAUDE-style event capture, automated flag for input-distribution shift. |

## 1. Study Design
**Recommendation:** Two-stage design. **Stage A (analytical/standalone):** retrospective, multi-center, case-enriched validation of the standalone algorithm on locked weights against a composite reference standard. **Stage B (clinical utility):** a multi-reader multi-case (MRMC) concurrent-read study measuring whether radiologist nodule triage (biopsy vs. surveillance) improves with the model as a second reader, ideally nested prospectively in an operating LDCT screening program. The clinical claim is a *triage decision-support* claim, so a reader-with-vs-without-AI comparison is the pivotal design — a standalone AUROC alone does not support the intended claim.
**Rationale:** No retrieved ClinicalTrials.gov record matches this device/use case — the returned trials are all therapeutic NSCLC drug trials (e.g., NCT04738487 KEYVIBE-003 n=1264; NCT07154706 TRUST-IV; NCT03786692) and are not design precedents for an imaging CADx triage tool; their endpoints (OS, PFS, DFS) are efficacy endpoints irrelevant to a risk-stratification device. The relevant precedent class is CADx software for lesions suspicious for cancer (product code POK, 21 CFR 892.2060, class 2), which is cleared on standalone performance + MRMC reader studies, not survival trials. The retrieved literature is entirely algorithm-development work (e.g., PMID 42125996 dual-branch lung-cancer classification; PMID 41933519 multicenter dual-branch IASLC grading; PMID 41557569 NGP-Net nodule growth prediction) — these establish the model family is active in research but none is a prospective clinical-validation design you can copy. Treat them as method context, not validation precedent.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Establish LDCT acquisition validity BEFORE any downstream risk claim. Pre-specify and document: (a) scanner vendors/models in scope, (b) tube-current/dose regime (screening LDCT specifically, not diagnostic-dose CT), (c) slice thickness and reconstruction kernel, (d) the 1 mm isotropic resampling step and its interpolation behavior on thin/subsolid nodules, and (e) upstream U-Net detector sensitivity, since any nodule the detector misses never reaches the classifier and silently caps system-level sensitivity. Require a phantom/repeat-scan repeatability test and a cross-vendor equivalence test as gating criteria.
**Rationale:** This is an imaging model, so the population-specific validity threat is *scanner/vendor/reconstruction-kernel/slice-thickness shift* — radiomics texture features (GLCM, GLRLM, wavelet first-order) are known to be highly sensitive to reconstruction kernel and voxel resampling, so the hand-crafted branch is the most fragile input surface. The detector→classifier cascade means detection recall is a hard pre-condition: report it separately. No retrieved record provides an acquisition benchmark — no established input-validity threshold was retrieved; the team/expert must set repeatability and cross-vendor tolerances.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 3. Performance Benchmarks
**Recommendation:** Pre-specify primary endpoints as (1) discrimination — AUROC for malignancy classification; (2) calibration — calibration slope/intercept and a calibration plot, since the claim is a *calibrated* probability; (3) for the doubling-time output, agreement vs. measured volumetric growth (e.g., limits of agreement), treated as a secondary/exploratory endpoint. The comparator must be a named, established clinical risk model — Brock/PanCan and/or Lung-RADS category — with a pre-specified non-inferiority or superiority margin. For the MRMC arm, the endpoint is change in reader AUROC and/or change in appropriate biopsy vs. surveillance decisions.
**Rationale:** No regulatory or consensus performance threshold for lung-nodule malignancy CADx was retrieved in this pipeline — **no established benchmark retrieved; the target must be set by the study team against a named comparator.** Do NOT adopt a number from the development literature (PMID 42125996, PMID 41933519) as an acceptance bar — those are internal validation figures on different cohorts and reference standards, not regulatory standards. The auxiliary doubling-time regression is not a validated clinical endpoint and should not carry a standalone claim without its own volumetry ground truth.
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 4. Ground Truth Strategy
**Recommendation:** Use a composite reference standard with a pre-specified hierarchy: (1) histopathology (biopsy/resection) as the gold standard where tissue exists; (2) for non-biopsied nodules, ≥24 months of imaging follow-up documenting resolution/stability (benign) or growth/diagnosis (malignant), with an adjudication panel resolving discordance. Record the reference-standard source for every nodule and analyze performance stratified by truth type, because verification bias (biopsied nodules are pre-selected as suspicious) will inflate apparent performance if unaddressed.
**Rationale:** Label reliability is a ceiling: benign labels derived from follow-up stability are softer than histology, and short follow-up will misclassify indolent malignancies — achievable sensitivity/specificity is capped by this. No retrieved record specifies a reference-standard protocol for this device; the NLST-style follow-up + pathology paradigm is the defensible convention but must be set by the expert panel here. The doubling-time output requires a separate volumetric ground truth (serial segmentations), which none of the retrieved records supplies.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 5. Sample Size
**Recommendation:** Power the study on the number of **malignant nodules (events)**, not the number of patients, because screen-detected malignancy prevalence is low and drives the confidence interval on sensitivity/AUROC. Pre-specify: target AUROC CI half-width (or non-inferiority margin vs. comparator), expected malignancy prevalence in this enriched sample, and the MRMC reader/case counts using an MRMC power calculation. Enrich the case set to obtain adequate malignant events while reporting prevalence-corrected operating points.
**Rationale:** No retrieved record establishes a sample-size precedent for this device — the therapeutic trials (n=16 to n=1264, e.g., NCT01783236 n=16, NCT04738487 n=1264) are powered for survival endpoints and are irrelevant to a diagnostic-accuracy/MRMC power calculation. **No validated sample-size benchmark retrieved; a biostatistician must derive it** from the pre-specified margin and expected event rate.
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 6. Subgroup Requirements
**Recommendation:** Pre-specify subgroup analyses (not post-hoc) for: (a) **scanner vendor / reconstruction kernel / slice thickness** — the primary imaging validity threat and the one most likely to break the radiomics branch; (b) **nodule type — solid vs. part-solid vs. pure ground-glass**, since subsolid nodules are both the hardest and the highest-stakes for the growth/malignancy call; (c) nodule size strata (including sub-centimeter); (d) sex and age band within 50–80; (e) site, to detect single-center overfitting. Each subgroup needs a minimum event count or an explicit "underpowered — descriptive only" flag.
**Rationale:** Retrieved method literature signals that subsolid nodules are a distinct, harder problem requiring dedicated modeling (PMID 42235590 DecX-Net for subsolid nodule segmentation; PMID 41365825 dual-energy CT for pure-solid adenocarcinoma grading), supporting nodule-type as a mandatory pre-specified subgroup. The scanner/kernel threat is physics, not optics — radiomics texture is kernel-dependent, so cross-vendor subgroup performance is a validity requirement, not a nicety. No subgroup performance benchmark was retrieved.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 7. Regulatory Pathway
**Recommendation:** Most likely **Class II, 510(k)**, under **product code POK — "Computer-Assisted Diagnostic Software For Lesions Suspicious For Cancer," 21 CFR 892.2060, Radiology panel** (retrieved classification). Frame the submission as a CADx concurrent-read decision-support device with a locked algorithm and a defined intended-use population (LDCT screening, 50–80, ≥20 pack-years). If no suitable predicate exists for the specific triage + doubling-time claim, the fallback is **De Novo**. The doubling-time output likely needs its own intended-use statement or should be dropped from the labeled claim to avoid expanding regulatory burden. This is a device pathway — the therapeutic-drug and PMA cardiovascular records retrieved are not applicable.
**Rationale:** POK (892.2060, class 2) is the on-point classification retrieved and is the standard route for lesion-characterization CADx. The other retrieved oncology device codes are **not** the right fit: SDA (Electrical Tumor Treatment Fields for NSCLC) is class 3 and therapeutic; the retrieved "branch"/"dual" 510(k)s (K964021 side-branch occlusion, K040829 vascular grafts, K103706 outpatient ECG) are keyword artifacts, not predicates. The retrieved PMA/MAUDE/recall records (P980049, dual-chamber pulse-generator injury reports, Class II recalls) are cardiovascular hardware and are relevant only as *safety-reasoning analogues*, not as a pathway. Confirm predicate existence with a formal 510(k) database search — this pipeline did not do a systematic predicate search.
**Confidence:** MEDIUM
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized

## 8. Post-Deployment Monitoring
**Recommendation:** Deploy with: (1) continuous **input-distribution monitoring** — flag when incoming scanner vendor/kernel/slice-thickness mix drifts from the validation distribution (the top failure mode for the radiomics branch); (2) ongoing **calibration monitoring** — recompute calibration slope/intercept on accruing outcomes, since a "calibrated probability" claim degrades silently under case-mix shift; (3) detector-recall auditing on any nodule later found malignant that the U-Net missed; (4) an adverse-event / misclassification capture process analogous to MAUDE reporting, with pre-defined triggers for false-negative malignancies; (5) periodic subgroup re-evaluation (nodule type, vendor). Define a re-validation / update-governance plan for any model change.
**Rationale:** The retrieved MAUDE injury reports (report numbers 3004209178-2020-07719, 2649622-2020-08347) and Class II recalls (Z-2480-2019 oxidation failure; Z-1087-2017 sterility) illustrate that post-market failure capture and defined failure-mode triggers are expected practice — apply the same discipline to silent algorithmic failure (drift, miscalibration, detector misses), which is this device's analogue of a hardware defect. No device-specific monitoring benchmark was retrieved; thresholds must be set by the team.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** That, on the specified LDCT screening population (adults 50–80, ≥20 pack-years, indeterminate nodules) and the validated scanner/reconstruction conditions, a locked version of the model stratifies nodule malignancy risk with pre-specified, calibrated discrimination performance relative to a named clinical comparator, and — in the MRMC arm — that radiologists triaging biopsy vs. surveillance perform measurably better with the tool as a concurrent read, within the tested subgroups.
**DOES NOT CERTIFY:**
- That the malignancy score or doubling-time estimate reflects true tumor biology / physiological growth — these remain model outputs, not tissue diagnoses.
- Autonomous or stand-alone diagnostic use, or replacement of biopsy/pathology.
- Performance on scanners, kernels, slice thicknesses, doses, or nodule types not represented in the validation set (esp. pure ground-glass and sub-centimeter nodules if underpowered).
- Generalization beyond the 50–80 / ≥20 pack-year screening population, or to non-screening (symptomatic/diagnostic-dose) CT.
- The standalone validity of the doubling-time regression output unless separately validated against serial volumetry.
- Any FDA clearance — regulatory authorization requires a submission and FDA review under the pathway in Field 7.
- A complete competitive/predicate landscape — no systematic 510(k) predicate search or licensed-database search was performed.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*