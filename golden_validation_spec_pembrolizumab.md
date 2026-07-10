# Grounded Clinical AI Validation Specification
## System under evaluation: Algorithm-plus-assay companion diagnostic selecting cancer patients for pembrolizumab (anti–PD-1)

*Every identifier below was retrieved and resolved this session: PMIDs → PubMed eutils; DOIs → Crossref; PMA/510(k)/DEN/product codes → openFDA device endpoints; NCT IDs → ClinicalTrials.gov API v2; drug records → openFDA Drugs@FDA / labeling. Numeric values are tagged **[retrieved-from-source]** or **[study-defined-placeholder]**.*

---

### 1. Study Design

**Recommendation.** Validate as a **companion diagnostic (CDx)**: the algorithm's output (PD-L1 score / TMB / MSI status) is the *test*, and its clinical validity must be established by linking the test result to pembrolizumab benefit in the intended tumor type(s). Use a design that ties test-positive vs test-negative strata to a treatment-effect readout — either (a) a prospective–retrospective analysis of banked specimens from a randomized pembrolizumab-vs-chemo trial (biomarker-stratified), or (b) a single-arm registrational cohort in a tissue-agnostic indication where the biomarker itself defines eligibility. Analytical validation of the assay/algorithm (Field 2) must precede and gate clinical-validity analysis. Include an assay/specimen-adequacy gate as a pre-analytic inclusion criterion.

**Rationale.** The pivotal pembrolizumab biomarker programs establish the accepted templates. KEYNOTE-024 randomized PD-L1 tumor-proportion-score-high NSCLC to pembrolizumab vs platinum chemotherapy — the biomarker-stratified RCT template (PMID 27718847; DOI 10.1056/NEJMoa1606774; NCT02142738). KEYNOTE-158 (basket, single-arm) grounded the tissue-agnostic TMB-high and MSI-H indications (PMID 32919526, 10.1016/S1470-2045(20)30445-9; PMID 31682550, 10.1200/JCO.19.02105; NCT02628067). KEYNOTE-177 provides the randomized MSI-H colorectal template (PMID 33264544, 10.1056/NEJMoa2017699; NCT02563002). Reporting should follow TRIPOD+AI for the prediction-model component (PMID 38626948, 10.1136/bmj-2023-078378) and STARD-AI for the diagnostic-accuracy component (PMID 40954311, 10.1038/s41591-025-03953-8).

**Confidence.** HIGH — multiple resolved randomized and single-arm registrational precedents.

**Expert review needed.** Biostatistician + regulatory affairs to fix whether a prospective–retrospective RCT stratification or a single-arm basket is appropriate for the *specific* claimed tumor type(s), and to pre-specify the test-positive cutoff before unblinding.

---

### 2. Input / Signal Validation (analytical validation — the pre-condition)

**Recommendation.** Before any algorithm output is interpreted, demonstrate that the **input measurement** agrees with a reference standard: (i) assay analytical validation — antibody clone/staining reproducibility for IHC, or limit-of-detection, orthogonal-concordance and reproducibility for NGS-derived TMB/MSI; (ii) for digital-pathology image inputs, scanner/image-quality QC and a specimen-adequacy gate (tumor cellularity, tissue area, focus) that rejects inadequate inputs; (iii) inter-reader / inter-assay concordance. Report positive-percent and negative-percent agreement vs the reference assay **[study-defined-placeholder thresholds — set a priori]**.

**Rationale.** PD-L1 IHC is assay- and clone-dependent: the Blueprint comparability studies showed the 22C3, 28-8, SP263 and SP142 assays are *not* freely interchangeable (Phase 1: PMID 27913228, 10.1016/j.jtho.2016.11.2228; real-world Phase 2: PMID 29800747, 10.1016/j.jtho.2018.05.013), which is why the CDx assay itself is regulated (22C3 pharmDx, PMA P150013). For TMB, cross-panel harmonization is non-trivial — the Friends of Cancer Research in-silico harmonization work defines how panel-derived TMB must be aligned to a reference (PMID 32217756, 10.1136/jitc-2019-000147). The original 22C3 companion-diagnostic development paper documents the analytical-validation expectations for the IHC input (PMID 27333219, 10.1097/PAI.0000000000000408). For image inputs, whole-slide-image analysis at clinical grade requires the input-quality controls described by Campanella et al. (PMID 31308507, 10.1038/s41591-019-0508-1).

**Confidence.** HIGH — analytical non-interchangeability and harmonization needs are directly documented.

**Expert review needed.** Pathology + assay-development lead to set concordance thresholds and the specimen-adequacy gate criteria for the exact specimen type (FFPE tissue vs image vs liquid).

---

### 3. Performance Benchmarks

**Recommendation.** Report **two tiers**: (a) *analytical* agreement of the algorithm output vs the reference CDx assay (PPA/NPA/OPA, reproducibility) and (b) *clinical validity* — differential treatment benefit in test-positive vs test-negative strata (ORR, PFS, OS hazard ratios). Do **not** hardcode any accuracy or effect-size number as an established acceptance standard; all acceptance thresholds are **[study-defined-placeholder]** and must be pre-registered.

**Rationale.** No FDA-published universal numeric accuracy floor exists for this device class (see Expected Conclusions). Effect sizes that *have been observed* in the grounding trials are context-specific, not acceptance criteria — e.g., KEYNOTE-024's PD-L1-high OS/PFS advantage (PMID 27718847) and the tissue-agnostic ORRs in TMB-high / MSI-H cohorts of KEYNOTE-158 (PMID 32919526; PMID 31682550). These are **[retrieved-from-source]** as historical context for powering, not thresholds to declare as standards.

**Confidence.** MEDIUM — precedent effect sizes are firmly grounded, but there is no single retrievable numeric acceptance benchmark to cite.

**Expert review needed.** Clinical + statistics to translate the intended claim into pre-specified acceptance thresholds and to decide whether OS, PFS, or ORR is the primary clinical-validity endpoint.

---

### 4. Ground Truth Strategy

**Recommendation.** Two reference standards, matching the two tiers: (a) for the input/test, the **validated companion-diagnostic assay** (e.g., PD-L1 IHC 22C3 pharmDx, PMA P150013; or an FDA-authorized NGS panel for TMB/MSI — FoundationOne CDx, PMA P170019; MSK-IMPACT, DEN170058) read under its scoring algorithm; (b) for clinical validity, **clinical outcome** on pembrolizumab (response by RECIST / survival). Pre-specify how discordant reference calls are adjudicated.

**Rationale.** The regulated CDx assay is the established analytical reference (P150013 verified, Agilent; P170019 verified, Foundation Medicine; DEN170058 verified, MSK-IMPACT De Novo). Clinical-outcome ground truth is what the pivotal trials used to establish that the biomarker selects benefit (KEYNOTE-024/158/177, PMIDs 27718847 / 32919526 / 33264544). MSI/MMR reference-standard testing conventions are covered in the KEYNOTE-158 and KEYNOTE-164 reports (PMID 31682550; PMID 31725351, 10.1200/JCO.19.02107).

**Confidence.** HIGH.

**Expert review needed.** Molecular pathology to lock the specific reference assay per biomarker and the discordance-adjudication rule.

---

### 5. Sample Size

**Recommendation.** Power the clinical-validity comparison on the treatment-effect endpoint within the test-positive stratum (and, where relevant, a test-negative contrast), not on raw classifier accuracy. Anchor enrollment magnitude to the grounding trials as **[retrieved-from-source]** reference points and inflate for the specimen-adequacy gate dropout **[study-defined-placeholder]**.

**Rationale.** Retrieved enrollment counts give realistic anchors: KEYNOTE-024 enrolled 305 (NCT02142738), KEYNOTE-177 enrolled 307 (NCT02563002), KEYNOTE-164 enrolled 124 (NCT02460198), and the KEYNOTE-158 basket enrolled 1609 across cohorts (NCT02628067) — all **[retrieved-from-source]** from ClinicalTrials.gov this session. A basket/tissue-agnostic claim needs the larger multi-cohort footprint; a single-tumor-type claim can be smaller.

**Confidence.** MEDIUM — enrollment anchors are exact, but the required N depends on the effect size and endpoint chosen in Fields 1/3.

**Expert review needed.** Biostatistician for the formal power calculation once endpoint and minimum detectable effect are fixed.

---

### 6. Subgroup Requirements

**Recommendation.** Pre-specify performance reporting across **tumor type** (critical for tissue-agnostic claims), **ancestry/race**, **sex**, **age**, **specimen type** (biopsy vs resection vs cytology; tissue vs image vs liquid), and **assay/scanner platform**. Report whether the test-positive definition performs consistently across these strata; flag any subgroup where the specimen-adequacy gate rejects disproportionately.

**Rationale.** The tissue-agnostic approvals rest on demonstrating benefit *across* multiple tumor types within the biomarker-defined group (KEYNOTE-158 basket, PMID 32919526 / 31682550). Assay-platform subgrouping is mandated by the demonstrated non-interchangeability of PD-L1 assays (Blueprint, PMID 27913228 / 29800747) and TMB panel-dependence (PMID 32217756). STARD-AI (PMID 40954311) and TRIPOD+AI (PMID 38626948) both require subgroup/fairness reporting for AI-enabled tests.

**Confidence.** HIGH for tumor-type and platform subgrouping; MEDIUM for ancestry (precedent trials under-report ancestry-stratified biomarker performance).

**Expert review needed.** Epidemiology / health-equity reviewer to set minimum subgroup sizes and the ancestry-representation floor, since the grounding trials do not establish one.

---

### 7. Regulatory Pathway

**Recommendation.** **Class III PMA companion diagnostic** is the established pathway for an assay that selects patients for pembrolizumab. The device class depends on the biomarker modality: PD-L1 IHC and NGS CDx panels are Class III PMA; a De Novo route exists for a novel NGS tumor-profiling reference (MSK-IMPACT). A digital-pathology **image-management/viewing** component is separately a Class II device (product code QKQ). Co-development and contemporaneous CDx labeling with the drug (BLA125514 / BLA761467) is required.

**Rationale — all resolved via openFDA this session:**
- Product code **PLS** — "Immunohistochemistry Assay, Antibody, Programmed Death-Ligand 1", **device class 3** (verified). Assays: PD-L1 IHC 22C3 pharmDx **P150013** (Agilent); VENTANA PD-L1 SP142 **P160002** (Ventana).
- Product code **PQP** — "Next Generation Sequencing Oncology Panel… Variant Detection System", **device class 3** (verified). Panels: FoundationOne CDx **P170019**; FoundationOne Liquid CDx **P190032** / **P200006** (Foundation Medicine).
- **DEN170058** — MSK-IMPACT, De Novo (Memorial Sloan Kettering), verified — the De Novo precedent for a tumor-profiling reference.
- Product code **QKQ** — "Digital Pathology Image Viewing and Management Software", **device class 2** (verified) — the pathway for the image-handling component.
- Drug side: pembrolizumab **BLA125514** (KEYTRUDA, Merck) and **BLA761467** (KEYTRUDA QLEX, Merck), both verified in Drugs@FDA; current label set_id 097d166f-b73b-41d3-9b37-7653cd2a0c41.

**Confidence.** HIGH.

**Expert review needed.** Regulatory affairs to confirm the exact product code and whether the algorithm is a new CDx PMA, a PMA supplement to an existing panel, or a De Novo — and to align CDx labeling with the drug label.

---

### 8. Post-Deployment Monitoring

**Recommendation.** Implement (i) continuous **specimen-adequacy-gate** monitoring (rejection rate by site/scanner/specimen type), (ii) assay/scanner lot-to-lot and platform drift surveillance, (iii) periodic re-concordance against the reference CDx assay, (iv) subgroup-stratified performance tracking (tumor type, ancestry, platform), and (v) an FDA medical-device-reporting / recall linkage for the device and adverse-outcome signals tied to test-directed treatment decisions.

**Rationale.** Assay non-interchangeability and platform drift (Blueprint, PMID 27913228 / 29800747; TMB harmonization, PMID 32217756) mean a CDx that passed at launch can degrade with reagent lots, scanners, or software updates. TRIPOD+AI (PMID 38626948) and STARD-AI (PMID 40954311) both call for monitoring of AI model performance after deployment. openFDA device adverse-event / recall endpoints (same infrastructure used to verify the PMA/510(k) records here) provide the surveillance data source.

**Confidence.** MEDIUM — monitoring *principles* are well grounded; no single retrievable numeric drift-threshold standard exists, so trigger thresholds are **[study-defined-placeholder]**.

**Expert review needed.** Quality/regulatory + clinical to set drift-alert thresholds and the re-validation cadence.

---

## SOURCE INVENTORY

### Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| KEYNOTE-024: pembrolizumab vs chemo, PD-L1-high NSCLC (biomarker-stratified RCT) | PMID 27718847 · 10.1056/NEJMoa1606774 | 1, 3, 5 |
| KEYNOTE-158: TMB-high tissue-agnostic outcomes (basket) | PMID 32919526 · 10.1016/S1470-2045(20)30445-9 | 1, 3, 6 |
| KEYNOTE-158: MSI-H noncolorectal, tissue-agnostic efficacy | PMID 31682550 · 10.1200/JCO.19.02105 | 1, 4, 6 |
| KEYNOTE-177: pembrolizumab in MSI-H metastatic colorectal (RCT) | PMID 33264544 · 10.1056/NEJMoa2017699 | 1, 4, 5 |
| KEYNOTE-164: pembrolizumab in MSI-H/dMMR colorectal (phase II) | PMID 31725351 · 10.1200/JCO.19.02107 | 4 |
| Companion-diagnostic PD-L1 22C3 IHC assay development | PMID 27333219 · 10.1097/PAI.0000000000000408 | 2 |
| Blueprint PD-L1 IHC comparability, Phase 1 (assay non-interchangeability) | PMID 27913228 · 10.1016/j.jtho.2016.11.2228 | 2, 6, 8 |
| Blueprint PD-L1 IHC comparability, Phase 2 (real-life samples) | PMID 29800747 · 10.1016/j.jtho.2018.05.013 | 2, 6, 8 |
| Friends of Cancer Research TMB harmonization (in-silico) | PMID 32217756 · 10.1136/jitc-2019-000147 | 2, 6, 8 |
| TRIPOD+AI reporting guidance for clinical prediction models | PMID 38626948 · 10.1136/bmj-2023-078378 | 1, 6, 8 |
| STARD-AI reporting guideline for AI diagnostic-accuracy studies | PMID 40954311 · 10.1038/s41591-025-03953-8 | 1, 6, 8 |
| Clinical-grade computational pathology on whole-slide images | PMID 31308507 · 10.1038/s41591-019-0508-1 | 2 |

*All 12 PMIDs resolved via PubMed esummary; all 12 DOIs returned HTTP 200 with matching titles from Crossref this session.*

### FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number / PMA-number) | Grounded field(s) |
|---|---|---|
| PD-L1 IHC antibody assay class (Class III) | product code **PLS** | 2, 4, 7 |
| NGS oncology panel, somatic/germline variant system (Class III) | product code **PQP** | 4, 7 |
| Digital pathology image viewing & management software (Class II) | product code **QKQ** | 7, 8 |
| PD-L1 IHC 22C3 pharmDx (Agilent) — pembrolizumab CDx | PMA **P150013** | 2, 4, 7 |
| VENTANA PD-L1 (SP142) Assay (Ventana) | PMA **P160002** | 2, 7 |
| FoundationOne CDx (Foundation Medicine) — TMB/NGS CDx | PMA **P170019** | 4, 7 |
| FoundationOne Liquid CDx (Foundation Medicine) | PMA **P190032** | 4, 7 |
| FoundationOne Liquid CDx (Foundation Medicine) | PMA **P200006** | 4, 7 |
| MSK-IMPACT NGS tumor-profiling (MSKCC) — De Novo precedent | De Novo **DEN170058** | 4, 7 |
| Pembrolizumab (KEYTRUDA, Merck) — biologic | BLA **125514** | 7 |
| Pembrolizumab (KEYTRUDA QLEX, Merck) — biologic | BLA **761467** | 7 |

*All PMA/DEN records and product codes resolved via openFDA device PMA / classification / 510(k) endpoints; both BLA numbers resolved via openFDA Drugs@FDA (sponsor: Merck Sharp Dohme) this session.*

### Trial registry use (ClinicalTrials.gov, API v2)

- **NCT02142738** (KEYNOTE-024, PHASE3, COMPLETED, enrollment 305) — informed Fields 1, 5.
- **NCT02628067** (KEYNOTE-158, PHASE2, ACTIVE_NOT_RECRUITING, enrollment 1609) — informed Fields 1, 5, 6 (tissue-agnostic footprint).
- **NCT02563002** (KEYNOTE-177, PHASE3, COMPLETED, enrollment 307) — informed Fields 1, 5.
- **NCT02460198** (KEYNOTE-164, PHASE2, COMPLETED, enrollment 124) — informed Field 5.
All four resolved this session with status, phase, and enrollment retrieved directly.

### Expected conclusions

- **Regulatory class/pathway:** the patient-selection assay is a **Class III PMA companion diagnostic** (PD-L1 IHC → code PLS; NGS TMB/MSI panel → code PQP), with a **De Novo** precedent for a novel NGS tumor-profiling reference (DEN170058) and a separate **Class II** pathway (code QKQ) for the digital-pathology image-handling component. CDx must be co-labeled with pembrolizumab (BLA125514 / BLA761467).
- **Regulatory NULL result:** *No FDA marketing authorization was found this session for a standalone algorithm that predicts pembrolizumab response directly from a digital-pathology image without an underlying authorized assay.* The authorized devices are the assays (PLS/PQP PMAs) and image-management software (QKQ); an image-only immunotherapy-response predictor as its own CDx was not located in openFDA. Searches for device_name "immunotherapy" and "whole slide imaging" returned no matching authorization.
- **Established numeric benchmark:** **None exists.** No universal FDA-published numeric accuracy floor or effect-size acceptance threshold for this device class was retrievable. All acceptance thresholds must be pre-specified per submission; observed trial effect sizes are historical context, not standards.

### Sources I wanted but could not access (coverage gaps)

- **FDA "List of Cleared or Approved Companion Diagnostic Devices (In Vitro and Imaging Tools)"** — this is a curated FDA web page, not an API endpoint; I verified the individual PMA/DEN records via openFDA but could not machine-query the consolidated CDx list to confirm the *drug-pairing* label linkage programmatically.
- **Full-text structured drug-label indication/CDx section** — I resolved the KEYTRUDA label set_id (097d166f-b73b-41d3-9b37-7653cd2a0c41) but did not parse the label's indication text to extract the exact biomarker cutoffs (e.g., TPS/CPS thresholds); those numeric cutoffs are therefore **not** asserted here as retrieved.
- **CDRH summaries of safety and effectiveness (SSED PDFs)** — the per-PMA effectiveness data (which would supply real analytical PPA/NPA numbers for Field 3) are PDF documents outside the openFDA JSON schema and were not retrieved.
- **NCCN / CAP-ASCP molecular testing guidelines** — not available through the four permitted APIs; MSI/PD-L1 testing conventions were grounded via PubMed primary literature instead.
