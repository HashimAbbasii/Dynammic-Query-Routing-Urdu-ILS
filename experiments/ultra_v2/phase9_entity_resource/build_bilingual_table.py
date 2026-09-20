# -*- coding: utf-8 -*-
"""Build query-independent Urdu↔English Wikipedia title table from dated SQL dumps.

Does not read KN/NL queries, TEST, M0, or frozen v2 phase 2–8 artifacts.
Does not retrieve. Resource construction only.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import random
import sys
import urllib.request
from datetime import datetime, timezone

_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_DIR = os.path.join(_DIR, "dumps")
ART = os.path.join(_DIR, "artifacts")

DUMP_DATE = "20260901"
BASE = f"https://dumps.wikimedia.org/urwiki/{DUMP_DATE}/"
FILES = [
    "urwiki-20260901-langlinks.sql.gz",
    "urwiki-20260901-page.sql.gz",
    "urwiki-20260901-redirect.sql.gz",
]
USER_AGENT = "ULTRA-v2-phase9/0.1 (research; Hashim Shazad; urwiki dump fetch)"
SAMPLE_SEED = 20260901


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def download(name: str) -> str:
    os.makedirs(DUMP_DIR, exist_ok=True)
    dest = os.path.join(DUMP_DIR, name)
    url = BASE + name
    if os.path.isfile(dest) and os.path.getsize(dest) > 0:
        print(f"exists {name} ({os.path.getsize(dest)} bytes)", flush=True)
        return dest
    print(f"GET {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as out:
        n = 0
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            n += len(chunk)
            if n % (20 * 1024 * 1024) < 1024 * 1024:
                print(f"  {name} {n / 1e6:.1f} MB", flush=True)
    os.replace(tmp, dest)
    print(f"saved {name} ({os.path.getsize(dest)} bytes)", flush=True)
    return dest


def mysql_unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            mapping = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "b": "\b", "Z": "\x1a"}
            out.append(mapping.get(nxt, nxt))
            i += 2
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def parse_insert_rows(sql_chunk: str):
    """Yield tuples from one or more MySQL INSERT ... VALUES (...),(...); chunks."""
    upper = sql_chunk.upper()
    marker = "VALUES"
    pos = 0
    while True:
        idx = upper.find(marker, pos)
        if idx < 0:
            return
        i = idx + len(marker)
        while i < len(sql_chunk) and sql_chunk[i].isspace():
            i += 1
        if i >= len(sql_chunk) or sql_chunk[i] != "(":
            pos = idx + 1
            continue
        row = []
        field = []
        in_str = False
        i += 1
        while i < len(sql_chunk):
            ch = sql_chunk[i]
            if in_str:
                if ch == "\\" and i + 1 < len(sql_chunk):
                    field.append(ch)
                    field.append(sql_chunk[i + 1])
                    i += 2
                    continue
                if ch == "'":
                    in_str = False
                    i += 1
                    continue
                field.append(ch)
                i += 1
                continue
            if ch == "'":
                in_str = True
                i += 1
                continue
            if ch == ",":
                row.append("".join(field))
                field = []
                i += 1
                continue
            if ch == ")":
                row.append("".join(field))
                yield tuple(x.strip() for x in row)
                row = []
                field = []
                i += 1
                while i < len(sql_chunk) and sql_chunk[i].isspace():
                    i += 1
                if i < len(sql_chunk) and sql_chunk[i] == ",":
                    i += 1
                    while i < len(sql_chunk) and sql_chunk[i].isspace():
                        i += 1
                    if i < len(sql_chunk) and sql_chunk[i] == "(":
                        i += 1
                        continue
                pos = i
                break
            field.append(ch)
            i += 1
        else:
            return


def iter_insert_tuples(gz_path: str, table: str):
    needle = f"INSERT INTO `{table}`".encode("ascii")
    buf = b""
    with gzip.open(gz_path, "rb") as f:
        while True:
            chunk = f.read(8 * 1024 * 1024)
            if not chunk:
                break
            buf += chunk
            while True:
                start = buf.find(needle)
                if start < 0:
                    if len(buf) > 16 * 1024 * 1024:
                        buf = buf[-65536:]
                    break
                end = buf.find(b";", start)
                if end < 0:
                    if start > 0:
                        buf = buf[start:]
                    break
                block = buf[start : end + 1].decode("utf-8", errors="replace")
                yield from parse_insert_rows(block)
                buf = buf[end + 1 :]


def as_int(x: str) -> int:
    x = x.strip()
    if x.upper() == "NULL" or x == "":
        return 0
    return int(x)


def wiki_title_display(raw: str) -> str:
    return mysql_unescape(raw).replace("_", " ")


def build(paths: dict[str, str]) -> dict:
    os.makedirs(ART, exist_ok=True)
    en_by_from: dict[int, str] = {}
    n_ll = 0
    n_ll_en = 0
    print("parse langlinks", flush=True)
    for row in iter_insert_tuples(paths["langlinks"], "langlinks"):
        n_ll += 1
        if len(row) < 3:
            continue
        ll_lang = mysql_unescape(row[1])
        ll_title = mysql_unescape(row[2])
        if ll_lang != "en":
            continue
        n_ll_en += 1
        en_by_from[as_int(row[0])] = ll_title
    print(f"  langlinks rows={n_ll} en={n_ll_en} unique_from={len(en_by_from)}", flush=True)

    page_by_id: dict[int, tuple[int, str, int]] = {}
    id_by_ns_title: dict[tuple[int, str], int] = {}
    n_page = 0
    print("parse page", flush=True)
    for row in iter_insert_tuples(paths["page"], "page"):
        n_page += 1
        if len(row) < 4:
            continue
        pid = as_int(row[0])
        ns = as_int(row[1])
        title = mysql_unescape(row[2])
        is_redir = as_int(row[3])
        page_by_id[pid] = (ns, title, is_redir)
        id_by_ns_title[(ns, title)] = pid
        if n_page % 500000 == 0:
            print(f"  page {n_page}", flush=True)
    print(f"  page rows={n_page}", flush=True)

    redir_by_from: dict[int, tuple[int, str]] = {}
    n_rd = 0
    print("parse redirect", flush=True)
    for row in iter_insert_tuples(paths["redirect"], "redirect"):
        n_rd += 1
        if len(row) < 3:
            continue
        rd_from = as_int(row[0])
        rd_ns = as_int(row[1])
        rd_title = mysql_unescape(row[2])
        redir_by_from[rd_from] = (rd_ns, rd_title)
    print(f"  redirect rows={n_rd}", flush=True)

    seen = set()
    out_rows = []

    def add(ur_raw: str, en_raw: str, row_type: str, src_id: int, tgt_id: int):
        ur = wiki_title_display(ur_raw)
        en = wiki_title_display(en_raw)
        if not ur or not en:
            return
        key = (ur, en, row_type)
        if key in seen:
            return
        seen.add(key)
        out_rows.append(
            {
                "ur_title": ur,
                "en_title": en,
                "row_type": row_type,
                "source_page_id": src_id,
                "target_page_id": tgt_id,
            }
        )

    n_article = 0
    for pid, en_raw in en_by_from.items():
        rec = page_by_id.get(pid)
        if rec is None:
            continue
        ns, title, _is_redir = rec
        if ns != 0:
            continue
        add(title, en_raw, "article", pid, pid)
        n_article += 1

    n_redir_kept = 0
    for rd_from, (rd_ns, rd_title) in redir_by_from.items():
        src = page_by_id.get(rd_from)
        if src is None:
            continue
        src_ns, src_title, _ = src
        if src_ns != 0 or rd_ns != 0:
            continue
        tgt_id = id_by_ns_title.get((rd_ns, rd_title))
        if tgt_id is None:
            continue
        tgt = page_by_id.get(tgt_id)
        if tgt is not None and tgt[2] == 1 and tgt_id in redir_by_from:
            hop_ns, hop_title = redir_by_from[tgt_id]
            hop_id = id_by_ns_title.get((hop_ns, hop_title))
            if hop_id is not None:
                tgt_id = hop_id
        en_raw = en_by_from.get(tgt_id)
        if not en_raw:
            continue
        add(src_title, en_raw, "redirect", rd_from, tgt_id)
        n_redir_kept += 1

    csv_path = os.path.join(ART, "bilingual_titles.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["ur_title", "en_title", "row_type", "source_page_id", "target_page_id"],
        )
        w.writeheader()
        w.writerows(out_rows)

    rng = random.Random(SAMPLE_SEED)
    sample = rng.sample(out_rows, min(20, len(out_rows)))
    summary = {
        "dump_date": DUMP_DATE,
        "base_url": BASE,
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_langlinks_rows": n_ll,
        "n_langlinks_en": n_ll_en,
        "n_page_rows": n_page,
        "n_redirect_rows": n_rd,
        "n_article_rows_emitted": n_article,
        "n_redirect_rows_emitted": n_redir_kept,
        "n_table_rows": len(out_rows),
        "n_unique_ur_titles": len({r["ur_title"] for r in out_rows}),
        "n_unique_en_titles": len({r["en_title"] for r in out_rows}),
        "sample_seed": SAMPLE_SEED,
        "sample_n": len(sample),
        "manual_curation": False,
        "query_benchmark_used": False,
        "csv_path": "artifacts/bilingual_titles.csv",
        "csv_sha256": sha256_file(csv_path),
        "csv_bytes": os.path.getsize(csv_path),
    }
    with open(os.path.join(ART, "bilingual_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ART, "sample20.json"), "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: summary[k] for k in ("n_table_rows", "csv_sha256", "csv_bytes")}, indent=2), flush=True)
    return summary


def main() -> int:
    os.makedirs(ART, exist_ok=True)
    paths = {}
    hashes = {}
    sizes = {}
    for name in FILES:
        key = name.split("-")[-1].replace(".sql.gz", "")
        dest = download(name)
        paths[key] = dest
        hashes[name] = sha256_file(dest)
        sizes[name] = os.path.getsize(dest)
        print(f"SHA-256 {name} {hashes[name]}", flush=True)
    manifest = {
        "dump_date": DUMP_DATE,
        "base_url": BASE,
        "user_agent": USER_AGENT,
        "downloaded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": {
            name: {
                "url": BASE + name,
                "path": f"dumps/{name}",
                "bytes": sizes[name],
                "sha256": hashes[name],
            }
            for name in FILES
        },
    }
    with open(os.path.join(ART, "download_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    build(paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
