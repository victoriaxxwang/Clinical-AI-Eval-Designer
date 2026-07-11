# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ literature layer)

## Inputs
- **AI model:** Dual-branch nodule classifier — inflated 3D ResNet-50 CNN on 64³ voxel patches (1 mm isotropic) + hand-crafted radiomics branch (wavelet first-order, GLCM, GLRLM texture), fused via gated multi-instance attention pooling; upstream U-Net detector localizes candidates; outputs a calibrated malignancy probability plus an auxiliary doubling-time regression.
- **Clinical use case:** Assign each screen-detected pulmonary nodule a calibrated malignancy-risk score and growth-rate estimate to triage biopsy vs. surveillance.
- **Patient population:** Adults 50–80, ≥20 pack-year smoking history, indeterminate pulmonary nodules on low-dose screening CT (LDCT).
- **Healthcare setting:** Outpatient lung cancer screening programs at tertiary imaging centers.
- **Intended clinical claim (INFERRED — team must confirm):** *"Among indeterminate pulmonary nodules detected on LDCT screening in high-risk adults, the model estimates malignancy risk with performance supporting nodule prioritization, as an adjunct to (not a replacement for) radiologist assessment and established risk models."* I am deliberately framing this as an **adjunctive risk-stratification / CADx** claim, not an autonomous diagnostic or biopsy-decision claim, because the latter would require a far higher evidentiary bar and prospective outcome data.

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Retrospective multi-reader multi-case (MRMC) reader study on an independent, temporally/geographically split LDCT cohort; prospective silent-mode phase before deployment |
| 2. Sensor/Input Validation | LDCT acquisition physics is the pre-condition — scanner vendor, dose, slice thickness, reconstruction kernel, resampling to 1 mm must be validated before any risk claim |
| 3. Performance Benchmarks | No lung-CADx efficacy benchmark retrieved; must be pre-specified by team against radiologist + established risk models (Brock/Lung-RADS) — not invented here |
| 4. Ground Truth | Composite reference: histopathology where biopsied + ≥2-year imaging follow-up / registry linkage for non-biopsied; label noise caps achievable performance |
| 5. Sample Size | No retrieved trial fixes N for this indication; must be powered on pre-specified AUC/sensitivity delta with enough cancers — expert biostatistician required |
| 6. Subgroups | Nodule type (solid/part-solid/GGN), size strata, scanner vendor/kernel, sex, age, nodule location; each pre-specified |
| 7. Regulatory Pathway | Most likely 510(k) Class II CADx software, product code POK, 21 CFR 892.2060 (Radiology) — regulatory counsel required |
| 8. Post-Deployment Monitoring | Calibration drift, scanner/protocol shift, detector miss rate, subgroup performance; MAUDE-style event capture |

## 1. Study Design
**Recommendation:** Primary evidence should be a **retrospective, fully-crossed multi-reader multi-case (MRMC) study** comparing readers-with-AI vs. readers-without-AI on an independent test set drawn from a **different time period and, ideally, different centers** than training. Follow this with a **prospective silent/shadow-mode phase** in the target screening programs (model runs, outputs logged but not shown) to confirm real-world detector+classifier performance before any live triage use. The auxiliary doubling-time output requires its own validation against serial-scan volumetry and should not be claimed until separately evidenced.
**Rationale:** The retrieved ClinicalTrials.gov record (NCT02780739, a randomized cognitive-training study) is **not relevant** to this indication — no lung-screening AI trial was retrieved, so no on-point trial design could be mapped. The closest regulatory analog, computer-assisted diagnostic software for cancerous lesions (product code POK, 21 CFR 892.2060), is a Radiology-panel CADx device class for which MRMC reader studies are the conventional evidentiary design. Because the intended claim is *adjunctive*, the design must isolate the incremental effect of the model on reader performance, not model-alone accuracy.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Before any malignancy-risk claim, validate the **LDCT acquisition and preprocessing chain** as an explicit pre-condition: (a) scanner manufacturer/model coverage, (b) tube-current/dose range consistent with low-dose screening, (c) native slice thickness and the effect of resampling to 1 mm isotropic, (d) reconstruction-kernel diversity (sharp vs. smooth kernels materially alter texture/radiomics features), (e) segmentation quality of the U-Net upstream, since the radiomics branch is computed *on the segmented volume* — a segmentation error propagates into every GLCM/GLRLM feature. Require a locked preprocessing spec and a per-scan input-quality gate that rejects or flags out-of-distribution acquisitions.
**Rationale:** The radiomics branch is a known **reconstruction-kernel/voxel-spacing–sensitive** input: wavelet and texture descriptors are physics-dependent, so kernel or spacing shift is a first-order validity threat, not a footnote. No retrieved record characterizes this model's scanner robustness. This is the imaging-model analog of the mandated population-physics threat (scanner/vendor/reconstruction-kernel shift).
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 3. Performance Benchmarks
**Recommendation:** Pre-specify primary and non-inferiority/superiority thresholds **before** the study. Candidate primary metric: change in reader AUC (reader+AI vs. reader-alone) and change in sensitivity at a fixed, clinically acceptable false-positive/recall rate. The model's standalone AUC, sensitivity, specificity at the operating point, and **calibration** (since the output is a calibrated probability — report calibration slope/intercept and a calibration plot, not just discrimination) must all be reported. Compare against **established clinical risk models** (e.g., Brock/PanCan, Lung-RADS category) as the incumbent benchmark.
**Rationale:** **No efficacy benchmark for lung-nodule CADx was retrieved** — the literature layer returned only generic dual-branch/dual-path architecture papers (e.g., brain-tumor segmentation PMID 42125192; DEF-Net PMID 41920949) with no lung-screening performance data, and no NLST/Brock/Lung-RADS records were retrieved. **Therefore no numeric target can be stated here — thresholds must be set by the study team / expert against radiologist performance and established risk models.** Do not adopt any figure not tied to a source.
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 4. Ground Truth Strategy
**Recommendation:** Use a **composite reference standard**: histopathology (biopsy/resection) with NSCLC subtyping for nodules that are sampled, and **≥24-month imaging follow-up plus cancer-registry linkage** for nodules that are not biopsied (stability = benign proxy; interval growth/diagnosis = malignant). Adjudicate discordant cases by a panel blinded to the model. For the doubling-time output, ground truth is serial volumetric measurement with a documented volumetry method and inter-reader variability estimate.
**Rationale:** Verification bias is intrinsic — benign nodules are rarely biopsied, so a pure-histology reference would systematically distort specificity. The composite standard is the standard workaround but introduces **label noise** (follow-up misclassifies slow-growing cancers as benign, and volumetric doubling-time has measurement error). Per the label-reliability constraint, achievable sensitivity/specificity is **capped by this reference-standard noise** — state the ceiling explicitly and estimate it. No retrieved record supplies a validated reference standard for this specific task.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 5. Sample Size
**Recommendation:** Size the study on the **pre-specified primary metric** (e.g., an MRMC reader-AUC difference, or standalone sensitivity at fixed specificity), powered with an adequate **number of confirmed cancers** — malignancy prevalence in screen-detected indeterminate nodules is low, so the cancer count, not total nodule count, governs power. Include an MRMC variance component for reader and case random effects. A biostatistician must compute N once the effect size, expected prevalence, reader count, and reference-standard noise are fixed.
**Rationale:** **No retrieved record fixes a sample size for this indication.** The only ClinicalTrials.gov enrollment retrieved (NCT02780739, n=521) is from an unrelated cognitive-training trial and must not be transferred. Per constraints, no N is invented here.
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 6. Subgroup Requirements
**Recommendation:** Pre-specify and power (or at minimum report with CIs) performance across: **nodule composition** (solid / part-solid / pure ground-glass — the radiomics and CNN branches behave very differently across these), **size strata** (sub-solid <6 mm through >8 mm solid), **scanner vendor and reconstruction kernel** (the physics threat from Field 2), **nodule location** (upper vs. lower lobe, perifissural/juxtapleural where segmentation is hardest), and demographic strata (**sex, age band within 50–80**). Report the U-Net detector's **per-subgroup miss rate**, since a missed candidate is a silent false negative the classifier never sees.
**Rationale:** The concrete population-physics threat here is **reconstruction-kernel/vendor shift × radiomics feature stability** and **nodule-type heterogeneity**, not demographics alone. No retrieved record reports subgroup performance for this model, so all subgroup validity is currently unestablished.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 7. Regulatory Pathway
**Recommendation:** The most defensible pathway is **510(k) clearance as Class II computer-assisted diagnostic (CADx) radiology software**, product code **POK**, regulation **21 CFR 892.2060** (Radiology panel — "Computer-Assisted Diagnostic Software For Lesions Suspicious For Cancer"), positioned as an **adjunct** to the radiologist. Predicate identification and substantial-equivalence argumentation (device description, intended use, performance testing) should follow that class. If the team instead pursues an autonomous or biopsy-directing claim, that likely escalates the evidentiary bar and may fall outside a straightforward 510(k) — confirm with counsel. Note that **electrical tumor-treatment fields for NSCLC (product code SDA, Class III)** and cancer NAAT/fluorescence assays (OYM, SAW, Class III) were retrieved but are **therapeutic/diagnostic-assay devices, not imaging CADx**, and are the wrong analog.
**Rationale:** POK / 892.2060 is the only retrieved classification that matches an imaging-based CADx-for-cancer function and is Class II with a defined regulation. The retrieved 510(k) records (K103706 outpatient ECG, K123671 outpatient management, K964021/K040829 vascular grafts, K940827 sunglasses) are **not predicates** for this device — none is a lung-imaging CADx. **The pipeline did not query Drugs@FDA/SPL/FAERS (device, not drug) and did not query non-US regulators (EMA/MHRA/PMDA); it is not a comprehensive predicate search** — a formal predicate search is required.
**Confidence:** MEDIUM
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized

## 8. Post-Deployment Monitoring
**Recommendation:** Deploy with a monitoring plan covering: (a) **calibration drift** of the malignancy probability over time and after any scanner/protocol upgrade (recalibration triggers pre-defined); (b) **input distribution monitoring** for new scanner vendors/kernels/dose protocols entering the screening program (ties to Field 2); (c) **U-Net detector miss/false-positive rate** tracked against reader recall; (d) **per-subgroup performance dashboards** (nodule type, size, vendor); (e) an **adverse-event/complaint capture** process analogous to MAUDE reporting for missed cancers or inappropriate triage. Establish a periodic reconciliation against pathology/registry outcomes.
**Rationale:** MAUDE and recall records retrieved (dual-chamber pulse-generator injury reports 3004209178-2020-07719, 2649622-2020-08347; recalls Z-1087-2017, Z-2480-2019) are unrelated hardware devices, but they illustrate the **class of post-market safety signal and failure-mode reporting** a deployed device must feed. For a triage model, the dominant post-deployment failure modes are silent calibration drift and dataset shift, which degrade risk scores without any overt malfunction — hence continuous outcome linkage is essential.
**Confidence:** MEDIUM
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** That, on an independent LDCT cohort of high-risk adults (50–80, ≥20 pack-years) with indeterminate screen-detected nodules acquired on the validated set of scanners/kernels, the model — used as an adjunct to a radiologist — changes reader risk-stratification performance by the pre-specified margin, with calibrated probabilities, across the pre-specified nodule-type and acquisition subgroups, judged against a composite histology-plus-follow-up reference standard.
**DOES NOT CERTIFY:**
- Physiological/biological ground truth — the composite reference has label noise that caps achievable accuracy.
- That the model should **direct biopsy vs. surveillance autonomously** — the claim is adjunctive risk stratification only.
- Validity of the **doubling-time regression** output, which requires separate volumetric validation.
- Performance on **scanners, kernels, doses, or centers outside the validated set**, or on populations outside the 50–80 / ≥20 pack-year screening cohort.
- Improved **patient outcomes** (stage shift, mortality, reduced unnecessary biopsy) — that requires prospective outcome trials not covered here.
- Regulatory clearance — this spec informs, but does not substitute for, an FDA submission.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*