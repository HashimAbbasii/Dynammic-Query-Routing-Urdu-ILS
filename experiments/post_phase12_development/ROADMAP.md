# Post-Phase-12 roadmap (locked process)

**Branch:** stay on `research/post-phase12` until a candidate is SELECTED.  
**Date opened:** 2026-09-05  
**Official M0 table (never overwritten):** 68/78 ExactSource Hit@5 (n=78); 27/40 K; 23/40 U Success@5.

This file is a **work plan**. It is not a promise that any later Hit@5 will rise. A failed module is a genuine result.

## Branch decision

| Option | Use when |
| --- | --- |
| **This branch (`research/post-phase12`)** | Stage 0 taxonomy, Module 3 protocol, R-dev runs, SELECT/KILL write-up, thesis chapters that report frozen M0 + R-dev negative results |
| New branch later (`research/unseen-<system>`)** | Only **after** SELECT: new sealed unseen queries, disjoint from R/K/U/H |
| Do **not** use `main` | Older SVM/MiniLM history; not the M0 freeze line |
| Do **not** fork a “improve-score” branch | Invites mixing design with test |

**Suggestion:** keep working here. Cut a new branch only if we SELECT a new retriever and start an unseen test. PLOS LaTeX lives in `Papers/PLOS_ONE/` on this same branch; do not treat paper edits as a new official metric.

## Full remaining work (until last thesis writing)

Gates: do not start a later row until the gate on the previous row is met. Times are one-person calendar, not a promised score.

| ID | Work | Where | Output | Gate to proceed | Calendar | Who |
| --- | --- | --- | --- | --- | --- | --- |
| **S0** | Error taxonomy on **frozen dumps only**. No new retrieval. Codes: HIT / RANK (source in 6–50) / ABSENT / NAT fail type. | `experiments/post_phase12_development/` | `ERROR_TAXONOMY.md` + counts CSV | **DONE (first pass 2026-09-05).** Largest official Roman bin = ABSENT. Largest R-dev KI bin = MIXED ABSENT. | 2–4 days | Agent + you review |
| **S1** | Pick **one** Module 3 family from the largest **fixable** bin (matching vs rerank vs MIXED routing). | Protocol file only | `module3/MODULE3_PROTOCOL.md` locked **before** run | Kill/select rule written in numbers; SHA table of frozen inputs | 1–2 days | Agent drafts; you approve |
| **S2** | One retrieval pass of that candidate on R-dev. | `module3/` | Top-50 CSV, manifest, hashes | Preflight SHA match; M0 files untouched | 0.5–2 days | Agent |
| **S3** | If candidate Top-5 leaves M0 NAT pool: union-pool labels (M3-E style). Else skip. | `m3e`-like folder | New qrels for M0 ∪ candidate; system-blind | Labels after dump; no peeking to retune | 2–5 days | You (labels); agent sheets |
| **S4** | SELECT or KILL in writing. | `MODULE3_RESULTS.md` | Decision paragraph | If KILL → skip S5–S6; M0 stays official | 1 day | Both |
| **S5** | **Only if SELECT:** freeze candidate (code + hashes). R-dev burned for that system. | freeze manifest | Frozen config JSON | No further edits to that system | 1 day | Agent |
| **S6** | **Only if SELECT:** new unseen set (new IDs, no reused KI sources), seal, retrieve once, label NAT. **New git branch.** | new experiment dir | Sealed queries + scores **beside** 68/78, 27/40, 23/40 | Disjoint from R/K/U/H | 2–4 weeks | Both |
| **T1** | Thesis: official results chapters = frozen M0 only. | `Thesis/FINAL/` | Word + `ULTRA_THESIS_SUBMISSION_DRAFT.md` | No R-dev numbers in the official table | ongoing after S0 | You + agent |
| **T2** | Thesis appendix / extra chapter: R-dev, Module 1 Δ=0, Module 2 reject, S0 taxonomy, later KILL/SELECT. | same | Clearly labeled **development**, not unseen | Do not average with 57.5% | after S4 | Agent drafts |
| **T3** | Limitations, future work, AU Word TOC/tables. | `HOW_TO_UPDATE_WORD_THESIS.md` | Submission Word | Manual TOC update remains yours | 2–4 days | You |
| **P1** | PLOS ONE: frozen M0 paper only (already templated). | `Papers/PLOS_ONE/` | `.tex` + PDF + figure uploads | Portal fields (funding, CRediT, ORCID, DAS) | parallel; not a new metric | You |

**If S4 = KILL:** last research experiment is S4. Thesis writing is T1–T3 using M0 + negative ablations. That is a complete genuine thesis. There is no requirement to “find a higher percentage.”

**If S4 = SELECT:** T1 still reports old official numbers; S6 is the only place a new unseen number is allowed.

## What we will not do

- Tune on K, U, H001–H040, or n=78  
- Edit the 198-key dictionary from failed queries  
- Stack M1+M2+a new idea after seeing scores  
- Average 87.18 / 67.50 / 57.50  
- Invent Hit@5  

## Immediate next (S0)

Start now on this branch: mechanical taxonomy from sealed K, U, and R-dev artifacts. No Module 3 retrieval.
