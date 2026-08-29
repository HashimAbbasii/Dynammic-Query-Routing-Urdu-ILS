# Data split

Frozen test (never in this experiment's labels or model selection):

- IDs H001–H040
- Source: `validate/dual_index_routing/labels/heldout_traps.py`
- Human dual-index judgments stay in `heldout_retrieval_template.csv`

New pool only (`QTRN_001` … `QTRN_260`):

| File | n | Fraction |
| --- | ---: | ---: |
| `oracle_train.csv` | 182 | 70% |
| `oracle_dev.csv` | 39 | 15% |
| `oracle_internal_val.csv` | 39 | 15% |
| `oracle_all.csv` | 260 | 100% |

Split method: shuffle within each oracle class (`HEADLINE` / `FULL` / `MIXED`), seed 42.

No query appears in more than one of train/dev/internal_val.
No frozen ID appears in the new pool.
