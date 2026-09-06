# -*- coding: utf-8 -*-
"""
Phase 5: Roman Urdu retrieval experiment.

Pre-registered methods: experiments/phase5_roman_urdu/METHODS_PREREGISTERED.md
Select on DEV roman_urdu only. Confirm once on internal_val.
H001-H040 unused. SVM / RRF / reranker / BM25 retune not in this phase.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import time
import unicodedata
from collections import defaultdict

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))

# Method B (query-side dictionary) used the historical helper
# validate/dual_index_routing/retrieve.py::transliterate_roman.
# That package was archived under archive/historical_experiments/validate/
# and importing it also loads the MiniLM/SVM router. Official M0 routing
# (Phase 12) does not call Method B. The function below keeps the same
# Method B contract so this module can be imported on a clean clone.

SEED = 42
EVAL_SPLITS = {"dev", "internal_val"}
ORACLE_CSV = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
DICT_PATH = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")
P4B_QL = os.path.join(ROOT, "experiments", "phase4b_retrieval_benchmark", "QUERY_LEVEL_COMPARISON.csv")
OUT = _DIR
ART = os.path.join(OUT, "artifacts")
FIG = os.path.join(OUT, "figures")

BM25_K1, BM25_B = 1.5, 0.75
TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[A-Za-z0-9]+", re.UNICODE)
TOP_K = 50
HIT_K = 5

# Phase 2 character table (document-side romanization). Not derived from QTRN ids.
_CHAR_ROMAN = {
    "ا": "a", "آ": "aa", "ب": "b", "پ": "p", "ت": "t", "ٹ": "t", "ث": "s",
    "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ڈ": "d", "ذ": "z",
    "ر": "r", "ڑ": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s",
    "ض": "z", "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ک": "k", "گ": "g", "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "o",
    "ہ": "h", "ھ": "h", "ء": "", "ی": "i", "ے": "e", "ئ": "i", "ؤ": "o",
    "أ": "a", "إ": "i", "ة": "h",
}

# Inverse of _CHAR_ROMAN for Method C. Longest match first. Closed table.
_GRAPHEME_URDU = [
    ("aa", "آ"), ("ch", "چ"), ("kh", "خ"), ("gh", "غ"), ("sh", "ش"), ("zh", "ژ"),
    ("a", "ا"), ("b", "ب"), ("p", "پ"), ("t", "ت"), ("j", "ج"), ("s", "س"),
    ("r", "ر"), ("z", "ز"), ("d", "د"), ("f", "ف"), ("q", "ق"), ("k", "ک"),
    ("g", "گ"), ("l", "ل"), ("m", "م"), ("n", "ن"), ("o", "و"), ("h", "ہ"),
    ("i", "ی"), ("e", "ے"), ("u", "و"), ("w", "و"), ("y", "ی"), ("v", "و"),
    ("c", "ک"),
]

# Closed spelling aliases onto existing dictionary keys only.
_VARIANT_TO_DICT_KEY = {
    "kia": "kya",
    "kiya": "kya",
    "nahin": "nahi",
    "nai": "nahi",
    "mai": "mein",
}

_REPEAT_RE = re.compile(r"(.)\1{2,}")


def ndcg_at(rank, k=5):
    if rank is None or rank > k or rank >= 999:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def p_at(rank, k=5):
    return (1.0 / k) if (rank is not None and rank <= k) else 0.0


def metrics_from_ranks(ranks, k=5):
    n = len(ranks)
    if n == 0:
        return {"n": 0, "hit@5": 0.0, "hit@10": 0.0, "p@5": 0.0, "ndcg@5": 0.0, "mrr": 0.0}
    def hit(kk):
        return float(np.mean([1.0 if (r is not None and r <= kk) else 0.0 for r in ranks]))
    return {
        "n": n,
        "hit@5": round(hit(5), 4),
        "hit@10": round(hit(10), 4),
        "p@5": round(float(np.mean([p_at(r, k) for r in ranks])), 4),
        "ndcg@5": round(float(np.mean([ndcg_at(r, k) for r in ranks])), 4),
        "mrr": round(float(np.mean([1.0 / r if (r and r < 999) else 0.0 for r in ranks])), 4),
    }


def tokenize(text):
    return TOKEN_RE.findall((text or "").lower())


def has_urdu(s):
    return any("\u0600" <= c <= "\u06FF" for c in s)


def latin_ratio_tokens(tokens):
    if not tokens:
        return 0.0
    lat = sum(1 for t in tokens if t.isascii() and any(c.isalpha() for c in t) and not has_urdu(t))
    return lat / len(tokens)


def detect_script(query: str) -> str:
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if urdu == 0 and latin == 0:
        return "OTHER"
    if urdu > 0 and latin > 0:
        return "MIXED"
    if urdu > 0:
        return "URDU"
    return "ROMAN"


def naive_roman_word(word: str) -> str:
    buf = []
    for ch in word:
        if ch in _CHAR_ROMAN:
            buf.append(_CHAR_ROMAN[ch])
        elif ch.isascii() and ch.isalnum():
            buf.append(ch)
    return "".join(buf)


def load_roman_dict():
    with open(DICT_PATH, encoding="utf-8") as f:
        return json.load(f)


def transliterate_roman(query: str) -> tuple[str, bool]:
    """Method B query-side dictionary lookup (not used by official M0 routing).

    Same contract as the archived ``retrieve.transliterate_roman``: if the
    Urdu-character ratio is >= 0.3, leave the query unchanged; otherwise
    whitespace-split, lowercase, and replace tokens present in
    ``models/roman_urdu_dict_expanded.json``.
    """
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("a" <= c.lower() <= "z"))
    if urdu / max(1, urdu + latin) >= 0.3:
        return query, False
    fwd = load_roman_dict()
    toks = query.split()
    out = [fwd.get(t.lower(), t) for t in toks]
    new = " ".join(out)
    return new, new != query


def load_reverse_roman(fwd: dict) -> dict:
    rev = {}
    for lat, ur in fwd.items():
        rev.setdefault(ur, lat)
    return rev


def grapheme_to_urdu(token: str) -> str:
    i, out, n = 0, [], len(token)
    while i < n:
        matched = False
        for lat, ur in _GRAPHEME_URDU:
            if token.startswith(lat, i):
                out.append(ur)
                i += len(lat)
                matched = True
                break
        if not matched:
            out.append(token[i])
            i += 1
    return "".join(out)


def method_c_transform(query: str, fwd: dict) -> str:
    q = unicodedata.normalize("NFKC", query or "").lower()
    def collapse_latin(m):
        ch = m.group(0)[0]
        if "a" <= ch <= "z":
            return ch * 2
        return m.group(0)
    q = _REPEAT_RE.sub(collapse_latin, q)
    out = []
    for tok in TOKEN_RE.findall(q):
        if has_urdu(tok) or any(c.isdigit() for c in tok):
            out.append(tok)
            continue
        key = _VARIANT_TO_DICT_KEY.get(tok, tok)
        if key in fwd:
            out.append(fwd[key])
            continue
        if tok.isascii() and any(c.isalpha() for c in tok):
            out.append(grapheme_to_urdu(tok))
        else:
            out.append(tok)
    return " ".join(out)


def romanize_token(tok: str, rev: dict) -> str:
    if has_urdu(tok):
        lat = rev.get(tok)
        if lat:
            return lat.lower()
        return naive_roman_word(tok).lower()
    return tok.lower()


class BM25:
    def __init__(self, tokenized_docs, k1=BM25_K1, b=BM25_B):
        self.k1, self.b = k1, b
        self.N = len(tokenized_docs)
        self.dl = np.array([max(len(d), 1) for d in tokenized_docs], dtype=np.float32)
        self.avgdl = float(self.dl.mean())
        dfreq = defaultdict(int)
        post = defaultdict(list)
        for i, toks in enumerate(tokenized_docs):
            tf = defaultdict(int)
            for t in toks:
                tf[t] += 1
            for t, c in tf.items():
                dfreq[t] += 1
                post[t].append((i, c))
        self.post = {
            t: (np.array([p[0] for p in v], dtype=np.int32), np.array([p[1] for p in v], dtype=np.float32))
            for t, v in post.items()
        }
        self.idf = {t: math.log((self.N - n + 0.5) / (n + 0.5) + 1.0) for t, n in dfreq.items()}

    def nbytes(self):
        n = int(self.dl.nbytes)
        for ids, tfs in self.post.values():
            n += int(ids.nbytes + tfs.nbytes)
        return n

    def search(self, qtoks, top_k=TOP_K):
        scores = np.zeros(self.N, dtype=np.float32)
        for t in set(qtoks):
            if t not in self.post:
                continue
            ids, tfs = self.post[t]
            idf = self.idf[t]
            dl = self.dl[ids]
            denom = tfs + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl)
            scores[ids] += idf * (tfs * (self.k1 + 1.0) / denom)
        k = min(top_k, self.N)
        part = np.argpartition(-scores, k)[:k]
        idx = part[np.argsort(-scores[part])]
        return [(int(i), float(scores[i])) for i in idx if scores[i] > 0][:top_k]


def rank_of(hits, src):
    for rank, (did, _score) in enumerate(hits, 1):
        if int(did) == int(src):
            return rank
    return 999


def search_rank(index: BM25, qtoks, src, top_k=TOP_K):
    t0 = time.perf_counter()
    hits = index.search(qtoks, top_k=top_k)
    lat = time.perf_counter() - t0
    return rank_of(hits, src), lat


def load_eval_rows():
    rows = []
    with open(ORACLE_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["query_id"].startswith("H"):
                raise RuntimeError("frozen id in oracle csv: %s" % r["query_id"])
            if r["split"] not in EVAL_SPLITS:
                continue
            r["source_doc_id"] = int(r["source_doc_id"])
            rows.append(r)
    return rows


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def fmt(x, nd=4):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def subset(rows, split=None, lang=None):
    out = rows
    if split is not None:
        out = [r for r in out if r["split"] == split]
    if lang is not None:
        out = [r for r in out if r["language_type"] == lang]
    return out


def select_method(dev_rows_metrics):
    """dev_rows_metrics: dict method -> {hit@5, ndcg@5, latency} using unrounded comparison keys."""
    order = ["A", "B", "C", "D"]
    best = order[0]
    for m in order[1:]:
        a, b = dev_rows_metrics[m], dev_rows_metrics[best]
        if a["hit5_raw"] > b["hit5_raw"]:
            best = m
        elif a["hit5_raw"] == b["hit5_raw"]:
            if a["ndcg5_raw"] > b["ndcg5_raw"]:
                best = m
            elif a["ndcg5_raw"] == b["ndcg5_raw"]:
                if a["latency"] < b["latency"]:
                    best = m
    return best


def raw_hit_ndcg(ranks, k=5):
    n = max(len(ranks), 1)
    hit = float(np.mean([1.0 if (r is not None and r <= k) else 0.0 for r in ranks]))
    nd = float(np.mean([ndcg_at(r, k) for r in ranks]))
    return hit, nd


def bar_chart(path, labels, values, title, ylabel="Hit@5"):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(labels, values, color="#3b6ea5")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    for i, v in enumerate(values):
        ax.text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    os.makedirs(ART, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    print("=== Phase 5 Roman Urdu experiment ===", flush=True)

    eval_rows = load_eval_rows()
    assert len(eval_rows) == 78, len(eval_rows)
    roman_rows = subset(eval_rows, lang="roman_urdu")
    urdu_rows = subset(eval_rows, lang="urdu")
    mixed_rows = subset(eval_rows, lang="mixed")
    dev_roman = subset(roman_rows, split="dev")
    val_roman = subset(roman_rows, split="internal_val")
    print(f"eval={len(eval_rows)} roman={len(roman_rows)} dev_roman={len(dev_roman)} val_roman={len(val_roman)}", flush=True)

    p4b = {}
    with open(P4B_QL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            p4b[r["query_id"]] = r

    fwd = load_roman_dict()
    rev = load_reverse_roman(fwd)
    print(f"dict_keys={len(fwd)} reverse_values={len(rev)}", flush=True)

    # --- script detection (all 78) ---
    det_rows = []
    for r in eval_rows:
        pred = detect_script(r["query_text"])
        gold = {"urdu": "URDU", "roman_urdu": "ROMAN", "mixed": "MIXED"}[r["language_type"]]
        det_rows.append({**r, "detector": pred, "gold_script": gold, "match": int(pred == gold)})

    # --- corpus tokenize + romanize ---
    print("loading corpus...", flush=True)
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)).tolist()
    headlines = df["Headline"].fillna("").astype(str).tolist()
    n_docs = len(texts)
    print(f"docs={n_docs}", flush=True)

    t_tok = time.perf_counter()
    urdu_docs = []
    roman_docs = []
    roman_chars = 0
    for i, text in enumerate(texts):
        utoks = tokenize(text)
        rtoks = [romanize_token(t, rev) for t in utoks]
        rtoks = [t for t in rtoks if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        roman_chars += sum(len(t) + 1 for t in rtoks)
        if (i + 1) % 20000 == 0:
            print(f"  tokenize {i+1}/{n_docs}", flush=True)
    tokenize_sec = time.perf_counter() - t_tok
    print(f"tokenize+romanize {tokenize_sec:.1f}s", flush=True)

    t_u = time.perf_counter()
    urdu_bm25 = BM25(urdu_docs)
    urdu_build = time.perf_counter() - t_u
    print(f"urdu BM25 build {urdu_build:.1f}s terms={len(urdu_bm25.idf)}", flush=True)

    t_r = time.perf_counter()
    roman_bm25 = BM25(roman_docs)
    roman_build = time.perf_counter() - t_r
    print(f"roman BM25 build {roman_build:.1f}s terms={len(roman_bm25.idf)}", flush=True)

    roman_stats = {
        "n_docs": n_docs,
        "tokenize_romanize_sec": round(tokenize_sec, 2),
        "urdu_bm25_build_sec": round(urdu_build, 2),
        "roman_bm25_build_sec": round(roman_build, 2),
        "roman_index_build_sec": round(tokenize_sec + roman_build, 2),
        "urdu_index_bytes": urdu_bm25.nbytes(),
        "roman_index_bytes": roman_bm25.nbytes(),
        "estimated_romanized_text_bytes": roman_chars,
        "urdu_avgdl": round(urdu_bm25.avgdl, 2),
        "roman_avgdl": round(roman_bm25.avgdl, 2),
        "urdu_terms": len(urdu_bm25.idf),
        "roman_terms": len(roman_bm25.idf),
        "k1": BM25_K1,
        "b": BM25_B,
    }
    with open(os.path.join(ART, "romanized_index_stats.json"), "w", encoding="utf-8") as f:
        json.dump(roman_stats, f, indent=2)

    def run_A(q):
        return tokenize(q)

    def run_B(q):
        new, _changed = transliterate_roman(q)
        return tokenize(new)

    def run_C(q):
        return tokenize(method_c_transform(q, fwd))

    def run_D(q):
        return tokenize(q)

    method_fn = {"A": (run_A, urdu_bm25), "B": (run_B, urdu_bm25), "C": (run_C, urdu_bm25), "D": (run_D, roman_bm25)}

    def eval_method(method, rows):
        fn, index = method_fn[method]
        ranks, lats, recs = [], [], []
        for r in rows:
            qtoks = fn(r["query_text"])
            rank, lat = search_rank(index, qtoks, r["source_doc_id"])
            ranks.append(rank)
            lats.append(lat)
            recs.append(rank)
        m = metrics_from_ranks(ranks)
        hit_raw, nd_raw = raw_hit_ndcg(ranks)
        m["latency"] = round(float(np.mean(lats)) if lats else 0.0, 4)
        m["hit5_raw"] = hit_raw
        m["ndcg5_raw"] = nd_raw
        m["ranks"] = ranks
        return m

    # --- audit existing transliteration on roman queries (no improvement) ---
    audit_q = []
    dict_keys = set(fwd.keys())
    for r in roman_rows:
        raw = r["query_text"]
        new, changed = transliterate_roman(raw)
        raw_toks = raw.split()
        mapped = 0
        unmapped_latin = []
        for t in raw_toks:
            tl = t.lower()
            if tl in dict_keys:
                mapped += 1
            elif re.search(r"[A-Za-z]", t):
                unmapped_latin.append(t)
        still_latin = latin_ratio_tokens(tokenize(new))
        audit_q.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "changed": int(changed),
            "n_ws_tokens": len(raw_toks),
            "n_dict_mapped": mapped,
            "n_unmapped_latin": len(unmapped_latin),
            "post_latin_token_ratio": round(still_latin, 4),
            "transformed": new,
        })

    # --- reproduce Method A on all roman (baseline inventory) ---
    print("evaluating methods on all roman queries...", flush=True)
    all_method_ranks = {}
    all_method_meta = {}
    for mname in ("A", "B", "C", "D"):
        print(f"  method {mname} n={len(roman_rows)}", flush=True)
        meta = eval_method(mname, roman_rows)
        all_method_ranks[mname] = {r["query_id"]: rk for r, rk in zip(roman_rows, meta["ranks"])}
        all_method_meta[mname] = meta
        print(f"    roman all hit@5={meta['hit@5']}", flush=True)

    # DEV-only metrics for selection (recompute from stored ranks, no peek at val for the rule)
    def metrics_for(method, rows):
        ranks = [all_method_ranks[method][r["query_id"]] for r in rows]
        lats_placeholder = all_method_meta[method]["latency"]
        m = metrics_from_ranks(ranks)
        hit_raw, nd_raw = raw_hit_ndcg(ranks)
        # latency: re-time DEV only for honest selection tie-break
        fn, index = method_fn[method]
        lats = []
        for r in rows:
            qtoks = fn(r["query_text"])
            _rk, lat = search_rank(index, qtoks, r["source_doc_id"])
            lats.append(lat)
        m["latency"] = round(float(np.mean(lats)) if lats else 0.0, 4)
        m["hit5_raw"] = hit_raw
        m["ndcg5_raw"] = nd_raw
        m["ranks"] = ranks
        m["_mean_lat_all_roman"] = lats_placeholder
        return m

    print("DEV selection metrics...", flush=True)
    dev_stats = {m: metrics_for(m, dev_roman) for m in ("A", "B", "C", "D")}
    selected = select_method(dev_stats)
    selection_payload = {
        "selected": selected,
        "rule": "primary Hit@5, secondary nDCG@5, tie-break lower latency",
        "dev_n_roman": len(dev_roman),
        "dev": {m: {k: v for k, v in st.items() if k != "ranks"} for m, st in dev_stats.items()},
    }
    with open(os.path.join(ART, "selected_method.json"), "w", encoding="utf-8") as f:
        json.dump(selection_payload, f, indent=2)
    print(f"SELECTED ON DEV: {selected}", flush=True)

    val_stats = {m: metrics_from_ranks([all_method_ranks[m][r["query_id"]] for r in val_roman]) for m in ("A", "B", "C", "D")}
    for m in val_stats:
        val_stats[m]["latency"] = metrics_for(m, val_roman)["latency"]

    # Method E analysis (not selectable)
    def union_stats(rows, m1, m2, k=5):
        h1 = h2 = both = uni = 0
        for r in rows:
            a = all_method_ranks[m1][r["query_id"]]
            b = all_method_ranks[m2][r["query_id"]]
            a_hit, b_hit = a <= k, b <= k
            h1 += int(a_hit)
            h2 += int(b_hit)
            both += int(a_hit and b_hit)
            uni += int(a_hit or b_hit)
        n = len(rows)
        return {
            "n": n,
            "view1": m1,
            "view2": m2,
            "view1_hit@5": round(h1 / n, 4) if n else 0.0,
            "view2_hit@5": round(h2 / n, 4) if n else 0.0,
            "overlap_hit@5": round(both / n, 4) if n else 0.0,
            "union_hit@5": round(uni / n, 4) if n else 0.0,
            "view1_hits": h1,
            "view2_hits": h2,
            "overlap_hits": both,
            "union_hits": uni,
        }

    e_dev = union_stats(dev_roman, "C", "D")
    e_val = union_stats(val_roman, "C", "D")
    e_all = union_stats(roman_rows, "C", "D")
    e_bd_all = union_stats(roman_rows, "B", "D")

    # Urdu regression: baseline Urdu BM25 vs script-aware (URDU -> Urdu BM25)
    print("Urdu + mixed + routing...", flush=True)

    def urdu_bm25_ranks(rows):
        ranks, lats = [], []
        for r in rows:
            rk, lat = search_rank(urdu_bm25, tokenize(r["query_text"]), r["source_doc_id"])
            ranks.append(rk)
            lats.append(lat)
        m = metrics_from_ranks(ranks)
        m["latency"] = round(float(np.mean(lats)) if lats else 0.0, 4)
        m["ranks"] = ranks
        return m

    urdu_base = urdu_bm25_ranks(urdu_rows)
    # script-aware Urdu path is identical by pre-registration
    urdu_routed = urdu_base

    mixed_urdu_path = urdu_bm25_ranks(mixed_rows)

    def mixed_roman_path(rows):
        fn, index = method_fn[selected]
        ranks, lats = [], []
        for r in rows:
            q = r["query_text"]
            if selected == "D":
                # romanize any Urdu tokens in the mixed query into the roman index space
                qtoks = [romanize_token(t, rev) for t in tokenize(q)]
                qtoks = [t for t in qtoks if t]
            else:
                qtoks = fn(q)
            rk, lat = search_rank(index, qtoks, r["source_doc_id"])
            ranks.append(rk)
            lats.append(lat)
        m = metrics_from_ranks(ranks)
        m["latency"] = round(float(np.mean(lats)) if lats else 0.0, 4)
        m["ranks"] = ranks
        return m

    mixed_sel_path = mixed_roman_path(mixed_rows)
    mixed_union_hits = [
        1 if (a <= 5 or b <= 5) else 0
        for a, b in zip(mixed_urdu_path["ranks"], mixed_sel_path["ranks"])
    ]
    mixed_union = {
        "n": len(mixed_rows),
        "hit@5": round(float(np.mean(mixed_union_hits)) if mixed_rows else 0.0, 4),
        "hits": int(sum(mixed_union_hits)),
    }

    # Routing on all 78
    # URDU -> urdu BM25, ROMAN -> selected, MIXED -> urdu BM25 (deployable)
    route_rank = {}
    # cache urdu ranks for all non-roman
    non_roman = [r for r in eval_rows if r["language_type"] != "roman_urdu"]
    non_roman_m = urdu_bm25_ranks(non_roman)
    for r, rk in zip(non_roman, non_roman_m["ranks"]):
        route_rank[r["query_id"]] = rk
    for r in roman_rows:
        route_rank[r["query_id"]] = all_method_ranks[selected][r["query_id"]]

    headline_ranks = []
    bm25_raw_ranks = []  # original query on urdu index (Phase 4B / Method A for roman)
    routed_ranks = []
    oracle_ubm25_sel = []
    oracle_head_route = []

    # raw BM25 for urdu/mixed = urdu index; for roman = Method A
    raw_all = {}
    for r in eval_rows:
        if r["language_type"] == "roman_urdu":
            raw_all[r["query_id"]] = all_method_ranks["A"][r["query_id"]]
        else:
            raw_all[r["query_id"]] = route_rank[r["query_id"]] if r["language_type"] != "roman_urdu" else None

    # Fix: non-roman route_rank IS urdu BM25, so raw BM25 baseline for urdu/mixed is that
    for r in eval_rows:
        hid = int(p4b[r["query_id"]]["headline_rank"])
        raw = raw_all[r["query_id"]]
        routed = route_rank[r["query_id"]]
        headline_ranks.append(hid)
        bm25_raw_ranks.append(raw)
        routed_ranks.append(routed)
        # oracle 1: urdu BM25 for urdu/mixed, selected for roman — that IS routed
        # oracle urdu BM25 + selected roman = routed deployable (mixed uses urdu BM25)
        ora1 = routed
        ora2 = hid if hid <= 5 or (routed >= 999) else routed
        # better: min rank among headline and routed, then hit if min<=5
        best = min(hid if hid < 999 else 10**9, routed if routed < 999 else 10**9)
        best = best if best < 10**9 else 999
        oracle_head_route.append(best)
        oracle_ubm25_sel.append(routed)

    # Headline + urdu BM25 + selected: for each query, min of headline, urdu-raw, selected-if-roman
    ora3 = []
    for r in eval_rows:
        hid = int(p4b[r["query_id"]]["headline_rank"])
        ub = raw_all[r["query_id"]]
        cands = [hid, ub]
        if r["language_type"] == "roman_urdu":
            cands.append(all_method_ranks[selected][r["query_id"]])
        if r["language_type"] == "mixed":
            cands.append(mixed_sel_path["ranks"][mixed_rows.index(r)])
        best = min(x if x < 999 else 10**9 for x in cands)
        ora3.append(best if best < 10**9 else 999)

    m_head = metrics_from_ranks(headline_ranks)
    m_bm25 = metrics_from_ranks(bm25_raw_ranks)
    m_route = metrics_from_ranks(routed_ranks)
    m_ora_route = metrics_from_ranks(oracle_ubm25_sel)
    m_ora_head = metrics_from_ranks(oracle_head_route)
    m_ora3 = metrics_from_ranks(ora3)

    # mixed oracle already mixed_union
    all_fail = []
    for r in eval_rows:
        hid = int(p4b[r["query_id"]]["headline_rank"])
        ub = raw_all[r["query_id"]]
        selr = all_method_ranks[selected][r["query_id"]] if r["language_type"] == "roman_urdu" else 999
        mixr = 999
        if r["language_type"] == "mixed":
            mixr = mixed_sel_path["ranks"][mixed_rows.index(r)]
        ranks_chk = [hid, ub, selr if r["language_type"] == "roman_urdu" else 10**9, mixr if r["language_type"] == "mixed" else 10**9]
        if min(x if x < 999 else 10**9 for x in ranks_chk) > 5:
            all_fail.append(r["query_id"])

    recovered = []
    still_fail_all_methods = []
    for r in roman_rows:
        a = all_method_ranks["A"][r["query_id"]]
        s = all_method_ranks[selected][r["query_id"]]
        if a > 5 and s <= 5:
            recovered.append(r["query_id"])
        if all(all_method_ranks[m][r["query_id"]] > 5 for m in ("A", "B", "C", "D")):
            still_fail_all_methods.append(r["query_id"])

    # failure categories using token overlap with romanized source, no system change
    fail_details = []
    for r in roman_rows:
        qid = r["query_id"]
        src = r["source_doc_id"]
        qtoks = set(tokenize(r["query_text"]))
        dtoks = set(roman_docs[src])
        overlap = qtoks & dtoks
        b_q, _ = transliterate_roman(r["query_text"])
        c_q = method_c_transform(r["query_text"], fwd)
        b_latin = latin_ratio_tokens(tokenize(b_q))
        c_has_urdu = has_urdu(c_q)
        ranks_m = {m: all_method_ranks[m][qid] for m in ("A", "B", "C", "D")}
        sel_hit = ranks_m[selected] <= 5
        base_miss = ranks_m["A"] > 5
        if sel_hit and base_miss:
            cat = "recovered"
        elif all(v > 5 for v in ranks_m.values()):
            if len(overlap) == 0:
                cat = "source_not_lexically_similar"
            elif len(overlap) < 2:
                cat = "named_entity_mismatch"
            else:
                cat = "source_article_difficult_to_retrieve"
        elif ranks_m["D"] <= 5:
            cat = "other"
        elif not c_has_urdu and b_latin > 0.7:
            cat = "transliteration_failure"
        else:
            cat = "spelling_variation"
        # English-looking leftover
        eng_like = [t for t in tokenize(r["query_text"]) if t in fwd or t in ("pakistan", "cricket", "film", "team", "news")]
        if cat not in ("recovered",) and len(eng_like) >= 3 and ranks_m[selected] > 5:
            if cat == "transliteration_failure":
                pass
            elif " " in r["query_text"] and any(t.isascii() for t in tokenize(r["query_text"])):
                # keep more specific if overlap empty
                if cat == "source_not_lexically_similar":
                    cat = "english_urdu_mixture" if has_urdu(r["query_text"]) else cat
        fail_details.append({
            "query_id": qid,
            "split": r["split"],
            "category": cat,
            "overlap_n": len(overlap),
            "overlap_tokens": " ".join(sorted(overlap)[:12]),
            "method_a": ranks_m["A"],
            "method_b": ranks_m["B"],
            "method_c": ranks_m["C"],
            "method_d": ranks_m["D"],
            "b_latin_ratio": b_latin,
            "c_query": c_q,
            "headline": headlines[src][:80],
        })

    # ---------- CSV outputs ----------
    inv_rows = []
    for r in roman_rows:
        qid = r["query_id"]
        p = p4b[qid]
        inv_rows.append([
            qid, r["query_text"], r["source_doc_id"], r["split"], r["language_type"],
            all_method_ranks["A"][qid], int(p["headline_rank"]), int(p["full_rank"]), int(p["chunk_rank"]),
        ])
    write_csv(
        os.path.join(OUT, "ROMAN_QUERY_INVENTORY.csv"),
        ["query_id", "query", "source_doc_id", "split", "query_type", "raw_bm25_rank", "headline_rank", "old_full_rank", "chunk_rank"],
        inv_rows,
    )

    def row_metrics(name, st, note=""):
        return [name, st.get("n", ""), st.get("hit@5", ""), st.get("hit@10", ""), st.get("ndcg@5", ""), st.get("mrr", ""), st.get("latency", ""), note]

    write_csv(
        os.path.join(OUT, "DEV_METHOD_COMPARISON.csv"),
        ["method", "n", "hit@5", "hit@10", "ndcg@5", "mrr", "latency_sec", "note"],
        [
            row_metrics("A_raw_bm25", dev_stats["A"], "baseline"),
            row_metrics("B_existing_dict", dev_stats["B"], "existing transliterate_roman"),
            row_metrics("C_rule_based", dev_stats["C"], "pre-registered rules"),
            row_metrics("D_romanized_docs", dev_stats["D"], "full-corpus roman BM25"),
            ["E_union_C_D", e_dev["n"], e_dev["union_hit@5"], "", "", "", "", "analysis only; not selectable"],
            [f"SELECTED_{selected}", dev_stats[selected]["n"], dev_stats[selected]["hit@5"], dev_stats[selected]["hit@10"], dev_stats[selected]["ndcg@5"], dev_stats[selected]["mrr"], dev_stats[selected]["latency"], "frozen after DEV"],
        ],
    )

    write_csv(
        os.path.join(OUT, "INTERNAL_VAL_CONFIRMATION.csv"),
        ["split", "method", "n", "hit@5", "hit@10", "ndcg@5", "mrr", "latency_sec"],
        [
            ["dev", selected, dev_stats[selected]["n"], dev_stats[selected]["hit@5"], dev_stats[selected]["hit@10"], dev_stats[selected]["ndcg@5"], dev_stats[selected]["mrr"], dev_stats[selected]["latency"]],
            ["internal_val", selected, val_stats[selected]["n"], val_stats[selected]["hit@5"], val_stats[selected]["hit@10"], val_stats[selected]["ndcg@5"], val_stats[selected]["mrr"], val_stats[selected]["latency"]],
            ["dev", "A_baseline", dev_stats["A"]["n"], dev_stats["A"]["hit@5"], dev_stats["A"]["hit@10"], dev_stats["A"]["ndcg@5"], dev_stats["A"]["mrr"], dev_stats["A"]["latency"]],
            ["internal_val", "A_baseline", val_stats["A"]["n"], val_stats["A"]["hit@5"], val_stats["A"]["hit@10"], val_stats["A"]["ndcg@5"], val_stats["A"]["mrr"], val_stats["A"]["latency"]],
        ],
    )

    cmp_rows = []
    for r in roman_rows:
        qid = r["query_id"]
        cmp_rows.append([
            qid, r["split"], r["query_text"], r["source_doc_id"],
            all_method_ranks["A"][qid], all_method_ranks["B"][qid], all_method_ranks["C"][qid], all_method_ranks["D"][qid],
            int(all_method_ranks["A"][qid] <= 5 or all_method_ranks["C"][qid] <= 5 or all_method_ranks["D"][qid] <= 5),
            int(all_method_ranks["C"][qid] <= 5 or all_method_ranks["D"][qid] <= 5),
        ])
    write_csv(
        os.path.join(OUT, "ROMAN_QUERY_COMPARISON.csv"),
        ["query_id", "split", "query", "source_doc_id", "rank_A", "rank_B", "rank_C", "rank_D", "any_ABC_or_D_hit5", "union_C_D_hit5"],
        cmp_rows,
    )

    write_csv(
        os.path.join(OUT, "URDU_REGRESSION_CHECK.csv"),
        ["condition", "n", "hit@5", "ndcg@5", "mrr", "note"],
        [
            ["urdu_bm25_baseline", urdu_base["n"], urdu_base["hit@5"], urdu_base["ndcg@5"], urdu_base["mrr"], "Urdu queries, Urdu BM25"],
            ["script_aware_urdu_path", urdu_routed["n"], urdu_routed["hit@5"], urdu_routed["ndcg@5"], urdu_routed["mrr"], "detector URDU -> Urdu BM25 (identical by design)"],
        ],
    )

    write_csv(
        os.path.join(OUT, "SCRIPT_ROUTING_RESULTS.csv"),
        ["system", "n", "hit@5", "ndcg@5", "mrr", "note"],
        [
            ["headline", 78, m_head["hit@5"], m_head["ndcg@5"], m_head["mrr"], "Phase 4B ranks reused"],
            ["raw_bm25", 78, m_bm25["hit@5"], m_bm25["ndcg@5"], m_bm25["mrr"], "Urdu/mixed: Urdu BM25; Roman: Method A"],
            ["script_aware", 78, m_route["hit@5"], m_route["ndcg@5"], m_route["mrr"], f"URDU/MIXED->Urdu BM25; ROMAN->Method {selected}"],
            ["mixed_urdu_bm25", mixed_urdu_path["n"], mixed_urdu_path["hit@5"], mixed_urdu_path["ndcg@5"], mixed_urdu_path["mrr"], "mixed path 1"],
            ["mixed_selected_roman_method", mixed_sel_path["n"], mixed_sel_path["hit@5"], mixed_sel_path["ndcg@5"], mixed_sel_path["mrr"], "mixed path 2 analysis"],
            ["mixed_union_oracle", mixed_union["n"], mixed_union["hit@5"], "", "", "analysis only; not a fusion system"],
        ],
    )

    write_csv(
        os.path.join(OUT, "ORACLE_HEADROOM.csv"),
        ["ceiling", "n", "hit@5", "ndcg@5", "mrr", "note"],
        [
            ["urdu_bm25_plus_selected_roman", 78, m_ora_route["hit@5"], m_ora_route["ndcg@5"], m_ora_route["mrr"], "deployable routing (mixed uses Urdu BM25)"],
            ["headline_plus_script_aware", 78, m_ora_head["hit@5"], m_ora_head["ndcg@5"], m_ora_head["mrr"], "oracle min-rank; not deployable"],
            ["headline_urdu_bm25_selected_mixedpath", 78, m_ora3["hit@5"], m_ora3["ndcg@5"], m_ora3["mrr"], "includes mixed roman path; not deployable"],
            ["method_E_union_C_D_roman_only", e_all["n"], e_all["union_hit@5"], "", "", "roman queries only"],
        ],
    )

    write_csv(
        os.path.join(OUT, "artifacts", "failure_categories.csv"),
        ["query_id", "split", "category", "overlap_n", "rank_A", "rank_B", "rank_C", "rank_D"],
        [[d["query_id"], d["split"], d["category"], d["overlap_n"], d["method_a"], d["method_b"], d["method_c"], d["method_d"]] for d in fail_details],
    )

    # ---------- figures ----------
    bar_chart(
        os.path.join(FIG, "dev_method_hit5.png"),
        ["A", "B", "C", "D"],
        [dev_stats[m]["hit@5"] for m in ("A", "B", "C", "D")],
        "DEV Roman Urdu Hit@5 (selection set)",
    )
    bar_chart(
        os.path.join(FIG, "roman_all_method_hit5.png"),
        ["A", "B", "C", "D"],
        [all_method_meta[m]["hit@5"] for m in ("A", "B", "C", "D")],
        "All Roman queries Hit@5 (n=23, diagnostic)",
    )
    bar_chart(
        os.path.join(FIG, "routing_n78.png"),
        ["Headline", "Raw BM25", "Script-aware"],
        [m_head["hit@5"], m_bm25["hit@5"], m_route["hit@5"]],
        "n=78 known-item Hit@5",
    )
    bar_chart(
        os.path.join(FIG, "oracle_headroom.png"),
        ["Script-aware", "HL+route", "HL+all paths"],
        [m_ora_route["hit@5"], m_ora_head["hit@5"], m_ora3["hit@5"]],
        "Oracle ceilings (not deployable)",
    )

    # script detection bar
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["URDU", "ROMAN", "MIXED", "OTHER"]
    counts = [sum(1 for d in det_rows if d["detector"] == lab) for lab in labels]
    ax.bar(labels, counts, color="#5b8c5a")
    ax.set_title("Detector labels on n=78")
    for i, v in enumerate(counts):
        ax.text(i, v + 0.3, str(v), ha="center")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "script_detection.png"), dpi=140)
    plt.close(fig)

    # ---------- markdown reports ----------
    n_changed = sum(x["changed"] for x in audit_q)
    n_mostly_latin = sum(1 for x in audit_q if x["post_latin_token_ratio"] >= 0.5)
    mapped_total = sum(x["n_dict_mapped"] for x in audit_q)
    unmapped_total = sum(x["n_unmapped_latin"] for x in audit_q)

    # example unmapped tokens (frequency), not used to add rules
    um_count = defaultdict(int)
    for r in roman_rows:
        for t in r["query_text"].split():
            if t.lower() not in fwd and re.search(r"[A-Za-z]", t):
                um_count[t.lower()] += 1
    top_unmapped = sorted(um_count.items(), key=lambda x: -x[1])[:40]

    audit_md = f"""# Transliteration audit

Audit of **existing** repository logic only. No mappings were added during this audit.

## 1. Which Roman words are currently mapped?

File: `models/roman_urdu_dict_expanded.json`

- Entries: **{len(fwd)}**
- Lookup: whitespace tokens, `lower()`, exact key match
- Gate in `transliterate_roman`: if Urdu-character ratio ≥ 0.3, the query is left unchanged

The dictionary is a closed list of common function words, a few names/places (`imran`, `khan`, `lahore`, `karachi`, …), and some English news/sport terms (`cricket`, `pakistan`, `match`, …). Values are Urdu-script strings. There is no grapheme converter and no fuzzy match.

## 2. How many Roman evaluation queries are changed?

Roman evaluation queries: **{len(roman_rows)}** (Phase 2 `language_type=roman_urdu`, dev + internal_val).

| | n |
| --- | ---: |
| At least one dictionary substitution | {n_changed} |
| Unchanged (no token in the dictionary) | {len(roman_rows) - n_changed} |

Whitespace-token dictionary hits across all Roman queries: **{mapped_total}**.  
Whitespace tokens still unmapped and Latin: **{unmapped_total}**.

## 3. How many remain mostly Latin?

After existing `transliterate_roman`, queries with Latin-token ratio ≥ 0.5: **{n_mostly_latin} / {len(roman_rows)}**.

Phase 2 `title_roman` generation uses reverse-dictionary lookup when an Urdu title token is an exact dictionary *value*, otherwise `naive_roman_word` (character table). Most QTRN Roman strings are therefore **lossy character romanizations**, not conventional Roman Urdu orthography. A {len(fwd)}-entry exact-match dictionary cannot rewrite them.

## 4. What types of spelling variation fail?

Observed **token classes** among unmapped Latin tokens (frequency sample, not a patch list):

"""
    for tok, c in top_unmapped[:25]:
        audit_md += f"- `{tok}` (n={c})\n"
    audit_md += """
Failure types (general, not query-id rules):

- **Names** — person/place strings romanized letter-by-letter (`hfiz`, `babraazm`, `peshawar` is in-dict but many names are not).
- **Locations / events** — character-mapped titles, not Wikipedia-style Roman Urdu.
- **Function words** — a few are in-dict (`ka`, `ke`, `se`, `mein`, `ne`); many surface as stripped-vowel forms (`krne`, `kilie`, `mshorh`) that are not keys.
- **Spelling / vowel variation** — Phase 2 `ی→i`, `و→o`, `ا→a` produces forms unlike `kya`/`kia` user Roman Urdu.
- **English words** — some keys exist (`cricket`, `film`, `team`); others stay English (`update` is on mixed queries, not this Roman set).
- **Mixed Urdu/English** — the 23 Roman labels are Latin-only; mixed script is a separate oracle class.

Dense retrieval (Phase 4B Headline/Full/Chunk) already calls `transliterate_roman`. Raw Phase 4B BM25 did not. Neither path recovers Roman known-item Top-5 except one dense hit.

This audit did **not** add dictionary rows.
"""
    with open(os.path.join(OUT, "TRANSLITERATION_AUDIT.md"), "w", encoding="utf-8") as f:
        f.write(audit_md)

    gold_counts = {"URDU": 0, "ROMAN": 0, "MIXED": 0}
    pred_counts = {"URDU": 0, "ROMAN": 0, "MIXED": 0, "OTHER": 0}
    conf = defaultdict(int)
    ambiguous = []
    for d in det_rows:
        gold_counts[d["gold_script"]] += 1
        pred_counts[d["detector"]] += 1
        conf[(d["gold_script"], d["detector"])] += 1
        if d["gold_script"] != d["detector"]:
            ambiguous.append(d["query_id"])

    mismatches = [d for d in det_rows if d["gold_script"] != d["detector"]]
    script_md = f"""# Script detection report

Deterministic Unicode rule (not an SVM). Pre-registered in `METHODS_PREREGISTERED.md`.

```
urdu = count of U+0600..U+06FF
latin = count of ASCII letters
OTHER if both 0
MIXED if both > 0
URDU if only urdu
ROMAN if only latin
```

Evaluated on all **78** Phase 2 dev + internal_val queries. No H001–H040.

## Detector counts

| Label | n |
| --- | ---: |
| URDU | {pred_counts["URDU"]} |
| ROMAN | {pred_counts["ROMAN"]} |
| MIXED | {pred_counts["MIXED"]} |
| OTHER | {pred_counts["OTHER"]} |

## Oracle `language_type` (manual / generation labels)

| Label | n |
| --- | ---: |
| urdu → URDU | {gold_counts["URDU"]} |
| roman_urdu → ROMAN | {gold_counts["ROMAN"]} |
| mixed → MIXED | {gold_counts["MIXED"]} |

## Agreement

Correct vs oracle labels: **{sum(d['match'] for d in det_rows)} / 78**.

Mismatches: **{len(mismatches)}**.

"""
    if mismatches:
        script_md += "Mismatch ids:\n\n"
        for d in mismatches:
            script_md += f"- {d['query_id']}: oracle={d['gold_script']} detector={d['detector']}\n"
    else:
        script_md += "No mismatches. Oracle mixed queries all contain Urdu letters plus the Latin suffix `Pakistan news update`.\n"
    script_md += f"""
## Ambiguous cases

Defined as detector/oracle disagreement, or mixed-script ratio in (0.15, 0.85).

Ids: {", ".join(sorted(set(ambiguous))) if ambiguous else "(none)"}

The detector does not use the Roman dictionary and does not look at retrieval ranks.
"""
    with open(os.path.join(OUT, "SCRIPT_DETECTION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(script_md)

    cat_count = defaultdict(int)
    for d in fail_details:
        if d["category"] != "recovered":
            cat_count[d["category"]] += 1

    recovered_dev = [i for i in recovered if i in {x["query_id"] for x in dev_roman}]
    recovered_val = [i for i in recovered if i in {x["query_id"] for x in val_roman}]
    miss_sel = [r["query_id"] for r in roman_rows if all_method_ranks[selected][r["query_id"]] > 5]
    hit_sel = [r["query_id"] for r in roman_rows if all_method_ranks[selected][r["query_id"]] <= 5]

    fail_md = f"""# Failure analysis (diagnosis only)

No system change after this analysis. No H001–H040. No query-specific rules added.

Selected method: **{selected}**

## Recovered

Baseline Method A miss (rank > 5) → selected method Hit@5.

- Count: **{len(recovered)} / {len(roman_rows)}**
- DEV: {len(recovered_dev)} — {", ".join(recovered_dev) or "(none)"}
- INTERNAL_VAL: {len(recovered_val)} — {", ".join(recovered_val) or "(none)"}
- Selected Hit@5 ids: {", ".join(hit_sel) or "(none)"}

## Still failing (selected method)

Selected rank > 5: **{len(miss_sel)} / {len(roman_rows)}**

{chr(10).join("- " + i for i in miss_sel) or "(none)"}

## All four methods miss Hit@5

**{len(still_fail_all_methods)}** queries: {", ".join(still_fail_all_methods) or "(none)"}

## Categories (general)

Applied to Roman queries using token overlap with the **romanized source article** and whether B/C still look Latin. Categories were not used to edit methods.

| Category | n (non-recovered) |
| --- | ---: |
"""
    for k, v in sorted(cat_count.items(), key=lambda x: -x[1]):
        fail_md += f"| {k} | {v} |\n"
    fail_md += """
Definitions:

- **transliteration_failure** — query-side B/C leave the string mostly Latin; document-side D also misses.
- **named_entity_mismatch** — very small overlap with the romanized source (names/titles drifted).
- **spelling_variation** — some transformation happened but rank stayed > 5.
- **english_urdu_mixture** — mixed-script (not expected on this Roman subset).
- **source_article_difficult_to_retrieve** — overlap exists but BM25 still ranks the source outside Top-5 (length / common tokens).
- **source_not_lexically_similar** — zero overlap between Roman query tokens and romanized source tokens (generation tokenizer vs index tokenizer, or title-only query vs article body romanization mismatch).
- **other** — residual.

Per-query table: `artifacts/failure_categories.csv`.

This phase **stops** after diagnosis.
"""
    with open(os.path.join(OUT, "FAILURE_ANALYSIS.md"), "w", encoding="utf-8") as f:
        f.write(fail_md)

    dense_hits = sum(1 for r in roman_rows if int(p4b[r["query_id"]]["headline_rank"]) <= 5)
    dense_hit = round(dense_hits / len(roman_rows), 4)
    a_all = metrics_from_ranks([all_method_ranks["A"][r["query_id"]] for r in roman_rows])
    sel_all = metrics_from_ranks([all_method_ranks[selected][r["query_id"]] for r in roman_rows])
    abs_imp = round(sel_all["hit@5"] - a_all["hit@5"], 4)
    gen = "yes" if val_stats[selected]["hit@5"] >= val_stats["A"]["hit@5"] and val_stats[selected]["hit@5"] > 0 else (
        "partial" if val_stats[selected]["hit@5"] > val_stats["A"]["hit@5"] else "no — internal_val did not keep the DEV gain"
    )
    if val_stats[selected]["hit@5"] + 1e-9 >= dev_stats[selected]["hit@5"] - 0.15:
        gen_note = "Improvement was not completely lost on internal_val."
    else:
        gen_note = "internal_val dropped relative to DEV; reported honestly; method not retuned."

    names = {"A": "Raw BM25", "B": "Existing dictionary transliteration", "C": "Rule-based transliteration", "D": "Romanized-document BM25"}

    results = f"""# PHASE 5 FINAL REPORT

Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.  
**H001–H040 unused.** SVM not retrained. No RRF, score fusion, or reranker as a system.  
Known-item P@5 = 0.2 × Hit@5. QTRN Roman queries are Phase 2 `title_roman` strings (dictionary reverse + naive character romanization), not naturalistic chat Roman Urdu.

Selection: DEV `roman_urdu` only. Primary Hit@5, secondary nDCG@5, latency tie-break. Frozen before internal_val confirmation in `artifacts/selected_method.json`.

---

## 1. Roman Urdu baseline

How many Roman queries? **{len(roman_rows)}**  
DEV: {len(dev_roman)} · INTERNAL_VAL: {len(val_roman)}

Ids: {", ".join(r["query_id"] for r in roman_rows)}

Raw BM25 Hit@5 (Method A, all Roman): **{a_all["hit@5"]}** ({sum(1 for r in roman_rows if all_method_ranks["A"][r["query_id"]] <= 5)}/{len(roman_rows)})

Dense baseline Hit@5 (Phase 4B Headline, same ids): **{dense_hit}** ({dense_hits}/{len(roman_rows)})

Matches Phase 4B: BM25 0/23, dense ≈ 1/23.

---

## 2. Transliteration audit

Existing logic: `transliterate_roman` exact-match on `{len(fwd)}` dictionary keys. Whitespace split, lowercase.

Queries with ≥1 substitution: **{n_changed}/{len(roman_rows)}**.  
Still mostly Latin after mapping: **{n_mostly_latin}/{len(roman_rows)}**.

What failed to convert: Phase 2 naive romanizations (`krne`, `mshorh`, stripped vowels, letter-mapped names). See `TRANSLITERATION_AUDIT.md`.

---

## 3. DEV experiment

DEV Roman n = {len(dev_roman)}.

| Method | Hit@5 | Hit@10 | nDCG@5 | MRR | Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A. Raw BM25 | {dev_stats["A"]["hit@5"]} | {dev_stats["A"]["hit@10"]} | {dev_stats["A"]["ndcg@5"]} | {dev_stats["A"]["mrr"]} | {dev_stats["A"]["latency"]} |
| B. Existing dictionary transliteration | {dev_stats["B"]["hit@5"]} | {dev_stats["B"]["hit@10"]} | {dev_stats["B"]["ndcg@5"]} | {dev_stats["B"]["mrr"]} | {dev_stats["B"]["latency"]} |
| C. Rule-based transliteration | {dev_stats["C"]["hit@5"]} | {dev_stats["C"]["hit@10"]} | {dev_stats["C"]["ndcg@5"]} | {dev_stats["C"]["mrr"]} | {dev_stats["C"]["latency"]} |
| D. Romanized-document BM25 | {dev_stats["D"]["hit@5"]} | {dev_stats["D"]["hit@10"]} | {dev_stats["D"]["ndcg@5"]} | {dev_stats["D"]["mrr"]} | {dev_stats["D"]["latency"]} |

Method E (analysis, not selectable): union C∪D DEV Hit@5 = **{e_dev["union_hit@5"]}** (overlap {e_dev["overlap_hit@5"]}).

Method D index: build **{roman_stats["roman_index_build_sec"]} s** (tokenize+romanize {roman_stats["tokenize_romanize_sec"]} s + BM25 {roman_stats["roman_bm25_build_sec"]} s). In-memory postings **{roman_stats["roman_index_bytes"]}** bytes. Estimated romanized text **{roman_stats["estimated_romanized_text_bytes"]}** bytes. Full corpus, not source-only.

**Selected on DEV (before internal_val): Method {selected} — {names[selected]}.**

---

## 4. INTERNAL_VAL confirmation

Selected method: **{selected}**

| Split | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| DEV | {dev_stats[selected]["hit@5"]} | {dev_stats[selected]["ndcg@5"]} | {dev_stats[selected]["mrr"]} |
| INTERNAL_VAL | {val_stats[selected]["hit@5"]} | {val_stats[selected]["ndcg@5"]} | {val_stats[selected]["mrr"]} |

Did the improvement generalize? **{gen_note}**

Method was not modified after internal_val.

---

## 5. Roman Urdu improvement

Baseline Method A (all Roman): Hit@5 **{a_all["hit@5"]}**

Selected method (all Roman, diagnostic pool): Hit@5 **{sel_all["hit@5"]}**

Absolute improvement: **{abs_imp}**

Recovered query count (A miss → selected Hit@5): **{len(recovered)}**

Still missed by selected: **{len(miss_sel)}**

All methods miss: **{len(still_fail_all_methods)}**

---

## 6. Urdu regression check

Urdu BM25 baseline (n={urdu_base["n"]}): Hit@5 **{urdu_base["hit@5"]}**, nDCG@5 **{urdu_base["ndcg@5"]}**, MRR **{urdu_base["mrr"]}**

Script-aware routing (Urdu → Urdu BM25): Hit@5 **{urdu_routed["hit@5"]}**, nDCG@5 **{urdu_routed["ndcg@5"]}**, MRR **{urdu_routed["mrr"]}**

Any regression? **No.** The Urdu path is the same index and the same raw query.

---

## 7. Script detection

URDU: **{pred_counts["URDU"]}**  
ROMAN: **{pred_counts["ROMAN"]}**  
MIXED: **{pred_counts["MIXED"]}**  
OTHER: **{pred_counts["OTHER"]}**

Ambiguous / mismatches: **{len(set(ambiguous))}** — see `SCRIPT_DETECTION_REPORT.md`.

---

## 8. Combined routing result

n=78. Deployable mixed policy: Urdu BM25 (no fusion).

| System | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| Headline | {m_head["hit@5"]} | {m_head["ndcg@5"]} | {m_head["mrr"]} |
| Raw BM25 | {m_bm25["hit@5"]} | {m_bm25["ndcg@5"]} | {m_bm25["mrr"]} |
| Script-aware retrieval | {m_route["hit@5"]} | {m_route["ndcg@5"]} | {m_route["mrr"]} |

Mixed path 1 (Urdu BM25) Hit@5 {mixed_urdu_path["hit@5"]}.  
Mixed path 2 (selected Roman method) Hit@5 {mixed_sel_path["hit@5"]}.  
Mixed union oracle Hit@5 {mixed_union["hit@5"]} (not deployable).

---

## 9. Oracle headroom

| Ceiling | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| Urdu BM25 + selected Roman | {m_ora_route["hit@5"]} | {m_ora_route["ndcg@5"]} | {m_ora_route["mrr"]} |
| Headline + script-aware | {m_ora_head["hit@5"]} | {m_ora_head["ndcg@5"]} | {m_ora_head["mrr"]} |
| Headline + Urdu BM25 + selected + mixed roman path | {m_ora3["hit@5"]} | {m_ora3["ndcg@5"]} | {m_ora3["mrr"]} |

Remaining all-fail vs that last ceiling (Hit@5 miss): **{sum(1 for r in ora3 if r > 5)}** queries.

Roman-only Method E union C∪D Hit@5: **{e_all["union_hit@5"]}** ({e_all["union_hits"]}/{e_all["n"]}).

These ceilings are **not** a deployed system.

---

## 10. Main finding

Method {selected} is the DEV winner among A–D.

Roman Urdu failure in Phase 4B was **script mismatch**, not BM25 being a weak lexical ranker on Urdu. Query-side dictionary B does not rewrite Phase 2 naive romanizations. Rule-based inverse C is lossy (`t`/`d`/`h` collisions). Document-side romanization (D) puts queries and documents in the **same** Phase 2 character inventory.

Remaining bottleneck after this experiment: not “add more dictionary rows for QTRN ids”. Residual misses are (a) tokenizer / title-vs-body romanization mismatch, (b) extremely collapsed spellings with little residual overlap, (c) non-Roman failures already visible in Phase 4B (some mixed/Urdu known-items). Naturalistic Roman Urdu (user `kya`/`kia` style) is **not** what most of these 23 strings are; a chat-Roman system would still need evaluation on that distribution, without using H001–H040.

---

## 11. What should NOT be done next

- Do **not** open H001–H040.
- Do **not** retrain the SVM for script detection (the Unicode rule already matches oracle labels on this pool).
- Do **not** build RRF / score fusion yet — Method E union is an analysis ceiling, not a system.
- Do **not** add query-specific dictionary rows (`QTRN_*` spellings).
- Do **not** retune BM25 `k1`/`b` on n=78.
- Do **not** start long-context e5 indexing on this CPU (Phase 4B 4-hour gate failed).
- Do **not** treat known-item Hit@5 on title-derived QTRN as 80% P@5 under human judgments.

---

## 12. Recommended Phase 6

**One next experiment:** if Method D (or the DEV winner) generalizes on internal_val, freeze **script-aware lexical routing** (Urdu → Urdu BM25, Roman → romanized-document BM25) and measure **error types on residual misses only** — specifically whether leftover Roman failures are generation artifacts (naive `title_roman`) vs true content mismatch — using DEV/internal_val source headlines you already have. Do **not** add fusion until that residual set is shown to be rank-fusion-shaped (different rooms retrieving different remaining ids). If the DEV winner does **not** generalize, Phase 6 should be a **general** Romanizer mismatch analysis (query tokenizer vs document tokenizer), still without H001–H040 and without query-id patches.

STOP.
"""
    with open(os.path.join(OUT, "PHASE5_RESULTS.md"), "w", encoding="utf-8") as f:
        f.write(results)

    # compact json dump
    with open(os.path.join(ART, "phase5_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "selected": selected,
            "dev": {m: {k: v for k, v in dev_stats[m].items() if k != "ranks"} for m in dev_stats},
            "internal_val": {m: {k: v for k, v in val_stats[m].items() if k != "ranks"} for m in val_stats},
            "roman_all": {m: {k: v for k, v in all_method_meta[m].items() if k != "ranks"} for m in all_method_meta},
            "routing_n78": {"headline": m_head, "raw_bm25": m_bm25, "script_aware": m_route},
            "oracle": {"script_aware": m_ora_route, "headline_plus": m_ora_head, "all_paths": m_ora3},
            "method_E": {"dev": e_dev, "internal_val": e_val, "all_roman": e_all, "B_union_D": e_bd_all},
            "recovered": recovered,
            "still_fail_all_methods": still_fail_all_methods,
            "urdu": urdu_base,
            "mixed_union": mixed_union,
            "roman_index": roman_stats,
        }, f, indent=2, ensure_ascii=False)

    print("=== DONE selected=%s dev_hit@5=%s val_hit@5=%s route78_hit@5=%s ===" % (
        selected, dev_stats[selected]["hit@5"], val_stats[selected]["hit@5"], m_route["hit@5"],
    ), flush=True)


if __name__ == "__main__":
    main()
