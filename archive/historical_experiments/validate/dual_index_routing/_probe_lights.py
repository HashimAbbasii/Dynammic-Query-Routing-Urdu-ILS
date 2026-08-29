# -*- coding: utf-8 -*-
"""Find live HIGH/MEDIUM/LOW queries without loading Chroma."""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from router import decide, confidence_tier

cands = [
    "کرکٹ میچ",
    "ڈالر کی قیمت کتنی بڑھی",
    "آج پاکستان کا اسکور کیا ہے",
    "پیٹرول کیوں مہنگا",
    "شکست کی وجہ",
    "ٹیم ہار کا تجزیہ",
    "آج لاہور کا درجہ حرارت کیا ہے",
    "cricket match ka nateeja",
    "aaj pakistan ka score kya hai",
    "why petrol price increased in pakistan last month",
    "xyz",
    "a",
    "کیا",
    "تفصیلی جائزہ وجوہات اور نتائج کے ساتھ وضاحت درکار ہے",
]
# add held-out
sys.path.insert(0, "labels")
from heldout_traps import HELDOUT_TRAPS

for row in HELDOUT_TRAPS:
    cands.append(row[4])

seen = set()
buckets = {"HIGH": [], "MEDIUM": [], "LOW": []}
for q in cands:
    if q in seen:
        continue
    seen.add(q)
    d = decide(q, "svm_v2")
    t = confidence_tier(d["confidence"])
    buckets[t].append((d["confidence"], d["label"], q[:60]))

for t in ("HIGH", "MEDIUM", "LOW"):
    print("====", t, "n=", len(buckets[t]))
    for row in sorted(buckets[t])[:8]:
        print(f"  {row[0]:6.1f}  {row[1]:5s}  {row[2]}")
