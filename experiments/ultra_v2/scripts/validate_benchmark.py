# -*- coding: utf-8 -*-
"""Validate ULTRA v2 benchmark CSV files.

Does not generate queries. Does not modify files. Does not run retrieval.
Exit 0: valid, or no query files yet (Phase 1 infrastructure).
Exit 1: validation errors.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
DEFAULT_BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")

SPLITS = ("train", "dev", "test")
KN_NAME = "queries_kn.csv"
NL_NAME = "queries_nl.csv"
QREL_NAME = "qrels.csv"

SCRIPTS = {"URDU", "ROMAN", "MIXED", "OTHER"}
INTENTS = {
    "factoid",
    "explanatory",
    "entity_person",
    "location",
    "event",
    "topical",
}
LENGTHS = {"short", "medium", "long"}
STATUSES = {"draft", "accepted", "sealed", "contaminated"}
SPLIT_VALS = {"train", "dev", "test"}
LABELS = {"A", "B", "C", "D", "E"}

KN_REQUIRED = [
    "query_id",
    "track",
    "script",
    "intent_type",
    "length_bin",
    "ambiguous",
    "query_text",
    "source_doc_id",
    "source_article_hash_or_identifier",
    "headline_overlap",
    "writer_id",
    "creation_timestamp",
    "split",
    "status",
]
NL_REQUIRED = [
    "query_id",
    "track",
    "script",
    "intent_type",
    "length_bin",
    "ambiguous",
    "query_text",
    "writer_id",
    "creation_timestamp",
    "split",
    "status",
]
QREL_REQUIRED = [
    "query_id",
    "doc_id",
    "annotator_id",
    "label",
    "official",
    "adjudicated",
]

RE_KN_ID = re.compile(r"^KN[0-9]{3,}$")
RE_NL_ID = re.compile(r"^NL[0-9]{3,}$")
RE_HIST = re.compile(r"^(QTRN_[0-9]+|H[0-9]{3,}|K[0-9]{3,}|U[0-9]{3,})$")
TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[A-Za-z0-9]+", re.UNICODE)
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")


def detect_script(query: str) -> str:
    """Must stay aligned with run_phase5.detect_script (import-only; do not edit M0)."""
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if urdu == 0 and latin == 0:
        return "OTHER"
    if urdu > 0 and latin > 0:
        return "MIXED"
    if urdu > 0:
        return "URDU"
    return "ROMAN"


def length_bin_of(text: str) -> str:
    n = len((text or "").split())
    if n <= 5:
        return "short"
    if n <= 12:
        return "medium"
    return "long"


def norm_text(text: str) -> str:
    return " ".join((text or "").split())


def m0_tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def headline_overlap(query: str, headline: str) -> float:
    q = m0_tokens(query)
    if not q:
        return 1.0
    h = m0_tokens(headline)
    return len(q & h) / float(len(q))


def err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    return fields, rows


def historical_query_texts() -> set[str]:
    """Exact and whitespace-normalized strings from frozen QTRN/K/U/H (read-only)."""
    texts: set[str] = set()
    candidates = [
        os.path.join(
            ROOT, "experiments", "phase12_new_unseen_evaluation", "queries_k.csv"
        ),
        os.path.join(
            ROOT, "experiments", "phase12_new_unseen_evaluation", "queries_u.csv"
        ),
        os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv"),
        os.path.join(
            ROOT, "experiments", "phase10c_human_relevance", "HELD_OUT_QRELS.csv"
        ),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        _, rows = load_csv(path)
        for r in rows:
            t = (r.get("query_text") or "").strip()
            if t:
                texts.add(t)
                texts.add(norm_text(t))
    return texts


def blocked_kn_source_ids() -> set[int]:
    """QTRN and Phase 12 K source ids must not be reused as v2 KN gold."""
    blocked: set[int] = set()
    paths = [
        os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv"),
        os.path.join(
            ROOT, "experiments", "phase12_new_unseen_evaluation", "queries_k.csv"
        ),
    ]
    for path in paths:
        if not os.path.isfile(path):
            continue
        _, rows = load_csv(path)
        for r in rows:
            raw = (r.get("source_doc_id") or "").strip()
            if not raw:
                continue
            try:
                blocked.add(int(raw))
            except ValueError:
                continue
    return blocked


def load_headlines() -> dict[int, str] | None:
    if not os.path.isfile(CORPUS):
        return None
    out: dict[int, str] = {}
    with open(CORPUS, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            idx_raw = (row.get("Index") or "").strip()
            try:
                idx = int(float(idx_raw)) if idx_raw else i
            except ValueError:
                idx = i
            out[idx] = row.get("Headline") or ""
    return out


def check_headers(fields: list[str], required: list[str], path: str, errors: list[str]) -> None:
    missing = [c for c in required if c not in fields]
    if missing:
        err(errors, "%s: missing columns %s" % (path, missing))


def check_common_row(
    r: dict[str, str],
    path: str,
    i: int,
    track: str,
    errors: list[str],
    id_set: set[str],
    text_index: dict[str, list[str]],
) -> None:
    loc = "%s row %s" % (path, i)
    qid = (r.get("query_id") or "").strip()
    qtext = (r.get("query_text") or "").strip()
    if not qid:
        err(errors, "%s: empty query_id" % loc)
    elif RE_HIST.match(qid):
        err(errors, "%s: historical/forbidden query_id %s" % (loc, qid))
    elif track == "KN" and not RE_KN_ID.match(qid):
        err(errors, "%s: query_id must match KN###, got %s" % (loc, qid))
    elif track == "NL" and not RE_NL_ID.match(qid):
        err(errors, "%s: query_id must match NL###, got %s" % (loc, qid))
    if qid:
        if qid in id_set:
            err(errors, "%s: duplicate query_id %s" % (loc, qid))
        id_set.add(qid)
    if not qtext:
        err(errors, "%s: empty query_text" % loc)
    else:
        text_index[qtext].append("%s:%s" % (path, qid or i))
        text_index[norm_text(qtext)].append("%s:%s" % (path, qid or i))

    if (r.get("track") or "").strip() != track:
        err(errors, "%s: track must be %s" % (loc, track))
    script = (r.get("script") or "").strip()
    if script not in SCRIPTS:
        err(errors, "%s: invalid script %s" % (loc, script))
    elif qtext and detect_script(qtext) != script:
        err(
            errors,
            "%s: script %s does not match detector %s"
            % (loc, script, detect_script(qtext)),
        )
    intent = (r.get("intent_type") or "").strip()
    if intent not in INTENTS:
        err(errors, "%s: invalid intent_type %s" % (loc, intent))
    lb = (r.get("length_bin") or "").strip()
    if lb not in LENGTHS:
        err(errors, "%s: invalid length_bin %s" % (loc, lb))
    elif qtext and length_bin_of(qtext) != lb:
        err(
            errors,
            "%s: length_bin %s does not match whitespace count (%s)"
            % (loc, lb, length_bin_of(qtext)),
        )
    amb = (r.get("ambiguous") or "").strip()
    if amb not in {"0", "1"}:
        err(errors, "%s: ambiguous must be 0 or 1" % loc)
    split = (r.get("split") or "").strip()
    if split not in SPLIT_VALS:
        err(errors, "%s: invalid split %s" % (loc, split))
    status = (r.get("status") or "").strip()
    if status not in STATUSES:
        err(errors, "%s: invalid status %s" % (loc, status))
    if not (r.get("writer_id") or "").strip():
        err(errors, "%s: empty writer_id" % loc)
    if not (r.get("creation_timestamp") or "").strip():
        err(errors, "%s: empty creation_timestamp" % loc)


def validate_kn(
    path: str,
    folder_split: str,
    errors: list[str],
    id_set: set[str],
    text_index: dict[str, list[str]],
    sources: dict[str, list[str]],
) -> int:
    fields, rows = load_csv(path)
    check_headers(fields, KN_REQUIRED, path, errors)
    n = 0
    for i, r in enumerate(rows, start=2):
        if not any((v or "").strip() for v in r.values()):
            continue
        n += 1
        check_common_row(r, path, i, "KN", errors, id_set, text_index)
        loc = "%s row %s" % (path, i)
        src = (r.get("source_doc_id") or "").strip()
        if not src:
            err(errors, "%s: KN requires source_doc_id" % loc)
        else:
            try:
                sid = int(src)
            except ValueError:
                err(errors, "%s: source_doc_id not an integer" % loc)
                sid = None
            if sid is not None and not (0 <= sid <= 111859):
                err(errors, "%s: source_doc_id out of range" % loc)
            if sid is not None:
                sources[str(sid)].append((r.get("query_id") or "").strip() or loc)
        ident = (r.get("source_article_hash_or_identifier") or "").strip()
        if not ident:
            err(errors, "%s: missing source_article_hash_or_identifier" % loc)
        ov = (r.get("headline_overlap") or "").strip()
        try:
            overlap = float(ov)
        except ValueError:
            err(errors, "%s: headline_overlap not a float" % loc)
            overlap = None
        if overlap is not None and not (0.0 <= overlap <= 1.0):
            err(errors, "%s: headline_overlap out of [0,1]" % loc)
        qtext = (r.get("query_text") or "").strip()
        if qtext and not m0_tokens(qtext):
            err(errors, "%s: query has no M0 tokens (|Q|=0)" % loc)
        status = (r.get("status") or "").strip()
        if overlap is not None and overlap >= 0.50 and status in {"accepted", "sealed"}:
            err(
                errors,
                "%s: headline_overlap %.4f >= 0.50 (protocol reject)"
                % (loc, overlap),
            )
        split = (r.get("split") or "").strip()
        if split and split != folder_split:
            err(
                errors,
                "%s: split=%s but file is under %s/" % (loc, split, folder_split),
            )
    return n


def validate_nl(
    path: str,
    folder_split: str,
    errors: list[str],
    id_set: set[str],
    text_index: dict[str, list[str]],
) -> int:
    fields, rows = load_csv(path)
    check_headers(fields, NL_REQUIRED, path, errors)
    if "source_doc_id" in fields:
        for i, r in enumerate(rows, start=2):
            if (r.get("source_doc_id") or "").strip():
                err(
                    errors,
                    "%s row %s: NL must not have source_doc_id" % (path, i),
                )
    n = 0
    for i, r in enumerate(rows, start=2):
        if not any((v or "").strip() for v in r.values()):
            continue
        n += 1
        check_common_row(r, path, i, "NL", errors, id_set, text_index)
        loc = "%s row %s" % (path, i)
        split = (r.get("split") or "").strip()
        if split and split != folder_split:
            err(
                errors,
                "%s: split=%s but file is under %s/" % (loc, split, folder_split),
            )
        amb = (r.get("ambiguous") or "").strip()
        status = (r.get("status") or "").strip()
        notes = (r.get("interpretation_notes") or "").strip()
        if amb == "1" and status in {"accepted", "sealed"} and not notes:
            err(errors, "%s: ambiguous NL requires interpretation_notes" % loc)
    return n


def validate_qrels(path: str, errors: list[str], known_ids: set[str]) -> int:
    fields, rows = load_csv(path)
    check_headers(fields, QREL_REQUIRED, path, errors)
    n = 0
    for i, r in enumerate(rows, start=2):
        if not any((v or "").strip() for v in r.values()):
            continue
        n += 1
        loc = "%s row %s" % (path, i)
        qid = (r.get("query_id") or "").strip()
        if not qid:
            err(errors, "%s: empty query_id" % loc)
        elif known_ids and qid not in known_ids:
            err(errors, "%s: qrel query_id not in benchmark %s" % (loc, qid))
        if (r.get("label") or "").strip() not in LABELS:
            err(errors, "%s: invalid label" % loc)
        for flag in ("official", "adjudicated"):
            if (r.get(flag) or "").strip() not in {"0", "1"}:
                err(errors, "%s: %s must be 0 or 1" % (loc, flag))
        try:
            int((r.get("doc_id") or "").strip())
        except ValueError:
            err(errors, "%s: doc_id not an integer" % loc)
    return n


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ULTRA v2 benchmark CSVs.")
    parser.add_argument(
        "--root",
        default=DEFAULT_BENCH,
        help="Benchmark root (default: experiments/ultra_v2/benchmark)",
    )
    parser.add_argument(
        "--skip-historical-duplicates",
        action="store_true",
        help="Disable the QTRN/K/U/H exact-string copy firewall (not recommended).",
    )
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    errors: list[str] = []
    id_set: set[str] = set()
    text_index: dict[str, list[str]] = defaultdict(list)
    sources: dict[str, list[str]] = defaultdict(list)
    n_kn = n_nl = n_q = 0
    found_any = False
    kn_rows_meta: list[tuple[str, int, dict[str, str]]] = []

    print("benchmark_root:", root)
    if not os.path.isdir(root):
        print("status: MISSING_ROOT")
        print("error: benchmark root does not exist")
        return 1

    for split in SPLITS:
        folder = os.path.join(root, split)
        kn = os.path.join(folder, KN_NAME)
        nl = os.path.join(folder, NL_NAME)
        qrel = os.path.join(folder, QREL_NAME)
        if os.path.isfile(kn):
            found_any = True
            n_kn += validate_kn(kn, split, errors, id_set, text_index, sources)
            _, rows = load_csv(kn)
            for i, r in enumerate(rows, start=2):
                if any((v or "").strip() for v in r.values()):
                    kn_rows_meta.append((kn, i, r))
        if os.path.isfile(nl):
            found_any = True
            n_nl += validate_nl(nl, split, errors, id_set, text_index)
        if os.path.isfile(qrel):
            found_any = True
            n_q += validate_qrels(qrel, errors, id_set)

    for text, locs in text_index.items():
        uniq = sorted(set(locs))
        if len(uniq) > 1:
            err(errors, "duplicate query_text (exact or whitespace-normalized) at %s" % uniq)

    for sid, qids in sources.items():
        if len(qids) > 1:
            err(errors, "duplicate source_doc_id %s used by %s" % (sid, qids))

    if kn_rows_meta:
        blocked = blocked_kn_source_ids()
        print("blocked_historical_source_ids:", len(blocked))
        for path, i, r in kn_rows_meta:
            raw = (r.get("source_doc_id") or "").strip()
            try:
                sid = int(raw)
            except ValueError:
                continue
            if sid in blocked:
                err(
                    errors,
                    "%s row %s: source_doc_id %s is a QTRN or Phase-12 K source"
                    % (path, i, sid),
                )

        headlines = load_headlines()
        if headlines is None:
            print("headline_overlap_recompute: SKIPPED (corpus missing)")
        else:
            print("headline_overlap_recompute: corpus_headlines", len(headlines))
            for path, i, r in kn_rows_meta:
                loc = "%s row %s" % (path, i)
                raw = (r.get("source_doc_id") or "").strip()
                try:
                    sid = int(raw)
                except ValueError:
                    continue
                if sid not in headlines:
                    err(errors, "%s: source_doc_id %s not in corpus Index" % (loc, sid))
                    continue
                qtext = (r.get("query_text") or "").strip()
                recomputed = headline_overlap(qtext, headlines[sid])
                status = (r.get("status") or "").strip()
                if recomputed >= 0.50 and status in {"accepted", "sealed"}:
                    err(
                        errors,
                        "%s: recomputed headline_overlap %.4f >= 0.50"
                        % (loc, recomputed),
                    )
                reported = (r.get("headline_overlap") or "").strip()
                try:
                    reported_f = float(reported)
                except ValueError:
                    continue
                if abs(reported_f - recomputed) > 1e-4:
                    err(
                        errors,
                        "%s: headline_overlap field %.6f != recomputed %.6f"
                        % (loc, reported_f, recomputed),
                    )

    if not args.skip_historical_duplicates and (n_kn or n_nl):
        hist = historical_query_texts()
        print("historical_query_strings:", len(hist))
        seen_hist = set()
        for text, locs in text_index.items():
            if text in hist:
                key = tuple(sorted(set(locs)))
                if key in seen_hist:
                    continue
                seen_hist.add(key)
                err(
                    errors,
                    "query_text copies a historical QTRN/K/U/H string at %s" % list(key),
                )

    print("kn_rows:", n_kn)
    print("nl_rows:", n_nl)
    print("qrel_rows:", n_q)
    print("unique_ids:", len(id_set))

    if not found_any:
        print("status: NO_QUERY_FILES")
        print(
            "note: expected until query collection is authorized. "
            "No KN/NL records generated."
        )
        return 0

    if errors:
        print("status: FAIL")
        print("n_errors:", len(errors))
        for e in errors:
            print("error:", e)
        return 1

    print("status: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
