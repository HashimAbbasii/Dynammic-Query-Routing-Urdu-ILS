# -*- coding: utf-8 -*-
"""Smoke-test live dual-index retrieve on a few queries. Slow first load."""
import json
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from retrieve import ultra_retrieve_dynamic

QUERIES = [
    "کرکٹ میچ",
    "cricket match ka nateeja",
    "پاکستان میں بڑھتی ہوئی مہنگائی اور روزگار کے مسائل پر حکومتی اقدامات کا جائزہ",
]
out = []
for q in QUERIES:
    r = ultra_retrieve_dynamic(q, top_k=3, system="svm_v2")
    slim = {
        "query": q,
        "label": r["label"],
        "mode": r["mode"],
        "confidence": r["confidence"],
        "roman_transliterated": r["roman_transliterated"],
        "top3": [{"headline": h["headline"], "score": h["score"]} for h in r["results"]],
    }
    out.append(slim)
    print(q, "->", r["label"], r["mode"], f"{r['confidence']:.1f}%")
    for h in slim["top3"]:
        print("   ", h["headline"][:80])

path = os.path.join(os.path.dirname(__file__), "live_smoke.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("wrote", path)
