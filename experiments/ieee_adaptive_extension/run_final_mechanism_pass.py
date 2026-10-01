#!/usr/bin/env python3
"""Final novelty round: deeper multi-level failure tags on Program B Roman n=80.
No TEST. No new retrieval. Read-only."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
P13 = ROOT / "experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv"
C2A = ROOT / "experiments/ieee_adaptive/C2A_CASE_ANNOTATIONS.csv"
BENCH_TRAIN = ROOT / "experiments/ultra_v2/benchmark/train/queries_kn.csv"
BENCH_DEV = ROOT / "experiments/ultra_v2/benchmark/dev/queries_kn.csv"


def load_queries() -> dict[str, dict]:
    rows = []
    for p in (BENCH_TRAIN, BENCH_DEV):
        rows.extend(csv.DictReader(p.open(encoding="utf-8-sig")))
    return {r["query_id"]: r for r in rows if (r.get("script") or "").upper() == "ROMAN"}


def tag_surface(q: str) -> list[str]:
    tags = []
    ql = q.lower()
    if re.search(r"\b[a-z]{1,3}\b", ql):  # short tokens common in RU
        pass
    if re.search(r"(.)\1{2,}", ql):
        tags.append("repeated_chars")
    if re.search(r"\b(cpec|adb|sbp|fbr|imf|ipl|t20|psl|gdp)\b", ql):
        tags.append("latin_acronym_or_abbrev")
    if re.search(r"\b(kyun|kya|kab|kitna|kitne|kis|kaise|mein|ke|ki|ko|se|par|ne)\b", ql):
        tags.append("urdu_function_words_roman")
    # English IR/news jargon often left in English
    en_jargon = [
        "follow-on",
        "chase",
        "target",
        "milestone",
        "external debt",
        "current account",
        "policy rate",
        "exchange rate",
        "box office",
        "live action",
        "hardcourt",
        "day night",
        "fixing",
        "innings",
        "rebound",
        "equities",
        "interface",
        "layout",
    ]
    if any(j in ql for j in en_jargon):
        tags.append("english_domain_jargon_untranslated")
    if re.search(r"\b(facebook|twitter|gmail|samsung|snapchat|google)\b", ql):
        tags.append("english_brand_token")
    if "'" in q or "-" in q:
        tags.append("hyphen_or_apostrophe")
    if not tags:
        tags.append("surface_unremarkable")
    return tags


def tag_linguistic(q: str, intent: str, c2a_lab: str) -> list[str]:
    tags = []
    ql = q.lower()
    # Underspecification: referring expression without name
    if re.search(r"\b(teen|nayi|naya|kisi|hosts)\b", ql) and not re.search(
        r"\b(umar|kangana|salman|shahid|mira|momina|joker|samsung|facebook|gmail|twitter)\b",
        ql,
    ):
        if "teen tennis" in ql or "nayi photo app" in ql or "hosts ko chase" in ql:
            tags.append("underspecified_referent")
    if c2a_lab == "B" and re.search(
        r"\b(umar|kangana|salman|shahid|mira|momina|jhanvi|amitabh)\b", ql
    ):
        tags.append("explicit_person_name")
    if re.search(r"\b(cpec|adb|sbp|fbr|imf|revenue board|state bank)\b", ql):
        tags.append("institutional_surface")
    if intent:
        tags.append(f"intent_{intent}")
    # Compositional: relation between two entities + event attribute
    entities = len(
        re.findall(
            r"\b(pakistan|india|england|iran|amreeka|kolkata|delhi|west indies|sri lanka|"
            r"facebook|twitter|samsung|gmail|cpec|adb|sbp)\b",
            ql,
        )
    )
    if entities >= 2 and re.search(r"\b(ke khilaf|vs|se muqabla|aur)\b", ql):
        tags.append("multi_entity_relation")
    if re.search(r"\b(kyun|kaise|kis|kitna|kitne|kab)\b", ql):
        tags.append("wh_question_form")
    if not tags:
        tags.append("linguistic_unclassified")
    return tags


def tag_bridge(c2a_lab: str, surface: list[str], ling: list[str]) -> str:
    """Single primary suspected bridge failure — not forced into old labels only."""
    if "underspecified_referent" in ling:
        return "underspecified_referent_no_linkable_surface"
    if c2a_lab == "A":
        return "institutional_descriptive_alias"  # closed C2a
    if c2a_lab == "D":
        return "same_en_name_script_conversion"
    if c2a_lab == "C":
        return "crosslingual_semantic_paraphrase"
    if c2a_lab == "E":
        return "rare_vocabulary_product"
    if "english_domain_jargon_untranslated" in surface and c2a_lab == "B":
        return "en_jargon_plus_entity_event_composition"
    if "english_brand_token" in surface:
        return "en_brand_in_urdu_news_framing"
    if "explicit_person_name" in ling or c2a_lab == "B":
        return "cross_script_or_docside_entity_variant"
    if c2a_lab == "G":
        return "other_or_ambiguous_need"
    return "heterogeneous_or_uncertain_bridge"


def main() -> None:
    qs = load_queries()
    assert len(qs) == 80, len(qs)
    p13 = {r["query_id"]: r for r in csv.DictReader(P13.open(encoding="utf-8-sig"))}
    c2a = {r["query_id"]: r for r in csv.DictReader(C2A.open(encoding="utf-8-sig"))}

    out_rows = []
    mech_among_cg = Counter()
    mech_among_rank = Counter()
    surface_cg = Counter()
    ling_cg = Counter()

    for qid, qr in sorted(qs.items()):
        q = qr["query_text"]
        pr = p13[qid]
        lab = (c2a.get(qid) or {}).get("classification", "")
        any5 = any(int(pr[f"{s}_hit@5"]) for s in ("bm25", "ng3", "dense"))
        in50 = any(int(pr[f"{s}_hit@50"]) for s in ("bm25", "ng3", "dense"))
        if any5:
            cg_fail = "0"
            rank_fail = "0"
            status = "SUCCESS"
        elif in50:
            cg_fail = "0"
            rank_fail = "1"
            status = "RANKING_FAILURE"
        else:
            cg_fail = "1"
            rank_fail = "0"
            status = "CG_FAILURE"

        surface = tag_surface(q)
        ling = tag_linguistic(q, qr.get("intent_type", ""), lab)
        bridge = tag_bridge(lab, surface, ling) if status != "SUCCESS" else "n/a_success"

        if status == "CG_FAILURE":
            mech_among_cg[bridge] += 1
            for t in surface:
                surface_cg[t] += 1
            for t in ling:
                ling_cg[t] += 1
        if status == "RANKING_FAILURE":
            mech_among_rank[bridge] += 1

        # confidence: high if C2A exists for CG; else medium
        conf = "high" if (qid in c2a and status == "CG_FAILURE") else (
            "medium" if status != "SUCCESS" else "n/a"
        )

        out_rows.append(
            {
                "query_id": qid,
                "split": qr.get("split", ""),
                "query_text": q,
                "query_type": qr.get("intent_type", ""),
                "writer_id": qr.get("writer_id", ""),
                "surface_failure": "|".join(surface) if status != "SUCCESS" else "",
                "linguistic_failure": "|".join(ling) if status != "SUCCESS" else "",
                "bridge_failure": bridge if status != "SUCCESS" else "",
                "candidate_generation_failure": cg_fail,
                "ranking_failure": rank_fail,
                "suspected_mechanism": bridge if status != "SUCCESS" else "success",
                "c2a_label": lab,
                "status": status,
                "confidence": conf,
                "notes": (c2a.get(qid) or {}).get("mechanism_explanation", "")[:160],
            }
        )

    fields = list(out_rows[0].keys())
    with (OUT / "FINAL_FAILURE_MECHANISM_PER_QUERY.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    summary = {
        "n": 80,
        "status_counts": dict(Counter(r["status"] for r in out_rows)),
        "cg_bridge_mechanisms": dict(mech_among_cg),
        "rank_bridge_mechanisms": dict(mech_among_rank),
        "cg_surface_tags": dict(surface_cg),
        "cg_linguistic_tags": dict(ling_cg),
        "underspecified_in_cg": mech_among_cg.get(
            "underspecified_referent_no_linkable_surface", 0
        ),
        "en_jargon_entity_comp_in_cg": mech_among_cg.get(
            "en_jargon_plus_entity_event_composition", 0
        ),
        "en_brand_in_cg": mech_among_cg.get("en_brand_in_urdu_news_framing", 0),
        "entity_variant_in_cg": mech_among_cg.get(
            "cross_script_or_docside_entity_variant", 0
        ),
        "institutional_in_cg": mech_among_cg.get("institutional_descriptive_alias", 0),
    }
    (OUT / "FINAL_MECHANISM_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
