# -*- coding: utf-8 -*-
"""R2-C0 diagnostic audit. TRAIN/DEV Roman KN only. No TEST. No M0 edits.

COUNTERFACTUAL calculations are overlap diagnostics, not official retrieval results.
"""
from __future__ import annotations

import csv
import json
import os
import pickle
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
CACHE = os.path.join(ART, "_index_cache.pkl")
FAIL_CSV = os.path.join(_DIR, "R2_B0_FAILURE_ANALYSIS.csv")
B0_CSV = os.path.join(ART, "r2_b0_per_query.csv")

sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402

FUNCTION = {
    "ka", "ke", "ki", "ko", "se", "ne", "ny", "sy", "hai", "hain", "ho", "hone",
    "mein", "par", "kya", "kiya", "kia", "kyun", "kab", "kis", "kitna", "kitne",
    "kitni", "tha", "thi", "thay", "thy", "aur", "ya", "to", "bhi", "nahi",
    "nahin", "nai", "kaise", "kaisa", "wali", "wala", "walay", "hue", "hui",
    "hua", "huin", "kar", "liye", "sath", "baad", "pehle", "tak", "hi", "bhi",
}
VOWELS = set("aeiou")
ENGLISH_HINT = {
    "world", "championship", "race", "air", "third", "round", "hosts", "chase",
    "target", "local", "equities", "opening", "rebound", "tension", "thriller",
    "margin", "tennis", "sensation", "canadian", "hardcourt", "title", "accounts",
    "revenue", "board", "hydrogen", "solar", "wind", "powered", "boat", "cup",
    "fixture", "tickets", "black", "mobile", "slow", "charge", "user", "side",
    "viral", "maths", "puzzle", "internet", "users", "confuse", "african", "kids",
    "hair", "compliment", "exchange", "tour", "boom", "supersonic", "passenger",
    "prototype", "unveil", "fable", "fitness", "maintain", "joint", "cooperation",
    "committee", "session", "jungle", "book", "live", "action", "box", "office",
    "record", "west", "indies", "day", "night", "series", "milestone", "test",
    "country", "director", "investment", "wrestler", "film", "poster", "director",
    "movie", "chameleon", "satellite", "minutes", "mission", "assume", "state",
    "bank", "external", "debt", "burden", "percent", "houston", "new", "year",
    "show", "community", "event", "bowling", "ranking", "number", "one", "germany",
    "top", "fixing", "case", "auction", "bushfire", "fund", "oscar", "short",
    "documentary", "category", "local", "oil", "gas", "output", "photo", "app",
    "android", "handset", "china", "launch", "minute", "sold", "out", "galaxy",
    "active", "leak", "caretaker", "finance", "minister", "projects", "current",
    "account", "deficit", "slow", "front", "design", "apple", "flagship",
    "twitter", "feature", "facebook", "snapchat", "messenger", "rooms", "group",
    "video", "chat", "add", "railway", "upgrade", "deadline", "track", "sales",
    "tax", "input", "deal", "lite", "note", "lineup", "final", "stadium",
    "personnel", "deploy", "foundation", "interface", "layout", "human", "like",
    "robots", "cameras", "mate",
}


def refuse_test(path: str) -> None:
    ap = os.path.abspath(path)
    if ap == TEST_DIR or ap.startswith(TEST_DIR + os.sep):
        raise SystemExit("REFUSED: TEST path %s" % ap)


def skeleton(tok: str) -> str:
    return "".join(c for c in tok if c.isalpha() and c not in VOWELS)


def tok_class(t: str) -> str:
    if t.isdigit() or any(c.isdigit() for c in t):
        return "number"
    if t in FUNCTION:
        return "function"
    if t in ENGLISH_HINT:
        return "english"
    return "other_latin"


def load_fail_map() -> dict[str, dict]:
    refuse_test(FAIL_CSV)
    out = {}
    with open(FAIL_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def load_b0() -> dict[str, dict]:
    refuse_test(B0_CSV)
    out = {}
    with open(B0_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def load_kn_roman() -> list[dict]:
    rows = []
    for split in ("train", "dev"):
        path = os.path.join(BENCH, split, "queries_kn.csv")
        refuse_test(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("script") or "").strip() != "ROMAN":
                    continue
                rows.append({
                    "query_id": r["query_id"],
                    "split": split,
                    "query_text": r["query_text"],
                    "source_doc_id": int(r["source_doc_id"]),
                })
    return rows


def romanize_with_path(tok: str, rev: dict) -> tuple[str, str]:
    if p5.has_urdu(tok):
        lat = rev.get(tok)
        if lat:
            return lat.lower(), "dict"
        return p5.naive_roman_word(tok).lower(), "fallback"
    return tok.lower(), "latin"


def main() -> int:
    print("R2-C0 diagnostic; TEST_accessed=no", flush=True)
    kn = load_kn_roman()
    b0 = load_b0()
    fail = load_fail_map()
    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    dict_values = set(fwd.values())

    import pandas as pd

    refuse_test(p5.CORPUS)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        body = df["combined_text"].fillna("").astype(str)
    else:
        body = df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)
    headlines = df["Headline"].fillna("").astype(str)

    roman_bm25 = None
    if os.path.isfile(CACHE):
        with open(CACHE, "rb") as f:
            blob = pickle.load(f)
        roman_bm25 = blob.get("roman_bm25")

    gold_docs_using_dict = 0
    gold_docs_using_fallback = 0
    fallback_fracs = []
    dict_fracs = []
    latin_fracs = []
    shorten_ratios = []
    empty_maps = 0
    fallback_tokens_total = 0
    urdu_tokens_total = 0
    collision_docs = 0

    per = []
    for r in kn:
        qid = r["query_id"]
        gold_id = r["source_doc_id"]
        qtoks = p5.tokenize(r["query_text"])
        gtext = str(body.iloc[gold_id])
        hline = str(headlines.iloc[gold_id])
        orig = p5.tokenize(gtext)
        paths = []
        md = []
        for t in orig:
            rt, path = romanize_with_path(t, rev)
            if rt:
                md.append(rt)
                paths.append(path)
            else:
                empty_maps += 1
            if path == "fallback" and rt:
                urdu_tokens_total += 1
                fallback_tokens_total += 1
                shorten_ratios.append(len(rt) / max(len(t), 1))
            elif path == "dict":
                urdu_tokens_total += 1
            elif path == "fallback":
                urdu_tokens_total += 1
        n_d = paths.count("dict")
        n_f = paths.count("fallback")
        n_l = paths.count("latin")
        n_p = max(len(paths), 1)
        if n_d:
            gold_docs_using_dict += 1
        if n_f:
            gold_docs_using_fallback += 1
        dict_fracs.append(n_d / n_p)
        fallback_fracs.append(n_f / n_p)
        latin_fracs.append(n_l / n_p)
        by_roman = defaultdict(set)
        for t, rt, path in zip(orig, [romanize_with_path(x, rev)[0] for x in orig], paths):
            if rt:
                by_roman[rt].add(t)
        if any(len(s) > 1 for s in by_roman.values()):
            collision_docs += 1

        orig_set = set(orig)
        md_set = set(md)
        qset = set(qtoks)
        orig_latin = {t for t in orig if t.isascii() and any(c.isalpha() for c in t)}
        overlap_md = qset & md_set
        overlap_orig = qset & orig_set  # almost only if query tokens appear as latin in gold
        overlap_orig_latin = qset & orig_latin
        content_q = [t for t in qtoks if tok_class(t) not in {"function", "number"}]
        content_overlap_md = set(content_q) & md_set
        fn_overlap = {t for t in qtoks if tok_class(t) == "function"} & md_set
        eng_q = [t for t in qtoks if tok_class(t) == "english"]
        eng_match_md = set(eng_q) & md_set
        eng_match_orig_latin = set(eng_q) & orig_latin

        q_sk = {skeleton(t) for t in qtoks if skeleton(t)}
        md_sk = {skeleton(t) for t in md if skeleton(t)}
        sk_overlap = q_sk & md_sk
        content_sk_q = {skeleton(t) for t in content_q if skeleton(t)}
        content_sk_overlap = content_sk_q & md_sk
        # Stricter counterfactual: content tokens only, skeleton length >= 3,
        # matched against non-function Method D tokens. Avoids air→r / ke→k collisions.
        content_md = [t for t in md if tok_class(t) not in {"function", "number"}]
        content_sk_q_ge3 = {skeleton(t) for t in content_q if len(skeleton(t)) >= 3}
        content_sk_md_ge3 = {skeleton(t) for t in content_md if len(skeleton(t)) >= 3}
        content_sk_ge3 = content_sk_q_ge3 & content_sk_md_ge3

        b0r = b0[qid]
        rank = 999 if b0r["gold_rank"] == "" else int(b0r["gold_rank"])
        hit5 = int(b0r["hit@5"])
        in50 = int(b0r["in_top50"])
        primary = "SUCCESS" if hit5 else fail[qid]["primary"]
        miss_side = "SUCCESS" if hit5 else fail[qid]["miss_side"]

        if in50 and rank > 5:
            cand_cat = 2
        elif hit5:
            cand_cat = 0  # success
        elif len(content_overlap_md) == 0:
            cand_cat = 1
        elif len(content_overlap_md) > 0 and not in50:
            cand_cat = 3
        else:
            cand_cat = 4

        competitors = []
        if roman_bm25 is not None and not hit5:
            hits = roman_bm25.search(qtoks, top_k=5)
            competitors = [int(did) for did, _s in hits[:3]]

        per.append({
            "query_id": qid,
            "split": r["split"],
            "source_doc_id": gold_id,
            "primary": primary,
            "miss_side": miss_side,
            "gold_rank": rank if rank < 999 else "",
            "hit@5": hit5,
            "in_top50": in50,
            "n_q": len(qtoks),
            "n_orig": len(orig),
            "n_md": len(md),
            "n_overlap_md": len(overlap_md),
            "n_overlap_orig_latin": len(overlap_orig_latin),
            "n_content_q": len(content_q),
            "n_content_overlap_md": len(content_overlap_md),
            "n_function_overlap_md": len(fn_overlap),
            "n_q_zero_md": sum(1 for t in qset if t not in md_set),
            "n_content_zero_md": sum(1 for t in set(content_q) if t not in md_set),
            "n_eng_q": len(eng_q),
            "n_eng_match_md": len(eng_match_md),
            "n_eng_match_orig_latin": len(eng_match_orig_latin),
            "n_skel_overlap": len(sk_overlap),
            "n_content_skel_overlap": len(content_sk_overlap),
            "n_content_skel_ge3": len(content_sk_ge3),
            "content_skel_ge3": " ".join(sorted(content_sk_ge3)),
            "frac_dict_tokens": round(n_d / n_p, 4),
            "frac_fallback_tokens": round(n_f / n_p, 4),
            "frac_latin_tokens": round(n_l / n_p, 4),
            "cand_cat": cand_cat,
            "competitors_top3": " ".join(str(x) for x in competitors),
            "q_tokens": " ".join(qtoks),
            "md_headline": " ".join(
                romanize_with_path(t, rev)[0]
                for t in p5.tokenize(hline)
                if romanize_with_path(t, rev)[0]
            )[:300],
            "overlap_md": " ".join(sorted(overlap_md)),
            "content_overlap_md": " ".join(sorted(content_overlap_md)),
            "content_skel_overlap": " ".join(sorted(content_sk_overlap)),
            "content_missing_md": " ".join(sorted(set(content_q) - md_set)),
        })

    n = len(per)
    succ = [p for p in per if p["hit@5"]]
    fail_rows = [p for p in per if not p["hit@5"]]
    room = [p for p in per if p["primary"] == "ROOM"]
    ent = [p for p in per if p["primary"] == "ENT"]
    vocab = [p for p in per if p["primary"] == "VOCAB"]

    def mean(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    def mean_key(rows, k):
        return mean([r[k] for r in rows])

    # entity distortion: ENT rows with content overlap 0 vs skeleton overlap > 0
    ent_zero_content = sum(1 for p in ent if p["n_content_overlap_md"] == 0)
    ent_skel_only = sum(1 for p in ent if p["n_content_overlap_md"] == 0 and p["n_content_skel_overlap"] > 0)
    room_skel_gain = sum(1 for p in room if p["n_content_skel_overlap"] > p["n_content_overlap_md"])
    room_zero_content = sum(1 for p in room if p["n_content_overlap_md"] == 0)

    vocab_skel_only = sum(1 for p in vocab if p["n_content_overlap_md"] == 0 and p["n_content_skel_overlap"] == 0)
    vocab_rep = sum(1 for p in vocab if p["n_content_skel_overlap"] > p["n_content_overlap_md"])

    eng_q_all = sum(p["n_eng_q"] for p in per)
    eng_md = sum(p["n_eng_match_md"] for p in per)
    eng_orig = sum(p["n_eng_match_orig_latin"] for p in per)

    summary = {
        "label": "R2-C0 diagnostic — not an official retrieval experiment",
        "test_accessed": False,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_roman_kn": n,
        "n_success": len(succ),
        "n_fail": len(fail_rows),
        "gold_docs": n,
        "gold_docs_using_dictionary": gold_docs_using_dict,
        "gold_docs_using_fallback": gold_docs_using_fallback,
        "avg_frac_dict_tokens": mean(dict_fracs),
        "avg_frac_fallback_tokens": mean(fallback_fracs),
        "avg_frac_latin_tokens": mean(latin_fracs),
        "avg_fallback_len_ratio": mean(shorten_ratios),
        "docs_with_roman_collisions": collision_docs,
        "empty_romanizations": empty_maps,
        "avg_overlap_md_all": mean_key(per, "n_overlap_md"),
        "avg_overlap_md_success": mean_key(succ, "n_overlap_md"),
        "avg_overlap_md_fail": mean_key(fail_rows, "n_overlap_md"),
        "avg_content_overlap_md_all": mean_key(per, "n_content_overlap_md"),
        "avg_content_overlap_md_success": mean_key(succ, "n_content_overlap_md"),
        "avg_content_overlap_md_fail": mean_key(fail_rows, "n_content_overlap_md"),
        "avg_overlap_orig_latin_all": mean_key(per, "n_overlap_orig_latin"),
        "avg_content_skel_overlap_all": mean_key(per, "n_content_skel_overlap"),
        "avg_content_skel_overlap_fail": mean_key(fail_rows, "n_content_skel_overlap"),
        "avg_content_skel_ge3_all": mean_key(per, "n_content_skel_ge3"),
        "avg_content_skel_ge3_fail": mean_key(fail_rows, "n_content_skel_ge3"),
        "avg_content_skel_ge3_success": mean_key(succ, "n_content_skel_ge3"),
        "zero_content_overlap_md": sum(1 for p in per if p["n_content_overlap_md"] == 0),
        "zero_overlap_md": sum(1 for p in per if p["n_overlap_md"] == 0),
        "counterfactual_skel_gain_fail": sum(
            1 for p in fail_rows if p["n_content_skel_overlap"] > p["n_content_overlap_md"]
        ),
        "counterfactual_skel_ge3_gain_fail": sum(
            1 for p in fail_rows if p["n_content_skel_ge3"] > p["n_content_overlap_md"]
        ),
        "zero_content_and_zero_skel_ge3": sum(
            1 for p in fail_rows
            if p["n_content_overlap_md"] == 0 and p["n_content_skel_ge3"] == 0
        ),
        "room_n": len(room),
        "room_zero_content": room_zero_content,
        "room_skel_gain": room_skel_gain,
        "room_skel_ge3_gain": sum(1 for p in room if p["n_content_skel_ge3"] > p["n_content_overlap_md"]),
        "room_zero_skel_ge3": sum(1 for p in room if p["n_content_skel_ge3"] == 0),
        "ent_n": len(ent),
        "ent_zero_content": ent_zero_content,
        "ent_skel_only": ent_skel_only,
        "ent_skel_ge3_gain": sum(1 for p in ent if p["n_content_skel_ge3"] > p["n_content_overlap_md"]),
        "ent_zero_content_with_skel_ge3": sum(
            1 for p in ent if p["n_content_overlap_md"] == 0 and p["n_content_skel_ge3"] > 0
        ),
        "vocab_n": len(vocab),
        "vocab_no_skel_no_exact": vocab_skel_only,
        "vocab_skel_gain": vocab_rep,
        "english_query_tokens_total": eng_q_all,
        "english_exact_match_method_d": eng_md,
        "english_exact_match_orig_latin": eng_orig,
        "cand_cat_success": sum(1 for p in per if p["cand_cat"] == 0),
        "cand_cat_1_no_content_path": sum(1 for p in per if p["cand_cat"] == 1),
        "cand_cat_2_rank": sum(1 for p in per if p["cand_cat"] == 2),
        "cand_cat_3_content_but_miss50": sum(1 for p in per if p["cand_cat"] == 3),
        "avg_n_q_success": mean_key(succ, "n_q"),
        "avg_n_q_fail": mean_key(fail_rows, "n_q"),
        "avg_n_content_success": mean_key(succ, "n_content_q"),
        "avg_n_content_fail": mean_key(fail_rows, "n_content_q"),
        "avg_n_eng_success": mean_key(succ, "n_eng_q"),
        "avg_n_eng_fail": mean_key(fail_rows, "n_eng_q"),
        "sample_size_note": "Hit@5 success n=4; comparisons vs fail n=47 are descriptive only.",
    }

    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "r2_c0_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    out_csv = os.path.join(_DIR, "R2_C0_REPRESENTATION_AUDIT.csv")
    fields = list(per[0].keys())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per)
    print(json.dumps({k: summary[k] for k in summary if k != "timestamp_utc"}, indent=2))
    print("wrote", out_csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
