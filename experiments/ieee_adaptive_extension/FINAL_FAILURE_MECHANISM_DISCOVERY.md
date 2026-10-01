# FINAL FAILURE MECHANISM DISCOVERY

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-novelty-extension`  
**Scope:** Roman Urdu → Urdu-script news IR (TRAIN/DEV only)  
**TEST accessed:** NO  
**Program A/B frozen artifacts modified:** NO

---

## 1. Population comparison

| Population | n | Query character | Headline / lexical overlap | Method-D / system signal |
|---|---:|---|---|---|
| **A (n=78 known-item DEV/VAL)** | 78 | Mixed: 46 Urdu title-like, 23 `title_roman`, 9 mixed | Urdu mean coverage ≈ **0.70**; overall mean ≈ 0.48 | ExactSource Hit@5 **68/78 = 87.18%**; Roman `title_roman` ≈ **22/23** |
| **K (hard title-like)** | 40 | 28 Urdu title-like; 12 ordinary Roman-of-headline | Urdu coverage ≈ **0.99**; Roman coverage ≈ **0** | Roman Method-D ≈ **1/12** |
| **Program B naturalistic Roman** | 80 | All naturalistic Roman Urdu ExactSource | Headline overlap ≈ **0** (78/80 meta-zero) | Method-D **5/80**; Dense **20/80**; BND union Top-50 **49/80** |

**Interpretation:** High Hit@5 on A is driven by **evaluation construction**, not by a solved naturalistic Roman→Urdu bridge.

---

## 2. What explains the 87.18%?

**68/78 = 87.18% ExactSource Hit@5** on the development known-item population is valid for that population only.

Evidence:

1. **46/78** Urdu queries are title-derived / title-like with high headline lexical coverage (mean ≈ 0.70) → BM25 Urdu matching is easy (Urdu subset Hit@5 ≈ 0.913 in prior development comparators).
2. **23/78** Roman queries are **`title_roman`**, built with the **same character-table / reverse-dictionary romanization family** used for Method D document-side indexing → Method D ≈ **22/23**.
3. Therefore the 87% figure is **not** naturalistic Roman Urdu retrieval accuracy. It is an empirical clue that **matched romanization + title-derived queries** inflate Hit@5.

---

## 3. Hard-query analysis

### Population K

- Being "from a headline" is **not** sufficient for Method D success.
- Ordinary Roman-of-headline ≈ **1/12** vs `title_roman` ≈ **22/23**.
- The critical variable is **romanization alignment with Method D**, not headline provenance alone.

### Program B (n=80)

| System | Hit@5 | Hit@50 |
|---|---:|---:|
| BM25 Method-D | 5/80 | 13/80 |
| NG3 | 10/80 | 19/80 |
| Dense | 20/80 | 36/80 |
| Hybrid | 17/80 | 40/80 |
| Oracle best-of (Top-5) | 28/80 | — |
| Union BM25+NG3+Dense Top-50 | — | **49/80** |

**Candidate-generation ceiling:** 49/80 = 61.25%  
**80% target:** 64/80 → requires ≥ **15 additional unique gold documents** in the candidate pool (plus ranking success).

---

## 4. Failure decomposition (n=80)

| Status | Count | Fraction |
|---|---:|---:|
| SUCCESS (gold in some expert Top-5) | 28 | 35.0% |
| RANKING_FAILURE (gold in union Top-50, not Top-5) | 21 | 26.3% |
| CG_FAILURE (gold absent from union Top-50) | **31** | **38.8%** |

**Dominant bottleneck:** candidate generation, then ranking.

---

## 5. Multi-level mechanism analysis (TRAIN/DEV)

Automated + rule-assisted LEVEL 1–5 tagging was run on all 80 Program B queries (`run_final_mechanism_pass.py` → `FINAL_FAILURE_MECHANISM_PER_QUERY.csv`). TEST was not used.

### LEVEL 1 — Surface (CG failures, n=31)

Recurring surface tags (non-exclusive):

| Surface tag | Count in CG |
|---|---:|
| Urdu function words in Roman | 31 |
| English domain jargon untranslated | 12 |
| Latin acronym / abbrev | 9 |
| English brand token | 5 |

Surface variation alone does **not** unify the failures; most CG misses remain after accounting for function-word Romanization.

### LEVEL 2 — Linguistic interpretation (CG)

| Linguistic tag | Count in CG |
|---|---:|
| WH-question form | 17 |
| Institutional surface | 10 |
| Intent: event | 10 |
| Intent: factoid | 8 |
| Intent: explanatory | 6 |
| Explicit person name | 4 |
| Multi-entity relation | 4 |
| Underspecified referent | 3 |

Queries are often **intent-rich** (factoid/event/WH) while providing **weak linkable anchors** to Urdu news phrasing.

### LEVEL 3–4 — Bridge / CG (primary discovery)

**Suspected bridge mechanisms among 31 CG failures:**

| Suspected mechanism | Count | Prevalence in CG |
|---|---:|---:|
| `en_jargon_plus_entity_event_composition` | 6 | 19.4% |
| `institutional_descriptive_alias` | 6 | 19.4% |
| `cross_script_or_docside_entity_variant` | 5 | 16.1% |
| `en_brand_in_urdu_news_framing` | 4 | 12.9% |
| `underspecified_referent_no_linkable_surface` | 3 | 9.7% |
| `same_en_name_script_conversion` | 3 | 9.7% |
| `crosslingual_semantic_paraphrase` | 2 | 6.5% |
| `rare_vocabulary_product` | 1 | 3.2% |
| `other_or_ambiguous_need` | 1 | 3.2% |

**No single bridge mechanism accounts for ≥15/31 CG failures.**

The prior coarse label "entity/name ≈ 18" fragments into:

- English jargon composed with entity/event cues
- institutional descriptive aliases (already gated as C2/C2a)
- cross-script / document-side entity variants
- English brand tokens framed in Urdu news language
- same English name needing script conversion
- underspecified referents without a linkable surface

### LEVEL 5 — Ranking (n=21)

Among ranking failures, bridge tags are mostly:

- `heterogeneous_or_uncertain_bridge` (18)
- `en_brand_in_urdu_news_framing` (3)

Ranking failures do **not** expose a clean, new discriminator beyond "gold is weakly preferred among heterogeneous candidates"—already attacked by Dense/Hybrid/RRF/reranking (closed).

---

## 6. Dominant mechanism (honest statement)

**There is no single dominant novel bridge.**

What the data show instead:

1. **Evaluation-structure mechanism (explains 87%):** matched `title_roman` + Urdu title-like overlap.
2. **Operational bottleneck (Program B):** **heterogeneous candidate-generation bridges**, fragmented across several known IR failure types.
3. Largest individual CG cells are only **6/31** each; none meets a prevalence bar for a standalone methodological claim aimed at recovering ≥15 new golds.

### Deepest recurring pattern that is *empirically visible* but *not novel*

**Code-switched compositional mismatch:** Roman Urdu function words + English jargon/brand/acronym + entity/event intent, against Urdu-script news that expresses the same facts with different lexicalization / aliasing / framing.

This is real. It is also covered by code-switching IR, mixed-language query IR, entity-centric CS, brand/entity linking, and classical MSIR/CLIR entity handling (see novelty matrix).

---

## 7. Evidence summary

- Population stats: `POPULATION_SUMMARY.json`
- Per-query LEVEL tags: `FINAL_FAILURE_MECHANISM_PER_QUERY.csv`
- Aggregate counts: `FINAL_MECHANISM_SUMMARY.json`
- Official Hit tables: Program B frozen evaluation artifacts (not modified)
- 87% construction explanation: Phase 1 discovery + creation-method breakdown (46 Urdu + 23 `title_roman`)

---

## 8. Uncertainty

- Mechanism tags are **heuristic** (surface/lexicon/pattern-based), not gold human annotation. Confidence is higher for institutional/acronym/brand cues; lower for paraphrase vs entity-variant boundary cases.
- Counts are on **n=80 TRAIN+DEV only**; prevalence may shift on sealed TEST (not inspected).
- Theoretical coverage of summing non-closed CG cells (≈ 6+5+4+3+3+2+1+1 = 25) **overcounts** because solutions would still be **combinations of known methods**, not one new mechanism.
- Ranking remains a separate 21-query bottleneck even if CG expands.

---

## 9. Remaining hypotheses (all rejected as novelty vehicles in this round)

| Hypothesis | Why investigated | Outcome |
|---|---|---|
| Underspecified referent / TOT-style bridge | 3 CG cases | Too rare; literature (TOT / known-item) covers it |
| EN jargon ⊕ entity/event composition | 6 CG cases | Code-switching / mixed-query IR literature |
| EN brand in Urdu framing | 4 CG cases | Brand EL + entity-preserving CLIR |
| Cross-script entity variant | 5 CG cases | MSIR / NETE / transliteration / EL |
| Institutional descriptive alias | 6 CG cases | **CLOSED C2/C2a** (need ≥8/31) |
| Latent event/relation graph | multi-entity tags | Not dominant; architecture-import / LLM-magic without new supervision signal |
| Single "missing intermediate representation" | gate §10–12 | **Not found** as one coherent, prevalent mechanism |

---

## 10. Conclusion of discovery pass

> **NO NEW MECHANISM** with sufficient prevalence, technical distinctness, and literature separation was identified inside Roman Urdu → Urdu news IR on the available TRAIN/DEV evidence.
