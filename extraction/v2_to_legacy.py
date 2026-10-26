"""Convert v2 extractions (out/*.json) into the legacy stage2/CLAIM JSONL shapes read by the
existing review-paper/analysis/*.py figure scripts, so figures keep their original styling.

Usage: python3 v2_to_legacy.py OUTDIR [--exclude R4154,R2434,R4671]
Writes OUTDIR/stage2_results.jsonl, stage2_results.filtered.jsonl, claim2024_results.jsonl
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASK = {"vessel_segmentation": "Vessel Segmentation", "object_detection_localization": "Object Detection & Localisation",
        "catheter_device_tracking": "Catheter & Device Tracking", "disease_classification_grading": "Disease Classification & Grading",
        "background_subtraction": "Background Subtraction", "image_enhancement_denoising": "Image Enhancement & Denoising",
        "temporal_sequence_modeling": "Temporal Sequence Modelling", "contrast_flow_analysis": "Contrast Flow Analysis",
        "motion_correction_registration": "Motion Correction & Registration", "outcome_prediction": "Outcome Prediction",
        "other": "other"}
MODALITY = {"DSA": "DSA", "xray_fluoroscopy": "fluoroscopy", "DSA_and_fluoroscopy": "DSA+fluoroscopy", "other": "other"}
ANATOMY = {"neurologic": "cerebral", "cardiac": "coronary", "aortic_thoracic": "thoracic", "abdominopelvic": "abdominal",
           "peripheral": "peripheral", "multi": "multi", "other": "other", "not_reported": None}
PUBTYPE = {"journal": "journal", "conference_full_paper": "conference", "conference_abstract": "conference",
           "preprint": "preprint", "book_chapter": "other", "other": "other"}
CLUSTERS = [("C01", 1, 2), ("C02", 3, 5), ("C03", 6, 9), ("C04", 10, 13), ("C05", 14, 16), ("C06", 17, 21),
            ("C07", 22, 26), ("C08", 27, 31), ("C09", 32, 36), ("C10", 37, 39), ("C11", 40, 42), ("C12", 43, 44)]


def cluster(items, a, b):
    """Cluster adherence: NA if every item is n/a, else Yes when at least half of the applicable items are reported."""
    s = [c for c in items[a - 1:b] if c != "a"]
    if not s:
        return "NA"
    return "Yes" if s.count("y") * 2 >= len(s) else "No"


def main(outdir, exclude):
    meta = {r["record_id"]: r for r in csv.DictReader(open(ROOT / "manifest.csv"))}
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    s2, cl = [], []
    for p in sorted((ROOT / "out").glob("R*.json")):
        r = json.loads(p.read_text()); rid = r["record_id"]
        if rid in exclude:
            continue
        m, ev = meta[rid], r["evaluation"]
        head = next((x for x in ev["metrics"] if x["value_0_100"] is not None), None)
        year = int(m["year"]) if m["year"] else r["study"]["year"]
        venue = m["journal_venue"] or r["study"]["venue"] or ""
        if re.search(r"spie", venue, re.I) or venue.strip().lower() == "medical imaging":
            venue = "Proceedings of SPIE"
        s2.append({
            "title": m["title"], "year": year, "_source_file": f"{rid}.pdf", "_md_file": f"{rid}.md", "record_id": rid,
            "study_identity": {"title": m["title"], "journal_or_venue": venue,
                               "year": year, "publication_type": PUBTYPE[r["study"]["publication_type"]]},
            "imaging": {"modality": MODALITY[r["imaging"]["modality"]], "anatomy": ANATOMY[r["imaging"]["territory"]],
                        "anatomy_detail": r["imaging"]["territory_detail"]},
            "task": {"primary_task": TASK[r["task"]["primary_task"]],
                     "secondary_tasks": [TASK[t] for t in r["task"]["secondary_tasks"]]},
            "method": {"architecture_name": ", ".join(r["method"]["architecture_names"]),
                       "temporal_modelling": r["method"]["temporal_category"] not in ("none", "not_determinable"),
                       "temporal_category": r["method"]["temporal_category"]},
            "evaluation": {"primary_metric": head and head["metric"], "primary_metric_value": head and head["value_0_100"],
                           "validation_design": ev["validation_design"]},
        })
        items = r["claim2024"]["items"]
        cl.append({"title": m["title"], "year": year, "_source_file": f"{rid}.pdf", "record_id": rid,
                   "claim2024_adherence": {cid: {"adherence": cluster(items, a, b)} for cid, a, b in CLUSTERS}})
    for name, rows in [("stage2_results.jsonl", s2), ("stage2_results.filtered.jsonl", s2), ("claim2024_results.jsonl", cl)]:
        (outdir / name).write_text("".join(json.dumps(x) + "\n" for x in rows))
    print(f"wrote {len(s2)} records to {outdir}")


if __name__ == "__main__":
    ex = set(sys.argv[sys.argv.index("--exclude") + 1].split(",")) if "--exclude" in sys.argv else set()
    main(sys.argv[1], ex)
