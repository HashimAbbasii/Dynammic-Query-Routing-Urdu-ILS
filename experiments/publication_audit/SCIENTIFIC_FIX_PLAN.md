# Scientific fix plan

**Date:** 6 September 2026  
**Source:** `CROSS_BRANCH_REVIEWER_SCIENTIFIC_AUDIT.md` + `CONTRIBUTION_REFRAMING.md`  
**Write target:** `publication/plos-one-final` only  
**New experiment:** none

---

## P0

1. Replace printed title and short title. Remove “adaptive dynamic query routing” as the scientific headline.
2. Rewrite abstract/intro/conclusions contribution sentences to match M0.
3. Limitations: name `research/post-phase12` as later exploratory development, not official, not mixed with Table 1. Do **not** paste R-dev 19/50 into official tables.

## P1

4. Abstract/limitations: A1 = query author + official judge; A2 does not remove dual-role bias.
5. README: submission branch `publication/plos-one-final`; drop “Adaptive” tagline.
6. Discussion: 10/12 Roman K misses absent from Top-50 ⇒ reranking the current list cannot recover them (observed ranks, not a new run).
7. Scope Phase 6 QUERY_AMBIGUITY family to the ten n=78 residuals; not the Phase 12 bottleneck.

## Not done (deliberate)

- No M0 / qrels / metric / A1 / A2 / Phase 12 dump edits
- No merge/cherry-pick of `research/post-phase12`
- No dense/hybrid/rerank experiment
- No McNemar invented from incomplete paired files
- Bibliography unchanged (REFERENCES STAGE already PASS)
- `.tex` filename unchanged

## Files to edit

| File | Why |
| --- | --- |
| `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` | Title, abstract, intro, methods identity, discussion, limitations, conclusions |
| `README.md` | Tagline, branch pointer, post-freeze scope |
| `REPRODUCE.md` | Branch + out-of-scope later development |
| This folder | plan / validation / attack / claim matrix |

## Success criterion

A reviewer can answer yes to: *Does the manuscript accurately describe what was implemented, and do the experiments support the claims?*
