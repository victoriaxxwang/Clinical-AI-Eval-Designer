# FDA fix — F5 critical finding: empty results are FALSE NEGATIVES (do not claim "open market")

*Date 2026-07-11. Answers Victoria's F5 questions. Live openFDA verified. Tripwire clean.*

## The finding

Our F3/F4 bridge searches for FDA codes/devices whose NAME or DEFINITION contains the
disease word. But **FDA clears most clinical AI models (SaMD) under GENERICALLY-named
product codes that do NOT contain the disease** — e.g. OEB/MYN ("Computer-Assisted
Detection"), QFM ("Computer-Assisted Detection Software"), QAS ("Radiological
Computer-Assisted Triage And Notification Software"). So our "no result" is a
**false negative**, not proof the market is empty. Verified:

- **Lung nodule CT AI EXISTS** (our NSCLC search returned nothing / bladder-FISH):
  AVIEW Lung Nodule CAD (K251203, K221592), Synapse Lung Nodule AI (K254075), Auto
  Lung Nodule Detection (K201560) — codes OEB/MYN/LLZ.
- **Stroke-triage AI EXISTS** (our stroke search returned only thrombectomy):
  BriefCase, Rapid ICH, qER-CTA, Brainomix 360 Triage Stroke, Rapid NCCT Stroke,
  Methinks — all under code QAS.

## Answers to Victoria's 3 questions

1. **"Did you mean clinical AI models?"** — Yes. "Imaging AI" = clinical AI models /
   AI software-as-a-medical-device (SaMD). Same thing.
2. **Why no improvement on some diseases** — the disease-NAMED FDA codes that exist
   are treatments/lab kits; the AI models exist but under generically-named CAD/triage
   codes our disease-name search doesn't reach.
3. **"Are we confident empties = no device / open market?"** — **NO. Do not claim
   open-market / first-mover from an empty result** — it would be overclaiming, and
   judges who know the space (Viz.ai, Rapid, Aidoc, Brainomix are famous) would catch
   it. The devices exist; our method just missed them.

## The fix (answers "is there another way to improve?") — YES

Add a **second search axis**: also query `/device/510k.json?search=device_name:<disease
or anatomy term>` directly, and/or sweep the known SaMD code family (OEB, MYN, QFM, QAS,
...). The recon shows this WOULD catch the lung-nodule and stroke AI devices we missed.
This turns the bridge from a **1-case win (DR only)** into a **broad win** (lung,
stroke, chest X-ray, etc. all get real AI predicates) — and removes the false-negative
overclaim risk.

## Revised F5 recommendation

GO is now stronger: with the second axis the FDA bridge is a broad, credible upgrade,
not just a DR showcase. But building it = second-axis code + re-score + wire into
wide-net + paid check = a sizable task. **Recommend COMPACT first** (context ~19%),
then build the second axis (F3b), re-score (F4b), then wire + paid check (F6).
