# Clinical Validation Specification

**Generated:** 2026-07-11
**Source:** Live retrieval — ClinicalTrials.gov, openFDA, PubMed (+ web search where noted)

## Inputs
- **AI model:** CNN-stem → ViT-encoder hybrid classifying dermoscopic images with fused patient metadata (site, age, sex) as tokens; SSL contrastive pretraining; balanced skin-tone/lesion-type sampler; outputs malignancy probability + seven-point-checklist attributes + MC-dropout uncertainty/abstention.
- **Clinical use case:** Binary benign vs. malignant classification of pigmented lesions with interpretable morphologic attributes and an uncertainty flag.
- **Patient population:** Adults presenting with suspicious or changing pigmented skin lesions.
- **Healthcare setting:** Dermatology outpatient clinics and teledermatology triage.
- **Intended clinical claim (INFERRED — team must confirm):** "As a concurrent decision-support aid, the model flags pigmented dermoscopic lesions as suspicious for melanoma to assist a qualified clinician's biopsy/referral decision." This is the most defensible framing: an **adjunctive, clinician-in-the-loop triage/CADx tool**, NOT an autonomous diagnostic or "rule-out biopsy" device. Any stronger claim (autonomous diagnosis, replacing histopathology, standalone teledermatology disposition) requires substantially higher evidence and is not supported by what was retrieved.

## Output at a Glance

| Field | Output summary |
|---|---|
| 1. Study Design | Prospective, multi-site reader study (clinician unaided vs. AI-aided) + external validation on unseen sites; not a single retrospective held-out split. |
| 2. Sensor / Input Validation | Dermoscope hardware/optics heterogeneity (polarized vs. non-polarized, magnification, vendor, teledermatology capture) is a pre-condition; image-acquisition validity must be established first. |
| 3. Performance Benchmarks | No FDA-cleared benchmark retrieved; literature reports high accuracy but on curated public sets. Sensitivity for melanoma is the safety-critical metric — must be set by study team vs. clinician reference. |
| 4. Ground Truth | Histopathology on biopsied lesions; expert-consensus dermoscopy + follow-up for non-biopsied benign lesions. Label noise (interobserver pathology variance) caps achievable performance. |
| 5. Sample Size | No retrieved sample-size precedent; must be powered on melanoma sensitivity with adequate malignant-case count and rare-subgroup enrollment — set by team statistician. |
| 6. Subgroups | Fitzpatrick skin tone (esp. IV–VI), acral/nail/mucosal sites, amelanotic melanoma, dermoscope type — all pre-specified. |
| 7. Regulatory Pathway | Likely FDA Class II via De Novo / 510(k) as a CADx software device; no on-point dermatology-AI predicate retrieved in this pull. Regulatory counsel required. |
| 8. Post-Deployment Monitoring | Track dataset/scanner drift, abstention rate, subgroup sensitivity, missed-melanoma feedback loop; MAUDE-style event capture. |

---

## 1. Study Design
**Recommendation:** Run a **prospective, multi-site clinical validation** with two components: (a) a **standalone** performance study on consecutively enrolled lesions with definitive ground truth, and (b) a **multi-reader multi-case (MRMC) reader study** comparing clinician performance unaided vs. AI-aided, since the inferred claim is adjunctive. External validation must use sites/dermoscopes NOT represented in training. A retrospective enrichment arm can supplement rare classes but cannot be the primary evidence.
**Rationale:** The retrieved literature is almost entirely **retrospective single-dataset model-development work** (e.g., hybrid CNN-transformer classifiers on curated dermoscopy: PMID 36611363, PMID 36037629, PMID 42014488, PMID 41888268 which itself uses metadata fusion analogous to this model). None report prospective clinical deployment or reader-study designs. This is exactly the evidence gap a validation spec must close: technical accuracy on ISIC-style archives does not establish clinical utility in an outpatient/teledermatology workflow. No matching prospective NCT was retrieved for this model class. The adjunctive claim demands a reader study because the endpoint is *clinician + AI* decision quality, not model accuracy in isolation.
**Confidence:** MEDIUM — design principles are well-established for imaging CADx; no directly matching prospective trial was retrieved.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 2. Sensor / Input Validation (Pre-Condition)
**Recommendation:** Before any diagnostic claim, establish **dermoscopic image-acquisition validity** across the hardware and capture conditions the model will actually see: polarized vs. non-polarized dermoscopy, contact vs. non-contact, magnification, vendor/optics, illumination, and — critically for teledermatology — **smartphone-attached dermatoscopes and remote image quality** (compression, focus, color calibration). Pre-specify automated input-quality gating and quantify performance degradation as image quality drops.
**Rationale:** The model's entire signal is the dermoscopic image; morphologic attributes (atypical network, blue-white veil) are optics-dependent and shift with polarization mode and color rendition. Retrieved recalls show device-integrity failures in dermatology hardware (laser power degradation, Z-1396-2019; sterility/package failures, Z-1381-2019) — a reminder that hardware variance is real and consequential, though those are treatment lasers, not imaging. No dermoscope-imaging input-validation study was retrieved. Teledermatology triage adds an uncontrolled acquisition environment that must be validated separately from in-clinic capture. Label/attribute reliability is meaningless if the input optics differ from training.
**Confidence:** MEDIUM — the threat is physics-grounded and specific; no retrieved study quantifies it for this model.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 3. Performance Benchmarks
**Recommendation:** Pre-specify **melanoma sensitivity as the primary safety metric** (missing melanoma is the high-harm error), with specificity as the efficiency co-primary, benchmarked against **board-certified dermatologists reading the same lesions** rather than against a fixed numeric target. Report the operating point, ROC/AUC, and — because the model abstains — performance on the *non-abstained* population plus the abstention rate. **No FDA-recognized numeric benchmark was retrieved; any target must be set by the study team/expert panel.**
**Rationale:** Retrieved papers report high accuracy/AUC on public archives (e.g., PMID 36611363, PMID 37627864, PMID 42036423), but these are **curated-dataset metrics, not clinical benchmarks**, and are inflated by dataset selection and clean acquisition. I will not import any of those numbers as a target — none is a regulatory standard. The clinically meaningful comparator is dermatologist performance in the same setting, established within the reader study (Field 1).
**Confidence:** MEDIUM — clear that sensitivity is the anchor metric; no retrieved benchmark number is usable as a target.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 4. Ground Truth Strategy
**Recommendation:** Use a **tiered reference standard**: (a) **histopathology** on all biopsied/excised lesions as the primary truth for malignancy; (b) for non-biopsied lesions judged benign, require **expert dermoscopic consensus plus documented clinical follow-up** (e.g., stability at a pre-specified interval) to avoid verification bias. Adjudicate pathology by ≥2 dermatopathologists with a tiebreaker, and **quantify interobserver agreement**. Auxiliary seven-point-checklist attributes need a separate expert-annotated reference.
**Rationale:** Dermatopathology has documented interobserver variability, especially for melanocytic/borderline lesions — so the **label is noisy and this caps achievable sensitivity/specificity**; the team must report the label-agreement ceiling. Verification bias is a specific hazard here: benign lesions are rarely biopsied, so a biopsy-only truth set skews the spectrum. No retrieved record specifies a reference-standard protocol for this model. The retrieved literature typically inherits archive labels (ISIC/HAM-style) without independent adjudication — insufficient for a clinical claim.
**Confidence:** MEDIUM — standard is well-understood; label-noise magnitude for this cohort not retrieved.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 5. Sample Size
**Recommendation:** Power the study on the **primary melanoma-sensitivity endpoint** with a pre-specified lower confidence bound, ensuring enough **confirmed malignant cases** (melanoma is low-prevalence, so total enrollment is driven by malignant-case count) and enough cases within each subgroup (Field 6) to estimate subgroup sensitivity, not just pool it. For the MRMC arm, power across both readers and cases. **No sample-size precedent was retrieved; the specific N must be computed by the study statistician** against the chosen sensitivity target and expected prevalence.
**Rationale:** No retrieved trial (no matching NCT) or FDA summary provides an enrollment figure for this device class in this pull. The retrieved model-development papers report dataset sizes but those are training-set counts, not clinically powered validation cohorts, and cannot be used as sample-size justification. I will not invent an N.
**Confidence:** LOW — no retrieved anchor for enrollment.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 6. Subgroup Requirements
**Recommendation:** Pre-specify and independently power (or at minimum pre-register with reporting) these subgroups: **Fitzpatrick skin tone, with explicit enrollment of IV–VI**; **anatomically hard sites** (acral, subungual/nail, mucosal, facial); **amelanotic/hypomelanotic melanoma**; **age extremes within the adult range**; and **dermoscope type / capture modality** (in-clinic vs. teledermatology). Report subgroup melanoma sensitivity separately.
**Rationale:** This is a physiology/optics threat, not a fairness afterthought: public dermoscopy archives underrepresent darker skin and non-standard sites, so a balanced *training* sampler (as this model uses) does NOT guarantee validated *performance* — it must be demonstrated on real subgroup data. Amelanotic melanoma is a known high-miss category for pigment-pattern models. The retrieved literature centers on ISIC-type data with limited skin-tone diversity and does not report skin-tone-stratified clinical performance (e.g., PMID 41888268 fuses metadata but validation-set tone diversity is not established in the record). Balanced training reduces but cannot certify subgroup validity.
**Confidence:** MEDIUM — threats are concrete and known; subgroup performance for this model not retrieved.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## 7. Regulatory Pathway
**Recommendation:** Treat as an **FDA Class II software-as-a-medical-device CADx** for lesion assessment, most plausibly via **De Novo** (if no suitable predicate) or **510(k)** if a dermatology CADx predicate is identified; the adjunctive, clinician-in-the-loop framing keeps it out of autonomous-diagnosis territory. Anchor claims language to the adjunctive claim only. **No on-point dermatology-AI predicate/product code was retrieved in this pull** — the returned dermatology 510(k)s are surgical lasers and culture plates (K862862, K861301, K862864), and the "outpatient" hits are cardiac telemetry (product code QYX, 870.1025) and unrelated management systems (K123671) — none is a valid predicate for pigmented-lesion CADx.
**Rationale:** The pipeline did not retrieve a matching dermatology image-CADx classification/product code, and it explicitly did NOT query some FDA endpoints; **absence here is not evidence that no predicate exists** (real-world dermatology-AI clearances have occurred and must be searched directly in the FDA databases). The MAUDE/recall records retrieved are treatment-laser safety signals, informative for post-market thinking (Field 8) but irrelevant to this software pathway. Claims must not be finalized on this thin regulatory retrieval.
**Confidence:** LOW — no matching predicate or product code retrieved; pathway inferred from device class logic.
**Expert review:** Expert working session — regulatory counsel required before any claims language is finalized.

## 8. Post-Deployment Monitoring
**Recommendation:** Implement continuous monitoring for: **dataset/acquisition drift** (new dermoscope models, teledermatology capture changes), **subgroup sensitivity tracking** over time (esp. skin tone IV–VI and rare sites), **abstention-rate stability** (a rising MC-dropout abstention rate signals distribution shift), and a **closed-loop missed-melanoma surveillance** process linking flagged-benign lesions to later biopsy/outcome. Establish an adverse-event capture process analogous to MAUDE for false-negative harm.
**Rationale:** MAUDE and recall records in this pull (Injury/Malfunction reports 2914019-2008-00005/-00010; recalls Z-1396-2019, Z-1381-2019) illustrate the post-market safety-reporting apparatus for dermatology devices and the reality of field failures — the model needs an equivalent failure-detection loop, since a false-negative melanoma is a delayed-harm event that won't surface without active follow-up. Drift is a documented risk for imaging models when scanner/optics change. No post-deployment monitoring plan for this model was retrieved.
**Confidence:** MEDIUM — monitoring principles established; specifics for this deployment not retrieved.
**Expert review:** Expert working session — assumptions need expert judgment before finalizing.

## What This Validation Certifies — and What It Does Not
**CERTIFIES:** A passing study would establish that, **as a concurrent adjunct to a qualified clinician**, the model's malignancy flag improves (or non-inferiorly matches at higher efficiency) clinician melanoma-detection sensitivity on pigmented dermoscopic lesions in adults, on the specific dermoscope hardware, capture modalities, sites, and skin-tone subgroups actually enrolled, against a histopathology-anchored reference standard.
**DOES NOT CERTIFY:**
- Autonomous diagnosis or any use replacing clinician judgment or histopathology.
- Performance on skin tones, anatomic sites (acral/nail/mucosal), amelanotic melanoma, or dermoscope/teledermatology capture types **not** enrolled.
- Accuracy beyond the label-noise ceiling set by dermatopathology interobserver variability.
- Standalone teledermatology disposition without image-quality validation (Field 2).
- Regulatory clearance — no valid predicate/pathway was confirmed in this retrieval.
- That balanced-sampler training equates to validated subgroup equity — that requires the subgroup data.

## Footer
*Output generated from live retrieval (ClinicalTrials.gov, openFDA device classification / 510(k)/De Novo / PMA / MAUDE / recalls, openFDA drug/biologic pathways where applicable — Drugs@FDA / SPL labeling / FAERS, and the Europe PMC / OpenAlex / Semantic Scholar / PubMed literature layer) and, where noted, web search. Cited identifiers should be verified before use. Benchmark numbers are literature-derived, not regulatory standards. Every field requires expert review before clinical or commercial application.*