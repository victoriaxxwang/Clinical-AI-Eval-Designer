# FDA fix — F1 recon findings (free, read-only; no engine edits)

*Date 2026-07-11. Live openFDA queries (no key needed) + code read of both engines.
Tripwire `2e6d49cdaa3106b6c29ee66b5df37e58` clean. Nothing edited.*

## How the FDA search works TODAY (both engines, identical)

- `search_openfda(keyword)` (engine.py:615, engine_widenet.py:748) queries FDA's
  device **classification** + **510(k)** endpoints with a single field filter:
  `search=device_name:{term}`.
- The `term`s come from the `fda_terms` list, which is built from **device / modality
  / setting / condition keywords** — NOT the recovered disease. Even in wide-net,
  `"fda": device` (widenet:396) — the FDA term is the device modality, so **the
  disease wide-net recovers never reaches the FDA search.** This is why melanoma
  returned surgical lasers + a bacti plate in B3: the search keyed off generic
  device words, not "melanoma".
- Conclusion: the FDA gap is a **shared blind spot** in the current design; wide-net's
  disease recovery is simply not wired into the FDA path. Fixing it is a *wide-net-only*
  upgrade (only wide-net has the disease to feed in).

## What FDA data IS searchable by disease (the good news)

FDA's **classification** endpoint has product codes whose `device_name` / `definition`
literally name the disease AND the device type. Searching `device_name:<disease>` and
`definition:<disease>` on `/device/classification.json` surfaces them. Then searching
`/device/510k.json?search=product_code:<CODE>` returns the actual cleared devices under
that code — the analogous predicates a validation spec wants.

### Live results (disease → best product code → real 510(k)s)

| Disease | Right product code found | Real 510(k)s under it |
|---|---|---|
| **Diabetic retinopathy** | **PIB** — "Diabetic Retinopathy Detection Device" [Ophthalmic] | **EyeArt (K223357), AEYE-DS (K240058), IDx-DR (K203629)** — the actual real-world AI predicates 🎯 |
| **Melanoma** | **OYD** — "Optical Diagnostic Device For Melanoma Detection" [Plastic Surgery] | (code is right; the AI devices cleared via De Novo, so 510k list is sparse) |
| **Stroke** | POL — "Neurovascular Mechanical Thrombectomy…Acute Ischemic Stroke" | Trevo, Solitaire, pRESET — but these are **treatment** devices, not diagnostic AI (device-type mismatch) |
| **Tuberculosis** | PEU/MWA — nucleic-acid TB detection systems [Microbiology] | Xpert MTB/RIF — reasonable lab-analog, not imaging AI |
| **Lung nodule** | mostly noise (heart-lung machine, tumor-treatment fields) |  |
| **Colon** | mostly noise (colon markers, HSV assays) |  |

## The key insight (drives F2)

The disease→product-code→510(k) chain **works and is dramatically better than today's
generic-keyword search** — on diabetic retinopathy it lands the *exact* real predicate
devices (EyeArt, IDx-DR). BUT a raw disease term surfaces **several** product codes,
only some of which are the right *AI-diagnostic-imaging* analog:

- **Signal**: PIB (DR detection), OYD (melanoma detection) — device_name contains the
  disease AND a **detection/diagnostic** word. These are exactly what we want.
- **Noise**: electrical stimulators, shock-wave foot-ulcer devices, spinal-cord
  stimulators, antibody assays — same disease, wrong device type.

So the disease alone isn't enough; the winner is **disease + device-type intent
(imaging AI diagnostic)** → prefer the product code whose `device_name` names both the
disease and a diagnostic/detection/software signal.

Two more notes:
- Some best-in-class AI devices (melanoma, some stroke-triage) were cleared via **De Novo**
  (`DEN…`), which the 510k endpoint returns mixed in — good, still a real predicate.
- Residual off-target codes are fine downstream: **cite-or-flag already quarantines
  non-analogous predicates** (proven in B3), so imperfect targeting degrades safely.

## Options for F2 (the disease→FDA-code bridge) — decision for Victoria

1. **Curated table** — hand-map each ~10 demo disease to its right product code
   (DR→PIB, melanoma→OYD, …). Precise & gold on the demo, but manual, demo-only,
   and "hand-picked" (less impressive as an automatic capability).
2. **Fully automatic live search** — disease term → classification codes → 510(k)s,
   no hand-mapping. General to any disease, but noisier (needs no curation but returns
   the stimulator/assay noise alongside the right code).
3. **Hybrid (recommended)** — automatic live search, then **rank/prefer** product
   codes whose `device_name` names both the disease and a diagnostic/detection/software
   signal (from the intervention type), cap to top N, let cite-or-flag quarantine the
   rest. General AND lands the right predicates on the demo cases; honest about residual
   noise. Slightly more logic than #2, far more credible than #1.

**Recommendation: Option 3.** It's automatic (a real capability, not hand-waving),
grounds to the true predicate devices on the demo diseases, and stays safe via
cite-or-flag. Lives in a NEW module (or the wide-net twin) — never touches frozen
engine.py.
