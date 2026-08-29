# -*- coding: utf-8 -*-
"""
Phase 1 forensic analysis. Reads frozen held-out P@5 + classification JSON.
Does not call the SVM, Chroma, or any index.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P5 = ROOT / "validate" / "dual_index_routing" / "labels" / "heldout_routed_p5.json"
CLF = ROOT / "validate" / "dual_index_routing" / "labels" / "heldout_classification.json"
OUT_JSON = Path(__file__).with_name("forensic_table.json")
OUT_CSV = Path(__file__).with_name("forensic_table.csv")
OUT_MD = Path(__file__).with_name("DIAGNOSIS.md")

# P@5 is in 0.1 steps with 0/0.5/1 graded labels. Equal P@5 => tie.
# "Similar" = P@5 equal (strict). Documented before counting.
SIMILAR_P5_EPS = 0.0
POOR_P5 = 0.20


def room(label: str) -> str:
    return "HEADLINE" if str(label).upper() == "SHORT" else "FULL"


def best_index(p_h: float, p_f: float, n_h: float, n_f: float) -> str:
    if abs(p_h - p_f) <= SIMILAR_P5_EPS:
        if abs(n_h - n_f) < 1e-12:
            return "TIE"
        return "HEADLINE" if n_h > n_f else "FULL"
    return "HEADLINE" if p_h > p_f else "FULL"


def categories(row: dict) -> list[str]:
    tags = []
    if row["gold_vs_oracle"] == "disagree":
        tags.append("E_gold_vs_oracle")
    if row["best_actual"] != "TIE" and row["svm_index"] != row["best_actual"]:
        tags.append("A_svm_misses_oracle")
    if row["wc_p5"] > row["svm_p5"] + 1e-12:
        tags.append("B_wordcount_beats_svm_p5")
    if row["svm_vs_gold"] == "agree" and row["svm_p5"] <= POOR_P5:
        tags.append("C_gold_correct_retrieval_poor")
    if row["best_actual"] == "TIE":
        tags.append("D_indexes_tied_p5")
    if not tags:
        tags.append("OK_svm_matches_oracle")
    return tags


def primary(tags: list[str]) -> str:
    order = [
        "E_gold_vs_oracle",
        "A_svm_misses_oracle",
        "B_wordcount_beats_svm_p5",
        "C_gold_correct_retrieval_poor",
        "D_indexes_tied_p5",
        "OK_svm_matches_oracle",
    ]
    for k in order:
        if k in tags:
            return k
    return tags[0]


def main() -> None:
    p5 = json.loads(P5.read_text(encoding="utf-8"))
    clf = {r["query_id"]: r for r in json.loads(CLF.read_text(encoding="utf-8"))["per_query"]}
    gold_proto = p5["gold_room_from_protocol"]

    rows = []
    for q in p5["per_query"]:
        qid = q["query_id"]
        c = clf[qid]
        p_h = float(q["always_headline"]["P@5"])
        p_f = float(q["always_full"]["P@5"])
        n_h = float(q["always_headline"]["nDCG@5"])
        n_f = float(q["always_full"]["nDCG@5"])
        gold = gold_proto[qid]
        svm = q["svm_v2"]["label"]
        wc = q["wordcount"]["label"]
        best = best_index(p_h, p_f, n_h, n_f)
        gold_idx = room(gold)
        svm_idx = room(svm)
        wc_idx = room(wc)
        row = {
            "query_id": qid,
            "query": q["query"],
            "script": c.get("script"),
            "trap_type": c.get("trap_type"),
            "v3_cue_hit": int(c.get("v3_cue_hit") or 0),
            "word_count": c.get("word_count"),
            "gold_protocol": gold,
            "svm": svm,
            "wordcount": wc,
            "svm_conf": round(float(c.get("svm_conf") or 0), 2),
            "svm_tier": c.get("svm_tier"),
            "headline_p5": p_h,
            "full_p5": p_f,
            "headline_ndcg5": round(n_h, 4),
            "full_ndcg5": round(n_f, 4),
            "svm_p5": float(q["svm_v2"]["P@5"]),
            "wc_p5": float(q["wordcount"]["P@5"]),
            "best_actual": best,
            "gold_index": gold_idx,
            "svm_index": svm_idx,
            "wc_index": wc_idx,
            "svm_vs_gold": "agree" if svm == gold else "disagree",
            "wc_vs_gold": "agree" if wc == gold else "disagree",
            "gold_vs_oracle": (
                "tie" if best == "TIE" else ("agree" if gold_idx == best else "disagree")
            ),
            "svm_vs_oracle": (
                "tie" if best == "TIE" else ("agree" if svm_idx == best else "disagree")
            ),
            "wc_vs_oracle": (
                "tie" if best == "TIE" else ("agree" if wc_idx == best else "disagree")
            ),
        }
        tags = categories(row)
        row["categories"] = tags
        row["primary"] = primary(tags)
        rows.append(row)

    def mean(key):
        return sum(r[key] for r in rows) / len(rows)

    n = len(rows)
    n_tie = sum(1 for r in rows if r["best_actual"] == "TIE")
    n_oracle_h = sum(1 for r in rows if r["best_actual"] == "HEADLINE")
    n_oracle_f = sum(1 for r in rows if r["best_actual"] == "FULL")
    n_gold_oracle_dis = sum(1 for r in rows if r["gold_vs_oracle"] == "disagree")
    n_svm_oracle_ok = sum(1 for r in rows if r["svm_vs_oracle"] == "agree")
    n_wc_oracle_ok = sum(1 for r in rows if r["wc_vs_oracle"] == "agree")
    n_svm_gold_ok = sum(1 for r in rows if r["svm_vs_gold"] == "agree")
    n_wc_gold_ok = sum(1 for r in rows if r["wc_vs_gold"] == "agree")
    n_b = sum(1 for r in rows if "B_wordcount_beats_svm_p5" in r["categories"])
    n_a = sum(1 for r in rows if "A_svm_misses_oracle" in r["categories"])
    n_c = sum(1 for r in rows if "C_gold_correct_retrieval_poor" in r["categories"])
    n_e = sum(1 for r in rows if "E_gold_vs_oracle" in r["categories"])
    n_d = sum(1 for r in rows if "D_indexes_tied_p5" in r["categories"])
    n_svm_better_p5 = sum(1 for r in rows if r["svm_p5"] > r["wc_p5"] + 1e-12)
    n_wc_better_p5 = sum(1 for r in rows if r["wc_p5"] > r["svm_p5"] + 1e-12)
    n_p5_tie = sum(1 for r in rows if abs(r["svm_p5"] - r["wc_p5"]) <= 1e-12)

    oracle_p5 = []
    for r in rows:
        if r["best_actual"] == "HEADLINE":
            oracle_p5.append(r["headline_p5"])
        elif r["best_actual"] == "FULL":
            oracle_p5.append(r["full_p5"])
        else:
            oracle_p5.append(r["headline_p5"])  # identical
    oracle_mean = sum(oracle_p5) / n

    summary = {
        "n": n,
        "similar_rule": "P@5 equal => TIE; if P@5 tied, higher nDCG@5 breaks the oracle index; both equal => TIE",
        "means": {
            "headline_p5": round(mean("headline_p5"), 4),
            "full_p5": round(mean("full_p5"), 4),
            "svm_p5": round(mean("svm_p5"), 4),
            "wordcount_p5": round(mean("wc_p5"), 4),
            "oracle_p5": round(oracle_mean, 4),
        },
        "oracle_index_counts": {"HEADLINE": n_oracle_h, "FULL": n_oracle_f, "TIE": n_tie},
        "vs_protocol_gold": {"svm_agree": n_svm_gold_ok, "wordcount_agree": n_wc_gold_ok},
        "vs_retrieval_oracle": {
            "svm_agree": n_svm_oracle_ok,
            "wordcount_agree": n_wc_oracle_ok,
            "gold_disagree_oracle": n_gold_oracle_dis,
        },
        "p5_head_to_head": {
            "svm_better": n_svm_better_p5,
            "wordcount_better": n_wc_better_p5,
            "tie": n_p5_tie,
        },
        "category_counts_multi_label": {
            "A_svm_misses_oracle": n_a,
            "B_wordcount_beats_svm_p5": n_b,
            "C_gold_correct_retrieval_poor": n_c,
            "D_indexes_tied_p5": n_d,
            "E_gold_vs_oracle": n_e,
        },
        "primary_counts": dict(Counter(r["primary"] for r in rows)),
    }

    OUT_JSON.write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    cols = [
        "query_id",
        "query",
        "gold_protocol",
        "svm",
        "wordcount",
        "headline_p5",
        "full_p5",
        "headline_ndcg5",
        "full_ndcg5",
        "best_actual",
        "svm_p5",
        "wc_p5",
        "svm_vs_gold",
        "svm_vs_oracle",
        "wc_vs_oracle",
        "gold_vs_oracle",
        "primary",
        "v3_cue_hit",
        "trap_type",
    ]
    lines = [",".join(cols)]
    for r in rows:
        vals = []
        for k in cols:
            v = r[k]
            s = str(v).replace('"', '""')
            if "," in s or " " in s:
                s = f'"{s}"'
            vals.append(s)
        lines.append(",".join(vals))
    OUT_CSV.write_text("\n".join(lines) + "\n", encoding="utf-8")

    md = f"""# Phase 1 diagnosis — why SVM loses P@5 to word count

**Experiment ID:** phase1-forensic-heldout40  
**Inputs:** `{P5.relative_to(ROOT)}`, `{CLF.relative_to(ROOT)}`  
**No model change. No re-retrieval.** Oracle labels here are diagnostic only (same 40 judgments). Do not train on them.

## Oracle rule (fixed before counting)

- Retrieval-optimal index = higher **P@5**.
- If P@5 is tied, break with **nDCG@5**.
- If both tie → **TIE** (routing does not matter for that query).

## Frozen means (recomputed from the same JSON)

| System | P@5 |
| --- | ---: |
| Always headline / θ=150 | {summary["means"]["headline_p5"]:.4f} |
| Always full | {summary["means"]["full_p5"]:.4f} |
| Word count ≥ 6 | {summary["means"]["wordcount_p5"]:.4f} |
| SVM (deployed) | {summary["means"]["svm_p5"]:.4f} |
| Oracle (pick better index per query) | {summary["means"]["oracle_p5"]:.4f} |

Oracle is only +{100*(summary["means"]["oracle_p5"]-summary["means"]["wordcount_p5"]):.1f} points over word count, and +{100*(summary["means"]["oracle_p5"]-summary["means"]["svm_p5"]):.1f} over SVM. The ceiling on this 40-query set is low because many queries are weak on **both** indexes.

## Who matches the retrieval-optimal index?

| Router | Agree with oracle | Agree with protocol gold |
| --- | ---: | ---: |
| SVM | {n_svm_oracle_ok}/{n - n_tie} (ties excluded from agree count; ties={n_tie}) | {n_svm_gold_ok}/{n} |
| Word count | {n_wc_oracle_ok}/{n - n_tie} | {n_wc_gold_ok}/{n} |
| Protocol gold vs oracle | disagrees on **{n_gold_oracle_dis}/{n}** | — |

P@5 head-to-head SVM vs word count: SVM better **{n_svm_better_p5}**, word count better **{n_wc_better_p5}**, tie **{n_p5_tie}**.

Oracle index split: headline **{n_oracle_h}**, full **{n_oracle_f}**, tie **{n_tie}**.

## Failure categories (multi-label; a query can sit in more than one)

| Code | Meaning | n |
| --- | --- | ---: |
| E | Protocol gold ≠ retrieval-optimal index | {n_e} |
| A | SVM did not pick the retrieval-optimal index | {n_a} |
| B | Word-count P@5 > SVM P@5 on that query | {n_b} |
| C | SVM matches protocol gold but P@5 ≤ {POOR_P5} | {n_c} |
| D | Headline and full P@5 tied | {n_d} |

Primary tag counts: `{summary["primary_counts"]}`.

## Diagnosis (answer to the Phase 1 question)

**The main bottleneck is not “SVM accuracy vs protocol labels.”** SVM already beats word count 60% vs 20% on those labels. The P@5 loss comes from three stacked facts:

1. **Label–index mismatch (E, n={n_e}).** “Headline enough vs need the article” is not the same objective as “which index returns better P@5.” Protocol gold disagrees with the retrieval-optimal index on {n_e}/40 queries. Training harder on those gold labels cannot be assumed to raise P@5.

2. **When SVM follows gold LONG on cue-short queries, the full-article index often hurts.** Examples: H001 (headline P@5 0.50 vs full 0.30), H002 (0.80 vs 0.00). SVM is “right” on the protocol and **wrong** for retrieval. Word count stays in the headline room and wins P@5.

3. **Index quality / evaluation (C and D).** Several queries are near-zero on both rooms (H007, H011, H015, H016, H020, H026, H033, H034). Routing cannot invent relevant documents. n=40 plus 0.5 graded labels is also a noisy ceiling: oracle P@5 is only {summary["means"]["oracle_p5"]:.4f}.

**Ranking of causes on this frozen set**

1. Routing **labels** (intuition ≠ retrieval-optimal) — dominant for the SVM vs word-count P@5 gap.  
2. **Full-article index noise** on short causal queries — dominant for Category A when SVM picks FULL.  
3. **Evaluation set** (small, many dead queries, headline often already good) — limits any router.  
4. SVM **classifier** vs word count — *not* the P@5 bottleneck; it is the classification winner.

Do not retrain the SVM next. Next legal step is Phase 2 **only after** a train/dev split that is **not** these 40 test judgments.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
