# Final claim–evidence audit (post Phase 6 scientific review)

**Manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`

Flagged tokens were searched. Remaining “routing” refers to **other papers** (bib11/bib12) or to an explicit **non-claim**.

| Claim | Evidence | Strength | Action |
| --- | --- | --- | --- |
| Title: script-aware BM25 for Urdu and Roman Urdu news search | M0 = Unicode detector + two BM25 indexes on news | Strong | Keep |
| Detector is deterministic Unicode, not a learned classifier | Methods M0 | Strong | Keep |
| 68/78 ExactSource Hit@5 on freeze pool | Phase 6/11 | Strong for that pool | Keep; not unseen |
| 27/40 K Hit@5 | `K_RESULTS.md` / S1 | Strong | Keep |
| 23/40 A1 Success@5 | `metrics.json` | Strong as A1 sample | Dual-role disclosed |
| A2 26/40 reliability only | S2 File | Strong | Do not replace A1 |
| Roman is the main limitation | K 1/12; U 6/18; 10/11 Roman K absent Top-50 | Strong as descriptive | Keep; n small |
| Script-aware selection repairs `title_roman` mismatch | Method A 0/23 vs D 22/23 | Strong on that construction | Wording: “repairs”, not “solves Roman IR” |
| Does not repair ordinary/chat Roman | K/U splits | Strong | Keep |
| M1–M4 do not replace M0 | all 68/78 | Strong | Keep |
| No SOTA / no learned routing algorithm | explicit non-claims | Protective | Keep |
| Post-phase12 not official | Limitations paragraph | Strong as scope | Keep; do not table 19/50 |
| “Query routing” (English IR literature) | bib11, bib12 | About **those** systems | Keep contrast |
| “reproducible evidence” (Conclusions) | code+queries+qrels in git; corpus not in git | Partial | Softened by methods: clone ≠ full retrieval |
| “usually puts something useful in the Top-5” (Urdu U) | 17/18 | Moderate (n=18) | Already “this U sample” |
| “often recovered the designated article” (Conclusions) | 68/78 and 26/28 K Urdu | Moderate | Tied to title-like / this collection |
| adaptive / dynamic (M0 capability) | — | Unsupported | **Removed** from title/abstract/conclusions |
| superior / robust / scalable / novel (M0) | — | Unsupported | **Not claimed** |

**Major unsupported scientific claims remaining:** none.

**RQ private table**

| RQ | Evidence answering it | Official result | Status |
| --- | --- | --- | --- |
| RQ1 | n=78 ExactSource | 68/78 | Answered (title-derived / `title_roman`) |
| RQ2 | Phase 12 K | 27/40; 87% does not transfer | Answered |
| RQ3 | Phase 12 U A1 | 23/40 | Answered |
| RQ4 | Phase 11 | all 68/78; no replace | Answered (“improve” is the question, not a claim) |
