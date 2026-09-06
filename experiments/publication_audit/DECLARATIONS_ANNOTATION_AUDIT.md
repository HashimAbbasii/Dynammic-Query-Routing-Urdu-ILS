# Declarations and annotation wording audit

Date: 6 September 2026  
Branch: `publication/plos-one-final`  
Canonical manuscript: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`

Mode: editorial consistency only. Scientific freeze unchanged.

**Status: PASS WITH AUTHOR CONFIRMATION REQUIRED**

---

## 1. Files inspected

- `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`
- `Papers/PLOS_ONE/plos_bibtex_sample.bib` (not edited)
- `Papers/PLOS_ONE/supporting_information/` (S1 Text, S2 File, S4 Table captions)
- `experiments/phase12_new_unseen_evaluation/`
- `experiments/phase12_human_relevance/`
- `experiments/phase12_independent_annotation/` (`AGREEMENT.md`, `INSTRUCTIONS.md`)
- `experiments/publication_audit/DATASET_SOURCE_CHAIN.md`
- `REPRODUCE.md`
- `README.md`
- `docs/REPRODUCIBILITY.md`
- `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` (contained stale “no second annotator” wording)

---

## 2. Changes made

| File | Change |
| --- | --- |
| Manuscript `.tex` | Abstract: removed “a single annotator”; official U result remains A1 23/40 |
| Manuscript `.tex` | Human protocol: A1 retained as official; A2 described as subsequent reliability check |
| Manuscript `.tex` | New Ethics subsection (supported facts only; no IRB exemption claim) |
| Manuscript `.tex` | Limitations: A1 official / A2 reliability wording |
| Manuscript `.tex` | Data availability: `REPRODUCE.md` pointer; clone does not contain article CSV |
| Manuscript `.tex` | Software: no claim of a completed clean-clone full-corpus rerun |
| Manuscript `.tex` | Portal-comment drafts marked AUTHOR CONFIRMATION REQUIRED |
| `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` | Removed “one annotator / no second-annotator agreement” |

Not changed: result tables, figures, qrels, A1 labels, A2 labels, M0, Phase 12 retrieval, frozen metrics.

---

## 3. Before / after (manuscript)

### Abstract

**Before:** “a single annotator judged the Top-5 useful … for 23/40 queries (57.50% …)”

**After:** “official human labels (A1) judged the Top-5 useful … for 23/40 queries (57.50% …)”

A2 percentages were not added to the abstract.

### Human relevance protocol

**Before:** “A second annotator later labeled the same frozen Top-5 independently … Official Success@5 remains Annotator 1 (23/40). Annotator-2 Success@5 is a reliability statistic and does not replace 23/40.”

**After:** “The original evaluation labels (A1) were retained as the official evaluation labels. An independent second annotation (A2) was subsequently conducted on the same 200 query-document judgments as a reliability check; A2 was not used to replace or recompute the reported A1 results … Official Success@5 remains Annotator 1 (23/40).”

### Ethics (new)

**Before:** none in the manuscript body. Portal comment claimed “IRB/ethics committee approval not required” (unsupported).

**After (body):** annotators labeled public news headlines/snippets; no search-user logs, interviews, or identifiable participant records were collected; no institutional ethics-board determination is recorded in the repository.

### Limitations

**Before:** “Official U labels are from one annotator, the first author … An independent second annotator labeled the same frozen Top-5 … That analysis does not replace 23/40 …”

**After:** “Official U labels (A1) were assigned by the first author … An independent second annotation (A2) was later conducted on the same 200 judgments as a reliability check … A2 was not used to replace or recompute 23/40 …”

### Data availability / code

**Before:** GitHub URL for dictionary, code, queries, qrels, reconstruction notes.

**After:** same claims, plus `REPRODUCE.md`, plus “A git clone does not contain the article-text corpus.” Software now states that a clean-clone full-corpus rerun was not claimed as completed for publication.

### Portal comments

**Before:** funding “no specific funding”; competing interests “none”; CRediT roles listed as facts; ethics “IRB not required.”

**After:** each of those is marked AUTHOR CONFIRMATION REQUIRED. Draft wording is retained only as a draft.

---

## 4. A1 / A2 consistency check

| Item | Status |
| --- | --- |
| Official U Success@5 | A1 **23/40 = 57.50%** in abstract, Table 1, discussion, SI captions |
| A2 Success@5 | **26/40 = 65.00%** only in SI (S2 File / S4 Table), as reliability |
| Five-way agreement | 135/200 = 67.50%; κ = 0.5490 |
| Binary agreement | 169/200 = 84.50%; κ = 0.6816 |
| A2 not averaged with A1 | Yes |
| A2 not in Table 1 | Yes |
| “single annotator” / “no second annotator” in manuscript body | Removed |
| Dual-role bias (A1 wrote queries) | Still stated; no “unbiased” / “bias-free” / “objective” claim |

Phrase “There is no single right article” in Discussion refers to the naturalistic IR task, not to the number of annotators.

---

## 5. Ethics status

**In-repo, supportable:** U labels are relevance judgments on public news headlines/snippets. No search-user study, no interviews, no identifiable participant dataset is described.

**Not supportable without confirmation:** that IRB/ethics review was “not required”; that an exemption was granted; that informed consent was obtained or waived; the identity of Annotator 2.

Manuscript body does **not** claim an IRB exemption.

---

## 6. CRediT status

Byline: Hashim Shazad, Adnan Aslam (Department of Creative Technologies, Air University, Islamabad).

A draft CRediT mapping exists only as a comment. Annotator 2 is **not named** in repository files. Roles cannot be finalized from the repository.

---

## 7. Funding status

No grant number, sponsor, or scholarship is recorded in the manuscript or `REPRODUCE.md`. A “no specific funding” sentence exists only as an unconfirmed portal draft.

---

## 8. Competing interests status

No competing-interest disclosure is recorded as an author-confirmed fact. A “no competing interests” sentence exists only as an unconfirmed portal draft.

---

## 9. Acknowledgments status

Current text: “This work was completed as part of an M.S. thesis at Air University, Islamabad.”

That matches repository thesis packaging. No additional people were invented. Annotator 2 is unnamed and is **not** acknowledged pending author confirmation.

---

## 10. Data availability status

Consistent with `DATASET_SOURCE_CHAIN.md` and `REPRODUCE.md`:

- Third-party compilation; Mendeley V3 DOI `10.17632/834vsxnb99.3`
- Kaggle Shahane Version 1
- 111,861 precursor records; 111,860 frozen articles
- SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Fresh provider-download SHA **not** completed
- Redistribution of news text **not** independently verified
- GitHub / SI do **not** contain the full article CSV

Claims were not strengthened or weakened.

---

## 11. Code availability status

Manuscript points to the GitHub repository and `REPRODUCE.md`. Software states that a clean-clone full-corpus rerun was **not** completed for publication. Official metrics remain copied from sealed Phase 8–12 reports.

---

## 12. AUTHOR CONFIRMATION REQUIRED

1. **Funding.** Confirm whether “The authors received no specific funding for this work” is accurate, or supply grant/sponsor text.
2. **Competing interests.** Confirm whether “The authors have declared that no competing interests exist” is accurate.
3. **CRediT.** Confirm each author’s CRediT roles. Do not submit the comment-block draft without review.
4. **Annotator 2 identity.** Name whether A2 is Hashim Shazad, Adnan Aslam, or a non-author. If a non-author, decide acknowledgment vs authorship. The repository does not name A2.
5. **Ethics / IRB.** Confirm whether Air University (or another body) reviewed, exempted, or did not review the annotation work. Do not submit “IRB not required” until confirmed.
6. **Acknowledgments.** Confirm the M.S. thesis / Air University sentence. Confirm whether anyone else should be named.
7. **ORCID.** Enter in Editorial Manager (not invented here).
8. **Permission to use** the third-party news compilation for this paper (DAS checkbox). Redistribution remains unverified.

---

## 13. Scientific results unchanged

- Table 1 still reports U Success@5 **23/40 = 57.50%**
- K Hit@5 still **27/40 = 67.50%**
- Development Hit@5 still **68/78 = 87.18%**
- A2 **26/40** not used as an official row
- No qrels, labels, figures, or result tables were edited

---

## 14. Freeze confirmation

- M0 unchanged
- Phase 12 unchanged
- A1 labels unchanged
- A2 interpretation: reliability only
- Metrics unchanged

---

## Out of scope (not edited)

These still say “one annotator” or similar. They are not the PLOS manuscript:

- `Thesis_template/FINAL/ULTRA_THESIS_SUBMISSION_DRAFT.md`
- `Papers/IEEE/FINAL/main.tex`
- `experiments/phase12_new_unseen_evaluation/PHASE12_SEALED_PROTOCOL.md` (sample-size planning language from sealing time)

PLOS SI files already state A1 official / A2 reliability.

---

## AUTHOR CONFIRMATION — RESOLVED

Author confirmation received 6 September 2026. Applied to the PLOS manuscript only (plus a name line in `S2_file.md` so the SI matches the caption).

| Item | Confirmation | Status |
| --- | --- | --- |
| Funding | No funding received | **RESOLVED** — manuscript: “No specific funding was received for this work.” |
| Competing interests | None | **RESOLVED** — manuscript: “The authors have declared that no competing interests exist.” |
| A2 identity | Areena Rahman | **RESOLVED** |
| A2 role | Model evaluation / independent relevance reliability evaluation | **RESOLVED** — CRediT Validation; A2 does not replace A1 23/40 |
| Supervisor acknowledgment | Confirmed | **RESOLVED** — “We thank Adnan Aslam for supervision.” |
| IRB/exemption | Not claimed | **CONFIRMED** — ethics subsection unchanged; no IRB, exemption, consent, or human-subjects approval added |

### Manuscript sections changed in this confirmation pass

- Title-page byline: added Areena Rahman (affiliation block unchanged; a separate affiliation for A2 was not provided).
- Human relevance protocol: named Areena Rahman as A2.
- Limitations: named Areena Rahman as A2.
- S2 File caption: named Areena Rahman; A2 26/40 still does not replace A1 23/40.
- Acknowledgments: supervisor thanks added; existing Air University thesis sentence kept.
- New sections: Funding; Competing interests; Author contributions.
- Portal comments: marked confirmed; ethics still forbids IRB language.

### Unchanged in this pass

Ethics body text. Table 1 and all scientific result tables. A1 23/40. A2 26/40 not added to Table 1. M0, Phase 12, qrels, labels, figures.

### Still not a scientific confirmation (unchanged)

- ORCID (enter in Editorial Manager).
- Permission-to-use the third-party news compilation (DAS checkbox). Redistribution remains unverified.

First-author byline name remains **Hashim Shazad** as already in the manuscript (not renamed).

**PASS — AUTHOR CONFIRMATION RESOLVED**

**NO SCIENTIFIC RESULTS CHANGED**
