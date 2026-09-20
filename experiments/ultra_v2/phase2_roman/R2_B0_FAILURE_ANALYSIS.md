# R2-B0 failure analysis — final classification

**Status:** PASS (diagnosis complete)  
**Date:** 2026-09-11  
**n:** 47 Hit@5 failures on Roman KN TRAIN+DEV  
**TEST was not accessed.** R2-1 was not implemented. Baseline `artifacts/r2_b0_*` files were not modified.

The counters `sibling_any=8`, `near_any=45`, `zero_content_overlap=26`, `zero_overlap=2` are **overlap statistics only**. They are not labels. This document assigns one primary category per failure.

---

## Mechanical side (MISS vs RANK)

| miss_side | Meaning | Count |
| --- | --- | ---: |
| MISS | gold absent from Top-50 | **45** |
| RANK | gold in Top-50, not Top-5 | **2** |
| **Total Hit@5 failures** | | **47** |

RANK IDs: KN014 (train, gold 79754, rank 44), KN048 (dev, gold 20073, rank 42).

The 45 MISS-side IDs still receive a **diagnostic** primary (ROOM / VOCAB / ENT / NEIGH). That does not move them to RANK. Primary **RANK** is used only for the two in-Top-50 cases.

---

## Why the preliminary counters are not the decision

| Counter | What it measured | Why it is not NORM |
| --- | --- | --- |
| sibling_any = 8 | Query token in a frozen dict family whose *other* key appears in gold | All 8 are `kya` (query) vs `kiya` (gold). Function word کیا. Content tokens still fail. **Not primary NORM.** |
| near_any = 45 | Some content token has edit-distance 1–2 to *some* gold token | Mostly noise (`teen`↔`mein`) or Method D character-table forms (`world`↔`orld`). Not closed aliases. **ROOM or ENT, not NORM.** |
| zero_content_overlap = 26 | No non-function query token in gold romanization | Candidate-generation gap. Spelling fold of `kya` cannot create those content tokens. |
| zero_overlap = 2 | KN001, KN017 | KN001 ROOM; KN017 VOCAB. No shared tokens to canonicalize. |

---

## Sibling audit (all 8) — NORM rejected

NORM requires: query form, gold form, systematic variation, **and** plausible BM25 overlap gain on the *information need*.

| ID | miss_side | Query form | Gold form | Variation | Why not primary NORM | Assigned primary |
| --- | --- | --- | --- | --- | --- | --- |
| KN010 | MISS | `kya` | `kiya` | dict siblings for کیا | Need is benami/FBR (`aif bi ar`, `bord`). Adding `kiya` does not recover those content tokens. | ROOM |
| KN014 | RANK | `kya` | `kiya` | same | Already in Top-50 at 44 via `mobile`/`hone`. Fail Top-5 is `charge`/`ghalti` vs `charj`/`ojh`. | RANK |
| KN021 | MISS | `kya` | `kiya` | same | Need is jungle/book (`jngl`/`bk`). | ROOM |
| KN025 | MISS | `kya` | `kiya` | same | Need is ADB (`ae di bi`) / country director. | ROOM |
| KN037 | MISS | `kya` | `kiya` | same | Need is photo app (`foto`/`chhre`). | ROOM |
| KN041 | MISS | `kya` | `kiya` | same | Need is caretaker/CPEC paraphrase, not کیا. | VOCAB |
| KN046 | MISS | `kya` | `kiya` | same | Need is ML-1/railway vs `arbon dollar projikt`. | VOCAB |
| KN054 | MISS | `kya` | `kiya` | same | Need is kangana/momina (`kngna`/`momnh`). | ENT |

**Primary NORM count = 0.** No other dictionary-sibling pattern (`aj`/`aaj`, `ny`/`ne`, `hy`/`hai`) was the dominant miss driver.

Canonicalizing `kya`→`kiya` would add a high-df function word. That is not a recurring content-canonicalization hypothesis for R2-1.

---

## Primary taxonomy (exactly one label; n=47)

| Category | Count | Percentage of 47 failures |
| --- | ---: | ---: |
| QAMB | 0 | 0.0% |
| ROOM | 19 | 40.4% |
| NORM | 0 | 0.0% |
| VOCAB | 9 | 19.1% |
| ENT | 16 | 34.0% |
| NEIGH | 1 | 2.1% |
| MISS | 0 | 0.0% |
| RANK | 2 | 4.3% |
| TEMP | 0 | 0.0% |
| **TOTAL** | **47** | **100%** |

`19 + 0 + 9 + 16 + 1 + 0 + 2 + 0 + 0 = 47`.

Generic diagnostic **MISS** is unused: every MISS-side row has a more specific supported label. Mechanical **miss_side=MISS** remains 45.

---

## TRAIN vs DEV (descriptive)

| Category | TRAIN failures (30) | DEV failures (17) |
| --- | ---: | ---: |
| QAMB | 0 | 0 |
| ROOM | 12 | 7 |
| NORM | 0 | 0 |
| VOCAB | 5 | 4 |
| ENT | 11 | 5 |
| NEIGH | 1 | 0 |
| MISS | 0 | 0 |
| RANK | 1 | 1 |
| TEMP | 0 | 0 |
| miss_side MISS | 29 | 16 |
| miss_side RANK | 1 | 1 |

ROOM + ENT dominate **both** splits. No TRAIN-only spelling pattern appears on DEV.

---

## ROOM (19, all miss_side=MISS)

Query in English or chat Roman; gold Method D tokens are `naive_roman_word` / letter-split Urdu.

Examples (not R2-1 mappings): `world`↔`orld` (KN001, KN013, KN050); `title`↔`taitl` (KN008); `kolkata`↔`kolkth` (KN006); `kahani`↔`khani` (KN018); `gmail`↔`ji mil` (KN051); `fbr`↔`aif bi ar` (KN047); `psl`↔`pi ais ail` (KN049).

This is index representation, not a 198-key alias list.

---

## ENT (16, all miss_side=MISS)

Distinctive name does not match the indexed romanization.

- Person: KN016, KN019, KN022, KN026, KN029, KN030, KN032, KN033, KN034, KN035, KN054  
- Product: KN040, KN043, KN052, KN053  
- Event: KN002  

---

## VOCAB (9, all miss_side=MISS)

Different lexemes, not spelling of the same token. KN017 (zero overlap, English product vs Urdu paraphrase); KN015 puzzle vs riazi soal; KN020/KN041 English CPEC vs Urdu راہداری; KN028/KN042 English macro terms; KN036 oil/gas/output; KN039 sold out; KN046 railway/ML-1 paraphrase.

---

## NEIGH (1, miss_side=MISS)

KN005: Iran–US equities rebound vs gold Pakistan exchange open. Neighbor topic, not a spelling pair.

---

## RANK (2)

**KN014** rank 44: in Top-50 via `mobile`/`hone`/`ki`/`hai`. Out of Top-5 because `charge`/`ghalti` ≠ `charj`/`ojh`. Ranking, not missing candidates.

**KN048** rank 42: in Top-50 via `10`/`2020`/`aur`. `samsung`≠`sam sng`. Ranking among 2020 phone stories.

---

## NORM patterns

**No sufficiently consistent normalization pattern was established from R2-B0.**

The only repeated dictionary sibling is `kya`→`kiya` (n=8), rejected as primary (table above). Character-table near-forms are ROOM/ENT, not closed canonicalization.

---

## Interpretation

R2-B0 misses because Method D indexes **title_roman-like** Latin while v2 queries are English or chat Roman. Structure is ROOM + ENT + VOCAB. Reverse-dict sibling fold (R2-1 as audited) does not have a content-bearing, recurring canonicalization problem to test.

---

## Decision

**R2-1 NOT YET JUSTIFIED**

Do not implement R2-1.

---

## Safety

- TEST was never accessed; TEST queries were not loaded; no TEST retrieval  
- M0, Phase 12, PLOS, historical qrels/results unchanged  
- `artifacts/r2_b0_per_query.csv` / `r2_b0_summary.json` not modified  
- Dictionary not modified; no BM25 retune; no R2-1 code executed  

Per-row labels: `R2_B0_FAILURE_ANALYSIS.csv` (`miss_side` + `primary`; 45 MISS + 2 RANK).
