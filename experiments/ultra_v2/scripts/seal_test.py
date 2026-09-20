# -*- coding: utf-8 -*-
"""Seal an existing ULTRA v2 TEST directory.

Does not create queries. Does not overwrite an existing seal unless --force.
Hashes every top-level data file except README.md and seal.json.
Metadata (timestamp, created_by, notes) is NOT part of aggregate_sha256.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from seal_common import (
    KIND,
    aggregate_sha256,
    file_records,
    list_sealable_files,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write a SHA-256 seal manifest for a TEST directory."
    )
    parser.add_argument("--input", required=True, help="Directory to seal")
    parser.add_argument("--output", required=True, help="Path to seal JSON")
    parser.add_argument(
        "--version",
        default="ultra-v2-benchmark-v0",
        help="Benchmark version string",
    )
    parser.add_argument("--created-by", default="", help="Optional operator id")
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing seal file",
    )
    args = parser.parse_args(argv)

    input_dir = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    print("input:", input_dir)
    print("output:", output_path)

    if not os.path.isdir(input_dir):
        print("status: FAIL")
        print("error: input directory does not exist")
        return 1

    if os.path.isfile(output_path) and not args.force:
        print("status: FAIL")
        print("error: seal already exists; pass --force to overwrite")
        return 1

    names = list_sealable_files(input_dir)
    if "queries_kn.csv" not in names and "queries_nl.csv" not in names:
        print("status: FAIL")
        print("error: expected queries_kn.csv and/or queries_nl.csv")
        print("note: seal_test.py does not generate a test set")
        return 1

    files_out = file_records(input_dir, names)
    if not files_out:
        print("status: FAIL")
        print("error: no sealable data files")
        return 1

    manifest = {
        "kind": KIND,
        "benchmark_version": args.version,
        "sealed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": args.created_by,
        "input_path": input_dir,
        "notes": args.notes,
        "files": files_out,
        "aggregate_sha256": aggregate_sha256(files_out),
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print("n_files:", len(files_out))
    for item in files_out:
        print("file:", item["relative_path"], item["bytes"], item["sha256"])
    print("aggregate_sha256:", manifest["aggregate_sha256"])
    print("note: README.md and seal.json are not hashed; extra data files are")
    print("status: SEALED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
