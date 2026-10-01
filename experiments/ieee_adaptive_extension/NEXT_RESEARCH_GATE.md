# NEXT RESEARCH GATE — Roman Urdu Novelty Extension Phase 1

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-novelty-extension`  
**HEAD:** (see git status at end of session)  
**Decision:** **NO-GO**

`TEST accessed: NO`  
`Program A modified: NO`  
`Program B modified: NO`

---

## Decision

### **NO-GO**

No sufficiently defensible **novel retrieval mechanism** was identified from the investigated failure mechanisms.

---

## Exact research question (investigated)

> Why does ExactSource Hit@5 reach 87.18% on the n=78 development/validation pool but collapse on harder Roman Urdu populations, and does that difference expose an under-addressed technical mechanism for a new method?

---

## Exact reason for NO-GO

1. **The 87% result is explained primarily by benchmark/query construction (H10 supported), not by a mysterious unsolved architecture:**
   - **46/78** Urdu title-derived / related queries → Urdu BM25 (Urdu subset Hit@5 ~0.913 in development comparators).
   - **23/78** Roman queries are **`title_roman`** — Phase 2 character-table / reverse-dictionary romanizations of titles, generated with the **same family of romanization** used to build Method D’s document index → Method D **22/23**.
   - Phase 5 documentation already states these are **not naturalistic chat Roman Urdu**.

2. **Hard populations differ in kind:**
   - **K Roman (12/40):** “ordinary Roman Urdu of headline” → Method D ~**1/12**.
   - **Program B n=80:** naturalistic Roman KN; `headline_overlap` ≈ 0 for 78/80; Method-D **5/80**; Dense **20/80**; BND ceiling **49/80**.

3. **The “missing bridge” (naturalistic Roman orthography ↔ Urdu / system-romanized docs) is real but literature-covered:**
   - Gupta SIGIR 2014 MSIR; FIRE fuzzy/phonetic MSIR; Prabhakar TALLIP 2021; Chari SIGIR 2025 transliterate-train; Butt 2025 Roman Urdu IR.
   - Gate §15 **automatically rejects** transliteration, phonetic matching, spelling normalization, dense/ColBERT/SPLADE/Doc2Query imports, and combination novelty.

4. Prior closed gates (C1, C2a, CG entity, architecture redesign) already blocked the remaining method-shaped candidates.

---

## What must happen next

**STOP method invention in this extension until/unless a new mechanism is found that survives §15 rejection and literature separation.**

Scientifically valuable next uses of this finding (not implementation of a “novel” method):

- Document the **title_roman vs naturalistic Roman** distribution shift in thesis/Program A Limitations (if/when writing — out of scope for this gate’s “no publication work” instruction beyond recording it).
- Keep Program A/B frozen.

## What must NOT happen next

- Do not implement multi-hypothesis transliteration / phonetic QE / transliterate-train / ColBERT / SPLADE / Doc2Query under a novelty claim.
- Do not revive adaptive routing / institutional alias / entity CG.
- Do not open TEST.
- Do not retune Program A/B.
- Do not chase 80% by swapping embeddings or RRF weights.
- Do not delete hard queries to restore 87%.

---

## 80% note

Reaching **64/80** remains **structurally incompatible** with the current BND Top-50 pool (**49/80**). Closing the naturalistic Roman bridge might raise coverage in principle, but under this gate that bridge is **not** a novel mechanism—so it does **not** authorize an implementation phase.
