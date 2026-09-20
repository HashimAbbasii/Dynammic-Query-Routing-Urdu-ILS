# -*- coding: utf-8 -*-
"""Shared TEST-seal hashing. Deterministic file order. Metadata is not hashed."""
from __future__ import annotations

import hashlib
import os

KIND = "ultra_v2_test_seal"
EXEMPT_NAMES = frozenset({"readme.md", "seal.json"})


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_exempt_name(name: str) -> bool:
    return os.path.basename(name).lower() in EXEMPT_NAMES


def list_sealable_files(directory: str) -> list[str]:
    """Top-level files except README and seal.json, sorted by name."""
    names = []
    for name in os.listdir(directory):
        if is_exempt_name(name):
            continue
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            names.append(name)
    names.sort()
    return names


def file_records(directory: str, names: list[str]) -> list[dict]:
    rows = []
    for name in names:
        path = os.path.join(directory, name)
        rows.append(
            {
                "relative_path": name,
                "bytes": os.path.getsize(path),
                "sha256": sha256_file(path),
            }
        )
    rows.sort(key=lambda x: x["relative_path"])
    return rows


def aggregate_sha256(files: list[dict]) -> str:
    ordered = sorted(files, key=lambda x: x["relative_path"])
    lines = ["%s %s" % (item["relative_path"], item["sha256"]) for item in ordered]
    payload = "\n".join(lines) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
