# -*- coding: utf-8 -*-
"""Frozen Phase-9 title matching (query-side). No retrieval.

Closed rules, written before scoring. Not derived from KN/NL query text.
"""
from __future__ import annotations

import os
import re
import unicodedata

# Verbatim M0 tokenizer (run_phase5.py TOKEN_RE + tokenize). Do not edit M0.
TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[A-Za-z0-9]+", re.UNICODE)

# Same 26-letter public orthography table as frozen Phase 7 (copied, not executed).
LETTER_URDU = {
    "a": "اے",
    "b": "بی",
    "c": "سی",
    "d": "ڈی",
    "e": "ای",
    "f": "ایف",
    "g": "جی",
    "h": "ایچ",
    "i": "آئی",
    "j": "جے",
    "k": "کے",
    "l": "ایل",
    "m": "ایم",
    "n": "این",
    "o": "او",
    "p": "پی",
    "q": "کیو",
    "r": "آر",
    "s": "ایس",
    "t": "ٹی",
    "u": "یو",
    "v": "وی",
    "w": "ڈبلیو",
    "x": "ایکس",
    "y": "وائی",
    "z": "زیڈ",
}

# Closed-class English function words + user-named magnet titles (Home/Go/Rise).
# Not built from the 51 queries.
STOP_UNIGRAMS = frozenset(
    {
        "a", "an", "the", "of", "in", "on", "to", "for", "and", "or", "but", "nor",
        "at", "by", "from", "with", "as", "is", "was", "are", "were", "be", "been",
        "being", "it", "its", "this", "that", "these", "those", "i", "you", "he",
        "she", "we", "they", "me", "my", "your", "his", "her", "our", "their",
        "not", "no", "yes", "if", "then", "than", "so", "because", "about",
        "into", "over", "after", "before", "up", "down", "out", "off", "via",
        "per", "vs", "de", "la", "el", "le", "da", "du", "von", "van",
        "home", "go", "rise",
    }
)

MAX_SPAN = 8
MAX_EN_HITS = 5
MAX_UR_PER_EN = 4
MIN_UNIGRAM_LEN = 5
INITIALISM_RE = re.compile(r"^[A-Z0-9]{2,6}$")
LATIN_INITIALISM_RE = re.compile(r"^[a-z]{2,6}$")
TRAILING_PAREN_RE = re.compile(r"\s*\([^)]*\)\s*$")
DAB_EN_RE = re.compile(r"\(\s*disambiguation\s*\)", re.I)
DAB_UR_RE = re.compile(r"ضد\s*ابہام|ضد\s*ابهام")
WORDLIST_SHA256 = "d6b3e04f1ac30be6525d41474166c0bff28486ecd8c48dcb0ab9c7c9cc05ed86"
WORDLIST_REL = os.path.join("resources", "google-10000-english-no-swears.txt")

_COMMON_ENGLISH: frozenset[str] | None = None


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def norm_en(title: str) -> str:
    return unicodedata.normalize("NFKC", title or "").strip().lower()


def heading_key(en_original: str) -> str:
    """English title with a single trailing parenthetical stripped, then NFKC+lower."""
    return norm_en(TRAILING_PAREN_RE.sub("", en_original or ""))


def compact_alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm_en(s))


def fold_ur_token(s: str) -> str:
    t = unicodedata.normalize("NFKC", s or "")
    return t.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")


def ur_token_key(title: str) -> str:
    """Folded Urdu token sequence. Spaces matter; concatenation is not a match."""
    return " ".join(fold_ur_token(t) for t in TOKEN_RE.findall(title or ""))


def letter_name_phrase(token: str) -> str | None:
    if not LATIN_INITIALISM_RE.fullmatch(token or ""):
        return None
    return " ".join(LETTER_URDU[ch] for ch in token)


def letter_name_key(token: str) -> str | None:
    phrase = letter_name_phrase(token)
    if phrase is None:
        return None
    return ur_token_key(phrase)


def is_initialism_title(en_original: str) -> bool:
    s = (en_original or "").replace(" ", "").replace(".", "")
    return bool(INITIALISM_RE.fullmatch(s)) and any(c.isalpha() for c in s)


def load_common_english(path: str | None = None) -> frozenset[str]:
    global _COMMON_ENGLISH
    if _COMMON_ENGLISH is not None and path is None:
        return _COMMON_ENGLISH
    import hashlib

    base = os.path.dirname(os.path.abspath(__file__))
    word_path = path or os.path.join(base, WORDLIST_REL)
    raw = open(word_path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != WORDLIST_SHA256:
        raise RuntimeError(f"wordlist sha mismatch: {got}")
    words = frozenset(
        ln.strip().lower()
        for ln in raw.decode("utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    )
    _COMMON_ENGLISH = words
    return words


def bundle_is_disambiguation(originals: list[str], entries: list[dict]) -> bool:
    if any(DAB_EN_RE.search(o or "") for o in originals):
        return True
    articles = [e for e in entries if e.get("row_type") == "article"]
    pool = articles if articles else entries
    if pool and all(DAB_UR_RE.search(e.get("ur_title") or "") for e in pool):
        return True
    if articles and any(DAB_UR_RE.search(e.get("ur_title") or "") for e in articles):
        return True
    return False


def lettername_unigram_allowed(token: str, originals: list[str], entries: list[dict]) -> bool:
    """L=1 Latin initialism that uniquely hits a Urdu letter-name title."""
    if token in STOP_UNIGRAMS:
        return False
    if bundle_is_disambiguation(originals, entries):
        return False
    words = load_common_english()
    if token in words:
        return False
    return True


def unigram_allowed(token: str, originals: list[str], entries: list[dict]) -> bool:
    if token in STOP_UNIGRAMS:
        return False
    if bundle_is_disambiguation(originals, entries):
        return False
    init = any(is_initialism_title(o) for o in originals)
    words = load_common_english()
    heading = heading_key(originals[0]) if originals else token
    if heading in words and not init:
        return False
    if len(token) >= MIN_UNIGRAM_LEN:
        return True
    return init


def select_ur_titles(entries: list[dict]) -> list[str]:
    articles = [e["ur_title"] for e in entries if e["row_type"] == "article"]
    redirects = [e["ur_title"] for e in entries if e["row_type"] != "article"]
    redirects.sort(key=lambda s: (len(s), s))
    out = []
    seen = set()
    for u in articles + redirects:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= MAX_UR_PER_EN:
            break
    return out


def _hit_from_rec(start: int, end: int, span: str, rec: dict) -> dict:
    originals = rec["originals"]
    return {
        "start": start,
        "end": end,
        "length": end - start,
        "span": span,
        "en_title": originals[0],
        "n_en_surface": len(originals),
        "n_ur_total": len(rec["entries"]),
        "ur_titles": select_ur_titles(rec["entries"]),
    }


def match_spans(tokens: list[str], en_index: dict, ur_compact_index: dict | None = None) -> list[dict]:
    """All exact-span hits that pass unigram filters (before overlap/cap)."""
    n = len(tokens)
    raw = []
    for i in range(n):
        for length in range(1, min(MAX_SPAN, n - i) + 1):
            j = i + length
            g = " ".join(tokens[i:j])
            rec = en_index.get(g)
            if rec is None:
                continue
            originals = rec["originals"]
            if length == 1:
                if not unigram_allowed(tokens[i], originals, rec["entries"]):
                    continue
            elif bundle_is_disambiguation(originals, rec["entries"]):
                continue
            raw.append(_hit_from_rec(i, j, g, rec))
        # L=1 only: Urdu letter-name reverse lookup for Latin initialism tokens.
        tok = tokens[i]
        phrase = letter_name_phrase(tok)
        if phrase and ur_compact_index:
            rows = ur_compact_index.get(letter_name_key(tok) or "") or []
            ens = []
            seen_en = set()
            for e in rows:
                en = e["en_title"]
                if en not in seen_en:
                    seen_en.add(en)
                    ens.append(en)
            if len(ens) == 1:
                rec = en_index.get(norm_en(ens[0]))
                if rec is not None and lettername_unigram_allowed(tok, rec["originals"], rec["entries"]):
                    if not any(h["start"] == i and h["end"] == i + 1 and h["en_title"] == rec["originals"][0] for h in raw):
                        raw.append(_hit_from_rec(i, i + 1, tok, rec))
    raw.sort(key=lambda h: (-h["length"], h["start"]))
    kept = []
    occupied = [False] * n
    for h in raw:
        if any(occupied[h["start"] : h["end"]]):
            continue
        kept.append(h)
        for k in range(h["start"], h["end"]):
            occupied[k] = True
        if len(kept) >= MAX_EN_HITS:
            break
    kept.sort(key=lambda h: h["start"])
    return kept


def add_dotted_initialism_aliases(en_index: dict) -> int:
    """Index compact alphanumeric form of dotted/spaced 2–6 initialism titles if unique.

    Does not overwrite an existing spaced/lowercase key.
    """
    compact_to_keys: dict[str, set[str]] = {}
    for key, rec in en_index.items():
        for o in rec["originals"]:
            if not is_initialism_title(o):
                continue
            c = compact_alnum(o)
            if not c or c == key:
                continue
            compact_to_keys.setdefault(c, set()).add(key)
    n_added = 0
    for c, keys in compact_to_keys.items():
        if len(keys) != 1:
            continue
        if c in en_index:
            continue
        en_index[c] = en_index[next(iter(keys))]
        n_added += 1
    return n_added
