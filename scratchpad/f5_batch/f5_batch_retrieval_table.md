# F5 batch — B2 retrieval sweep (frozen vs wide-net, no API key)

10 Claude-Science cases. **frozen surfaced disease: 0/10** · **wide-net surfaced disease: 0/10** · **gate pass (frozen misses ∧ wide-net surfaces): 0/10** · **FDA sections identical between arms: 10/10** · **literature diverged: 10/10**.

| Case | Oracle disease | Frozen surfaced | Wide-net surfaced | Gate pass | FDA identical | Lit diverged |
|---|---|---|---|---|---|---|
| nsclc_lung_ct_cnn | Carcinoma, Non-Small-Cell Lung | ❌ | ❌ | — | = | ✅ |
| ischemic_stroke_ct_ensemble | Ischemic Stroke | ❌ | ❌ | — | = | ✅ |
| copd_exacerbation_survival | Pulmonary Disease, Chronic Obstructive | ❌ | ❌ | — | = | ✅ |
| aki_rnn_inpatient | Acute Kidney Injury | ❌ | ❌ | — | = | ✅ |
| tb_chest_xray_densenet | Tuberculosis, Pulmonary | ❌ | ❌ | — | = | ✅ |
| diabetic_retinopathy_fundus | Diabetic Retinopathy | ❌ | ❌ | — | = | ✅ |
| melanoma_dermoscopy_transformer | Melanoma | ❌ | ❌ | — | = | ✅ |
| crohns_endoscopy_video_cnn | Crohn Disease | ❌ | ❌ | — | = | ✅ |
| t2dm_incident_risk_ehr | Diabetes Mellitus, Type 2 | ❌ | ❌ | — | = | ✅ |
| mdd_relapse_multimodal | Depressive Disorder, Major | ❌ | ❌ | — | = | ✅ |

**Reading:** *Gate pass* = the heart-failure demo condition reproduced (frozen misses the disease, wide-net recovers it). *FDA identical* = the two arms returned byte-identical openFDA sections (wide-net never touches the FDA product-code path — the documented Phase-2 bound). *Lit diverged* = wide-net changed the literature the downstream spec/panel would reason over.
