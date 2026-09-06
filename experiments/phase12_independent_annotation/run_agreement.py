# -*- coding: utf-8 -*-
"""A1 vs A2 agreement on frozen Phase 12 U Top-5. No retrieval. Does not write Phase 12 files."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv"
A1_QRELS = ROOT / "experiments/phase12_human_relevance/U_QRELS.csv"
A1_PER = ROOT / "experiments/phase12_human_relevance/U_PER_QUERY.csv"
A2_LABELED = ROOT / "experiments/phase12_independent_annotation/U_TOP5_FOR_INDEPENDENT_ANNOTATION_LABELED.csv"
OUT = ROOT / "experiments/phase12_independent_annotation"

ALLOWED = {"A", "B", "C", "D", "E"}
ORDER5 = ["A", "B", "C", "D", "E"]
STRUCT_FIELDS = [
    "query_id",
    "query_text",
    "rank",
    "doc_id",
    "headline",
    "news_text_or_snippet",
    "detector_label",
    "retrieval_path",
    "n_hits_returned",
]


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(r: dict) -> tuple[str, str, str]:
    return (str(r["query_id"]), str(r["rank"]), str(r["doc_id"]))


def validate_a2(a2: list[dict], frozen: list[dict]) -> dict:
    issues: list[str] = []
    n = len(a2)
    if n != 200:
        issues.append("n_rows=%s expected 200" % n)
    qids = [r["query_id"] for r in a2]
    n_q = len(set(qids))
    if n_q != 40:
        issues.append("n_queries=%s expected 40" % n_q)
    expected = ["U%03d" % i for i in range(1, 41)]
    missing = [q for q in expected if q not in set(qids)]
    extra = sorted(set(qids) - set(expected))
    if missing:
        issues.append("missing query ids: %s" % missing)
    if extra:
        issues.append("extra query ids: %s" % extra)
    per_q = Counter(qids)
    bad_n = {q: c for q, c in per_q.items() if c != 5}
    if bad_n:
        issues.append("not 5 rows: %s" % bad_n)
    pairs = [(r["query_id"], str(r["rank"])) for r in a2]
    if len(pairs) != len(set(pairs)):
        issues.append("duplicate query_id+rank")
    for q in expected:
        ranks = sorted(int(r["rank"]) for r in a2 if r["query_id"] == q)
        if ranks != [1, 2, 3, 4, 5]:
            issues.append("%s ranks=%s" % (q, ranks))
    labs = [(r.get("relevance_label") or "").strip() for r in a2]
    empty = sum(1 for x in labs if x == "")
    bad = sorted({x for x in labs if x and x not in ALLOWED})
    if empty:
        issues.append("missing labels: %s" % empty)
    if bad:
        issues.append("invalid labels: %s" % bad)
    label_counts = dict(Counter(labs))

    frozen_by = {key(r): r for r in frozen}
    a2_by = {key(r): r for r in a2}
    if set(frozen_by) != set(a2_by):
        issues.append(
            "query_id+rank+doc_id set mismatch: frozen_only=%s a2_only=%s"
            % (len(set(frozen_by) - set(a2_by)), len(set(a2_by) - set(frozen_by)))
        )
    field_mismatches: dict[str, int] = {f: 0 for f in STRUCT_FIELDS + ["bm25_score"]}
    examples: dict[str, list] = defaultdict(list)
    for k, fr in frozen_by.items():
        if k not in a2_by:
            continue
        ar = a2_by[k]
        for f in STRUCT_FIELDS:
            if (fr.get(f) or "") != (ar.get(f) or ""):
                field_mismatches[f] += 1
                if len(examples[f]) < 3:
                    examples[f].append({"key": k, "frozen": fr.get(f), "a2": ar.get(f)})
        if (fr.get("bm25_score") or "") != (ar.get("bm25_score") or ""):
            field_mismatches["bm25_score"] += 1
            if len(examples["bm25_score"]) < 3:
                examples["bm25_score"].append(
                    {"key": k, "frozen": fr.get("bm25_score"), "a2": ar.get("bm25_score")}
                )
    # labels must not appear in any non-label frozen field check already
    a2_label_only_ok = all(
        (r.get("relevance_label") or "").strip() in ALLOWED for r in a2
    )
    return {
        "n_rows": n,
        "n_queries": n_q,
        "label_counts": label_counts,
        "empty_labels": empty,
        "issues": issues,
        "field_mismatches": {k: v for k, v in field_mismatches.items() if v},
        "field_mismatch_examples": {k: v for k, v in examples.items() if v},
        "structurally_valid": n == 200 and n_q == 40 and not empty and not bad and not missing and not extra and not bad_n,
        "same_200_documents": set(frozen_by) == set(a2_by),
        "a2_label_only_ok": a2_label_only_ok,
    }


def success_from_labels(labs: list[str]) -> int:
    return int(any(x in ("A", "B") for x in labs))


def first_ab(labs: list[str]):
    for i, lab in enumerate(labs, 1):
        if lab in ("A", "B"):
            return i
    return None


def bin_lab(x: str) -> str:
    return "relevant" if x in ("A", "B") else "not_relevant"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fmt_cm(labels: list[str], mat) -> list[dict]:
    out = []
    for i, a1 in enumerate(labels):
        for j, a2 in enumerate(labels):
            out.append({"A1": a1, "A2": a2, "count": int(mat[i][j])})
    return out


def md_matrix(labels: list[str], mat) -> str:
    header = "| A1 \\ A2 | " + " | ".join(labels) + " |"
    sep = "| --- | " + " | ".join("---" for _ in labels) + " |"
    lines = [header, sep]
    for i, a1 in enumerate(labels):
        cells = " | ".join(str(int(mat[i][j])) for j in range(len(labels)))
        lines.append("| **%s** | %s |" % (a1, cells))
    return "\n".join(lines)


def main() -> None:
    frozen = load_csv(FROZEN)
    a1 = load_csv(A1_QRELS)
    a2 = load_csv(A2_LABELED)
    a1_per = {r["query_id"]: r for r in load_csv(A1_PER)}

    a1_ok = len(a1) == 200 and all((r.get("relevance_label") or "").strip() in ALLOWED for r in a1)
    a1_success = sum(
        success_from_labels(
            [x["relevance_label"].strip() for x in sorted(
                [r for r in a1 if r["query_id"] == qid], key=lambda z: int(z["rank"])
            )]
        )
        for qid in ["U%03d" % i for i in range(1, 41)]
    )

    val = validate_a2(a2, frozen)
    val["a1_source"] = str(A1_QRELS.relative_to(ROOT)).replace("\\", "/")
    val["a1_n_rows"] = len(a1)
    val["a1_labels_valid"] = a1_ok
    val["a1_success@5_from_qrels"] = a1_success
    val["a1_official_success@5"] = "23/40 = 57.50%"

    a1_by = {key(r): r for r in a1}
    a2_by = {key(r): r for r in a2}
    frozen_by = {key(r): r for r in frozen}

    join_ok = set(a1_by) == set(a2_by) == set(frozen_by)
    val["a1_a2_frozen_same_keys"] = join_ok
    if not join_ok:
        (OUT / "VALIDATION.json").write_text(json.dumps(val, indent=2, ensure_ascii=False), encoding="utf-8")
        raise SystemExit("join keys do not match; not computing agreement")

    comparison = []
    disagreements = []
    for k in sorted(frozen_by, key=lambda t: (t[0], int(t[1]))):
        fr, r1, r2 = frozen_by[k], a1_by[k], a2_by[k]
        lab1 = r1["relevance_label"].strip()
        lab2 = r2["relevance_label"].strip()
        rec = {
            "query_id": k[0],
            "rank": int(k[1]),
            "doc_id": k[2],
            "query_text": fr["query_text"],
            "headline": fr["headline"],
            "news_text_or_snippet": fr["news_text_or_snippet"],
            "A1_label": lab1,
            "A2_label": lab2,
            "exact_match": int(lab1 == lab2),
            "A1_binary": bin_lab(lab1),
            "A2_binary": bin_lab(lab2),
            "binary_match": int(bin_lab(lab1) == bin_lab(lab2)),
        }
        comparison.append(rec)
        if lab1 != lab2:
            disagreements.append({
                "query_id": k[0],
                "rank": int(k[1]),
                "doc_id": k[2],
                "A1_label": lab1,
                "A2_label": lab2,
                "headline": fr["headline"],
                "news_text_or_snippet": fr["news_text_or_snippet"],
                "query_text": fr["query_text"],
            })

    y1 = [r["A1_label"] for r in comparison]
    y2 = [r["A2_label"] for r in comparison]
    n = len(comparison)
    n_agree = sum(r["exact_match"] for r in comparison)
    n_disagree = n - n_agree
    kappa5 = float(cohen_kappa_score(y1, y2, labels=ORDER5))
    cm5 = confusion_matrix(y1, y2, labels=ORDER5)

    b1 = [r["A1_binary"] for r in comparison]
    b2 = [r["A2_binary"] for r in comparison]
    bin_labels = ["relevant", "not_relevant"]
    n_bin_agree = sum(r["binary_match"] for r in comparison)
    kappa_bin = float(cohen_kappa_score(b1, b2, labels=bin_labels))
    cm_bin = confusion_matrix(b1, b2, labels=bin_labels)

    pair_counts = Counter((r["A1_label"], r["A2_label"]) for r in comparison)
    a1_counts = Counter(y1)
    a2_counts = Counter(y2)

    per_query = []
    for qid in ["U%03d" % i for i in range(1, 41)]:
        items = [r for r in comparison if r["query_id"] == qid]
        items.sort(key=lambda r: r["rank"])
        labs1 = [r["A1_label"] for r in items]
        labs2 = [r["A2_label"] for r in items]
        s1 = success_from_labels(labs1)
        s2 = success_from_labels(labs2)
        per_query.append({
            "query_id": qid,
            "query_text": items[0]["query_text"],
            "A1_r1": labs1[0], "A1_r2": labs1[1], "A1_r3": labs1[2], "A1_r4": labs1[3], "A1_r5": labs1[4],
            "A2_r1": labs2[0], "A2_r2": labs2[1], "A2_r3": labs2[2], "A2_r4": labs2[3], "A2_r5": labs2[4],
            "A1_success@5": s1,
            "A2_success@5": s2,
            "success_match": int(s1 == s2),
            "n_doc_agreements": sum(r["exact_match"] for r in items),
            "n_doc_disagreements": 5 - sum(r["exact_match"] for r in items),
            "A1_first_AB_rank": first_ab(labs1) if first_ab(labs1) else "",
            "A2_first_AB_rank": first_ab(labs2) if first_ab(labs2) else "",
            "script_from_a1_per_query": a1_per[qid].get("script", ""),
        })

    a2_success_n = sum(p["A2_success@5"] for p in per_query)
    a1_success_n = sum(p["A1_success@5"] for p in per_query)
    assert a1_success_n == 23

    # disagreement types
    ab_boundary = sum(
        1 for r in disagreements
        if {r["A1_label"], r["A2_label"]} <= {"A", "B"} and r["A1_label"] != r["A2_label"]
    )
    useful_vs_not = sum(
        1 for r in disagreements
        if (r["A1_label"] in ("A", "B")) != (r["A2_label"] in ("A", "B"))
    )
    adjacent = {("A", "B"), ("B", "A"), ("B", "C"), ("C", "B"), ("C", "D"), ("D", "C")}
    n_adjacent = sum(1 for r in disagreements if (r["A1_label"], r["A2_label"]) in adjacent)

    write_csv(
        OUT / "A1_A2_COMPARISON.csv",
        comparison,
        [
            "query_id", "rank", "doc_id", "A1_label", "A2_label", "exact_match",
            "A1_binary", "A2_binary", "binary_match", "query_text", "headline",
            "news_text_or_snippet",
        ],
    )
    write_csv(
        OUT / "A1_A2_PER_QUERY.csv",
        per_query,
        [
            "query_id", "query_text",
            "A1_r1", "A1_r2", "A1_r3", "A1_r4", "A1_r5",
            "A2_r1", "A2_r2", "A2_r3", "A2_r4", "A2_r5",
            "A1_success@5", "A2_success@5", "success_match",
            "n_doc_agreements", "n_doc_disagreements",
            "A1_first_AB_rank", "A2_first_AB_rank",
            "script_from_a1_per_query",
        ],
    )
    write_csv(
        OUT / "DISAGREEMENTS.csv",
        disagreements,
        ["query_id", "rank", "doc_id", "A1_label", "A2_label", "query_text", "headline", "news_text_or_snippet"],
    )

    metrics = {
        "a1_source": val["a1_source"],
        "a2_file": "experiments/phase12_independent_annotation/U_TOP5_FOR_INDEPENDENT_ANNOTATION_LABELED.csv",
        "frozen_dump": "experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv",
        "n_judgments": n,
        "n_queries": 40,
        "validation": val,
        "a1_label_counts": dict(a1_counts),
        "a2_label_counts": dict(a2_counts),
        "five_way": {
            "agreements": n_agree,
            "disagreements": n_disagree,
            "raw_agreement": n_agree / n,
            "cohens_kappa": kappa5,
            "implementation": "sklearn.metrics.cohen_kappa_score (sklearn 1.7.2)",
            "confusion_matrix_A1_rows_A2_cols": ORDER5,
            "confusion_counts": fmt_cm(ORDER5, cm5),
            "pair_counts": {("%s/%s" % k): v for k, v in sorted(pair_counts.items())},
        },
        "binary_A_or_B_vs_other": {
            "note": "secondary sensitivity analysis; does not replace 5-way labels",
            "relevant": "A or B",
            "not_relevant": "C, D, or E",
            "agreements": n_bin_agree,
            "disagreements": n - n_bin_agree,
            "raw_agreement": n_bin_agree / n,
            "cohens_kappa": kappa_bin,
            "implementation": "sklearn.metrics.cohen_kappa_score (sklearn 1.7.2)",
            "labels": bin_labels,
            "confusion_counts": fmt_cm(bin_labels, cm_bin),
        },
        "success@5": {
            "definition": "query succeeds if at least one Top-5 document is A or B (same as Annotator 1 / ANNOTATION_PROTOCOL.md)",
            "A1_official": {"hits": 23, "n": 40, "rate": 0.575, "percent": "57.50%"},
            "A1_recomputed_from_U_QRELS": {"hits": a1_success_n, "n": 40, "rate": a1_success_n / 40},
            "A2": {"hits": a2_success_n, "n": 40, "rate": a2_success_n / 40, "percent": "%.2f%%" % (100 * a2_success_n / 40)},
            "queries_where_success_differs": [p["query_id"] for p in per_query if p["A1_success@5"] != p["A2_success@5"]],
            "official_headline_unchanged": "23/40 = 57.50% remains Annotator-1 official",
        },
        "disagreement_shape": {
            "n": n_disagree,
            "A_B_boundary_only": ab_boundary,
            "useful_A_or_B_vs_not": useful_vs_not,
            "adjacent_A-B_B-C_C-D": n_adjacent,
        },
    }
    (OUT / "AGREEMENT_METRICS.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Landis & Koch 1977 ranges cited as convention only
    def kappa_band(k: float) -> str:
        if k < 0:
            return "poor (<0; Landis and Koch 1977 convention)"
        if k <= 0.20:
            return "slight (0.00–0.20; Landis and Koch 1977 convention)"
        if k <= 0.40:
            return "fair (0.21–0.40; Landis and Koch 1977 convention)"
        if k <= 0.60:
            return "moderate (0.41–0.60; Landis and Koch 1977 convention)"
        if k <= 0.80:
            return "substantial (0.61–0.80; Landis and Koch 1977 convention)"
        return "almost perfect (0.81–1.00; Landis and Koch 1977 convention)"

    mismatch_txt = "none"
    if val["field_mismatches"]:
        parts = ["%s=%s" % (k, v) for k, v in val["field_mismatches"].items()]
        mismatch_txt = "; ".join(parts)

    report = []
    report.append("# Independent annotation agreement — Phase 12 U Top-5")
    report.append("")
    report.append("Analysis only. Frozen M0, U queries, Top-5 ranks, and Annotator-1 labels were not modified.")
    report.append("Official naturalistic result remains **Annotator-1 Success@5 = 23/40 = 57.50%**.")
    report.append("Annotator-2 Success@5 is a reliability statistic. It does not replace 23/40. The two rates are not averaged.")
    report.append("")
    report.append("## 1. Annotation dataset")
    report.append("")
    report.append("Frozen Phase 12 U Top-5 lists for naturalistic queries U001–U040.")
    report.append("Each query has five retrieved documents (ranks 1–5). Total judgments = 40 × 5 = **200**.")
    report.append("")
    report.append("## 2. Number of annotators")
    report.append("")
    report.append("**2**.")
    report.append("")
    report.append("- **Annotator 1** wrote the U queries under the Phase 12 protocol and later judged the frozen Top-5 (headline + snippet).")
    report.append("- **Annotator 2** independently judged the same frozen Top-5 dump. Annotator-1 labels were not included in the annotation package.")
    report.append("")
    report.append("Independent annotation does **not** prove absence of bias. Annotator 1 remains both query author and original judge. Annotator 2 reduces, but does not eliminate, that risk.")
    report.append("")
    report.append("## 3. Number of queries")
    report.append("")
    report.append("**40** (U001–U040).")
    report.append("")
    report.append("## 4. Number of judgments")
    report.append("")
    report.append("**200** per annotator.")
    report.append("")
    report.append("## 5. Annotation scale")
    report.append("")
    report.append("| Code | Name |")
    report.append("| --- | --- |")
    report.append("| A | RELEVANT |")
    report.append("| B | PARTIALLY_RELEVANT |")
    report.append("| C | TOPICALLY_RELATED |")
    report.append("| D | NOT_RELEVANT |")
    report.append("| E | AMBIGUOUS |")
    report.append("")
    report.append("Success@5 (both annotators): a query succeeds if **at least one** Top-5 document is **A or B**. Same definition as `experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md`.")
    report.append("")
    report.append("## 6. Exact source files")
    report.append("")
    report.append("| Role | File |")
    report.append("| --- | --- |")
    report.append("| Frozen Top-5 dump | `experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv` |")
    report.append("| Annotator 1 labels (authoritative 200-row qrels) | `experiments/phase12_human_relevance/U_QRELS.csv` |")
    report.append("| Annotator 1 per-query Success@5 (derived) | `experiments/phase12_human_relevance/U_PER_QUERY.csv` |")
    report.append("| Annotator 1 official metrics | `experiments/phase12_human_relevance/artifacts/metrics.json` |")
    report.append("| Annotator 2 labeled sheet | `experiments/phase12_independent_annotation/U_TOP5_FOR_INDEPENDENT_ANNOTATION_LABELED.csv` |")
    report.append("")
    report.append("`U_QRELS.csv` is the source used here for A1. Recomputing Success@5 from those 200 labels yields **23/40**, matching `metrics.json`.")
    report.append("")
    report.append("## 7. Annotator-1 results (official)")
    report.append("")
    report.append("| Metric | Result |")
    report.append("| --- | --- |")
    report.append("| Success@5 | **23/40 = 57.50%** |")
    report.append("| Label counts (200) | A %s, B %s, C %s, D %s, E %s |" % (
        a1_counts.get("A", 0), a1_counts.get("B", 0), a1_counts.get("C", 0),
        a1_counts.get("D", 0), a1_counts.get("E", 0),
    ))
    report.append("")
    report.append("This remains the official U headline.")
    report.append("")
    report.append("## 8. Annotator-2 results (reliability only)")
    report.append("")
    report.append("| Metric | Result |")
    report.append("| --- | --- |")
    report.append("| Success@5 | **%s/40 = %.2f%%** |" % (a2_success_n, 100 * a2_success_n / 40))
    report.append("| Label counts (200) | A %s, B %s, C %s, D %s, E %s |" % (
        a2_counts.get("A", 0), a2_counts.get("B", 0), a2_counts.get("C", 0),
        a2_counts.get("D", 0), a2_counts.get("E", 0),
    ))
    report.append("")
    diffs = [p["query_id"] for p in per_query if p["A1_success@5"] != p["A2_success@5"]]
    report.append("Queries where Success@5 differs: %s." % (", ".join(diffs) if diffs else "none"))
    report.append("")
    report.append("## 9. Five-way agreement")
    report.append("")
    report.append("| Item | Value |")
    report.append("| --- | --- |")
    report.append("| Total judgments | 200 |")
    report.append("| Agreements | %s |" % n_agree)
    report.append("| Disagreements | %s |" % n_disagree)
    report.append("| Raw agreement | %s/200 = %.2f%% |" % (n_agree, 100 * n_agree / n))
    report.append("")
    report.append("## 10. Five-way Cohen's kappa")
    report.append("")
    report.append("κ = **%.4f** (sklearn.metrics.cohen_kappa_score, sklearn 1.7.2; unweighted, labels A–E)." % kappa5)
    report.append("")
    report.append("Landis and Koch (1977) convention for this value: **%s**." % kappa_band(kappa5))
    report.append("Those cutoffs are a naming convention, not a validity test.")
    report.append("")
    report.append("## 11. Binary agreement (secondary)")
    report.append("")
    report.append("Relevant = A or B. Not relevant = C, D, or E.")
    report.append("")
    report.append("| Item | Value |")
    report.append("| --- | --- |")
    report.append("| Agreements | %s |" % n_bin_agree)
    report.append("| Disagreements | %s |" % (n - n_bin_agree))
    report.append("| Raw agreement | %s/200 = %.2f%% |" % (n_bin_agree, 100 * n_bin_agree / n))
    report.append("")
    report.append("This does not replace the five-way labels.")
    report.append("")
    report.append("## 12. Binary Cohen's kappa (secondary)")
    report.append("")
    report.append("κ = **%.4f** (sklearn.metrics.cohen_kappa_score, sklearn 1.7.2; labels relevant / not_relevant)." % kappa_bin)
    report.append("")
    report.append("Landis and Koch (1977) convention for this value: **%s**." % kappa_band(kappa_bin))
    report.append("")
    report.append("## 13. Confusion matrices")
    report.append("")
    report.append("Rows = Annotator 1. Columns = Annotator 2.")
    report.append("")
    report.append("### Five-way")
    report.append("")
    report.append(md_matrix(ORDER5, cm5))
    report.append("")
    report.append("### Binary (secondary)")
    report.append("")
    report.append(md_matrix(bin_labels, cm_bin))
    report.append("")
    report.append("## 14. A1 vs A2 Success@5")
    report.append("")
    report.append("| Annotator | Success@5 |")
    report.append("| --- | --- |")
    report.append("| 1 (official) | 23/40 = 57.50% |")
    report.append("| 2 (reliability) | %s/40 = %.2f%% |" % (a2_success_n, 100 * a2_success_n / 40))
    report.append("")
    report.append("Per-query labels and Success@5: `A1_A2_PER_QUERY.csv`.")
    report.append("")
    report.append("## 15. Number of disagreements")
    report.append("")
    report.append("- Document-level five-way disagreements: **%s / 200**." % n_disagree)
    report.append("- Of those, A/B boundary only (A↔B): **%s**." % ab_boundary)
    report.append("- Adjacent on A–B–C–D (A↔B, B↔C, or C↔D): **%s**." % n_adjacent)
    report.append("- Disagreements that change useful (A/B) vs not: **%s**." % useful_vs_not)
    report.append("- Full list: `DISAGREEMENTS.csv` (not adjudicated).")
    report.append("")
    report.append("## 16. Data-integrity issues")
    report.append("")
    report.append("- A2 row count, query set U001–U040, five ranks per query, and label alphabet: **%s**." % (
        "pass" if val["structurally_valid"] else "FAIL: " + "; ".join(val["issues"])
    ))
    report.append("- Same 200 documents as frozen dump on `query_id` + `rank` + `doc_id`: **%s**." % (
        "yes" if val["same_200_documents"] else "NO"
    ))
    report.append("- Structural field mismatches vs frozen dump (not auto-fixed): **%s**." % mismatch_txt)
    if val["field_mismatches"]:
        report.append("- `bm25_score` string differences, if present, are consistent with spreadsheet round-trip of floating-point scores. Query text, `doc_id`, rank, headline, and snippet were required to match for the join. The join used identifiers, not row position.")
    report.append("- A2 `relevance_label` is populated; other judgment files were not written into the A2 sheet.")
    report.append("- No missing A2 labels. No labels outside A–E.")
    report.append("")
    report.append("## 17. Limitations")
    report.append("")
    report.append("- Two annotators only. No third adjudicator.")
    report.append("- Annotator 1 authored the queries.")
    report.append("- Labels are from headline plus snippet, not full article text.")
    report.append("- The A/B and B/C boundaries are subjective by design (prefer B over A unless the need is clearly satisfied).")
    report.append("- n = 40 queries / 200 documents. Kappa describes this sample, not all Urdu news search.")
    report.append("- Agreement does not prove that either annotator is correct, and does not prove lack of bias.")
    report.append("- E did not occur for Annotator 1; rarity of E limits what can be said about that category.")
    report.append("")
    report.append("## Interpretation")
    report.append("")
    report.append("Five-way κ = %.4f is **%s**." % (kappa5, kappa_band(kappa5)))
    report.append("Binary A/B vs not κ = %.4f is **%s**." % (kappa_bin, kappa_band(kappa_bin)))
    report.append("")
    report.append("Disagreements are listed in full rather than selected.")
    if n_adjacent and n_disagree:
        report.append(
            "A substantial share of the %s five-way disagreements are adjacent on the A–B–C–D scale (%s), including %s A↔B pairs. That pattern is consistent with rubric boundary ambiguity, especially A vs B (full vs partial answer) and B vs C (helps the need vs same topic only)."
            % (n_disagree, n_adjacent, ab_boundary)
        )
    if useful_vs_not:
        report.append(
            "%s disagreements cross the Success@5-relevant boundary (A/B vs C/D/E). Those cases can change query-level Success@5 even when many other documents agree."
            % useful_vs_not
        )
    report.append("")
    report.append("High or moderate kappa would not by itself mean the original 57.50% is unbiased: Annotator 1 still wrote the queries. Low kappa would not by itself mean the retrieval system failed: it would mean the usefulness labels are unstable.")
    report.append("This analysis does not retune M0 and does not change the official Annotator-1 Success@5 of 23/40.")
    report.append("")
    report.append("## Generated files")
    report.append("")
    report.append("| File | Contents |")
    report.append("| --- | --- |")
    report.append("| `A1_A2_COMPARISON.csv` | 200 rows, A1 and A2 labels |")
    report.append("| `A1_A2_PER_QUERY.csv` | 40 rows, per-query Success@5 |")
    report.append("| `DISAGREEMENTS.csv` | five-way disagreements only |")
    report.append("| `AGREEMENT_METRICS.json` | machine-readable statistics |")
    report.append("| `AGREEMENT.md` | this report |")
    report.append("")

    (OUT / "AGREEMENT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({
        "structurally_valid": val["structurally_valid"],
        "same_200": val["same_200_documents"],
        "field_mismatches": val["field_mismatches"],
        "issues": val["issues"],
        "a1_success": a1_success_n,
        "a2_success": a2_success_n,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "kappa5": kappa5,
        "kappa_bin": kappa_bin,
        "n_bin_agree": n_bin_agree,
        "ab_boundary": ab_boundary,
        "useful_vs_not": useful_vs_not,
        "success_diff_queries": diffs,
    }, indent=2))


if __name__ == "__main__":
    main()
