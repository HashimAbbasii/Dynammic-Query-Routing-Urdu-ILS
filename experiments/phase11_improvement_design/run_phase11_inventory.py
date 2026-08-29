# -*- coding: utf-8 -*-
"""
Phase 11 inventory only.
Train split + existing dict/variant map + train source rows.
No BM25. No H001-H040. No dictionary writes.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
TRAIN = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_train.csv")
DICT = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")
sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402

OUT = _DIR

# Closed English-looking dict keys (keys that are English/news loanwords in the existing 198-key file).
DICT_ENGLISH_KEYS = {
    "actor", "army", "bank", "batting", "bowling", "business", "century",
    "computer", "court", "cpec", "cricket", "dollar", "drama", "economy",
    "election", "fielding", "film", "flood", "football", "four", "game",
    "goal", "government", "hospital", "imf", "important", "india", "internet",
    "leader", "loss", "market", "match", "mobile", "navy", "news", "out",
    "over", "pakistan", "party", "petrol", "pm", "police", "price", "psl",
    "ptv", "run", "school", "score", "serious", "six", "speech", "team",
    "technology", "today", "vote", "wicket", "win",
}

FUNCTION_KEYS = {
    "aaj", "aj", "aur", "bhi", "do", "gaya", "geya", "hai", "hain", "hi",
    "ho", "hoga", "hui", "ka", "ke", "ki", "kiya", "ko", "kya", "lekin",
    "mein", "na", "nahi", "ne", "ny", "par", "phir", "se", "sy", "tha",
    "thi", "thy", "sehat",
}

# High-df function-word *class* from dict + Phase 5 variant map. Not from H queries.
STOP_CANDIDATES = ["ka", "ki", "ke", "ko", "se", "sy", "mein", "hai", "hain", "ne", "ny", "par", "aur", "bhi", "kya", "kiya"]


def is_latin(tok):
    return bool(tok) and all(("a" <= c <= "z") or c.isdigit() for c in tok)


def main():
    with open(DICT, encoding="utf-8") as f:
        fwd = json.load(f)
    rev = p5.load_reverse_roman(fwd)
    by_ur = defaultdict(list)
    for lat, ur in fwd.items():
        by_ur[ur].append(lat)

    rows = list(csv.DictReader(open(TRAIN, encoding="utf-8")))
    assert len(rows) == 182, len(rows)
    ids = [r["query_id"] for r in rows]
    assert all(not i.startswith("H") for i in ids), "train contains H ids"
    assert all(i.startswith("QTRN_") for i in ids)

    lang = Counter(r["language_type"] for r in rows)
    method = Counter(r["creation_method"] for r in rows)
    roman = [r for r in rows if r["language_type"] == "roman_urdu"]
    mixed = [r for r in rows if r["language_type"] == "mixed"]
    urdu = [r for r in rows if r["language_type"] == "urdu"]

    qtok_roman = Counter()
    dict_hits = Counter()
    nondict = Counter()
    variant_hits = Counter()
    english_in_roman_q = Counter()
    func_in_roman_q = Counter()
    for r in roman:
        for t in p5.tokenize(r["query_text"]):
            qtok_roman[t] += 1
            if t in fwd:
                dict_hits[t] += 1
            else:
                nondict[t] += 1
            key = p5._VARIANT_TO_DICT_KEY.get(t)
            if key:
                variant_hits[t] += 1
            if t in DICT_ENGLISH_KEYS:
                english_in_roman_q[t] += 1
            if t in FUNCTION_KEYS or t in STOP_CANDIDATES:
                func_in_roman_q[t] += 1

    mixed_latin = Counter()
    mixed_urdu = Counter()
    for r in mixed:
        for t in p5.tokenize(r["query_text"]):
            if p5.has_urdu(t):
                mixed_urdu[t] += 1
            elif is_latin(t):
                mixed_latin[t] += 1

    # Headline Method D vs query tokens (train roman only). Not BM25.
    src_ids = sorted({int(r["source_doc_id"]) for r in rows})
    print("loading corpus headlines for %s train source ids..." % len(src_ids), flush=True)
    df = p5.pd.read_csv(p5.CORPUS, encoding="utf-8-sig", usecols=["Headline", "News Text"])
    naive_vs_methodd = Counter()  # (query_form, methodd_form)
    q_not_in_hl_roman = Counter()
    latin_in_source = Counter()  # latin tokens in train source headline+lead snippet
    english_query_and_source_latin = Counter()
    english_query_not_in_hl_roman = Counter()

    for r in roman:
        did = int(r["source_doc_id"])
        hl = str(df["Headline"].iloc[did] or "")
        body = str(df["News Text"].iloc[did] or "")[:400]
        qtoks = p5.tokenize(r["query_text"])
        qset = set(qtoks)
        hl_utoks = p5.tokenize(hl)
        hl_roman = []
        for u in hl_utoks:
            rr = p5.romanize_token(u, rev)
            if rr:
                hl_roman.append(rr)
            naive = p5.naive_roman_word(u).lower() if p5.has_urdu(u) else u.lower()
            md = rr
            if naive and md and naive != md:
                if naive in qset:
                    naive_vs_methodd[(naive, md)] += 1
        hl_rset = set(hl_roman)
        for t in qtoks:
            if t not in hl_rset:
                q_not_in_hl_roman[t] += 1
                if t in DICT_ENGLISH_KEYS or (t.isascii() and t.isalpha() and len(t) >= 4 and t in p5.tokenize(hl + " " + body)):
                    english_query_not_in_hl_roman[t] += 1
        src_latin = [t for t in p5.tokenize(hl + " " + body) if t.isascii() and t.isalpha() and len(t) >= 3]
        for t in src_latin:
            latin_in_source[t] += 1
        for t in qtoks:
            if t in src_latin:
                english_query_and_source_latin[t] += 1

    # Also latin tokens in ALL train source headlines (all language types)
    latin_train_hl = Counter()
    for r in rows:
        did = int(r["source_doc_id"])
        hl = str(df["Headline"].iloc[did] or "")
        for t in p5.tokenize(hl):
            if t.isascii() and t.isalpha() and len(t) >= 3:
                latin_train_hl[t] += 1

    dup_keys = {ur: lats for ur, lats in by_ur.items() if len(lats) > 1}

    summary = {
        "n_train": 182,
        "language_type": dict(lang),
        "creation_method": dict(method),
        "n_roman_urdu": len(roman),
        "n_mixed": len(mixed),
        "n_urdu": len(urdu),
        "n_roman_query_tokens": int(sum(qtok_roman.values())),
        "n_roman_unique_tokens": len(qtok_roman),
        "n_roman_tokens_in_dict": int(sum(dict_hits.values())),
        "n_roman_tokens_not_in_dict": int(sum(nondict.values())),
        "heldout_h_ids_in_train": False,
        "bm25_run": False,
        "dictionary_modified": False,
    }

    with open(os.path.join(OUT, "TRAIN_SPLIT_SUMMARY.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    def dump_counter(path, ctr, extra_header=None):
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["token", "freq_train"] + (extra_header or []))
            for tok, n in ctr.most_common():
                w.writerow([tok, n])

    dump_counter(os.path.join(OUT, "TRAIN_ROMAN_TOKEN_FREQ.csv"), qtok_roman)
    dump_counter(os.path.join(OUT, "TRAIN_ROMAN_DICT_HITS.csv"), dict_hits)
    dump_counter(os.path.join(OUT, "TRAIN_ROMAN_NONDICT.csv"), nondict)
    dump_counter(os.path.join(OUT, "TRAIN_ROMAN_ENGLISH_DICTKEYS.csv"), english_in_roman_q)
    dump_counter(os.path.join(OUT, "TRAIN_ROMAN_FUNCTION_TOKENS.csv"), func_in_roman_q)
    dump_counter(os.path.join(OUT, "TRAIN_MIXED_LATIN_TOKENS.csv"), mixed_latin)
    dump_counter(os.path.join(OUT, "TRAIN_SOURCE_HEADLINE_LATIN.csv"), latin_train_hl)

    with open(os.path.join(OUT, "DICT_DUPLICATE_VALUES.json"), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in sorted(dup_keys.items())}, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "_raw_naive_vs_methodd.json"), "w", encoding="utf-8") as f:
        json.dump({("%s\t%s" % k): v for k, v in naive_vs_methodd.most_common()}, f, indent=2)

    with open(os.path.join(OUT, "_raw_q_not_in_headline_roman.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["token", "freq_train_roman_queries_not_in_source_headline_methodd"])
        for t, n in q_not_in_hl_roman.most_common(80):
            w.writerow([t, n])

    with open(os.path.join(OUT, "_raw_english_in_query_and_source.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["token", "freq"])
        for t, n in english_query_and_source_latin.most_common():
            w.writerow([t, n])

    print("SUMMARY", json.dumps(summary, indent=2))
    print("roman n", len(roman), "mixed", len(mixed))
    print("top roman tokens", qtok_roman.most_common(25))
    print("variant map hits in train roman", dict(variant_hits))
    print("dup dict values", len(dup_keys))
    print("naive vs methodd pairs", len(naive_vs_methodd), naive_vs_methodd.most_common(20))
    print("english dictkeys in roman q", english_in_roman_q.most_common())
    print("mixed latin", mixed_latin.most_common())
    print("func", func_in_roman_q.most_common())
    print("latin in train headlines top", latin_train_hl.most_common(30))
    print("english q and source latin", english_query_and_source_latin.most_common())


if __name__ == "__main__":
    main()
