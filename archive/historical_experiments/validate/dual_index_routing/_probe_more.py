# -*- coding: utf-8 -*-
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from router import decide, confidence_tier
qs = [
    "؟",
    "the",
    "123",
    "a b c d e f g h",
    "why did pakistan lose the match in detail please explain",
    "petrol price",
    "score",
    "آج",
    "xyz abc",
]
for q in qs:
    d = decide(q, "svm_v2")
    t = confidence_tier(d["confidence"])
    print(f"{d['confidence']:6.1f} {t:6s} {d['label']:5s} {q[:50]}")
