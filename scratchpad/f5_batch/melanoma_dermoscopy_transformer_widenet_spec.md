# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ web search where noted)

## Inputs
- **AI model:** ViT-hybrid (CNN stem → vision-transformer encoder) classifying dermoscopic images with metadata tokens (site, age, sex) via cross-attention; outputs malignancy probability + seven-point-checklist attribute predictions + Monte Carlo–dropout uncertainty with abstention; contrastive self-supervised pretraining; skin-tone/lesion-type balanced sampler.
- **Clinical use case:** Binary benign-vs-malignant classification of pigmented lesions from dermoscopy, with interpretable morphologic attributes and an uncertainty/abstain flag.
- **Patient population:** Adults presenting with suspicious or changing pigmented skin lesions.
- **Healthcare setting:** Dermatology outpatient clinics and teledermatology triage services.
- **Intended clinical claim (inferred — stated assumption):** No claim was supplied. The most defensible claim I assume is: *"As an assistive adjunct (not autonomous), the model, on dermoscopic images meeting defined quality standards, stratifies pigmented lesions by melanoma risk to support clinician triage/referral decisions, at a sensitivity non-inferior to a defined clinician comparator, with a pre-specified abstention rate."* An autonomous "diagnose/rule-out melanoma" claim is NOT assumed — that would demand a substantially higher regulatory and evidentiary bar.

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Prospective, multi-reader multi-site observational validation on consecutively enrolled lesions; AI-vs-clinician and AI-assisted-vs-unassisted reads against histopathology; locked model. |
| 2. Sensor/Input Validation | Dermoscopy acquisition (device/polarization/magnification/resolution) must be validated first; image-quality gate + abstention behavior characterized before any accuracy claim. |
| 3. Performance Benchmarks | Sensitivity-prioritized (melanoma miss = harm); AUC/sens/spec vs clinician comparator. No regulatory benchmark retrieved — team/experts must set targets. |
| 4. Ground Truth | Histopathology as reference standard; account for inter-pathologist discordance for melanoma as a ceiling on achievable performance. |
| 5. Sample Size | Must be powered on melanoma cases (rare), not total lesions. No retrieved study sized for THIS task — must be computed by team. |
| 6. Subgroups | Fitzpatrick skin tone, anatomic site, lesion subtype, age/sex, acquisition device — pre-specified, each powered enough to detect degradation. |
| 7. Regulatory Pathway | Likely FDA Class II CADx (computer-assisted diagnostic), 510(k)/De Novo; no on-point dermoscopy AI predicate retrieved here. Regulatory counsel required. |
| 8. Post-Deployment Monitoring | Data drift (new dermatoscopes/teledermatology cameras), skin-tone subgroup drift, abstention-rate drift, missed-melanoma feedback loop. |

## 1. Study Design
**Recommendation:** Prospective, multi-site observational validation on **consecutively enrolled** pigmented lesions clinically selected for biopsy, with the model locked (frozen weights, frozen threshold, frozen abstention rule) before enrollment. Run two comparisons: (a) standalone AI vs. clinician(s), and (b) a multi-reader multi-case (MRMC) arm measuring clinician performance **unassisted vs. AI-assisted**, since the inferred claim is assistive. Enroll across both deployment contexts (in-clinic dermoscopy AND teledermatology triage) because image acquisition differs materially between them.
**Rationale:** The retrieved oncology-imaging AI studies are predominantly observational diagnostic-accuracy designs comparing AI to clinician/pathologist reference — e.g., AI-vs-endoscopist-vs-pathologist (NCT04864587), integrated-model discrimination of lesion risk categories (NCT07660718), and AUC-against-pathology designs (NCT06703112). This is the appropriate template. Consecutive enrollment (vs. curated case sets) is essential to avoid spectrum bias, which inflates dermoscopy-AI performance. An assistive claim requires the MRMC "does the clinician do better with the tool" arm, not just standalone accuracy. No dermoscopy-specific melanoma validation trial was retrieved in this pull — the design is mapped from adjacent CNN-oncology imaging studies, so confidence is capped.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Before any accuracy claim, validate the **imaging chain**: dermatoscope model(s), contact vs. polarized (non-contact) illumination, magnification, sensor resolution, color calibration/white balance, and — critically for teledermatology — smartphone-attached vs. dedicated dermatoscope capture. Characterize the model across each acquisition configuration and define an **explicit image-quality gate** (focus, illumination, framing, artifact). Separately characterize the Monte Carlo–dropout abstention behavior: what fraction of real-world images it abstains on, and whether abstention correlates with poor image quality vs. genuinely hard lesions.
**Rationale:** Dermoscopy AI is acutely sensitive to acquisition domain shift — polarization mode, magnification, and camera pipeline change lesion color/texture, which are the exact features the model reads. The retrieved MAUDE/recall records for dermatology laser devices (report 2914019-2008-00005; recalls Z-1396-2019, Z-1381-2019) are about power/sterility failure modes, not imaging — but they underscore that device-level failure modes must be logged and monitored. openFDA device terms retrieved include "dermoscopic," but no cleared dermoscopy-acquisition standard was returned here. Input validity is a physics precondition: a malignancy probability computed on an out-of-distribution image is untrustworthy regardless of headline AUC.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 3. Performance Benchmarks
**Recommendation:** Prioritize **sensitivity for melanoma** (a missed melanoma is the high-harm error), with specificity as a co-primary to control unnecessary biopsies/referrals. Report per-lesion sensitivity, specificity, AUROC, and (given assistive claim) the change in clinician sensitivity/specificity with AI assistance. Pre-specify targets as non-inferiority-to-clinician-comparator or superiority-of-assisted-read. **No regulatory performance threshold for dermoscopic melanoma classification was retrieved in this pull** — targets must be set by the study team with expert dermatology/biostatistics input and justified against the clinician comparator, not asserted.
**Rationale:** Retrieved CNN-oncology studies report AUC as the primary discrimination metric (NCT06703112; NCT07660718; PMID 31525737; PMID 33465354), confirming AUC as a standard descriptor — but AUC alone is insufficient for a screening/triage tool where the operating point (threshold) drives melanoma misses. None of the retrieved records establishes a numeric sensitivity/specificity floor for this indication. Do not import numbers from gastric/thyroid/bladder CNN papers as if they were melanoma benchmarks.
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 4. Ground Truth Strategy
**Recommendation:** **Histopathology of the excised/biopsied lesion** as the primary reference standard. For lesions not biopsied (benign, not excised), use a pre-specified adjudicated standard (expert consensus + adequate clinical follow-up interval to confirm benignity) and report it as a separate, weaker reference tier. Quantify and report **inter-pathologist diagnostic discordance for melanoma**, and treat it as a ceiling on achievable sensitivity/specificity.
**Rationale:** Retrieved pathology-anchored AI studies use pathological diagnosis as ground truth (NCT06703112 "Pathological diagnosis"; NCT06540846 histopathological subclassification; PMID 42223560 whole-slide reference). But melanoma histopathology is known to have meaningful inter-observer disagreement, especially for borderline melanocytic lesions — so a noisy label caps the model's demonstrable accuracy (constraint 7). A non-biopsied "benign by follow-up" arm introduces verification bias that must be pre-specified, not hidden.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 5. Sample Size
**Recommendation:** Power the study on the **number of confirmed melanomas**, not total lesions — melanoma prevalence among pigmented lesions is low, so the melanoma count is the binding constraint for the sensitivity confidence interval. Additionally power each pre-specified subgroup (Section 6) sufficiently to detect clinically meaningful performance degradation. **No retrieved study was sized for THIS task**; the enrollment figures in the retrieved records (n=100 NCT07660718; n=500 NCT04864587; n=584 NCT06703112; n=5000 NCT05193656/NCT03857373) are for other organs/tasks and must not be copied — the required N must be computed from the target sensitivity CI width and expected melanoma prevalence.
**Rationale:** Diagnostic-accuracy sample size is driven by the rarer class and desired CI precision at the chosen operating point. The retrieved n's span two orders of magnitude precisely because the target task and prevalence differ — illustrating that no single number transfers. Any figure not derived from a pre-specified power calculation would be invented (constraint 1).
**Confidence:** LOW
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 6. Subgroup Requirements
**Recommendation:** Pre-specify and independently report performance across: **Fitzpatrick skin phototype (I–VI)**, anatomic site (acral, facial, trunk, nail/subungual, mucosal), lesion subtype (nevus, dysplastic nevus, seborrheic keratosis, lentigo, melanoma subtypes), age band, sex, and **acquisition device / illumination mode**. Each subgroup must have enough melanoma cases to detect degradation, not merely be "represented." Report abstention rate by subgroup.
**Rationale:** The concrete population validity threat here is **physiology, not optics**: melanin density and background pigmentation differ across skin tones and change lesion appearance in dermoscopy, and dermoscopy datasets historically under-represent darker skin and acral/nail sites where melanoma in pigmented skin more often arises — so a headline AUC can mask systematic failure in exactly the highest-risk-of-missed-diagnosis subgroups (constraint 6). The model's balanced sampler is a mitigation *claim* that must be *verified* on held-out prospective data. No subgroup-stratified dermoscopy performance data were retrieved in this pull.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## 7. Regulatory Pathway
**Recommendation:** Under the assumed **assistive** claim, this is most plausibly an FDA **Class II computer-assisted diagnostic (CADx) / software-as-a-medical-device** device (lesion-assessment adjunct), pursued via **510(k)** if a suitable predicate exists or **De Novo** if not; an autonomous "rules out melanoma" claim would raise the bar substantially and possibly the class. Do not assert a specific product code or predicate: **no on-point dermoscopy/melanoma CADx predicate was retrieved** — the returned 510(k) dermatology records (K862862, K862864 surgical lasers; K861301 bacti plate) and the outpatient/telemetry codes (product code QYX, 21 CFR 870.1025; K103706; K123671) are NOT analogous devices and must not be cited as predicates. This pipeline did not query all FDA device endpoints and did not query non-US regulators (EMA/MHRA/PMDA) — a proper predicate search is required.
**Rationale:** The retrieved openFDA dermatology entries are physical devices (lasers, culture plates), not imaging-AI software; using them as a predicate would misstate the pathway (constraint 4). The correct predicate/pathway determination depends on FDA databases and precedents beyond this retrieval's coverage.
**Confidence:** LOW
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized

## 8. Post-Deployment Monitoring
**Recommendation:** Monitor: (a) **acquisition drift** as new dermatoscopes and teledermatology cameras enter use; (b) **skin-tone and site subgroup performance drift**; (c) **abstention-rate drift** (rising abstention = silent input-quality degradation); (d) a **missed-melanoma feedback loop** linking model outputs to eventual histopathology to catch false-negatives; and (e) a device-failure/complaint log analogous to MAUDE surveillance. Pre-define trigger thresholds for retraining/recall.
**Rationale:** Retrieved MAUDE and recall records for dermatology devices (report 2914019-2008-00005/-00010; recalls Z-1396-2019, Z-1381-2019) demonstrate the expected post-market safety-signal machinery — apply the same discipline to software failure modes (drift, subgroup degradation), which are the AI-specific analog. These are safety signals, not efficacy evidence. Teledermatology in particular introduces uncontrolled camera variability post-launch that in-clinic validation cannot fully anticipate.
**Confidence:** MEDIUM
**Expert review:** Expert working session — assumptions need expert judgment before finalizing

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** That, on dermoscopic images meeting the defined quality gate and acquisition configurations tested, in adults with suspicious/changing pigmented lesions across the enrolled sites, the locked model — as an assistive adjunct — stratifies melanoma risk at a sensitivity/specificity characterized against histopathology and against a defined clinician comparator, with quantified performance in each pre-specified subgroup (skin tone, site, subtype) and a characterized abstention rate.
**DOES NOT CERTIFY:**
- Autonomous diagnosis or safe rule-out of melanoma without clinician review.
- Performance on lesion types, anatomic sites, skin tones, dermatoscopes, or teledermatology cameras not represented in the study.
- Any physiological/biological ground truth beyond the histopathology reference — which is itself label-limited by inter-pathologist discordance.
- Regulatory clearance or any specific FDA pathway/predicate (not established here).
- Performance on non-pigmented lesions or pediatric populations.
- Clinical outcome benefit (mortality, biopsy-rate reduction) unless a dedicated outcome study is run.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*