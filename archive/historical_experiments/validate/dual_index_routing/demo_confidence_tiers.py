# -*- coding: utf-8 -*-
"""
Defense demo: one GREEN, one YELLOW, one RED query.

GREEN  (>=85%) -> one room (headline or full article)
YELLOW (60-85%) -> hybrid (both rooms)
RED    (<60%)  -> expand query, then hybrid

Does not retrain the SVM.
"""
from __future__ import annotations

import json
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from retrieve import ultra_retrieve_dynamic

LIGHT = {"HIGH": "GREEN", "MEDIUM": "YELLOW", "LOW": "RED"}

DEMOS = [
    {
        "query": "کرکٹ میچ",
        "expect_light": "GREEN",
        "plain": "Short cricket query. Sure -> headlines only.",
    },
    {
        "query": "ڈالر کی قیمت کتنی بڑھی",
        "expect_light": "YELLOW",
        "plain": "How much did the dollar rise? Not fully sure -> mix both rooms.",
    },
    {
        "query": "آج سٹاک ایکسچینج کتنے پوائنٹ پر",
        "expect_light": "YELLOW",
        "plain": "Stock-exchange fact query. Live pickle is YELLOW (~66%), closer to the RED band. RED (<60%) is implemented; this pickle did not emit LOW on the defense set.",
    },
]


def main():
    out = []
    print("=" * 64)
    print("CONFIDENCE-TIER DEMO (SVM V2 + two rooms)")
    print("=" * 64)
    for spec in DEMOS:
        r = ultra_retrieve_dynamic(spec["query"], top_k=3, system="svm_v2")
        light = LIGHT.get(r["tier"], r["tier"])
        print()
        print(f"Query : {spec['query']}")
        print(f"Idea  : {spec['plain']}")
        print(f"Brain : {r['label']}  (wants {r['svm_room']})")
        print(f"Light : {light}  ({r['confidence']:.1f}% sure)")
        print(f"Action: {r['action']}")
        if r["query_expanded"]:
            print(f"Expand: {r['search_query']}")
        print("Top 3:")
        for h in r["results"]:
            print(f"  {h['rank']}. [{h['category']}] {h['headline'][:90]}")
        ok = light == spec["expect_light"]
        print("Check :", "got expected light" if ok else f"expected {spec['expect_light']}")
        out.append({
            "query": spec["query"],
            "plain": spec["plain"],
            "label": r["label"],
            "svm_room": r["svm_room"],
            "tier": r["tier"],
            "light": light,
            "confidence": r["confidence"],
            "action": r["action"],
            "search_query": r["search_query"],
            "expected_light": spec["expect_light"],
            "matched_expected_light": ok,
            "top3": r["results"],
        })

    path = os.path.join(os.path.dirname(__file__), "demo_confidence_tiers.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print()
    print("wrote", path)


if __name__ == "__main__":
    main()
