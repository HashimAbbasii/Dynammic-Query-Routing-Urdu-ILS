# Scientific fix validation (Phase 6 master review)

**Branch:** `publication/plos-one-final`  
**New experiments:** none  
**Frozen numbers:** unchanged

## Freeze paths

Not modified: M0 code, K/U dumps, A1 qrels, A2 sheets, Phase 11 JSON, bibliography, figure binaries.

## Framing (this pass)

- Printed title: Script-aware BM25 retrieval for Urdu and Roman Urdu news search
- “script-aware index selection” used for M0; “routing” retained only for literature contrast or explicit non-claims
- Evaluation hierarchy A–D in Methods
- Post-phase12: official wording that later work did not tune/replace M0, K, U, A1
- Reproducibility: git materials vs third-party corpus distinguished
- Conclusions: does not claim to solve Urdu/Roman retrieval
- Phase 6 taxonomy still scoped to 10 freeze-pool misses
- Abstract “most designated sources” bound to 68/78 freeze pool

## Numbers

See `MANUSCRIPT_NUMBERS_AUDIT.md`. S1 Table Hit@5 yes=27, no=13, URDU=28, ROMAN=12. No STOP discrepancies.

## Residual packaging (not this phase)

- `.tex` filename still contains old routing phrase
- GitHub default branch is `main`
- Stale lines in some older DAS audit drafts vs live `.tex`
- PLOS formatting not started (per instruction)
