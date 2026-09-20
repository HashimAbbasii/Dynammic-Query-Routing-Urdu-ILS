# ULTRA v2 Phase 9 — Bilingual Wikipedia title expansion (query-side)

**Document type:** pre-registration / controlled design  
**Experiment ID:** PHASE9-WPTITLES  
**Directory:** `experiments/ultra_v2/phase9_entity_resource/`  
**Branch:** `research/ultra-v2-strengthening`  
**Timestamp (UTC, written after resource build, before any retrieval scoring):** `2026-09-15T18:30:00Z`

This file must not be silently rewritten after Phase-9 scores are observed.

Phase 2–8 artifacts stay frozen. M0 / `run_phase5.py` stay read-only (import at execution time only). No TEST. No live Wikipedia API. No Wikidata `wb_items_per_site` dump. No document re-index.

**Status: DESIGN FROZEN — RETRIEVAL NOT EXECUTED.**

---

## 1. Scientific question / hypothesis

**H1:** A query-independent Urdu↔English Wikipedia title/redirect table can recover ExactSource golds that frozen Method-D BM25, dense e5-small, R2-NG3, and 2-way hybrid **all miss**, by matching Roman query token n-grams to English Wikipedia titles and adding Method-D romanizations of the linked Urdu titles/redirects as extra query tokens on the Method-D BM25 index.

**H0:** The expansion does not put any of the frozen 23 four-way misses into Top-50, and/or it mainly injects noise that regresses existing Method-D successes.

These hypotheses will not be changed after seeing scores.

This is **not** entity linking, NER, or Wikidata typing. It is bilingual **title aliasing** that Wikipedia editors already encoded.

---

## 2. Resource provenance (built query-independently)

Dated dump folder (not `latest`): **`https://dumps.wikimedia.org/urwiki/20260901/`**  
Licence to attribute: Wikipedia **CC BY-SA 4.0**.  
User-Agent used for download: `ULTRA-v2-phase9/0.1 (research; Hashim Shazad; urwiki dump fetch)`  
Builder: `build_bilingual_table.py`  
Table construction **did not** read KN/NL CSVs, the 23-miss list, gold documents, or TEST.

### 2.1 Downloaded files (SHA-256 of bytes on disk)

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `urwiki-20260901-langlinks.sql.gz` | 166,442,090 | `baafc0ae92bb6f27d2568e275b9adf2dd3ff38eb220fa5772841979c44cd9b1f` |
| `urwiki-20260901-page.sql.gz` | 93,037,172 | `a08eaf932e385892501afbab0259a5b33f36e5ce954a971236a435454edf8347` |
| `urwiki-20260901-redirect.sql.gz` | 9,473,175 | `7abe39a936c53745d02c513f0814eaee4e71edfc376309da33e2b4a9fc081991` |

URLs are `https://dumps.wikimedia.org/urwiki/20260901/` plus the filename. Manifest: `artifacts/download_manifest.json`.

### 2.2 Parse rules (already applied; not to be changed for scoring)

- Keep `langlinks` rows with `ll_lang='en'` only.
- Join `page` on `ll_from = page_id`. Keep **namespace 0** only.
- Emit **article** rows: Urdu `page_title` ↔ English `ll_title` (underscores → spaces).
- Emit **redirect** rows: namespace-0 redirects whose target (one extra hop if the target is itself a redirect) has an English langlink. Urdu surface = redirect page title; English = target’s English title.
- No hand edits. No frequency cutoff. No query-derived allow/deny list.

### 2.3 Final table

| Item | Value |
| --- | --- |
| Path | `artifacts/bilingual_titles.csv` |
| Rows | **1,239,037** |
| Article rows | 500,683 |
| Redirect rows | 738,354 |
| Unique Urdu titles | 1,238,968 |
| Unique English titles | 496,463 |
| CSV bytes | 102,620,316 |
| CSV SHA-256 | `7686f02d5bb2110eb4cccc7cdbd326324e4f7fa5e4dd34d7125a76d7795cf55d` |
| Manual curation | **false** |
| Query benchmark used | **false** |

Parse diagnostics (not filters): 14,616,015 langlink rows of which 1,280,436 English; 2,988,000 page rows; 1,128,977 redirect rows.

Random sample of 20 rows (seed **20260901**, dump date, not a query id): `artifacts/sample20.json`. Examples include `Santha Rama Rau`, `Adam Christopher`, `Cushing, Iowa`, `Siddi`, `S.G. Hulme Beaman` — not selected by looking at KN IDs.

---

## 3. Frozen matching / expansion procedure (before scoring)

Population at execution: Roman KN TRAIN+DEV **n=51**. Queries are tokenized only at retrieval time. The **table is not subset using those queries**.

### 3.1 Indexes built from the CSV only

- Normalize English title: Unicode NFKC, lowercase, strip leading/trailing whitespace. (Titles in the CSV already use spaces, not underscores.)
- Map `normalized_en_title → list of Urdu titles` (all article and redirect rows). Duplicate `(ur, en)` pairs already removed at build.

### 3.2 Query match (exact, no threshold to tune)

**Case:** **insensitive.** Query tokens come from frozen M0 `tokenize`, which lowercases. English keys are NFKC + lowercase. Wikipedia `Home` and query `home` are the same key. This is the Phase 7-style risk; it is closed by the unigram filters below, not by case-sensitive matching (M0 tokens are already lowercased, so case-sensitive match is not available without changing M0).

**Spans:** every `i..j` with span length `L = j-i` in **`[1, min(8, n)]`**, `g = " ".join(tokens[i:j])` must **equal** a normalized English title. No fuzzy, prefix, substring-inside-title, stemming, or parenthesis stripping.

**Unigram (`L = 1`) allowed only if both:** *(superseded before scoring by §3.2a after the v1 match-preview NO-GO; kept here as the rejected v1 rule)*

1. token ∉ frozen `STOP_UNIGRAMS` (closed-class English function words **plus** `home`, `go`, `rise` — the magnet titles named before scoring, not from KN text);
2. **either** `len(token) ≥ 5` **or** at least one original English title for that key is an **initialism**: after removing spaces and `.`, the string matches `^[A-Z0-9]{2,6}$` and contains a letter (e.g. `FBR`, `IPL`, `U.S.` → `US`).

So `go` / `home` / `rise` / `the` cannot fire. `pakistan` can (length ≥ 5). `fbr` can only if Wikipedia stored an all-caps 2–6 character title/redirect.

**Multi-token spans (`L ≥ 2`):** no stopword test (needed for names like `will smith`). Exact full-title equality only.

**Overlaps / caps (Phase 7 noise control):**

1. Collect all spans that pass the filters.
2. Sort by span length **descending**, then left offset ascending.
3. Greedy **non-overlapping** keep (a kept span occupies its token indices; nested/shorter hits on the same tokens are dropped).
4. Keep at most **5** English titles per query.
5. Per kept English title, add at most **4** Urdu surfaces: all `article` rows first, then redirects shortest-first.

Constants live in `match_rule.py`: `MAX_SPAN=8`, `MAX_EN_HITS=5`, `MAX_UR_PER_EN=4`, `MIN_UNIGRAM_LEN=5`, `STOP_UNIGRAMS`. They will not be searched after scores.

Matching-only preview (no retrieval): `run_match_preview.py` → `artifacts/phase9_match_preview.csv`. v1 preview archived as `phase9_match_preview_v1.csv`.

### 3.2a Amendment (2026-09-17, after v1 preview, still before any retrieval)

Triggered by a design NO-GO on the v1 preview’s own match objects (wrong-sense common-noun titles; target Latin initialisms not firing). Not retuned on Hit@k.

**Issue 1 diagnosis (resource, not the `^[A-Z0-9]{2,6}$` gate):** In the frozen 1,239,037-row table, exact English titles `FBR` / `IPL` / `CPEC` / `ADB` / `JLO` have **zero** rows (case-insensitive). Compact alphanumeric forms (`f.b.r.` → `fbr`, etc.) also have **zero** rows. Those strings are **not** Urdu `page_title`s either. Full English article titles **do** exist for Asian Development Bank, China–Pakistan Economic Corridor, Indian Premier League, Jennifer Lopez. **Federal Board of Revenue does not** (only FBISE and FBR Capital Markets). Forming first-letter acronyms from multiword English titles is **rejected**: IPL/ADB/CPEC/FBR/JLO are all many-to-one collisions with unrelated people/places (16,531 colliding acronyms table-wide).

**Issue 1 correction (query-independent, aliases Wikipedia actually stored):**

- Secondary English keys: if an original English title is a 2–6 character initialism after removing spaces/dots, **and** its compact alphanumeric form is unique and does not already exist as a primary key, index that compact form. (Addresses dotted titles such as `U.S.`; does not invent missing FBR/IPL rows.)
- Urdu letter-name reverse lookup (same 26-letter public table as frozen Phase 7, copied into `match_rule.py`): for an L=1 token matching `^[a-z]{2,6}$`, build the space-joined Urdu letter names and match **the folded token sequence** of a `ur_title` (NFKC + yeh/kaf folding per token). Concatenating letter names without spaces is **forbidden** (it would equate `ای`+`کے` with the unrelated title `ایکے`). Keep **only if exactly one** English title is attached. Drop if that bundle is a disambiguation page or if the Latin token is in the common-word list / `STOP_UNIGRAMS`. This uses editor-encoded redirects such as `آئی پی ایل` → Indian Premier League. It does **not** fire when no such Urdu title exists (FBR, CPEC, ADB, JLO in this dump).

**Issue 2 correction (wrong-sense unigrams):**

1. Frozen third-party wordlist `resources/google-10000-english-no-swears.txt` (Google 10k no-swears, MIT, SHA-256 `d6b3e04f1ac30be6525d41474166c0bff28486ecd8c48dcb0ab9c7c9cc05ed86`, 9,894 lines). For L=1 English-title hits, after stripping one trailing `(…)` from the English heading, if that heading is in the list **and** the English title is not an initialism, **reject**. Not derived from KN/NL text. Frequency lists include some proper names (countries, a few brands); that is accepted as the cost of a closed general list, not patched per query.
2. Disambiguation: reject a hit if any English original matches `\(\s*disambiguation\s*\)`, or if any **article** Urdu title (or every row when there is no article row) contains `ضد ابہام` / `ضد ابهام`. The urwiki `page` SQL dump has no disambiguation flag; category/template dumps were not in Option 2. Parentheticals in titles are the available metadata.
3. L≥2 hits also use the disambiguation test; they do **not** use the 10k list (needed for names like `will smith`).

v1 overlap/caps unchanged. No BM25 until this amended rule is approved.

### 3.3 Expansion tokens

Keep every original query token.

For each matched Urdu title:

1. Tokenize the Urdu title with the same frozen `tokenize`.
2. Map each token with frozen Method D `romanize_token` (reverse-dict first key else `_CHAR_ROMAN` / `naive_roman_word`), identical to the document-side Method D path.
3. Append those Latin tokens to the query token list.

Do **not** insert Perso-Arabic tokens into the BM25 query (they would not match the romanized document index). Do **not** switch indexes via `detect_script` if expansion would make the string MIXED; **force Method D BM25** for every one of the 51 Roman KN queries, as Phase 7 did.

If a query has zero title hits, retrieve with the original tokens (Method D unchanged for that query).

### 3.4 Retrieval

| Item | Value |
| --- | --- |
| Index | Frozen Method-D roman BM25 (`phase2_roman/artifacts/_index_cache.pkl` if meta matches) |
| k1, b | 1.5, 0.75 |
| Depth | Top-50 |
| Documents | **not** reprocessed |
| Encoder / NG3 / RRF / rerank / letter-name | **forbidden** on this run |

Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`, n=111,860. Dictionary SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`.

---

## 4. Metrics

Primary (n=51): ExactSource Hit@1, Hit@5, Hit@10, Hit@50, MRR (0 if gold not in Top-50).

Secondary (not for retuning):

- Overlap of Hit@50 with frozen Method-D BM25, Dense, NG3, 2-way Hybrid (frozen CSVs; SHA gates at execution).
- Recovery of the **23** four-way misses (Phase 6 list):  
  KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN051, KN054.
- ROOM Category 1 (same 11 IDs): KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.
- Count of queries with ≥1 title hit (diagnostic).
- Distinguish MISS (gold not in Top-50) vs RANK (in Top-50, outside Top-5).

---

## 5. Decision labels (choose exactly one after the single scored run)

- `PHASE9 SUPPORTED` — expansion recovers a substantial share of the 23 four-way misses into Top-50 without destroying most existing Method-D Top-50 successes.
- `PHASE9 PARTIALLY SUPPORTED` — at least one of the 23 (or a clear title-match gold among the 51) enters Top-50, but most of the 23 remain out and/or there are important Method-D regressions.
- `PHASE9 UNSUPPORTED` — zero recoveries of the 23, or candidate generation is noise relative to frozen Method D.
- `BLOCKED` — corpus/query/CSV gate fail, cache meta mismatch, TEST access, or table SHA mismatch.

No “≥80% = success” rule. No second matching procedure after seeing scores.

---

## 6. Stop / leakage

- No TEST query files (do not list or open them)
- Do not subset the bilingual table using the 51 queries or the 23 IDs
- Do not add gazetteer rows by inspecting gold documents
- Do not re-index documents
- Do not fuse into hybrid/3-way RRF in this experiment
- Do not iterate n-gram length, parentheses-stripping, or fuzzy match after scores
- Do not commit the `.sql.gz` dumps or the 102 MB CSV; hashes above are the frozen identity

---

## 7. What this file does not authorize

Execution of retrieval. That requires an explicit go-ahead after this preregistration is hashed and confirmed.
