# Module 2 R-dev ablation results

Pre-specified lexical retrieval candidates. M0 baseline from frozen artifacts.  
No Module 1 stacking. No embeddings. No post-hoc parameter changes.  
R-dev development / ablation only — **no generalization claim**.

---

## A. M0 frozen baseline

| Track | Metric | Result |
| --- | --- | --- |
| KI | ExactSource Hit@5 | 19/50 = 38.00% |
| NAT | Success@5 (frozen M0-pool qrels) | 12/50 = 24.00% |

**NAT pool limitation:** `qrels_r_dev.csv` labels **M0 Top-5 documents only**. Newly retrieved documents outside that pool cannot receive NAT credit. R080 remains in the NAT denominator (zero M0 hits).

---

## B. M2-A results

**Configuration:** `char_wb` 3-gram tokens via `sklearn.TfidfVectorizer(analyzer="char_wb", ngram_range=(3,3)).build_analyzer()`; scored with `run_phase5.BM25` **k1=1.5**, **b=0.75**; M0 routing; Method D document romanization unchanged; raw query (no M1).

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 = 38.0% | 12/50 = 24.0% |
| M2-A | 20/50 = 40.0% | 8/50 = 16.0% |
| Delta (hits) | **+1** | **-4** |

KI source-rank distribution (M2-A): `1-5: 20`, `6-10: 3`, `11-50: 12`, `miss_or_absent: 15`  
KI source-rank distribution (M0): `1-5: 19`, `6-10: 4`, `11-50: 8`, `miss_or_absent: 19`

KI improved queries: R001, R018, R041, R042  
KI worsened queries: R023, R027, R049  
NAT improved: *(none)*  
NAT worsened: R051, R074, R087, R096  

Ranking lists changed vs M0: **100 / 100**

---

## C. M2-B results

**Configuration:** Word BM25 on `Headline` and `News Text` separately; **RRF k=60**; BM25 **k1=1.5**, **b=0.75**; per-channel Top-50 then fuse to Top-50; tie-break: higher RRF then lower `doc_id`; M0 routing; Method D unchanged; raw query (no M1).

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 = 38.0% | 12/50 = 24.0% |
| M2-B | 18/50 = 36.0% | 8/50 = 16.0% |
| Delta (hits) | **-1** | **-4** |

KI source-rank distribution (M2-B): `1-5: 18`, `6-10: 6`, `11-50: 7`, `miss_or_absent: 19`  
KI source-rank distribution (M0): `1-5: 19`, `6-10: 4`, `11-50: 8`, `miss_or_absent: 19`

KI improved queries: R018, R035  
KI worsened queries: R013, R014, R027  
NAT improved: *(none)*  
NAT worsened: R053, R061, R074, R087  

Ranking lists changed vs M0: **98 / 100**

---

## D. KI comparison

| Candidate | Overall | URDU | ROMAN | MIXED | Δ hits vs M0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| M0 | 19/50 | 11/17 | 1/5 | 7/28 | — |
| M2-A | 20/50 | 13/17 | 1/5 | 6/28 | +1 |
| M2-B | 18/50 | 10/17 | 1/5 | 7/28 | −1 |

---

## E. NAT comparison (frozen M0-pool qrels)

| Candidate | Overall | URDU | ROMAN | MIXED | Δ hits vs M0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| M0 | 12/50 | 1/1 | 7/37 | 4/12 | — |
| M2-A | 8/50 | 1/1 | 3/37 | 4/12 | −4 |
| M2-B | 8/50 | 1/1 | 5/37 | 2/12 | −4 |

Script labels use frozen M0 `detect_script` (R080 included via detector fallback; NAT ROMAN n=37).

---

## F. Script-stratified comparison

Same numbers as tables D–E. Guardrail-relevant deltas:

| Stratum | M2-A Δ hits | M2-B Δ hits |
| --- | ---: | ---: |
| KI URDU | +2 | −1 |
| KI MIXED | −1 | 0 |
| KI ROMAN | 0 | 0 |
| NAT URDU | 0 | 0 |
| NAT MIXED | 0 | −2 |
| NAT ROMAN | −4 | −2 |

---

## G. Improved / worsened / unchanged

| Candidate | KI improved | KI worsened | KI unchanged | NAT improved | NAT worsened | NAT unchanged |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M2-A | 4 | 3 | 43 | 0 | 4 | 46 |
| M2-B | 2 | 3 | 45 | 0 | 4 | 46 |

---

## H. Ranking-change analysis

| Candidate | Ranking lists changed vs M0 |
| --- | ---: |
| M2-A | 100 / 100 |
| M2-B | 98 / 100 |

Both candidates substantially reorder M0 lists (representation/fusion change is active, not a no-op).

---

## I. Regression analysis

### M2-A

- Aggregate KI **+1**, but KI MIXED **−1** (7/28 → 6/28).
- NAT overall **−4**, concentrated in NAT ROMAN (7/37 → 3/37).
- URDU KI improved (+2); URDU NAT unchanged.
- **Not** an unconditional improvement under the pre-registered guardrails.

### M2-B

- Aggregate KI **−1** (URDU KI −1; MIXED KI unchanged).
- NAT overall **−4** (ROMAN −2, MIXED −2).
- **Not** promising under the pre-specified configuration.

---

## J. Interpretation

1. **M2-A** changes the lexical representation enough to move all 100 rankings. Net KI gain is small (+1) and offset by a MIXED KI loss and a clear NAT regression under frozen pool qrels (partly expected when Top-5 leaves the labeled M0 pool).
2. **M2-B** does not improve KI; headline/body RRF (k=60) hurts slightly overall and regresses NAT MIXED/ROMAN.
3. Neither candidate supports promoting a new official system from R-dev alone.
4. NAT regressions must be read with the **pool limitation**: Success@5 cannot credit new unlabeled documents.

---

## K. Scientific decision

- **M2-A:** Aggregate KI +1 but **not** an unconditional improvement (MIXED KI regression; material NAT regression). **Not selected** as a frozen replacement for M0 on the basis of this ablation.
- **M2-B:** Null/negative on KI and NAT under the pre-specified configuration. **Not selected.**
- **Module 2 lexical candidates (M2-A, M2-B) do not clear the guardrailed success criterion on R-dev.**
- Do **not** invent M2-C/D, combine M2-A+M2-B, stack M1, or move to neural retrieval without a new pre-registration.
- Do **not** claim future unseen performance.

Future work (not run): only if separately pre-registered — e.g. identity/date features for P1, or a new NAT annotation protocol if a candidate is frozen for usefulness measurement beyond the M0 pool.
