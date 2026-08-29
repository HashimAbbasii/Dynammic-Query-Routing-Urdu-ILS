# PHASE 5 FINAL REPORT

Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.  
**H001–H040 unused.** SVM not retrained. No RRF, score fusion, or reranker as a system.  
Known-item P@5 = 0.2 × Hit@5. QTRN Roman queries are Phase 2 `title_roman` strings (dictionary reverse + naive character romanization), not naturalistic chat Roman Urdu.

Selection: DEV `roman_urdu` only. Primary Hit@5, secondary nDCG@5, latency tie-break. Frozen before internal_val confirmation in `artifacts/selected_method.json`.

---

## 1. Roman Urdu baseline

How many Roman queries? **23**  
DEV: 13 · INTERNAL_VAL: 10

Ids: QTRN_016, QTRN_031, QTRN_034, QTRN_038, QTRN_056, QTRN_067, QTRN_070, QTRN_088, QTRN_094, QTRN_106, QTRN_128, QTRN_133, QTRN_139, QTRN_155, QTRN_175, QTRN_191, QTRN_196, QTRN_205, QTRN_211, QTRN_214, QTRN_220, QTRN_229, QTRN_232

Raw BM25 Hit@5 (Method A, all Roman): **0.0** (0/23)

Dense baseline Hit@5 (Phase 4B Headline, same ids): **0.0435** (1/23)

Matches Phase 4B: BM25 0/23, dense ≈ 1/23.

---

## 2. Transliteration audit

Existing logic: `transliterate_roman` exact-match on `198` dictionary keys. Whitespace split, lowercase.

Queries with ≥1 substitution: **22/23**.  
Still mostly Latin after mapping: **22/23**.

What failed to convert: Phase 2 naive romanizations (`krne`, `mshorh`, stripped vowels, letter-mapped names). See `TRANSLITERATION_AUDIT.md`.

---

## 3. DEV experiment

DEV Roman n = 13.

| Method | Hit@5 | Hit@10 | nDCG@5 | MRR | Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A. Raw BM25 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0009 |
| B. Existing dictionary transliteration | 0.0 | 0.0 | 0.0 | 0.0 | 0.0073 |
| C. Rule-based transliteration | 1.0 | 1.0 | 0.8004 | 0.7359 | 0.0052 |
| D. Romanized-document BM25 | 1.0 | 1.0 | 0.9331 | 0.9103 | 0.0065 |

Method E (analysis, not selectable): union C∪D DEV Hit@5 = **1.0** (overlap 1.0).

Method D index: build **100.6 s** (tokenize+romanize 66.3 s + BM25 34.3 s). In-memory postings **116.1 MB**. Estimated romanized text **147.7 MB**. Full corpus (111,860 docs), not source-only.

**Selected on DEV (before internal_val): Method D — Romanized-document BM25.**

C and D tied primary Hit@5 = 1.0 on DEV. Secondary nDCG@5 chose D (0.9331 vs 0.8004). Latency was not used. The method was frozen in `artifacts/selected_method.json` before internal_val was interpreted.

---

## 4. INTERNAL_VAL confirmation

Selected method: **D**

| Split | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| DEV | 1.0 | 0.9331 | 0.9103 |
| INTERNAL_VAL | 0.9 | 0.8131 | 0.7944 |

Did the improvement generalize? **Yes.** DEV 13/13 Hit@5 → internal_val 9/10 Hit@5 (the miss is rank **9**, so Hit@10 = 1.0). Absolute Hit@5 stayed far above the 0.0 baseline. The method was not modified after internal_val.

C was not selected. A post-hoc diagnostic (not used for selection): C would have been 6/10 Hit@5 on internal_val. The nDCG@5 tie-break on DEV picked the method that also held up better on val.

---

## 5. Roman Urdu improvement

Baseline Method A (all Roman): Hit@5 **0.0**

Selected method (all Roman, diagnostic pool): Hit@5 **0.9565**

Absolute improvement: **0.9565**

Recovered query count (A miss → selected Hit@5): **22**

Still missed by selected: **1**

All methods miss: **1**

---

## 6. Urdu regression check

Urdu BM25 baseline (n=46): Hit@5 **0.913**, nDCG@5 **0.8676**, MRR **0.8592**

Script-aware routing (Urdu → Urdu BM25): Hit@5 **0.913**, nDCG@5 **0.8676**, MRR **0.8592**

Any regression? **No.** The Urdu path is the same index and the same raw query.

---

## 7. Script detection

URDU: **46**  
ROMAN: **23**  
MIXED: **9**  
OTHER: **0**

Ambiguous: **0 detector errors** (78/78 agreement with oracle labels).  
The 9 MIXED queries are mixed-script by generation (`Pakistan news update` suffix), not detector failures. See `SCRIPT_DETECTION_REPORT.md`.

---

## 8. Combined routing result

n=78. Deployable mixed policy: Urdu BM25 (no fusion).

| System | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| Headline | 0.4487 | 0.4009 | 0.3885 |
| Raw BM25 | 0.5897 | 0.5509 | 0.5434 |
| Script-aware retrieval | 0.8718 | 0.8107 | 0.797 |

Mixed path 1 (Urdu BM25) Hit@5 0.4444.  
Mixed path 2 (selected Roman method) Hit@5 0.4444.  
Mixed union oracle Hit@5 0.4444 (not deployable).

---

## 9. Oracle headroom

| Ceiling | Hit@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: |
| Urdu BM25 + selected Roman | 0.8718 | 0.8107 | 0.797 |
| Headline + script-aware | 0.9103 | 0.8703 | 0.8615 |
| Headline + Urdu BM25 + selected + mixed roman path | 0.9103 | 0.8712 | 0.8626 |

Remaining all-fail vs that last ceiling (Hit@5 miss): **7** queries.

Roman-only Method E union C∪D Hit@5: **0.9565** (22/23).

These ceilings are **not** a deployed system.

---

## 10. Main finding

The Phase 4B Roman collapse (0/23 BM25, 1/23 dense) was **script mismatch**. It is largely solvable with a **second BM25 index** whose documents are romanized with the same Phase 2 `_CHAR_ROMAN` + reverse-dictionary procedure that created the `title_roman` queries.

- Existing dictionary B: still **0/13** DEV Hit@5. It does not rewrite naive romanizations.
- Rule-based inverse C: **13/13** DEV Hit@5 but weaker nDCG@5 (lossy letter collisions) and a harder internal_val drop if it had been chosen.
- Romanized-document D: **13/13** DEV, **9/10** internal_val. The one miss (QTRN_031) is rank 9 with high token overlap — a ranking/competition miss, not a remaining script miss.
- Script-aware routing on n=78: Hit@5 **0.5897 → 0.8718** with **no Urdu regression** (still 0.913).
- Mixed two-view union adds **nothing** (0.4444 = 0.4444).

Caveat: these 23 strings are Phase 2 `title_roman` artifacts, not chat-style Roman Urdu. Method D is the right fix for **this** distribution. It is not proof that a 198-word dictionary will serve naturalistic `kya`/`kia` queries.

After this experiment the remaining bottleneck on n=78 is **not Roman script**. It is the leftover Urdu/mixed known-item misses (script-aware misses 10/78; Headline uniquely recovers 3 of them; 7 remain even as an oracle).

---

## 11. What should NOT be done next

- Do **not** open H001–H040.
- Do **not** retrain the SVM for script detection (Unicode already matches all 78 oracle labels).
- Do **not** build RRF / score fusion — Method E union equals D on Roman, and mixed union equals Urdu BM25 alone.
- Do **not** add query-specific dictionary rows for `QTRN_*` spellings.
- Do **not** switch from D to C after seeing internal_val.
- Do **not** retune BM25 `k1`/`b` on n=78.
- Do **not** start long-context e5 indexing on this CPU (Phase 4B 4-hour gate failed).
- Do **not** treat 0.8718 known-item Hit@5 on title-derived QTRN as 80% P@5 under human judgments.
- Do **not** keep expanding the Roman dictionary as the main Roman strategy for this eval pool.

---

## 12. Recommended Phase 6

**One experiment:** freeze script-aware lexical routing (URDU/MIXED → Urdu BM25, ROMAN → Method D) and run a **residual known-item diagnosis** on the 10 n=78 misses — 1 Roman (rank 9) plus Urdu/mixed — using only DEV/internal_val source headlines already in the oracle files.

Goal: decide whether those misses are “wrong room” (Headline uniquely has 3 of them) or “source not lexically recoverable”. Do **not** implement RRF until that catalog shows a fusion-shaped leftover. Do **not** use H001–H040.

STOP.
