# -*- coding: utf-8 -*-
"""Rebuild a *candidate* clean_articles.csv from a local urdu_news.csv.

Implements the same pandas steps as
archive/historical_experiments/notebooks/01_preprocessing.ipynb.

Does not download the third-party news dataset.
Does not overwrite data/clean_articles.csv (the frozen file).
Does not change M0, queries, labels, or official metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

EXPECTED_SHA256 = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
COLUMNS = [
    "Index",
    "Headline",
    "News Text",
    "Category",
    "Date",
    "URL",
    "Source",
    "News length",
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct a candidate corpus CSV without overwriting the freeze."
    )
    parser.add_argument(
        "--input",
        default=os.path.join("data", "urdu_news.csv"),
        help="Local precursor CSV (default: data/urdu_news.csv)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("data", "clean_articles.reconstructed.csv"),
        help="Candidate output path (must not be data/clean_articles.csv)",
    )
    args = parser.parse_args(argv)

    in_path = os.path.abspath(args.input)
    out_path = os.path.abspath(args.output)
    frozen = os.path.abspath(os.path.join("data", "clean_articles.csv"))

    if out_path == frozen:
        print("refusing to overwrite frozen data/clean_articles.csv")
        print("write a candidate path such as data/clean_articles.reconstructed.csv")
        return 2

    if not os.path.isfile(in_path):
        print("status: INPUT_MISSING")
        print("input:", in_path)
        print("obtain the third-party source and place it at this path; see REPRODUCE.md")
        return 2

    try:
        import pandas as pd
    except ImportError:
        print("status: PANDAS_MISSING")
        print("install the environment in requirements.txt")
        return 2

    df = pd.read_csv(in_path, encoding="utf-8-sig", encoding_errors="replace")
    print("input_rows:", len(df))
    print("input_cols:", len(df.columns))
    if len(df.columns) != 8:
        print("warning: expected 8 columns (Index, Headline, News Text, Category, Date, URL, Source, News length)")
    df.columns = COLUMNS
    df = df.dropna()
    df = df.reset_index(drop=True)
    df["combined_text"] = df["Headline"] + " " + df["News Text"]
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    digest = sha256_file(out_path)
    print("output:", out_path)
    print("output_rows:", len(df))
    print("output_bytes:", os.path.getsize(out_path))
    print("output_sha256:", digest)
    print("expected_sha256:", EXPECTED_SHA256)
    print("hash:", "MATCH" if digest == EXPECTED_SHA256 else "MISMATCH")
    print("status:", "MATCH" if digest == EXPECTED_SHA256 else "MISMATCH")
    if digest != EXPECTED_SHA256:
        print("a row-count match is not sufficient; pandas to_csv can differ across versions")
        print("do not replace data/clean_articles.csv to force a hash match")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
