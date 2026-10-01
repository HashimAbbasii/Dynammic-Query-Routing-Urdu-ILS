#!/usr/bin/env python3
"""Phase 1 failure-mechanism discovery: population comparison. No TEST. No new retrieval."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CORPUS = ROOT / "data" / "clean_articles.csv"
ORACLE = ROOT / "experiments" / "phase2_oracle" / "oracle_all.csv"
K_PATH = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_k.csv"
U_PATH = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_u.csv"
BENCH_TRAIN = ROOT / "experiments" / "ultra_v2" / "benchmark" / "train" / "queries_kn.csv"
BENCH_DEV = ROOT / "experiments" / "ultra_v2" / "benchmark" / "dev" / "queries_kn.csv"
P13 = (
    ROOT
    / "experiments"
    / "ultra_v2"
    / "phase13_population"
    / "artifacts"
    / "scoring"
    / "PHASE13_SCORING_PER_QUERY.csv"
)
C2A = ROOT / "experiments" / "ieee_adaptive" / "C2A_CASE_ANNOTATIONS.csv"
FD = ROOT / "experiments" / "ieee_adaptive" / "FAILURE_DECOMPOSITION_PER_QUERY.csv"

# Official Hit@5 from frozen reports (do not recompute Program A)
HIT5_N78 = {
    # From DEVELOPMENT_RESULTS: Method D 22/23 Roman; Urdu BM25 strong; overall 68/78
}
# K Hit@5 per script from paper: Urdu 26/28, Roman 1/12 (documented)
K_ROMAN_HIT5 = {"hit": 1, "n": 12}  # from Program A manuscript narrative


def script_label(q: str) -> str:
    ur = sum(1 for c in q if "\u0600" <= c <= "\u06ff")
    lat = sum(1 for c in q if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if ur and lat:
        return "MIXED"
    if ur:
        return "URDU"
    if lat:
        return "ROMAN"
    return "OTHER"


def toks(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+|[\u0600-\u06FF]+", (s or "").lower())


def coverage(q: str, h: str) -> float:
    qt = set(toks(q))
    if not qt:
        return 0.0
    return len(qt & set(toks(h))) / len(qt)


def jaccard(q: str, h: str) -> float:
    qt, ht = set(toks(q)), set(toks(h))
    if not qt and not ht:
        return 0.0
    return len(qt & ht) / len(qt | ht)


def char_bigram_jaccard(q: str, h: str) -> float:
    def grams(s: str) -> set[str]:
        s = re.sub(r"\s+", "", (s or "").lower())
        return {s[i : i + 2] for i in range(max(0, len(s) - 1))}

    a, b = grams(q), grams(h)
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def has_acronym(q: str) -> int:
    return 1 if re.search(r"\b[A-Z]{2,}\b", q or "") or re.search(
        r"\b(cpec|adb|sbp|fbr|imf|ipl|t20|psl)\b", (q or "").lower()
    ) else 0


def load_heads() -> dict[int, str]:
    heads: dict[int, str] = {}
    with CORPUS.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            raw = row.get("Index")
            try:
                idx = int(raw)
            except (TypeError, ValueError):
                continue
            heads[idx] = row.get("Headline") or ""
    return heads


def enrich(qid: str, pop: str, q: str, gid: int | None, heads: dict, **extra) -> dict:
    h = heads.get(gid, "") if gid is not None else ""
    cov = coverage(q, h) if h else ""
    jac = jaccard(q, h) if h else ""
    cb = char_bigram_jaccard(q, h) if h else ""
    return {
        "query_id": qid,
        "population": pop,
        "query_type": extra.get("query_type", ""),
        "script_type": script_label(q),
        "language_type_meta": extra.get("language_type_meta", ""),
        "creation_method": extra.get("creation_method", ""),
        "query_length_chars": len(q or ""),
        "query_length_tokens": len(toks(q)),
        "lexical_overlap_cov": round(cov, 4) if cov != "" else "",
        "normalized_overlap_jaccard": round(jac, 4) if jac != "" else "",
        "char_bigram_jaccard": round(cb, 4) if cb != "" else "",
        "semantic_category": extra.get("semantic_category", ""),
        "entity_indicator": extra.get("entity_indicator", ""),
        "acronym_indicator": has_acronym(q),
        "spelling_variation": extra.get("spelling_variation", ""),
        "headline_overlap_meta": extra.get("headline_overlap_meta", ""),
        "candidate_generation_status": extra.get("cg_status", ""),
        "ranking_status": extra.get("rank_status", ""),
        "failure_level": extra.get("failure_level", ""),
        "failure_mechanism": extra.get("failure_mechanism", ""),
        "hit5_known": extra.get("hit5_known", ""),
        "evidence_note": extra.get("evidence_note", ""),
        # do not export full query_text into public CSV? prompt asks for analysis CSV
        # include query_text for TRAIN/DEV legitimate pops only; omit for safety on sealed
        "query_text": q if extra.get("include_text", True) else "",
        "source_doc_id": gid if gid is not None else "",
    }


def mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), 4) if xs else None


def pct(xs: list[float], pred) -> float | None:
    return round(100 * sum(1 for x in xs if pred(x)) / len(xs), 2) if xs else None


def summarize(rows: list[dict], key_cov="lexical_overlap_cov") -> dict:
    cov = [float(r[key_cov]) for r in rows if r[key_cov] != ""]
    jac = [float(r["normalized_overlap_jaccard"]) for r in rows if r["normalized_overlap_jaccard"] != ""]
    cb = [float(r["char_bigram_jaccard"]) for r in rows if r["char_bigram_jaccard"] != ""]
    return {
        "n": len(rows),
        "scripts": dict(Counter(r["script_type"] for r in rows)),
        "mean_cov": mean(cov),
        "median_cov": round(sorted(cov)[len(cov) // 2], 4) if cov else None,
        "pct_cov_ge_0.5": pct(cov, lambda x: x >= 0.5),
        "pct_cov_eq_0": pct(cov, lambda x: x == 0.0),
        "mean_jaccard": mean(jac),
        "mean_char_bigram_jaccard": mean(cb),
        "mean_tokens": mean([float(r["query_length_tokens"]) for r in rows]),
        "pct_acronym": pct([float(r["acronym_indicator"]) for r in rows], lambda x: x == 1),
        "creation_methods": dict(Counter(r["creation_method"] for r in rows if r["creation_method"])),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    heads = load_heads()
    assert len(heads) > 100000, len(heads)
    per_query: list[dict] = []

    # Population A: n=78
    ora = list(csv.DictReader(ORACLE.open(encoding="utf-8-sig")))
    pool = [r for r in ora if r["split"] in ("dev", "internal_val")]
    assert len(pool) == 78, len(pool)
    for r in pool:
        gid = int(float(r["source_doc_id"]))
        q = r["query_text"]
        # creation_method from oracle
        cm = r.get("creation_method") or ""
        # title-derived signal: high coverage expected for title shorten / title_roman
        cov = coverage(q, heads.get(gid, ""))
        # Hypothesis features
        mech = ""
        level = ""
        if cov >= 0.5:
            mech = "high_lexical_overlap_title_like"
            level = "MATCH_LIKELY_LEXICAL"
        elif cov == 0:
            mech = "zero_token_overlap_with_headline"
            level = "LEVEL2_OR_3_BRIDGE_OR_CG"
        per_query.append(
            enrich(
                r["query_id"],
                "A_n78_dev_internal_val",
                q,
                gid,
                heads,
                language_type_meta=r.get("language_type", ""),
                creation_method=cm,
                query_type="known_item_title_derived",
                semantic_category=r.get("query_category", ""),
                evidence_note=f"protocol={r.get('protocol_label','')}",
                failure_mechanism=mech,
                failure_level=level,
                include_text=True,
            )
        )

    # Population B: K001-K040 (sealed after creation but query text is published in Program A eval — allowed, not v2 TEST)
    krows = list(csv.DictReader(K_PATH.open(encoding="utf-8-sig")))
    assert len(krows) == 40
    for r in krows:
        gid = int(float(r["source_doc_id"]))
        q = r["query_text"]
        note = r.get("notes") or ""
        is_roman_ordinary = "ordinary Roman" in note
        per_query.append(
            enrich(
                r["query_id"],
                "B_K001_K040",
                q,
                gid,
                heads,
                creation_method=note.split(";")[0].strip(),
                query_type="known_item_title_like_or_ordinary_roman",
                evidence_note=note[:120],
                spelling_variation="ordinary_roman_of_headline" if is_roman_ordinary else "",
                include_text=True,
            )
        )

    # Population C: U — naturalistic, NO gold — overlap N/A
    urows = list(csv.DictReader(U_PATH.open(encoding="utf-8-sig")))
    assert len(urows) == 40
    for r in urows:
        q = r["query_text"]
        per_query.append(
            enrich(
                r["query_id"],
                "C_U001_U040",
                q,
                None,
                heads,
                query_type="naturalistic_no_gold",
                creation_method="human_naturalistic",
                evidence_note="no ExactSource gold; Success@5 human labels only",
                failure_level="N/A_NO_GOLD",
                failure_mechanism="naturalistic_usefulness_not_exactsource",
                include_text=True,
            )
        )

    # Population D: Program B Roman KN train+dev n=80
    brow: list[dict] = []
    for p in (BENCH_TRAIN, BENCH_DEV):
        brow.extend(csv.DictReader(p.open(encoding="utf-8-sig")))
    roman = [r for r in brow if (r.get("script") or "").upper() == "ROMAN"]
    # Prefer phase13 list of 80 if needed
    assert len(roman) == 80, len(roman)

    # Merge P13 ranks + FD + C2A
    p13 = {
        r["query_id"]: r
        for r in csv.DictReader(P13.open(encoding="utf-8-sig"))
    }
    fd = {
        r["query_id"]: r
        for r in csv.DictReader(FD.open(encoding="utf-8-sig"))
    } if FD.exists() else {}
    c2a = {
        r["query_id"]: r
        for r in csv.DictReader(C2A.open(encoding="utf-8-sig"))
    } if C2A.exists() else {}

    for r in roman:
        qid = r["query_id"]
        gid = int(float(r["source_doc_id"]))
        q = r["query_text"]
        pr = p13.get(qid, {})
        fr = fd.get(qid, {})
        any_hit5 = fr.get("current_hit5_any_expert") or ""
        # compute from p13 if needed
        if pr:
            any_hit5 = int(
                any(int(pr.get(f"{s}_hit@5") or 0) for s in ("bm25", "ng3", "dense"))
            )
            in_pool = int(
                any(int(pr.get(f"{s}_hit@50") or 0) for s in ("bm25", "ng3", "dense"))
            )
            if any_hit5:
                cg, rk, level = "in_pool", "already_top5", "SUCCESS"
                mech = "retrieved_by_some_expert"
            elif in_pool:
                cg, rk, level = "in_pool", "below_top5", "LEVEL4_RANKING"
                mech = "ranking_within_bnd_pool"
            else:
                cg, rk, level = "absent", "n/a", "LEVEL3_CANDIDATE_GENERATION"
                lab = (c2a.get(qid) or {}).get("classification", "")
                mech = {
                    "A": "institutional_alias_bridge",
                    "B": "entity_name_heterogeneous",
                    "C": "semantic_paraphrase_bridge",
                    "D": "script_orthographic_same_en",
                    "E": "vocabulary_mismatch",
                    "G": "other",
                }.get(lab, fr.get("secondary_mechanism") or "cg_unknown")
                # Level 1 vs 2 refinement for CG
                if lab == "D":
                    level = "LEVEL1_OR_2_SCRIPT_REPRESENTATION"
                elif lab in ("A", "C", "E") or mech.startswith("entity"):
                    level = "LEVEL2_BRIDGING_AND_LEVEL3_CG"
        else:
            cg = rk = level = mech = ""
            any_hit5 = ""

        per_query.append(
            enrich(
                qid,
                "D_programB_roman_kn_n80",
                q,
                gid,
                heads,
                query_type="known_item_naturalistic_roman",
                creation_method=r.get("writer_id", ""),
                headline_overlap_meta=r.get("headline_overlap", ""),
                semantic_category=r.get("intent_type", ""),
                cg_status=cg,
                rank_status=rk,
                failure_level=level,
                failure_mechanism=mech,
                hit5_known=any_hit5,
                entity_indicator=1 if (c2a.get(qid) or {}).get("classification") == "B" else "",
                evidence_note=f"split={r.get('split')}; status={r.get('status')}",
                include_text=True,
            )
        )

    # Write per-query CSV
    fields = list(per_query[0].keys())
    with (OUT / "FAILURE_MECHANISM_PER_QUERY.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per_query)

    # Summaries by population and script slices
    summary = {}
    for pop in sorted({r["population"] for r in per_query}):
        rows = [r for r in per_query if r["population"] == pop]
        summary[pop] = summarize(rows)
        # script slices with gold
        for sc in ("ROMAN", "URDU", "MIXED"):
            sub = [r for r in rows if r["script_type"] == sc and r["lexical_overlap_cov"] != ""]
            if sub:
                summary[f"{pop}__{sc}"] = summarize(sub)

    # Hypothesis tests (descriptive)
    a = [r for r in per_query if r["population"] == "A_n78_dev_internal_val"]
    a_rom = [r for r in a if r["script_type"] == "ROMAN"]
    k = [r for r in per_query if r["population"] == "B_K001_K040"]
    k_rom = [r for r in k if r["script_type"] == "ROMAN"]
    d = [r for r in per_query if r["population"] == "D_programB_roman_kn_n80"]

    def covs(rows):
        return [float(r["lexical_overlap_cov"]) for r in rows if r["lexical_overlap_cov"] != ""]

    hypotheses = {
        "H1_dev_higher_lexical_overlap": {
            "A_all_mean_cov": mean(covs(a)),
            "A_roman_mean_cov": mean(covs(a_rom)),
            "K_all_mean_cov": mean(covs(k)),
            "K_roman_mean_cov": mean(covs(k_rom)),
            "D_roman_mean_cov": mean(covs(d)),
            "A_roman_pct_cov_ge_0.5": pct(covs(a_rom), lambda x: x >= 0.5),
            "K_roman_pct_cov_ge_0.5": pct(covs(k_rom), lambda x: x >= 0.5),
            "D_roman_pct_cov_ge_0.5": pct(covs(d), lambda x: x >= 0.5),
            "A_roman_pct_cov_0": pct(covs(a_rom), lambda x: x == 0.0),
            "D_roman_pct_cov_0": pct(covs(d), lambda x: x == 0.0),
            "interpretation": (
                "If A Roman mean coverage >> D Roman, H1 supported: "
                "87% pool is title-lexical; hard Roman KN is low-overlap."
            ),
        },
        "H10_benchmark_construction": {
            "A_creation_methods": dict(Counter(r["creation_method"] for r in a)),
            "K_creation_methods": dict(Counter(r["creation_method"] for r in k)),
            "D_writers": dict(Counter(r["creation_method"] for r in d)),
            "D_headline_overlap_meta_zero_or_empty": sum(
                1
                for r in d
                if not r["headline_overlap_meta"]
                or float(r["headline_overlap_meta"] or 0) == 0
            ),
            "note": "A=title-derived QTRN; K=title-like/ordinary Roman of headline; D=naturalistic Roman with ~0 headline_overlap meta",
        },
        "D_failure_levels": dict(Counter(r["failure_level"] for r in d)),
        "D_failure_mechanisms_among_LEVEL3": dict(
            Counter(
                r["failure_mechanism"]
                for r in d
                if "LEVEL3" in (r["failure_level"] or "") or "LEVEL2" in (r["failure_level"] or "")
            )
        ),
        "official_hit5_reference_not_recomputed": {
            "A_overall": "68/78=87.18%",
            "A_roman_methodD": "22/23 from DEVELOPMENT_RESULTS",
            "K_overall": "27/40=67.50%",
            "K_roman": "1/12 from Program A manuscript narrative",
            "K_urdu": "26/28 from Program A manuscript narrative",
            "U_success5": "23/40=57.50% (not ExactSource)",
            "D_dense": "20/80",
            "D_bnd_ceiling": "49/80",
        },
    }

    (OUT / "POPULATION_SUMMARY.json").write_text(
        json.dumps({"summaries": summary, "hypotheses": hypotheses}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(hypotheses["H1_dev_higher_lexical_overlap"], indent=2))
    print("D levels", hypotheses["D_failure_levels"])
    print("wrote", OUT / "FAILURE_MECHANISM_PER_QUERY.csv")


if __name__ == "__main__":
    main()
