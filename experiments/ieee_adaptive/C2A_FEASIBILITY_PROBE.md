# C2a Feasibility Probe

**Institutional Latin acronym / English institution phrase ↔ Urdu descriptive alias**

**Status:** complete  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Timestamp (local):** 2026-09-22  
**Decision:** **NO-GO**

C1 query-only adaptive routing remains **CLOSED** and was not revived.

---

## 1. Objective

Answer:

> Is the institutional Latin acronym / English institution phrase ↔ Urdu descriptive institutional alias failure mechanism **sufficiently prevalent** and **sufficiently addressable** among Program B candidate-generation all-misses to justify a new IEEE-oriented method?

Pre-declared primary prevalence threshold (from C2): **≥ 8 confirmed** institutional-alias misses among the **31** BM25∪NG3∪Dense Hit@50 all-miss queries.

---

## 2. Protocol

1. **Operational definition written before gold inspection** (§5).  
2. Identify the 31 all-miss queries from frozen Phase 13 scoring (TRAIN+DEV only).  
3. **Query-first** preliminary scan for institutional surfaces (acronyms / English institution phrases).  
4. Assign labels with the pre-declared scheme (§6 of master prompt / §5–6 below).  
5. **Only then** inspect TRAIN/DEV gold article text for candidate A cases; set `MECHANISM_CONFIRMED`.  
6. Count confirmed A among 31; compute n=80 institutional-surface prevalence.  
7. Non-gold resource / retrieval probe **only if** prevalence ≥ 8 (threshold failed → probe not used to chase GO).  
8. Literature sanity check for acronym/org-alias prior art.  
9. Decision **GO** or **NO-GO** only.

**Blinding limitation (documented):** Query text and gold `source_doc_id` live in the same Phase 13 CSV. Classification used **query text first** for preliminary institutional-surface detection and non-A labels; gold **Headline/News Text** were opened only for verification of the 10 query-side institutional candidates and for completing the annotation table. Gold document IDs are **not** exported in the public annotation CSV.

---

## 3. TEST Isolation

```text
TEST_CONTENT_ACCESSED = FALSE
```

No TEST query files, golds, or retrieval outputs were opened.

---

## 4. Program A/B Integrity

| Check | Status |
| --- | --- |
| Program A modified | **No** |
| Program B modified | **No** |
| Frozen metrics overwritten | **No** |
| C1 routing revived | **No** |
| Retrieval parameters tuned | **No** |

Input evidence: `experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv`  
SHA-256: `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66`  
Corpus rows for gold verification only: `data/clean_articles.csv` (TRAIN/DEV golds referenced by Phase 13).

---

## 5. Operational Definition

A query is **INSTITUTIONAL_ALIAS (A)** only if **all** hold:

1. **Query-side:** Roman/Latin institutional identifier — acronym/initialism **or** English institutional phrase (e.g. `CPEC`, `FBR`, `ADB`, `SBP`, `IMF`, `revenue board`, `state bank`).  
2. **Document-side:** Same institution expressed with a **substantially different Urdu descriptive / full-name** surface (e.g. `CPEC` → `اقتصادی راہداری`; `ADB` → `ایشیائی ترقیاتی بینک`), not merely the same Latin acronym repeated.  
3. **Retrieval:** Gold absent from BM25∪NG3∪Dense Top-50 (candidate-generation miss).  
4. **Distinction:** Not ordinary same-lexeme script conversion alone; not generic synonymy; not person/location/product entity alone; not pure ranking failure.

**Explicit exclusions:**

| Pattern | Label instead |
| --- | --- |
| Same English institution name in Latin query and Urdu-script loan (`state bank` ↔ `اسٹیٹ بینک`) | **D** script/orthographic |
| Latin acronym ↔ Urdu **letter-name** only (`IMF` ↔ `ئی ایم ایف`) without descriptive full name | **D** (Phase-7-like), not A |
| Person / film / app / sports team | **B** |
| Macro bilingual paraphrase without institution alias | **C** |

Labels used: **A** INSTITUTIONAL_ALIAS · **B** NON_INSTITUTIONAL_ENTITY · **C** SEMANTIC_PARAPHRASE · **D** SCRIPT_ORTHOGRAPHIC · **E** VOCABULARY · **F** CODE_MIXING · **G** OTHER · **H** UNCERTAIN.

---

## 6. Annotation Results

| Quantity | Value |
| --- | ---: |
| Total Hit@50 all-miss (BM25∪NG3∪Dense) | **31** |
| Confirmed INSTITUTIONAL_ALIAS (`MECHANISM_CONFIRMED=TRUE`) | **6** |
| Percentage of 31 | **19.4%** (6/31) |
| Pre-declared threshold | **≥ 8** |
| Threshold met? | **No** |

### Label distribution (n=31)

| Label | n |
| --- | ---: |
| A INSTITUTIONAL_ALIAS (confirmed) | 6 |
| B NON_INSTITUTIONAL_ENTITY | 18 |
| C SEMANTIC_PARAPHRASE | 2 |
| D SCRIPT_ORTHOGRAPHIC | 3 |
| E VOCABULARY | 1 |
| G OTHER | 1 |
| H UNCERTAIN | 0 |

Confirmed A IDs: **KN010, KN020, KN025, KN041, KN042, KN117**.

Artifact: `experiments/ieee_adaptive/C2A_CASE_ANNOTATIONS.csv`  
SHA-256: `8988da1adbff940ee30aa07fd36d1e788c5d2e919eba66b980beb85ed138e009`

Wilson-style intuition (not overstated): 6/31 is a real minority mechanism; interval under binomial uncertainty easily includes values below the 8/31 bar. **Do not treat 6 as “almost 8.”**

---

## 7. Case-Level Evidence

### Confirmed A (representative)

| ID | Query surface | Gold Urdu institutional surface | Why A + candidate-gen miss |
| --- | --- | --- | --- |
| KN020 | `cpec` | `اقتصادی راہداری` / China–Pakistan corridor phrasing | Latin acronym ↔ descriptive Urdu name; not in BND Top-50 |
| KN041 | `cpec` | `پاک چین اقتصادی راہداری` | Same mechanism |
| KN025 | `adb` | `ایشیائی ترقیاتی بینک` / `ایشین ڈیویلپمنٹ بینک` | Acronym ↔ descriptive bank name; Latin `ADB` absent |
| KN010 | `revenue board` | `فیڈرل بورڈ اف ریونیو` (+ `ایف بی ار`) | English institution phrase ↔ Urdu full institutional name |
| KN042 | `SBP` | `اسٹیٹ بینک` | Acronym ↔ expanded name (not letter-name `اس بی پی`) |
| KN117 | `sbp` | `اسٹیٹ بینک` | Same as KN042 |

### Important counterexamples (rejected as A)

| ID | Query surface | Why **not** confirmed A |
| --- | --- | --- |
| KN109 | `state bank` | Doc also uses `اسٹیٹ بینک` — **same English institution name**, Urdu script only → **D** |
| KN028 | `state bank` + `external debt` | Institution side is script of same EN name; miss also **VOCAB** (`غیر ملکی قرضوں`) → **C/D** |
| KN093 | `imf` | Doc uses letter-name `ئی ایم ایف` only; **no** `بین الاقوامی مالیاتی فنڈ` → **D** (Phase-7-like) |
| KN047 | `fbr` + `sindh revenue board` | Letter-name `ایف بی` + `سندھ ریونیو بورڈ` (script of same EN words) → **D/B**, not descriptive alias |

These counterexamples show why naive “any org token” counting would inflate prevalence past the honest threshold.

---

## 8. Broader n=80 Prevalence

Pre-declared detector (acronym token list + English institution phrases) on all 80 TRAIN+DEV queries:

| Quantity | n |
| --- | ---: |
| Queries with institutional surface detector fire | **10** |
| Of those, BND Hit@50 all-miss | **10** |
| Of those, any BND Hit@50 success | **0** |

All detector-positive institutional queries in this benchmark are among the 31 all-misses. That shows the **phenomenon is hard when present**, but **presence is rare** (10/80 = 12.5% by surface detector; **6/80 = 7.5%** confirmed A after gold verification).

This supports: mechanism **exists** and is **difficult**, but is **not common enough** on this n=80 set to clear the pre-declared ≥8/31 research-justification bar for a dedicated IEEE method.

---

## 9. Non-Gold Resource Probe

**Not executed as a GO-path retrieval probe** because the primary prevalence threshold failed (6 < 8).

**Addressability note (existing Program B evidence, not a new probe):** Phase 9 already tested a public Wikipedia title/redirect resource under a frozen match rule and reported **CPEC/FBR/ADB/JLO-class** absent as exact English title keys; letter-name (Phase 7) failed Quad-23 recovery. Those controlled negatives remain: even if one built a method, **off-the-shelf WP exact-title bridging is known-weak** for this niche — but that does **not** override the prevalence NO-GO.

No benchmark-specific alias dictionary was constructed from gold.

---

## 10. Feasibility Result

| Criterion | Required | Observed | Pass? |
| --- | --- | --- | --- |
| Confirmed A among 31 all-miss | ≥ 8 | **6** | **Fail** |
| Distinguishable from script-gap / letter-name / same-EN-name script | Yes | Yes for the 6; 4 near-misses correctly rejected | Pass (definition) |
| Non-gold resource shows meaningful addressability | Required for GO | Not demonstrated; WP/letter-name prior negatives | Fail / unmet |
| Isolated Hit@50 +3 probe without Hybrid regression | Optional if prevalent | **Not run** (prevalence fail) | N/A |

**Overall feasibility for authorizing a new method study:** **negative**.

---

## 11. Literature Sanity Check

| Work | Acronyms | Urdu | Roman Urdu | Cross-script | Institution aliases | Candidate generation | Main overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Jacquet et al. LREC 2016 — cross-lingual MW entity↔acronym linking | Yes | Unclear/multi | No | Yes | Yes (multilingual expansions) | Resource building | **Strong overlap** with alias inventories |
| Wentland et al. LREC 2008 — multilingual NE resource | Yes | Possible via WP | No | Yes | Yes | NE translation/translit | Adjacent CLIR NE |
| Name variants / EDL (LDK 2019 etc.) | Yes | General | No | Multilingual | Org name variants | Linking features | Adjacent |
| Gupta SIGIR 2014 MSIR | Spelling | No | No | Yes | No (term variants) | QE | Script/spelling, not institutional alias |
| Chari et al. SIGIR 2025 transliterate-train | No | No | No | Yes | No | Neural script gap | Different mechanism |
| Phase 7/9 ULTRA | Yes | Yes | Yes | Yes | Attempted WP/letter-name | Yes | Empirical negatives |
| Butt et al. 2025 RU IR | Limited | No (Roman corpus) | Yes | Pipeline | No | BM25+rerank | Different setting |

**Wording:** Cross-lingual acronym↔expansion resources and org-name variant linking are **already studied**. No claim of “never done.” For Roman Urdu → Urdu **news** IR specifically, no identical packaged method was identified in the searched set — but given prevalence failure, that residual niche is **too small here** to justify a method paper.

---

## 12. What Is Already Known

- Candidate-generation dominates Program B misses (31/80 BND Top-50 misses).  
- ROOM / ENT / VOCAB structure from R2-B0.  
- Letter-name and Wikipedia title expansion do not solve institutional hard cases (Phases 7/9/11).  
- Query-only expert routing fails (C1).  
- Script-gap neural repair is published (Chari 2025).  
- Multilingual acronym↔expansion linking exists (Jacquet et al.).

---

## 13. What Remains Potentially Novel

A **narrow** Roman-Urdu-news institutional-alias candidate-generation method remains *conceptually* distinct from pure script-gap work — but on **this** evidence base it is **not prevalent enough** (6 confirmed / 31) to clear the pre-declared bar. Residual novelty without prevalence is insufficient for GO.

---

## 14. Decision

# **NO-GO**

Reasons (any one would suffice; several apply):

1. Confirmed institutional-alias all-misses = **6 < 8**.  
2. Several tempting near-misses are **script conversion** or **letter-name**, not descriptive alias — inflating them would violate the protocol.  
3. Non-gold addressability for a method was **not** established; prior WP/letter-name probes were negative.  
4. Mechanism is real but **rare** on n=80 (6–10 queries depending on strictness).

---

## 15. If GO: Future Research Question

**N/A — decision is NO-GO.** No method-development experiment is authorized from C2a.

---

## 16. Limitations

- n=31 / n=80 is small; ExactSource known-item setting.  
- Gold-informed verification required for document-side alias confirmation (inherent to mechanism definition).  
- Institutional surface detector is a fixed list + phrase regex — may miss rare orgs; may include borderline sports acronyms (IPL treated as **B**, not A).  
- Strict exclusion of letter-name-only and same-EN-name script cases reduces count; a looser definition could raise counts but would **collapse into Phase 7 / script-gap**, which C2 rejected as novelty.  
- No TEST generalization.

---

## 17. Reproducibility / Hashes

| Item | Value |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Phase 13 CSV SHA-256 | `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66` |
| Annotations CSV | `experiments/ieee_adaptive/C2A_CASE_ANNOTATIONS.csv` |
| Annotations SHA-256 | `8988da1adbff940ee30aa07fd36d1e788c5d2e919eba66b980beb85ed138e009` |
| This report | `experiments/ieee_adaptive/C2A_FEASIBILITY_PROBE.md` |
| Program A modified | No |
| Program B modified | No |
| TEST accessed | No |

---

**End of C2a.** Stop. Do not invent another method from this negative gate.
