# Clinical AI Validation Specification — Reference Answer Key

**System under evaluation:** Over-the-counter / direct-to-consumer algorithm that analyzes a
single-lead ECG waveform (plus a PPG irregular-rhythm signal, behind a signal-quality/wear gate)
recorded on a consumer wearable, to flag possible atrial fibrillation (AFib) and notify the wearer.
**Intended use:** screening/notification prompting clinical confirmation — NOT a diagnosis and NOT a
substitute for a 12-lead ECG or clinician judgment. **Setting:** ambulatory, unsupervised.
**Population:** adults without prior AFib diagnosis, across ages, skin tones, wrist sizes, activity states.

> Grounding note: every identifier below was retrieved AND resolved this session
> (PMID→PubMed E-utilities; DOI→Crossref; product code / K-number / DEN-number→openFDA; NCT→ClinicalTrials.gov v2 API).
> Numbers are tagged **[retrieved-from-source]** or **[study-defined-placeholder]**.
> No numeric threshold below is asserted as an FDA-established pass/fail standard, because none exists (see Expected conclusions).

---

## 1. Study Design

**Recommendation.** Run a prospective, multi-site diagnostic-accuracy study in the intended
unsupervised ambulatory setting, structured in two tiers that mirror the two authorized product
families: (a) a **PPG irregular-rhythm-notification (IRN) arm** evaluated as a screening pathway
whose endpoint is confirmation of AFib on a reference monitor after a notification, and (b) an
**on-demand single-lead ECG arm** evaluated as a rhythm classifier (AFib vs sinus vs
inconclusive) against a reference tracing. Enrollment should be prospective and community-based
(not a clinic convenience sample), because the DTC claim is about self-selected asymptomatic wearers.

**Rationale.** This two-arm design follows the precedent set by the pivotal wearable AFib studies:
the Apple Heart Study assessed a wrist PPG notification pathway with post-notification ambulatory-ECG
patch confirmation in a self-enrolled population (PMID 31722151, DOI 10.1056/NEJMoa1901183; registered
NCT03335800, N=419,927 [retrieved-from-source]), and the Fitbit Heart Study used the same
notification-then-confirmation architecture (PMID 36148649, DOI 10.1161/CIRCULATIONAHA.122.060291;
design paper PMID 33865810, DOI 10.1016/j.ahj.2021.04.003; software-validation registration
NCT04176926, N=472 [retrieved-from-source]). The mSToPS trial (PMID 29998336, DOI 10.1001/jama.2018.8102;
NCT02506244, N=6,135 [retrieved-from-source]) and Heartline (NCT04276441, N=34,244 [retrieved-from-source])
establish that outcome/effectiveness context for wearable AFib screening is evaluated in large pragmatic
enrollments, distinct from the smaller signal-level validation cohort.

**Confidence: HIGH** — the design pattern is directly evidenced by the FDA-authorized predicate devices
and their published pivotal studies.

**Expert review needed.** A cardiac electrophysiologist and a diagnostic-study biostatistician should
confirm the split between the signal-validation cohort (Field 2/5) and the screening-yield cohort, and
whether an outcomes co-primary (e.g., time-to-diagnosis) is in scope.

---

## 2. Input / Signal Validation

**Recommendation.** Before any accuracy claim, validate the **input measurement** itself: (i) the
single-lead wearable ECG waveform must be shown to agree with a simultaneously recorded reference
ECG (e.g., a clinical single-lead or 12-lead tracing) at the level of interpretable morphology, and
(ii) the signal-quality/wear-detection gate must be characterized — report the proportion of
recordings the gate labels "unclassifiable/poor quality" and demonstrate that the gate suppresses
low-quality PPG/ECG rather than passing it to the classifier. Treat the PPG IRN tachogram and the
ECG waveform as two separate inputs each needing its own quality gate.

**Rationale.** The regulatory definitions make signal validation a distinct pre-condition: the OTC
ECG software code specifies a device that "creates, analyzes, and displays electrocardiograph data"
(product code QDA, 21 CFR 870.2345 [retrieved-from-source, openFDA classification]), and the OTC PPG
code specifies software that "analyzes photoplethysmograph data … for identifying irregular heart
rhythms" (product code QDB, 21 CFR 870.2790 [retrieved-from-source]) — two different signals, two
different authorizations (De Novo DEN180044 for QDA and DEN180042 for QDB [retrieved-from-source,
openFDA]). Both pivotal studies report a substantial **"unclassifiable" fraction** as a first-class
result, i.e. signal quality gates a large share of recordings before rhythm interpretation (PMID
31722151; PMID 36148649). Head-to-head work shows ECG-based and PPG-based inputs have materially
different diagnostic accuracy, so each input must be validated on its own (PMID 40212135, DOI
10.1097/MS9.0000000000003155).

**Confidence: HIGH** — that input/signal quality is a separate gated pre-condition is explicit in both
the product-code definitions and the pivotal-study reporting.

**Expert review needed.** A signal-processing engineer should define the reference-agreement metric for
the raw waveform (beat-detection concordance vs. morphology) and set the acceptable unclassifiable-rate
ceiling for the wear/quality gate.

---

## 3. Performance Benchmarks

**Recommendation.** Report sensitivity, specificity, and positive predictive value (PPV) against the
reference standard **with 95% CIs**, separately for the ECG classifier and the PPG notification pathway,
and stratified by activity state. Because this is a low-prevalence screening use, PPV and the
false-notification burden are the operationally decisive metrics and must be reported at the expected
population prevalence, not at cohort prevalence. All target values are **[study-defined-placeholder]** —
prespecify them in the protocol; do not treat any as an FDA threshold.

**Rationale.** Published synthesis gives the realistic performance envelope but not a mandated cutoff:
a 2025 systematic review/meta-analysis of smartwatch AFib detection (PMID 41182224, DOI
10.1016/j.jacadv.2025.102133) and an earlier diagnostic-accuracy systematic review of smartwatch
arrhythmia detection (PMID 34448706, DOI 10.2196/28974) both report pooled sensitivity/specificity
generally in the high range but with wide heterogeneity and confidence intervals, which is why the
value must be prespecified per study rather than copied as a standard. The Apple Heart Study's headline
PPV of the notification pathway (PMID 31722151) illustrates why PPV, not sensitivity alone, governs the
DTC screening claim. ECG-vs-PPG accuracy differs enough (PMID 40212135) that a single blended benchmark
would be misleading.

**Confidence: MEDIUM** — the metrics to report are well-established; specific numeric targets are not
standardized across the literature and must be justified per protocol.

**Expert review needed.** Statistician + EP to set prespecified sensitivity/specificity/PPV targets and
the maximum tolerable false-notification rate at population prevalence.

---

## 4. Ground Truth Strategy

**Recommendation.** Use a **time-synchronized reference-ECG standard adjudicated by blinded
cardiologists**. For the PPG notification arm, the reference is an ambulatory ECG patch worn during the
window following a notification (capturing paroxysmal AFib); for the on-demand ECG arm, the reference is
a simultaneous physician-overread ECG. Adjudicators must be blinded to the device output, and an
inconclusive/uninterpretable reference category must be defined a priori.

**Rationale.** This is the ground-truth architecture of the authorized predicates: the Apple Heart Study
confirmed PPG notifications with a subsequently mailed ambulatory ECG patch and clinician overread (PMID
31722151), and the Fitbit Heart Study used the same patch-confirmation reference (PMID 36148649; design
PMID 33865810). The patch-as-reference approach itself is validated by mSToPS, which used a home ECG
patch to establish incident AFib (PMID 29998336). Guideline context confirms clinician-confirmed ECG —
not a wearable — remains the diagnostic reference standard for AFib (USPSTF statement, PMID 35076659, DOI
10.1001/jama.2021.23732).

**Confidence: HIGH** — reference standard and blinded adjudication are consistently used across all
predicate pivotal studies.

**Expert review needed.** EP to specify the post-notification patch duration and the incident-vs-prevalent
AFib definition; a study-methodologist to lock the blinding/adjudication protocol.

---

## 5. Sample Size

**Recommendation.** Power the **signal/classifier validation cohort** on the width of the specificity and
PPV confidence intervals at expected prevalence — typically hundreds of confirmed-rhythm subjects for the
ECG classifier, sized so the lower 95% CI bound clears the prespecified target. Power the **screening-yield
/ notification cohort** separately and much larger (tens of thousands), because AFib prevalence in
undiagnosed adults is low and the endpoint is confirmed notifications. All sizes below are
**[study-defined-placeholder]** anchored to precedent enrollment, not fixed requirements.

**Rationale.** The precedent enrollments (all [retrieved-from-source]) show the two-tier sizing: the
software-validation registrations are in the hundreds (Fitbit validation NCT04176926, N=472), while the
population screening/effectiveness studies are far larger (Apple Heart Study NCT03335800, N=419,927;
Heartline NCT04276441, N=34,244; mSToPS NCT02506244, N=6,135). The low event rate that drives the large
screening N is consistent with the USPSTF's characterization of asymptomatic AFib prevalence (PMID 35076659).

**Confidence: MEDIUM** — the two-tier structure and order-of-magnitude are firmly evidenced; exact N
depends on the prespecified CI width and prevalence assumption, which are protocol choices.

**Expert review needed.** Biostatistician to run the formal CI-width / precision calculation once Field 3
targets and the prevalence assumption are fixed.

---

## 6. Subgroup Requirements

**Recommendation.** Prespecify and report performance (and the unclassifiable/gate rate from Field 2)
across: **skin tone (Fitzpatrick scale)**, **wrist size / anthropometry**, **age bands**, **sex**, and
**activity/motion state**. Skin tone and motion are the highest-priority axes for a wrist PPG device and
must be enrolled to adequacy, not merely reported post hoc. Report whether the signal-quality gate
disproportionately excludes any subgroup — a differential gate rate is itself a fairness failure even if
conditional accuracy looks equal.

**Rationale.** Optical PPG accuracy and data quality are affected by skin pigmentation: a controlled study
found pigmentation influences PPG heart-rate accuracy and data quality (PMID 40968160, DOI
10.1007/s00421-025-05977-x), and a methods study frames fairness/bias in wrist-PPG heart-rate estimation
as an explicit evaluation axis (PMID 41875538, DOI 10.1088/1361-6579/ae56ae). Motion/activity state
degrades PPG and is the dominant source of the unclassifiable fraction seen in the pivotal studies (PMID
31722151; PMID 36148649). ECG- vs PPG-input differences (PMID 40212135) mean subgroup effects may differ
between the two arms and must be reported per arm.

**Confidence: HIGH** (that skin tone / motion / wrist size are required subgroups) —
**MEDIUM** on prescribing exact per-cell sample counts, which are protocol-defined.

**Expert review needed.** A bias/fairness methodologist plus a dermatologist to fix the Fitzpatrick
enrollment quotas and the differential-gate-rate acceptance criterion.

---

## 7. Regulatory Pathway

**Recommendation.** Pursue **FDA 510(k) clearance as a Class II device**, citing the established
product codes and a legally marketed predicate — **QDA** (Electrocardiograph Software for Over-the-Counter
Use, 21 CFR 870.2345) for the on-demand ECG classifier, and **QDB** (Photoplethysmograph Analysis Software
for Over-the-Counter Use, 21 CFR 870.2790) for the irregular-rhythm notification feature. A new De Novo is
**not** required because both device types already exist; the original De Novo grants (DEN180044 → QDA;
DEN180042 → QDB, both Apple, 2018-09-11 [retrieved-from-source]) created the classifications that now serve
as predicates.

**Rationale.** openFDA confirms both codes are Class II with active 510(k) lineages [all retrieved-from-source]:
QDA predicates include K201168 (Samsung), K200948 (Fitbit), K221774 (Garmin), K230292 (Samsung ECG with
irregular-heart-rhythm notification), K243236 (WHOOP), and K240795 (Withings); QDB predicates include
K212516 (Apple IRNF) and K212372 (Fitbit Irregular Rhythm Notifications). The De Novo-then-510(k) trajectory
(De Novo established the class in 2018; subsequent entrants cleared via 510(k)) is exactly the pathway a new
DTC entrant follows. Both product-code definitions state the device "is not intended to provide a diagnosis,"
which matches and constrains the intended claim.

**Confidence: HIGH** — pathway, class, product codes, regulation numbers, and multiple predicates are all
resolved in openFDA this session.

**Expert review needed.** A regulatory-affairs specialist to select the single most appropriate predicate
per arm and to confirm no design feature (e.g., a new autonomous-diagnosis claim) would push the device out
of QDA/QDB and trigger a De Novo/PMA.

---

## 8. Post-Deployment Monitoring

**Recommendation.** Operate a post-market surveillance program covering: (i) real-world **false-notification
rate and PPV drift** at population prevalence; (ii) the **unclassifiable/gate rate** trended over OS/firmware
and hardware revisions; (iii) **subgroup performance monitoring** (skin tone, wrist size, age) to catch
fairness regressions; (iv) mandatory **MDR adverse-event reporting** (e.g., missed AFib leading to harm, or
over-notification driving unnecessary care) through FDA MAUDE; and (v) a change-control plan for algorithm
updates, since these are software devices updated frequently.

**Rationale.** The device class is defined as software (QDA/QDB [retrieved-from-source]), and the labeled
claim is screening-with-confirmation, so the dominant post-market risks are PPV erosion and over-notification —
the same metrics the pivotal studies foregrounded (PMID 31722151; PMID 36148649). Cost-effectiveness of
wearable AFib screening is sensitive to the false-positive/confirmation cascade, underscoring why
over-notification must be monitored, not just missed cases (Fitbit Heart Study economic analysis, PMID 36003419,
DOI 10.1001/jamahealthforum.2022.2419). USPSTF's "insufficient" screening verdict (PMID 35076659) means real-world
benefit/harm evidence is expected to accrue post-market.

**Confidence: MEDIUM** — the surveillance components are well-grounded in the device class and evidence base;
specific reporting thresholds/frequencies are program design choices, not established standards.

**Expert review needed.** Regulatory + post-market surveillance lead to define the algorithm change-control
protocol (and whether a Predetermined Change Control Plan applies) and the subgroup-drift alerting thresholds.

---

# SOURCE INVENTORY

## Peer-reviewed literature

| Source (one-line description) | Identifier (PMID · DOI) | Grounded field(s) |
|---|---|---|
| Apple Heart Study — smartwatch PPG notification, patch confirmation (NEJM 2019) | PMID 31722151 · 10.1056/NEJMoa1901183 | 1, 2, 3, 4, 8 |
| Fitbit Heart Study — PPG AFib detection results (Circulation 2022) | PMID 36148649 · 10.1161/CIRCULATIONAHA.122.060291 | 1, 2, 3, 4, 8 |
| Fitbit Heart Study — rationale & design (Am Heart J 2021) | PMID 33865810 · 10.1016/j.ahj.2021.04.003 | 1, 4 |
| Fitbit Heart Study — cost-effectiveness of wearable AF screening (JAMA Health Forum 2022) | PMID 36003419 · 10.1001/jamahealthforum.2022.2419 | 8 |
| mSToPS — home wearable continuous ECG patch screening RCT (JAMA 2018) | PMID 29998336 · 10.1001/jama.2018.8102 | 1, 4, 5 |
| Smartwatch AFib detection — systematic review & meta-analysis (JACC Adv 2025) | PMID 41182224 · 10.1016/j.jacadv.2025.102133 | 3 |
| Smartwatch cardiac-arrhythmia detection — diagnostic-accuracy systematic review (JMIR 2021) | PMID 34448706 · 10.2196/28974 | 3 |
| ECG-based vs PPG-based diagnostic-accuracy comparison (Ann Med Surg 2025) | PMID 40212135 · 10.1097/MS9.0000000000003155 | 2, 3, 6 |
| USPSTF recommendation — screening for atrial fibrillation (JAMA 2022) | PMID 35076659 · 10.1001/jama.2021.23732 | 4, 5, 6, 8 |
| Skin pigmentation influence on PPG heart-rate accuracy & data quality (Eur J Appl Physiol 2026) | PMID 40968160 · 10.1007/s00421-025-05977-x | 6 |
| Fair/trustworthy heart-rate estimation from wrist PPG — bias evaluation (Physiol Meas 2026) | PMID 41875538 · 10.1088/1361-6579/ae56ae | 6 |

## FDA regulatory records

| Record | Identifier (product code / K-number / DEN-number) | Grounded field(s) |
|---|---|---|
| OTC Electrocardiograph Software (Class II, 21 CFR 870.2345) | product code **QDA** | 2, 3, 7, 8 |
| OTC Photoplethysmograph Analysis Software (Class II, 21 CFR 870.2790) | product code **QDB** | 2, 3, 7, 8 |
| Apple ECG App — De Novo that established QDA | **DEN180044** | 7 |
| Apple Irregular Rhythm Notification Feature — De Novo that established QDB | **DEN180042** | 7 |
| Samsung ECG Monitor App (510(k), QDA) | **K201168** | 7 |
| Fitbit ECG App (510(k), QDA) | **K200948** | 7 |
| Garmin ECG App (510(k), QDA) | **K221774** | 7 |
| Samsung ECG Monitor App with Irregular Heart Rhythm Notification (510(k), QDA) | **K230292** | 7 |
| WHOOP ECG Feature (510(k), QDA) | **K243236** | 7 |
| Withings ECG App (510(k), QDA) | **K240795** | 7 |
| Apple IRNF App (510(k), QDB) | **K212516** | 7 |
| Fitbit Irregular Rhythm Notifications (510(k), QDB) | **K212372** | 7 |

## Trial registry use (ClinicalTrials.gov)

- **NCT03335800** — Apple Heart Study (COMPLETED, N=419,927): informed Fields 1, 4, 5 (screening-yield cohort scale and notification→patch-confirmation design).
- **NCT04176926** — Fitbit software-validation study (COMPLETED, N=472): informed Fields 1, 5 (signal/classifier validation cohort size, distinct from the screening cohort).
- **NCT02506244** — mSToPS / mHealth Screening to Prevent Strokes (COMPLETED, N=6,135): informed Fields 4, 5 (patch reference standard, mid-scale screening enrollment).
- **NCT04276441** — Heartline (COMPLETED, N=34,244): informed Fields 1, 5 (large pragmatic outcome/effectiveness enrollment context).
- All NCT records, statuses, and enrollment counts retrieved and resolved this session via the ClinicalTrials.gov v2 API [retrieved-from-source].

## Expected conclusions

- **Regulatory class / pathway:** Class II, **510(k)** clearance, product codes **QDA** (21 CFR 870.2345, ECG arm) and **QDB** (21 CFR 870.2790, PPG-notification arm), with multiple legally marketed predicates available. No PMA required.
- **Regulatory NULL result:** No De Novo submission is needed for a new entrant — the device types already exist (originated by **DEN180044** and **DEN180042** in 2018). There is **no FDA authorization for an autonomous DTC AFib *diagnosis*** device: both QDA and QDB are explicitly defined as "not intended to provide a diagnosis," so a diagnostic (rather than screening/notification) claim has no existing clearance pathway in these codes.
- **Established numeric benchmark:** **None exists.** No FDA-mandated sensitivity/specificity/PPV threshold governs this device class; the literature provides a performance *envelope* (with wide heterogeneity) but not a standard. Every numeric target in this spec is study-defined-placeholder. Additionally, the USPSTF found evidence **insufficient** (I statement) to recommend for or against AFib screening in asymptomatic adults (PMID 35076659) — i.e., there is no guideline-endorsed screening-performance bar either.

## Sources I wanted but could not access (coverage gaps)

- **Drugs@FDA / drug labeling:** Not applicable to this device — no drug or biologic is involved. I did not query it (correctly), so drug-label grounding is intentionally absent rather than a gap.
- **openFDA PMA endpoint:** Not queried because the device is 510(k)/De Novo, not PMA; no PMA number is cited (a PMA citation here would be a false positive).
- **FDA device summary / decision documents (510(k) & De Novo PDFs) and FDA guidance documents:** openFDA exposes the structured *metadata* (applicant, dates, product code) that I verified, but the full-text summary/decision PDFs and FDA guidance documents are not available through the JSON APIs reachable this session — so specific labeled indications, tested subgroup counts, and any performance numbers stated inside those documents could NOT be verified and are therefore not cited as numeric standards.
- **FDA MAUDE (adverse-event) database:** Referenced conceptually in Field 8 but not queried this session for device-specific event counts; any real-world adverse-event rate would need separate MAUDE retrieval before citation.
- **Manufacturer clinical/validation reports and IFU documents:** Not accessible; no proprietary performance figures are cited.
