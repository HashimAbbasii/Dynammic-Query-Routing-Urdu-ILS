# Contribution reconstruction (before manuscript edits)

**Branch:** `publication/plos-one-final`  
**Date:** 6 September 2026  
**Rule:** Do not invent a stronger contribution than the frozen experiments support.

---

## Current contribution claim

Title and abstract present the work as **adaptive dynamic query routing** for Urdu IR. The methods then redefine that phrase as Unicode script-conditional index choice (not a learned SHORT/LONG classifier). The body contribution sentence is already narrower: a frozen script-aware BM25 system, separated evaluations, and a measured Roman Urdu limitation.

That split is the problem: the **title sells a routing method**; the **experiments measure a hashed lexical freeze**.

---

## Actual implemented contribution

M0 is a **deterministic Unicode script detector** plus **two Okapi BM25 indexes** on 111,860 Urdu news articles:

- URDU / MIXED / OTHER → Urdu BM25 on `combined_text`
- ROMAN → Method D BM25 on romanized documents (character table + 198-key reverse dictionary)
- Queries are **not** rewritten
- The detector is **not** a classifier and does **not** adapt online
- A historical SVM SHORT/LONG router and MiniLM dual-index were **not** retained (SVM graded P@5 0.3300 vs word-count 0.3650 on H001–H040)

**What the routing mechanism contributes (development n=78):** Urdu-only BM25 Hit@5 = 0.5897; script-aware M0 = 0.8718, because Method D recovered 22/23 development Roman `title_roman` queries that Method A (raw Roman → Urdu index) scored 0/23. That is **script-mismatch repair**, not sparse-vs-dense routing.

**What Phase 12 contributes:** the 87.18% figure does **not** transfer to ordinary Roman titles (K Roman 1/12; overall K 27/40). Human usefulness on naturalistic queries is 23/40 (A1), with Urdu 17/18 and Roman 6/18.

**What later `research/post-phase12` contributes:** a **new development** pool and failed lexical patches. Not official. Not Table 1.

---

## Evidence

| Question | Answer | Source |
| --- | --- | --- |
| What problem is solved? | Native-script BM25 misses Latin-script Roman Urdu queries even when the article exists | Phase 5 Method A 0/23; intro |
| Why is script-aware index choice necessary? | A single Urdu index does not token-match ordinary Latin queries | Method A vs D on n=23 Roman |
| What does the detector contribute vs one index? | On n=78, +0.2821 Hit@5 vs Urdu-only BM25 | Table 2 |
| Unified retrieval? | Urdu-only 0.5897 on n=78; Method A 0/23 Roman | Table 2 / Phase 5 |
| Urdu vs Roman vs mixed? | Dev Urdu high; K Urdu 26/28 vs Roman 1/12; U 17/18 vs 6/18 vs mixed 0/4 | K_RESULTS; metrics.json |
| Evaluation demonstration | Three non-exchangeable rates under a freeze | Table 1 |
| Novel vs CURE / MS MARCO / English routers? | Different protocol and collection; not a leaderboard; not Adaptive-RAG | manuscript non-claims |
| Contribution type | **Empirical / evaluation-oriented system measurement**, with a simple deterministic method | this reconstruction |

---

## What can be claimed strongly

1. A hashed freeze of script-aware BM25 on this news corpus.
2. Development known-item ExactSource Hit@5 = 68/78 (87.18%) for **title-derived** queries, including `title_roman`.
3. That score is **not** unseen chat-style usefulness.
4. Sealed K ExactSource Hit@5 = 27/40; drop is concentrated on ordinary Roman titles; most of those misses never enter Top-50.
5. Official U Success@5 = 23/40 (A1); A2 = 26/40 is reliability only.
6. Query-side expansions M1–M4 did not replace M0 (all 68/78).
7. Method D is necessary for `title_roman` known-item and **insufficient** for ordinary/chat Roman on K/U.
8. M0 is not an SVM and not MiniLM.

---

## What must be softened

- “Adaptive” / “dynamic” as properties of M0.
- “Strong” native-script language as a population claim (n=18 and n=28 slices).
- “Routing” as English IR routing (sparse/dense, RAG depth, learned policy).
- Implying Phase 12 isolates the detector vs always-Urdu (that ablation is n=78 only).
- Phase 6 QUERY_AMBIGUITY (10 freeze-pool misses) as the sealed-set bottleneck.

---

## What should not be claimed

- First Urdu retriever; SOTA vs CURE or Urdu MS MARCO.
- Learned or online adaptation.
- Generalization beyond this news dump and these query families.
- 87.18% real-world accuracy or 80% unseen usefulness.
- A2 removes dual-role bias.
- Post-phase12 R-dev scores as official or as unseen tests.
- That a Top-50 reranker would fix official Roman K (10/12 sources absent).

---

## Recommended scientific positioning

**PLOS ONE measurement paper:** freeze a simple script-aware lexical retriever for Urdu news; keep known-item recovery separate from human usefulness; report that native-script search works on this collection and ordinary Roman Urdu does not.

Positioning is **empirical IR evaluation**, not a new routing algorithm.

---

## Recommended title candidates

1. **Script-aware BM25 retrieval for Urdu and Roman Urdu news search** (recommended)
2. Script-conditional lexical retrieval for Urdu news: native-script and Roman Urdu evaluation
3. Dual-index BM25 for Urdu news search under Perso-Arabic and Roman scripts
4. Measuring script-aware lexical retrieval for Urdu news
5. Unicode script detection and BM25 for Urdu and Roman Urdu news retrieval

**Chosen title:** `Script-aware BM25 retrieval for Urdu and Roman Urdu news search`

**Short title:** `Script-aware BM25 for Urdu news search`

**Why not keep “routing” in the title:** the word is still accurate in methods (index selection) but in a title it invites Adaptive-RAG / SVM comparisons the official system does not win. Methods may say “script-aware routing” if defined as choosing which BM25 index to open.

**Filename:** keep `Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` to avoid breaking packaging paths; the **printed title** changes.

---

## RQ mapping (existing experiments only)

| RQ | Existing experiment | Evidence | Result | Conclusion |
| --- | --- | --- | --- | --- |
| RQ1 | Phase 2/5/8 n=78 ExactSource | PHASE11 / Phase 6 | 68/78 | Yes, for title-derived / `title_roman` known-item |
| RQ2 | Phase 12 K | `K_RESULTS.md` | 27/40; URDU 26/28, ROMAN 1/12 | 87% does not transfer; Urdu titles still high |
| RQ3 | Phase 12 U A1 | `metrics.json` | 23/40; URDU 17/18, ROMAN 6/18 | Sample usefulness; not ExactSource |
| RQ4 | Phase 11 M0–M4 | `PHASE11_ABLATION_RESULTS.md` | all 68/78 | Do not replace M0 |

No new RQ. No new experiment.

---

## Experiment decision

| Candidate | Verdict |
| --- | --- |
| Dense / hybrid / rerank on K/U | NOT NECESSARY for this positioning |
| Urdu-only re-run on sealed K | OPTIONAL diagnostic; **not run** (title change + existing Method A 0/23) |
| Import R-dev 19/50 into Table 1 | FORBIDDEN |
| Replace A1 with A2 | FORBIDDEN |
