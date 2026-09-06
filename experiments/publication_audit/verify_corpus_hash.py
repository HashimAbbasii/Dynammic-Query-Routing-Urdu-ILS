# -*- coding: utf-8 -*-
"""Verify a local corpus file against the frozen ULTRA clean_articles.csv identity.

Does not modify any dataset. Does not run preprocessing or retrieval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys

EXPECTED_SHA256 = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_BYTES = 540050203
EXPECTED_ROWS = 111860


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def count_data_rows(path: str) -> int:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare a corpus CSV to the frozen ULTRA SHA-256 / size / row count."
    )
    parser.add_argument(
        "--path",
        default=os.path.join("data", "clean_articles.csv"),
        help="Path to a corpus CSV (default: data/clean_articles.csv)",
    )
    args = parser.parse_args(argv)
    path = os.path.abspath(args.path)

    print("corpus_path:", path)
    if not os.path.isfile(path):
        print("status: MISSING")
        print("expected_sha256:", EXPECTED_SHA256)
        return 2

    size = os.path.getsize(path)
    digest = sha256_file(path)
    try:
        n_rows = count_data_rows(path)
        row_note = ""
    except Exception as exc:
        n_rows = None
        row_note = "row_count_error: %s" % exc

    print("bytes:", size)
    print("expected_bytes:", EXPECTED_BYTES)
    print("sha256:", digest)
    print("expected_sha256:", EXPECTED_SHA256)
    if n_rows is None:
        print("data_rows:", "NOT_AVAILABLE")
        if row_note:
            print(row_note)
    else:
        print("data_rows:", n_rows)
        print("expected_data_rows:", EXPECTED_ROWS)

    hash_ok = digest == EXPECTED_SHA256
    print("hash:", "MATCH" if hash_ok else "MISMATCH")
    if size != EXPECTED_BYTES:
        print("size:", "MISMATCH")
    else:
        print("size:", "MATCH")
    if n_rows is not None:
        print("rows:", "MATCH" if n_rows == EXPECTED_ROWS else "MISMATCH")

    print("status:", "MATCH" if hash_ok else "MISMATCH")
    return 0 if hash_ok else 1


if __name__ == "__main__":
    sys.exit(main())
