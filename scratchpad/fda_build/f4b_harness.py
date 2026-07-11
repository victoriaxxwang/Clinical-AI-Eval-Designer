"""F4b: re-score all 10 demo diseases through the TWO-AXIS bridge (F3b).

Free (openFDA needs no key). Runs the new disease_to_fda on each case's oracle
disease AND wide-net's recovered disease, capturing both axes so we can measure
what the second (device-name) axis adds vs the F3 code-only baseline.
Writes f4b_scoring.json. Does not touch engine.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "experimental"))
import fda_bridge  # noqa: E402

# oracle + recovered disease per case, lifted from f4_scoring.json
CASES = {
    "nsclc_lung_ct_cnn":            ("Carcinoma, Non-Small-Cell Lung", "Lung Neoplasms"),
    "ischemic_stroke_ct_ensemble":  ("Ischemic Stroke", "Ischemic Stroke"),
    "copd_exacerbation_survival":   ("Pulmonary Disease, Chronic Obstructive", "Lung Diseases"),
    "aki_rnn_inpatient":            ("Acute Kidney Injury", "Wounds and Injuries"),
    "tb_chest_xray_densenet":       ("Tuberculosis, Pulmonary", "Tuberculosis, Pulmonary"),
    "diabetic_retinopathy_fundus":  ("Diabetic Retinopathy", "Diabetic Retinopathy"),
    "melanoma_dermoscopy_transformer": ("Melanoma", "Neoplasms"),
    "crohns_endoscopy_video_cnn":   ("Crohn Disease", "Crohn Disease"),
    "t2dm_incident_risk_ehr":       ("Diabetes Mellitus, Type 2", "Diabetes Mellitus"),
    "mdd_relapse_multimodal":       ("Depressive Disorder, Major", ""),
}


def run_one(disease):
    if not disease:
        return {"phrase": "", "status": "(no disease)", "code_predicates": 0,
                "name_devices": [], "top_code": None}
    text, status, meta = fda_bridge.disease_to_fda(disease)
    ranked = meta["ranked_codes"]
    return {
        "phrase": disease,
        "status": status,
        "code_predicates": sum(len(v) for v in meta["predicates"].values()),
        "top_code": ranked[0][0] if ranked else None,
        "top_name": ranked[0][1] if ranked else None,
        "name_devices": [
            {"k": d["k_number"], "name": d["device_name"], "code": d["product_code"],
             "date": d["decision_date"], "applicant": d["applicant"],
             "match": d.get("match_term", "")}
            for d in meta["name_axis_devices"]
        ],
    }


def main():
    out = {}
    for case, (oracle, recovered) in CASES.items():
        out[case] = {
            "oracle": oracle, "recovered": recovered,
            "ORACLE": run_one(oracle),
            "RECOVERED": run_one(recovered),
        }
        o = out[case]["ORACLE"]
        print("%-34s oracle=%-38s code_preds=%d name_axis=%d"
              % (case, oracle, o["code_predicates"], len(o["name_devices"])))
    dest = os.path.join(HERE, "f4b_scoring.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote", dest)


if __name__ == "__main__":
    main()
