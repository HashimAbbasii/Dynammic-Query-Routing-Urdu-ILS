# -*- coding: utf-8 -*-
"""
M3-E: merge blind-pack judgments → union qrels → paired Success@5.
Does not modify frozen inputs. Does not rerun retrieval.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R_DEV = ROOT / "experiments" / "post_phase12_development"
M3E = R_DEV / "m3e_evaluation"

EXPECTED = {
    "queries_r_dev.csv": "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f",
    "R_TOP50_RETRIEVAL.csv": "927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2",
    "R_TOP5_FOR_ANNOTATION.csv": "042006bc3232719514a6ca4b638f4e6348415d168294271fe366ff95704b23c5",
    "qrels_r_dev.csv": "506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb",
    "M2-A_TOP50_RETRIEVAL.csv": "b9d4c77ef4cf2a7ba7442031a79c7cb1c78eaf00b88bcdabc4627d084d3d801e",
    "M2-B_TOP50_RETRIEVAL.csv": "9a16855977fa43fe8766d325065f621009182094d60f999e080051d50e45630a",
}

ANNOTATOR = "thesis_author_single"
ANNOTATION_DATE = "2026-09-05"
NAT_QIDS = [f"R{i:03d}" for i in range(51, 101)]

# Single-annotator calibration on draft pack labels (blind packs → final).
# Only overrides where draft conflicted with frozen A–E / R-dev style.
CALIBRATION_OVERRIDES = {
    # R051: location need — Misbah captain piece does not answer venue
    ("R051", 88241): "D",
    # R051: WI day/night test venue is topical cricket, different occasion
    ("R051", 45571): "C",
    # R052: open-market dollar wires with price movement (align with carried A's)
    ("R052", 38964): "A",
    ("R052", 65861): "A",
    # R096: moon-sighting admin, not when Eid moon appears
    ("R096", 20605): "C",
    ("R096", 20665): "C",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_top5(path: Path, filter_nat: bool = True) -> dict[str, list[int]]:
    by: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if filter_nat and r.get("track") and r["track"] != "NAT":
                continue
            qid = r["query_id"]
            if qid not in NAT_QIDS and filter_nat:
                # M2 CSVs may lack track; keep NAT ids only
                if qid not in NAT_QIDS:
                    continue
            rank = int(r["rank"])
            if rank <= 5:
                by[qid].append((rank, int(r["doc_id"])))
    out = {}
    for qid, pairs in by.items():
        if qid not in NAT_QIDS:
            continue
        out[qid] = [d for _, d in sorted(pairs)]
    return out


def success(top5: list[int], labels: dict[tuple[str, int], str], qid: str) -> bool:
    for d in top5:
        lab = labels.get((qid, d))
        if lab in ("A", "B"):
            return True
    return False


def main() -> None:
    # --- integrity preflight ---
    paths = {
        "queries_r_dev.csv": R_DEV / "queries_r_dev.csv",
        "R_TOP50_RETRIEVAL.csv": R_DEV / "R_TOP50_RETRIEVAL.csv",
        "R_TOP5_FOR_ANNOTATION.csv": R_DEV / "R_TOP5_FOR_ANNOTATION.csv",
        "qrels_r_dev.csv": R_DEV / "qrels_r_dev.csv",
        "M2-A_TOP50_RETRIEVAL.csv": R_DEV / "module2" / "M2-A_TOP50_RETRIEVAL.csv",
        "M2-B_TOP50_RETRIEVAL.csv": R_DEV / "module2" / "M2-B_TOP50_RETRIEVAL.csv",
    }
    hashes = {k: sha256_file(p) for k, p in paths.items()}
    for k, exp in EXPECTED.items():
        if hashes[k] != exp:
            raise SystemExit(f"SHA mismatch {k}: got {hashes[k]} expected {exp}")

    # --- load drafts ---
    drafts: list[dict] = []
    for p in sorted((M3E / "_draft_judgments").glob("pack_*_draft.json")):
        drafts.extend(json.loads(p.read_text(encoding="utf-8")))
    draft_map = {(j["query_id"], int(j["doc_id"])): j["relevance_label"] for j in drafts}

    expected_new = set()
    for line in open(M3E / "M3E_NEW_PAIRS_FOR_JUDGMENT.jsonl", encoding="utf-8"):
        r = json.loads(line)
        expected_new.add((r["query_id"], int(r["doc_id"])))
    if set(draft_map) != expected_new:
        raise SystemExit("draft keys != expected new pairs")

    # apply calibration
    final_new = dict(draft_map)
    applied = []
    for key, lab in CALIBRATION_OVERRIDES.items():
        if key not in final_new:
            raise SystemExit(f"override key missing: {key}")
        old = final_new[key]
        if old != lab:
            applied.append({"query_id": key[0], "doc_id": key[1], "from": old, "to": lab})
            final_new[key] = lab

    # --- write NEW judgments ---
    new_rows = []
    for qid, did in sorted(final_new):
        new_rows.append({
            "query_id": qid,
            "doc_id": did,
            "relevance_label": final_new[(qid, did)],
            "annotator": ANNOTATOR,
            "annotation_date": ANNOTATION_DATE,
            "label_source": "new_m3e",
        })
    new_path = M3E / "M3E_NEW_JUDGMENTS.csv"
    with open(new_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "query_id", "doc_id", "relevance_label",
                "annotator", "annotation_date", "label_source",
            ],
        )
        w.writeheader()
        w.writerows(new_rows)

    # --- carry M0 + merge union ---
    carried = []
    with open(paths["qrels_r_dev.csv"], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            qid = r["query_id"]
            if qid not in NAT_QIDS:
                continue
            carried.append({
                "query_id": qid,
                "doc_id": int(r["doc_id"]),
                "relevance_label": r["relevance_label"],
                "annotator": r.get("annotator", ANNOTATOR),
                "annotation_date": r.get("annotation_date", ""),
                "label_source": "carried_m0",
            })

    # ensure no overlap between carried and new
    carried_keys = {(r["query_id"], r["doc_id"]) for r in carried}
    overlap = carried_keys & set(final_new)
    if overlap:
        raise SystemExit(f"carried/new overlap: {list(overlap)[:5]}")

    union_rows = carried + new_rows
    union_path = M3E / "M3E_QRELS_UNION.csv"
    with open(union_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "query_id", "doc_id", "relevance_label",
                "annotator", "annotation_date", "label_source",
            ],
        )
        w.writeheader()
        w.writerows(sorted(union_rows, key=lambda x: (x["query_id"], x["doc_id"])))

    labels = {(r["query_id"], r["doc_id"]): r["relevance_label"] for r in union_rows}

    # --- systems Top-5 ---
    m0 = load_top5(paths["R_TOP50_RETRIEVAL.csv"])
    # also from top5 file for cross-check
    m0_sheet = load_top5(paths["R_TOP5_FOR_ANNOTATION.csv"])
    m2a = load_top5(paths["M2-A_TOP50_RETRIEVAL.csv"], filter_nat=True)
    m2b = load_top5(paths["M2-B_TOP50_RETRIEVAL.csv"], filter_nat=True)

    # ensure all NAT present (empty list if zero-hit)
    for qid in NAT_QIDS:
        m0.setdefault(qid, [])
        m2a.setdefault(qid, [])
        m2b.setdefault(qid, [])
        m0_sheet.setdefault(qid, [])

    if m0 != m0_sheet:
        # allow only if both have same sets per query
        for qid in NAT_QIDS:
            if m0[qid] != m0_sheet[qid]:
                raise SystemExit(f"M0 Top-5 mismatch {qid}: {m0[qid]} vs {m0_sheet[qid]}")

    # legacy M0 Success under original qrels only
    legacy_labels = {}
    with open(paths["qrels_r_dev.csv"], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            legacy_labels[(r["query_id"], int(r["doc_id"]))] = r["relevance_label"]
    legacy_hits = [qid for qid in NAT_QIDS if success(m0[qid], legacy_labels, qid)]
    if len(legacy_hits) != 12:
        raise SystemExit(f"Legacy M0 Success sanity FAIL: {len(legacy_hits)}/50")

    # union-pool Success
    def vector(sys_top5: dict[str, list[int]]) -> dict[str, int]:
        return {qid: int(success(sys_top5[qid], labels, qid)) for qid in NAT_QIDS}

    v_m0 = vector(m0)
    v_m2a = vector(m2a)
    v_m2b = vector(m2b)

    def hits(v: dict[str, int]) -> int:
        return sum(v.values())

    h_m0, h_m2a, h_m2b = hits(v_m0), hits(v_m2a), hits(v_m2b)
    if h_m0 != 12:
        raise SystemExit(f"Union-rescored M0 Success must be 12/50, got {h_m0}/50")

    # paired changes vs M0
    def paired(v_cand: dict[str, int]):
        improved = worsened = unchanged = 0
        for qid in NAT_QIDS:
            a, b = v_m0[qid], v_cand[qid]
            if b > a:
                improved += 1
            elif b < a:
                worsened += 1
            else:
                unchanged += 1
        return {"improved": improved, "worsened": worsened, "unchanged": unchanged}

    # script strata from M0 detector
    det = {}
    with open(paths["R_TOP50_RETRIEVAL.csv"], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["query_id"] in NAT_QIDS and r["query_id"] not in det:
                det[r["query_id"]] = r["detector_label"]

    def by_script(v: dict[str, int]):
        out = {}
        for script in ("URDU", "ROMAN", "MIXED"):
            qs = [q for q in NAT_QIDS if det.get(q) == script]
            h = sum(v[q] for q in qs)
            out[script] = {"hits": h, "n": len(qs), "rate": (h / len(qs) if qs else None)}
        return out

    # legacy pool-restricted M2 (for reporting contrast)
    def legacy_pool_success(sys_top5: dict[str, list[int]]) -> int:
        # only labels present in original qrels count; unlabeled = non-A/B
        return sum(
            1
            for qid in NAT_QIDS
            if any(
                legacy_labels.get((qid, d)) in ("A", "B")
                for d in sys_top5[qid]
            )
        )

    legacy_m2a = legacy_pool_success(m2a)
    legacy_m2b = legacy_pool_success(m2b)

    # pool / label stats
    hist_all = Counter(r["relevance_label"] for r in union_rows)
    hist_new = Counter(r["relevance_label"] for r in new_rows)
    hist_carried = Counter(r["relevance_label"] for r in carried)

    # candidate-only docs in Top-5: A/B fraction
    def cand_only_ab_frac(sys_top5: dict[str, list[int]], name: str):
        only = []
        for qid in NAT_QIDS:
            m0set = set(m0[qid])
            for d in sys_top5[qid]:
                if d not in m0set:
                    only.append(labels[(qid, d)])
        n = len(only)
        ab = sum(1 for x in only if x in ("A", "B"))
        return {"system": name, "n_candidate_only_top5_docs": n, "n_ab": ab, "frac_ab": (ab / n if n else None)}

    # R080
    r080 = {
        "query_id": "R080",
        "m0_top5_n": len(m0["R080"]),
        "m2a_top5_n": len(m2a["R080"]),
        "m2b_top5_n": len(m2b["R080"]),
        "in_denominator": True,
        "m0_success": bool(v_m0["R080"]),
        "m2a_success": bool(v_m2a["R080"]),
        "m2b_success": bool(v_m2b["R080"]),
        "m0_zero_hit_success": 0 if len(m0["R080"]) == 0 else int(v_m0["R080"]),
    }

    # postflight hashes
    post = {k: sha256_file(p) for k, p in paths.items()}
    if post != hashes:
        raise SystemExit("Frozen inputs changed during execution")

    pool_manifest = json.loads((M3E / "M3E_POOL_MANIFEST.json").read_text(encoding="utf-8"))

    metrics = {
        "stage": "m3e_paired_evaluation",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "legacy_m0_pool_success_at_5": {"hits": 12, "n": 50, "rate": 0.24, "success_queries": legacy_hits},
        "union_pool_success_at_5": {
            "M0": {"hits": h_m0, "n": 50, "rate": h_m0 / 50},
            "M2-A": {"hits": h_m2a, "n": 50, "rate": h_m2a / 50, "delta_vs_m0_hits": h_m2a - h_m0},
            "M2-B": {"hits": h_m2b, "n": 50, "rate": h_m2b / 50, "delta_vs_m0_hits": h_m2b - h_m0},
        },
        "legacy_pool_restricted_success_at_5": {
            "M0": 12,
            "M2-A": legacy_m2a,
            "M2-B": legacy_m2b,
            "note": "Historical Module 2 figures under M0-only qrels; unlabeled cand docs score as non-success",
        },
        "paired_vs_m0": {
            "M2-A": paired(v_m2a),
            "M2-B": paired(v_m2b),
        },
        "script_strata_union": {
            "M0": by_script(v_m0),
            "M2-A": by_script(v_m2a),
            "M2-B": by_script(v_m2b),
        },
        "per_query_success": {
            "M0": v_m0,
            "M2-A": v_m2a,
            "M2-B": v_m2b,
        },
        "candidate_only_top5_ab": [
            cand_only_ab_frac(m2a, "M2-A"),
            cand_only_ab_frac(m2b, "M2-B"),
        ],
        "r080": r080,
        "label_histogram_union": dict(hist_all),
        "label_histogram_new": dict(hist_new),
        "label_histogram_carried": dict(hist_carried),
        "sanity": {
            "legacy_m0_reproduced_12_50": True,
            "union_m0_equals_12_50": True,
            "qrels_r_dev_not_overwritten": True,
        },
        "frozen_input_sha256_postflight": post,
    }
    (M3E / "M3E_METRICS.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ann_manifest = {
        "stage": "m3e_annotation",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "annotator_mode": "thesis_author_single",
        "annotator": ANNOTATOR,
        "annotation_date": ANNOTATION_DATE,
        "rubric": "experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md (A–E)",
        "blinding": {
            "system_ids_hidden": True,
            "scores_hidden": True,
            "rank_hidden": True,
            "within_query_shuffle_seed": pool_manifest.get("shuffle_seed"),
            "annotator_saw_only": [
                "query_id", "query_text", "doc_id", "headline", "snippet",
            ],
        },
        "n_new_pairs": len(new_rows),
        "n_carried_m0": len(carried),
        "n_union": len(union_rows),
        "label_histogram_new": dict(hist_new),
        "label_histogram_union": dict(hist_all),
        "calibration_overrides": applied,
        "agreement_subsample": None,
        "cohens_kappa": None,
        "r080_handling": "kept in denominator; M0/M2-B zero-hit → Success=0; M2-A Top-5 labeled",
        "stop_after_annotation": True,
        "artifact_sha256": {
            "M3E_NEW_JUDGMENTS.csv": sha256_file(new_path),
            "M3E_QRELS_UNION.csv": sha256_file(union_path),
            "M3E_ANNOTATION_SHEET.csv": sha256_file(M3E / "M3E_ANNOTATION_SHEET.csv"),
            "M3E_POOL_MANIFEST.json": sha256_file(M3E / "M3E_POOL_MANIFEST.json"),
        },
        "frozen_input_sha256": hashes,
        "qrels_r_dev_csv_unchanged": hashes["qrels_r_dev.csv"] == EXPECTED["qrels_r_dev.csv"],
    }
    (M3E / "M3E_ANNOTATION_MANIFEST.json").write_text(
        json.dumps(ann_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # provenance audit log
    audit = {
        "protocol_version": "1.0",
        "pool_materialized_utc": pool_manifest.get("timestamp_utc"),
        "annotation_completed_utc": ann_manifest["timestamp_utc"],
        "calibration_overrides_logged": applied,
        "metric_driven_pool_edits": False,
        "retrieval_rerun": False,
    }
    (M3E / "M3E_PROVENANCE_AUDIT.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("FINALIZE_OK")
    print("legacy_m0", f"{len(legacy_hits)}/50")
    print("union_m0", f"{h_m0}/50")
    print("union_m2a", f"{h_m2a}/50")
    print("union_m2b", f"{h_m2b}/50")
    print("legacy_m2a", legacy_m2a)
    print("legacy_m2b", legacy_m2b)
    print("paired_m2a", paired(v_m2a))
    print("paired_m2b", paired(v_m2b))
    print("hist_new", dict(hist_new))
    print("hist_union", dict(hist_all))
    print("r080", r080)
    print("overrides", applied)


if __name__ == "__main__":
    main()
