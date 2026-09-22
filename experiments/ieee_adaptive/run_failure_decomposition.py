#!/usr/bin/env python3
"""ULTRA v2 failure decomposition — TRAIN/DEV n=80 only. No TEST. No new retrieval."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE13 = (
    ROOT
    / "experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv"
)
C2A = ROOT / "experiments/ieee_adaptive/C2A_CASE_ANNOTATIONS.csv"
OUT_DIR = Path(__file__).resolve().parent
PER_QUERY = OUT_DIR / "FAILURE_DECOMPOSITION_PER_QUERY.csv"
MECH_SUM = OUT_DIR / "FAILURE_MECHANISM_SUMMARY.csv"
SUMMARY_JSON = OUT_DIR / "FAILURE_DECOMPOSITION_SUMMARY.json"

SYSTEMS = {
    "bm25": "bm25_rank",
    "ng3": "ng3_rank",
    "dense": "dense_rank",
    "hybrid": "hybrid_rank",
}

# Pre-declared primary failure categories (mutually exclusive).
# Assigned AFTER computing ranks, using deterministic rules below.
# Annotation rules for CG secondary mechanisms (pre-declared):
# Prefer existing C2A labels for BND miss50 queries when available;
# otherwise mark UNKNOWN_PENDING_MANUAL (do not invent after peeking).


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_rank(row: dict, key: str) -> int | None:
    v = (row.get(key) or "").strip()
    if v == "":
        return None
    return int(float(v))


def in_top(row: dict, key: str, k: int) -> bool:
    rk = parse_rank(row, key)
    return rk is not None and rk <= k


def best_rank(row: dict, comps: list[str]) -> int | None:
    ranks = []
    for c in comps:
        rk = parse_rank(row, SYSTEMS[c])
        if rk is not None and rk <= 50:
            ranks.append(rk)
    return min(ranks) if ranks else None


def rank_bucket(rk: int | None) -> str:
    if rk is None or rk > 50:
        return "miss50"
    if rk <= 5:
        return "1-5"
    if rk <= 10:
        return "6-10"
    if rk <= 20:
        return "11-20"
    return "21-50"


def complementarity_label(row: dict, k: int) -> str:
    bits = []
    for name in ("bm25", "ng3", "dense"):
        if int(row[f"{name}_hit@{k}"]):
            bits.append(name.upper() if name != "ng3" else "NG3")
    return "+".join(bits) if bits else "none"


def primary_category(row: dict) -> tuple[str, str, str]:
    """Return (primary, candidate_generation_status, ranking_status).

    Rules (pre-declared, mutually exclusive):
    A SUCCESS: Dense Hit@5 OR Hybrid Hit@5 OR BM25 Hit@5 OR NG3 Hit@5
       — use Dense as current-best deployable first-stage Hit@5 for 'current';
         also flag any-expert Hit@5 as success_any.
    For decomposition relative to BND union (the candidate pool of interest):
      - SUCCESS_ANY_EXPERT_HIT5 if any of BM25/NG3/Dense Hit@5
      - RANKING_FAILURE if gold in BND Top-50 but no expert Hit@5
      - CANDIDATE_GENERATION_FAILURE if gold absent from BND Top-50
    Representation / ambiguity / benchmark: only if secondary evidence later;
    default primary stays structural (SUCCESS / RANKING / CG).
    """
    any_hit5 = any(int(row[f"{s}_hit@5"]) for s in ("bm25", "ng3", "dense"))
    in_pool = any(int(row[f"{s}_hit@50"]) for s in ("bm25", "ng3", "dense"))
    if any_hit5:
        return "SUCCESS", "in_pool", "already_top5"
    if in_pool:
        return "RANKING_FAILURE", "in_pool", "below_top5"
    return "CANDIDATE_GENERATION_FAILURE", "absent", "n/a"


def load_c2a() -> dict[str, dict]:
    if not C2A.exists():
        return {}
    out = {}
    with C2A.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            out[row["query_id"]] = row
    return out


def map_c2a_to_mechanism(label: str) -> str:
    """Map C2A letter labels (from C2A_FEASIBILITY_PROBE) to secondary mechanisms."""
    m = {
        "A": "acronym_institution",  # INSTITUTIONAL_ALIAS
        "B": "entity_name",  # NON_INSTITUTIONAL_ENTITY
        "C": "semantic_paraphrase",  # SEMANTIC_PARAPHRASE
        "D": "orthographic_variation",  # SCRIPT_ORTHOGRAPHIC
        "E": "lexical_mismatch",  # VOCABULARY
        "F": "other",
        "G": "other",
        "H": "other",
    }
    return m.get((label or "").strip().upper(), "other")


def main() -> None:
    assert PHASE13.exists(), PHASE13
    rows = list(csv.DictReader(PHASE13.open(encoding="utf-8-sig")))
    assert len(rows) == 80
    assert all(r["split"] in ("train", "dev") for r in rows)
    c2a = load_c2a()

    unions = {
        "BM25": ["bm25"],
        "NG3": ["ng3"],
        "Dense": ["dense"],
        "Hybrid": ["hybrid"],
        "BM25_U_NG3": ["bm25", "ng3"],
        "BM25_U_Dense": ["bm25", "dense"],
        "NG3_U_Dense": ["ng3", "dense"],
        "BM25_U_NG3_U_Dense": ["bm25", "ng3", "dense"],
    }

    coverage = {}
    for name, key in SYSTEMS.items():
        coverage[name] = {
            f"hit@{k}": sum(1 for r in rows if in_top(r, key, k))
            for k in (1, 5, 10, 20, 50)
        }

    ceilings = {}
    for uname, comps in unions.items():
        n_pool = sum(1 for r in rows if best_rank(r, comps) is not None)
        ceilings[uname] = {
            "PERFECT_RANKING_UPPER_BOUND_hit5": n_pool,
            "pct": round(100.0 * n_pool / 80, 2),
        }

    # Per-query export
    per_query_rows = []
    primary_counts = Counter()
    mech_counts = Counter()
    cg_recoverability = Counter()

    for r in rows:
        bm25_r = parse_rank(r, "bm25_rank")
        ng3_r = parse_rank(r, "ng3_rank")
        dense_r = parse_rank(r, "dense_rank")
        hybrid_r = parse_rank(r, "hybrid_rank")
        union_r = best_rank(r, ["bm25", "ng3", "dense"])
        primary, cg_status, rank_status = primary_category(r)
        primary_counts[primary] += 1

        # Secondary mechanism: only assign for CG failures from C2A when present
        secondary = ""
        notes = ""
        recoverability = ""
        if primary == "CANDIDATE_GENERATION_FAILURE":
            ann = c2a.get(r["query_id"])
            if ann:
                lab = (ann.get("classification") or "").strip().upper()
                secondary = map_c2a_to_mechanism(lab)
                notes = f"c2a_label={lab};confirmed={ann.get('mechanism_confirmed','')}"
                # Pre-declared recoverability heuristics (not a method claim):
                # A/D: surface bridging might help in principle (C2a already showed A rare)
                # B: entity resources uncertain / crowded
                # C/E: deep bilingual paraphrase / vocab — often intrinsically hard
                # G/H: uncertain
                if lab in ("A", "D"):
                    recoverability = "plausibly_recoverable"
                elif lab == "B":
                    recoverability = "uncertain"
                elif lab in ("C", "E"):
                    recoverability = "likely_intrinsically_difficult"
                else:
                    recoverability = "uncertain"
            else:
                secondary = "unknown_no_c2a"
                recoverability = "uncertain"
                notes = "no_c2a_annotation"
            mech_counts[secondary] += 1
            cg_recoverability[recoverability] += 1
        elif primary == "RANKING_FAILURE":
            # Which expert has gold deepest/shallowest
            secondary = "ordering_within_existing_pool"
            recoverability = "ranking_headroom"
            notes = f"best_bnd_rank={union_r}"
        else:
            secondary = ""
            recoverability = "already_success"
            notes = "any_expert_hit5"

        current_hit5_dense = int(r["dense_hit@5"])
        current_hit5_any = int(
            any(int(r[f"{s}_hit@5"]) for s in ("bm25", "ng3", "dense"))
        )
        current_hit5_hybrid = int(r["hybrid_hit@5"])

        per_query_rows.append(
            {
                "query_id": r["query_id"],
                "split": r["split"],
                "cohort": r["cohort"],
                "current_hit5_dense": current_hit5_dense,
                "current_hit5_hybrid": current_hit5_hybrid,
                "current_hit5_any_expert": current_hit5_any,
                "bm25_gold_rank": bm25_r if bm25_r is not None else "",
                "ng3_gold_rank": ng3_r if ng3_r is not None else "",
                "dense_gold_rank": dense_r if dense_r is not None else "",
                "hybrid_gold_rank": hybrid_r if hybrid_r is not None else "",
                "union_bnd_best_rank": union_r if union_r is not None else "",
                "bm25_hit50": int(r["bm25_hit@50"]),
                "ng3_hit50": int(r["ng3_hit@50"]),
                "dense_hit50": int(r["dense_hit@50"]),
                "hybrid_hit50": int(r["hybrid_hit@50"]),
                "complementarity_hit50": complementarity_label(r, 50),
                "complementarity_hit5": complementarity_label(r, 5),
                "primary_failure_category": primary,
                "secondary_mechanism": secondary,
                "candidate_generation_status": cg_status,
                "ranking_status": rank_status,
                "cg_recoverability_class": recoverability,
                "notes": notes,
            }
        )

    # Ranking headroom buckets for systems + BND
    buckets = {}
    for name, key in SYSTEMS.items():
        buckets[name] = dict(
            Counter(rank_bucket(parse_rank(r, key)) for r in rows)
        )
    buckets["BND_best"] = dict(
        Counter(rank_bucket(best_rank(r, ["bm25", "ng3", "dense"])) for r in rows)
    )

    # Complementarity
    comp50 = dict(Counter(complementarity_label(r, 50) for r in rows))
    comp5 = dict(Counter(complementarity_label(r, 5) for r in rows))

    dense_hit5 = coverage["dense"]["hit@5"]
    hybrid_hit5 = coverage["hybrid"]["hit@5"]
    any_expert_hit5 = sum(
        1 for r in rows if any(int(r[f"{s}_hit@5"]) for s in ("bm25", "ng3", "dense"))
    )
    bnd_ceiling = ceilings["BM25_U_NG3_U_Dense"]["PERFECT_RANKING_UPPER_BOUND_hit5"]
    ranking_headroom = primary_counts["RANKING_FAILURE"]
    cg_headroom = primary_counts["CANDIDATE_GENERATION_FAILURE"]

    target = 64  # 80% of 80
    summary = {
        "TEST_CONTENT_ACCESSED": False,
        "population": "Roman KN TRAIN+DEV ExactSource n=80",
        "source_csv": str(PHASE13.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256_file(PHASE13),
        "n": 80,
        "coverage": coverage,
        "PERFECT_RANKING_UPPER_BOUND": ceilings,
        "primary_counts": dict(primary_counts),
        "ranking_buckets": buckets,
        "complementarity_hit50": comp50,
        "complementarity_hit5": comp5,
        "dense_hit5": dense_hit5,
        "hybrid_hit5": hybrid_hit5,
        "oracle_best_of_3_hit5": any_expert_hit5,
        "bnd_candidate_generation_ceiling_hit5": bnd_ceiling,
        "ranking_headroom_queries": ranking_headroom,
        "cg_failure_queries": cg_headroom,
        "cg_mechanism_counts": dict(mech_counts),
        "cg_recoverability": dict(cg_recoverability),
        "target_80pct": {
            "target_hits": target,
            "current_best_hit5_dense": dense_hit5,
            "additional_needed_from_dense": target - dense_hit5,
            "additional_needed_from_oracle28": target - any_expert_hit5,
            "ceiling_bnd_union": bnd_ceiling,
            "compatible_with_bnd_ceiling": bnd_ceiling >= target,
            "gap_beyond_ceiling": max(0, target - bnd_ceiling),
        },
        "hybrid_rank_failures_hit50_not_hit5": sum(
            1 for r in rows if int(r["hybrid_hit@50"]) and not int(r["hybrid_hit@5"])
        ),
        "dense_rank_failures_hit50_not_hit5": sum(
            1 for r in rows if int(r["dense_hit@50"]) and not int(r["dense_hit@5"])
        ),
    }

    with PER_QUERY.open("w", encoding="utf-8", newline="") as f:
        fields = list(per_query_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per_query_rows)

    with MECH_SUM.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["mechanism", "count", "pct_of_cg_failures", "pct_of_n80"],
        )
        w.writeheader()
        for mech, cnt in sorted(mech_counts.items(), key=lambda x: -x[1]):
            w.writerow(
                {
                    "mechanism": mech,
                    "count": cnt,
                    "pct_of_cg_failures": round(100.0 * cnt / max(cg_headroom, 1), 2),
                    "pct_of_n80": round(100.0 * cnt / 80, 2),
                }
            )

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Console summary (ASCII only)
    print("TEST_CONTENT_ACCESSED = FALSE")
    print("n=", len(rows))
    print("coverage dense hit5", dense_hit5)
    print("oracle hit5", any_expert_hit5)
    print("BND ceiling", bnd_ceiling)
    print("primary", dict(primary_counts))
    print("ceilings", {k: v["PERFECT_RANKING_UPPER_BOUND_hit5"] for k, v in ceilings.items()})
    print("comp50", comp50)
    print("buckets BND", buckets["BND_best"])
    print("wrote", PER_QUERY.name, MECH_SUM.name, SUMMARY_JSON.name)


if __name__ == "__main__":
    main()
