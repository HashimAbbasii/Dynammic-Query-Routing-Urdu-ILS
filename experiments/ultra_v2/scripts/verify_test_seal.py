# -*- coding: utf-8 -*-
"""Verify an ULTRA v2 TEST seal manifest.

Detects missing, modified, and added data files. Does not repair files.
Metadata timestamp/created_by/notes are ignored for identity.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from seal_common import (
    KIND,
    aggregate_sha256,
    file_records,
    list_sealable_files,
    sha256_file,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify an ULTRA v2 TEST seal.")
    parser.add_argument("--seal", required=True, help="Path to seal JSON")
    parser.add_argument(
        "--root",
        default="",
        help="Directory that contains the sealed files (default: input_path in manifest)",
    )
    args = parser.parse_args(argv)

    seal_path = os.path.abspath(args.seal)
    print("seal:", seal_path)
    if not os.path.isfile(seal_path):
        print("status: FAIL")
        print("error: seal file missing")
        return 1

    with open(seal_path, encoding="utf-8") as f:
        man = json.load(f)

    if man.get("kind") != KIND:
        print("status: FAIL")
        print("error: kind is not %s" % KIND)
        return 1

    root = os.path.abspath(args.root) if args.root else os.path.abspath(man.get("input_path") or "")
    print("root:", root)
    if not os.path.isdir(root):
        print("status: FAIL")
        print("error: sealed directory missing")
        return 1

    errors: list[str] = []
    files = list(man.get("files") or [])
    if not files:
        errors.append("manifest has no files")

    expected = {item.get("relative_path") or "" for item in files}
    expected.discard("")
    present = set(list_sealable_files(root))

    for name in sorted(expected - present):
        errors.append("missing file %s" % name)
    for name in sorted(present - expected):
        errors.append("added file %s" % name)

    recomputed: list[dict] = []
    for item in files:
        rel = item.get("relative_path") or ""
        if not rel:
            errors.append("manifest entry missing relative_path")
            continue
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        digest = sha256_file(path)
        size = os.path.getsize(path)
        recomputed.append({"relative_path": rel, "bytes": size, "sha256": digest})
        if size != int(item.get("bytes", -1)):
            errors.append(
                "size mismatch %s: got %s expected %s" % (rel, size, item.get("bytes"))
            )
        if digest != item.get("sha256"):
            errors.append(
                "sha256 mismatch %s: got %s expected %s" % (rel, digest, item.get("sha256"))
            )

    if recomputed:
        agg = aggregate_sha256(recomputed)
        print("aggregate_sha256_got:", agg)
        print("aggregate_sha256_expected:", man.get("aggregate_sha256"))
        if agg != man.get("aggregate_sha256"):
            errors.append("aggregate_sha256 mismatch")

    live = file_records(root, list_sealable_files(root))
    if live:
        live_agg = aggregate_sha256(live)
        print("aggregate_sha256_live_dir:", live_agg)

    if errors:
        print("status: FAIL")
        print("n_errors:", len(errors))
        for e in errors:
            print("error:", e)
        return 1

    print("n_files:", len(files))
    print("status: MATCH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
