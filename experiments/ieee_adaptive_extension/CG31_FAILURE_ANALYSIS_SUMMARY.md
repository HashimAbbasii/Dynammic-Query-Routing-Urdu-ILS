# CG Failure Analysis Summary (n=31)

**Annotation date:** 2026-09-22  
**Scope:** Program B TRAIN+DEV ExactSource queries where gold is absent from BM25∪NG3∪Dense Top-50.  
**Sources:** phase13 `queries_kn.csv` + `data/clean_articles.csv` golds.  
**Method:** Stage 1 query-first; Stages 2–4 after gold comparison. No method design.  
**Workbook:** `experiments/ieee_adaptive_extension/31_CG_Failure_Analysis_Template.xlsx`

## Artifact confirmation

- 31 CG failures confirmed from `FINAL_FAILURE_MECHANISM_PER_QUERY.csv` (status=CG_FAILURE).
- Query texts and gold IDs confirmed from phase13 TRAIN/DEV `queries_kn.csv`.
- Gold headlines/text confirmed from `data/clean_articles.csv` (31/31 found).

## Coverage aggregates

- **Covered:** 17/31
- **Partial:** 14/31
- **Uncovered:** 0/31
- **Potential_New_Mechanism = Yes:** 0/31

## Mechanism clusters (coarse)

- **institutional_acronym_or_alias:** 8/31
- **en_brand_or_title_script_bridge:** 6/31
- **cross_script_entity_or_person:** 5/31
- **en_jargon_entity_event_composition:** 3/31
- **underspecified_or_descriptive_referent:** 3/31
- **sports_entity_acronym_script:** 2/31
- **same_en_name_script_plus_jargon:** 2/31
- **rare_product_translit_translate:** 1/31
- **semantic_or_vocab_paraphrase:** 1/31

## Uncovered + Potential_New_Mechanism = Yes

None. No case was both Uncovered and judged to require a new mechanism.

## Evidence test for a shared new phenomenon

The 31 misses fragment across known categories: institutional acronym/alias, brand/title script bridging,
person/geo name variants, English jargon composed with entities/events, underspecified referents,
same-English-name script conversion plus jargon, and bilingual paraphrase.
Underspecified cases (KN008, KN037, and related descriptive aliases) are explainable as tip-of-the-tongue /
descriptive known-item phenomena; they remain Partial because dense matching could still help, and they do not
share a distinct uncovered structure beyond that known class.

## Conclusion

On this evidence, **no candidate new failure mechanism survives**. Residual difficulty is heterogeneous and
largely Covered or Partial under transliteration, entity linking, acronym expansion, dense multilingual retrieval,
and/or query expansion.
