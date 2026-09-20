# -*- coding: utf-8 -*-
"""R2 Phase-2 decision audit. Read-only verification of existing TRAIN/DEV artifacts.

Does not implement retrieval. Does not load TEST query CSVs.
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter

_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.abspath(os.path.join(_DIR, "..", "benchmark"))
TEST_DIR = os.path.join(BENCH, "test")


def refuse_test(path: str) -> None:
    ap = os.path.abspath(path)
    if ap == TEST_DIR or ap.startswith(TEST_DIR + os.sep):
        if os.path.basename(ap) == "seal.json":
            return
        raise SystemExit("REFUSED: TEST query path %s" % ap)


def main() -> int:
    print("R2 Phase-2 decision audit; TEST query CSVs not loaded", flush=True)
    b0_path = os.path.join(_DIR, "R2_B0_FAILURE_ANALYSIS.csv")
    c0_path = os.path.join(_DIR, "R2_C0_REPRESENTATION_AUDIT.csv")
    r21_path = os.path.join(_DIR, "R2_1_PER_QUERY.csv")
    for p in (b0_path, c0_path, r21_path):
        refuse_test(p)
    b0 = list(csv.DictReader(open(b0_path, encoding="utf-8")))
    c0 = list(csv.DictReader(open(c0_path, encoding="utf-8")))
    r21 = list(csv.DictReader(open(r21_path, encoding="utf-8")))
    assert len(b0) == 47
    assert Counter(r["miss_side"] for r in b0) == Counter({"MISS": 45, "RANK": 2})
    assert Counter(r["primary"] for r in b0)["ROOM"] == 19
    assert Counter(r["primary"] for r in b0)["ENT"] == 16
    assert Counter(r["primary"] for r in b0)["VOCAB"] == 9
    assert len(c0) == 51
    assert sum(int(r["hit@5"]) for r in c0) == 4
    assert sum(int(r["in_top50"]) for r in c0) == 6
    room1 = [r["query_id"] for r in c0 if r["primary"] == "ROOM" and r["cand_cat"] == "1"]
    assert len(room1) == 11
    assert sum(int(r["baseline_hit50"]) for r in r21) == 6
    assert sum(int(r["treatment_hit50"]) for r in r21) == 6
    assert sum(int(r["recovered"]) for r in r21) == 0
    seal = os.path.join(TEST_DIR, "seal.json")
    refuse_test(seal)
    man = json.loads(open(seal, encoding="utf-8").read())
    assert man.get("kind") == "ultra_v2_test_seal"
    print("verified R2-B0/C0/R2-1 counts; seal kind ok; TEST CSVs not opened")
    print("ROOM Category 1 n=11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
