# Manuscript numbers audit

**Date:** 6 September 2026  
**Manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
**Rule:** if a discrepancy exists, STOP. None found.

| Artifact | Number | Source | Verified? |
| --- | ---: | --- | --- |
| Table 1 / Abstract | 68/78 = 87.18% ExactSource Hit@5 | Phase 6/11; freeze | Yes |
| Table 1 CI | 77.68–93.68% | SciPy binomtest on 68/78 (prior calc) | Yes (unchanged) |
| Dev nDCG@5 / MRR | 0.8107 / 0.797 | Phase 6 | Yes |
| Table 1 / Abstract | 27/40 = 67.50% K Hit@5 | `K_RESULTS.md`; S1 Table 27 yes / 13 no | Yes |
| Table 1 CI | 50.87–81.43% | 27/40 | Yes |
| Table 1 / Abstract | 23/40 = 57.50% A1 Success@5 | `metrics.json` | Yes |
| Table 1 CI | 40.89–72.96% | 23/40 | Yes |
| Table 2 | MiniLM 0.2564 / 0.2821 / 0.4487; Urdu-only 0.5897; M0 0.8718; oracle 0.9103 | Phase 4/8 comparators | Yes (manuscript-internal vs prior freeze docs) |
| Table 3 | all M0–M4 68/78; train Roman 0.9531 | `PHASE11_ABLATION_RESULTS.md` | Yes |
| Table 4 | Hit@1 20/40; Hit@5 27/40; Hit@10 28/40; Hit@50 30/40 | `K_RESULTS.md` | Yes |
| Table 4 ranks | K002=6, K010=49, K031=17; 10 not in Top-50 | S1 Table | Yes |
| K script | URDU 26/28; ROMAN 1/12 | S1: 28 URDU, 12 ROMAN; 1 Roman yes (K007) | Yes |
| Table 5 | Success@5 23/40; P@5 0.2050; nDCG@5 0.6460; MRR 0.4542 | `metrics.json` | Yes |
| Table 5 labels | A 41, B 26, C 53, D 80, E 0 | `metrics.json` | Yes |
| Table 6 | URDU 17/18; ROMAN 6/18; MIXED 0/4 | `metrics.json` | Yes |
| Table 6 other slices | factoid 9/14; expl. 9/14; NE 5/12; short 9/12; med 6/16; long 8/12; temp 3/4 | `metrics.json` | Yes |
| A2 | 26/40; 135/200; κ 0.5490; 169/200; κ 0.6816 | `AGREEMENT.md` / S2 File | Yes |
| Corpus | 111,860; 540,050,203 bytes; SHA `8992a6ac…` | freeze / S3 File | Yes |
| Precursor | 111,861 → drop truncated row | Corpus subsection / S3 | Yes |
| BM25 | k1=1.5, b=0.75; retrieve 50; cutoff 5 | freeze JSON | Yes |
| Dictionary | 198 keys; SHA `30c3f61a…` | freeze | Yes |
| S3 Table | Method A/B 0/13; C 13/13 nDCG 0.8004; D 13/13 nDCG 0.9331; IV D 9/10 | `S3_table.csv` | Yes |
| H diagnostic | 25/40 Success@5; P@5 0.1250 | Phase 10C | Yes (not official U) |
| Method A Roman n=23 | 0/23 | Phase 5 / manuscript | Yes |
| Method D Roman n=23 | 22/23 | Phase 5 | Yes |

**Discrepancies requiring STOP:** none.

**Scope notes (not errors):** Phase 6 qualitative labels apply only to 10/78 misses. Table 6 mixed n=4 is descriptive. Train-Roman 61/64 is a selection diagnostic, not unseen.
