# Phase 3B Evaluation Set — Line-Ending Normalization Note

This note documents a byte-level discrepancy discovered between the
originally recorded freeze-time MD5 hash of
`validate/phase3/phase3_evaluation_set.csv` and the MD5 of the file as
committed to GitHub. It exists purely for provenance/audit clarity and
does **not** modify the evaluation CSV, its metadata JSON, or any
frozen data.

## 1. Original freeze-time representation

- Encoding: UTF-8 with BOM
- Line endings: CRLF
- MD5: `b442ab2ffbd85a98734d49e62450aaa9`

This is the hash recorded in `phase3_evaluation_set_metadata.json` at
freeze time (`freeze_timestamp_utc: 2026-08-16T11:42:15.991961+00:00`).

## 2. GitHub commit representation

- Commit: `d54d6aa`
- Encoding: UTF-8 with BOM
- Line endings: LF
- MD5: `faef0d264ec2915baf1f3948a9b78e66`

Verified directly from the committed Git blob (`git cat-file -p
d54d6aa:validate/phase3/phase3_evaluation_set.csv`), not from a local
working-tree checkout, so this MD5 reflects exactly what is stored in
the repository at that commit.

## 3. Root cause

The repository's `.gitattributes` (present since the initial commit,
unchanged at `d54d6aa`) contains:

```
* text=auto
```

This blanket rule instructs Git to auto-detect text files and
normalize their line endings to LF when storing blobs in the
repository. It applied to this CSV on `git add`/commit, converting its
original CRLF line endings to LF. This normalization is independent of
any `core.autocrlf` or `core.eol` local Git configuration (neither is
set in this repository) — it is enforced by `.gitattributes` at the
repository level.

## 4. Content verification

The discrepancy is **byte-level line-ending normalization only**. It
is not a content change. The following was independently verified
against the committed CSV (commit `d54d6aa`) and matches the frozen
specification exactly:

- Total rows: 60 (P3_001–P3_060, exact sequence, no gaps or duplicates)
- Columns: 13
- No duplicate queries
- word_count column consistent with `len(query.split())` for all 60 rows
- Bucket distribution: 2-4w=12, 5-6w=20, 7-9w=12, 10-19w=16
- Script distribution: urdu=30, roman=30
- Primary set (n=50) gold labels: SHORT=16, LONG=34
- Secondary set (n=10): all gold_label fields blank/null, ambiguous=True

No query, content, or label modification occurred as a result of this
discrepancy. It is confirmed to be an encoding-level artifact of the
Git storage/commit process, not a data-level change.

## 5. Commit status

Commit `d54d6aa` remains unchanged and is not being rewritten,
amended, or force-pushed as part of this documentation. The committed
CSV and its content stand as-is.

## 6. How to interpret the two MD5 values

- `b442ab2ffbd85a98734d49e62450aaa9` — the **historical freeze-time
  byte hash**, computed on the original UTF-8 BOM + CRLF bytes at the
  moment the Phase 3B evaluation set was frozen. This value remains
  the record of what was frozen and is not being replaced or
  superseded.
- `faef0d264ec2915baf1f3948a9b78e66` — the **GitHub repository
  representation hash**, identifying the UTF-8 BOM + LF bytes as
  normalized and stored by Git at commit `d54d6aa`. This value
  identifies the file as it actually exists in the repository today.

Both hashes are valid records of the same underlying content, computed
over two different byte-level line-ending representations.

## 7. Reproducibility warning

Future byte-level MD5 comparisons involving this file (or any other
CSV in this repository subject to `* text=auto`) must specify the
exact encoding and line-ending representation being hashed (UTF-8 BOM
+ CRLF vs. UTF-8 BOM + LF), since a plain MD5-equality check alone
cannot distinguish "content changed" from "line endings normalized by
Git." Content-level verification — rather than raw MD5 equality alone
— should rely on the committed CSV together with the documented schema
and validation checks listed in Section 4 above (row count, column
count, ID sequence, word_count consistency, bucket/script/label
distributions).
