# Development / validation known-item (Phase 2, n = 78)

**Metric:** ExactSource Hit@5 (the designated source document appears in the Top-5).

**Official result:** **68/78 = 87.18%**

This is a genuine development/validation known-item result on title-derived queries (including development `title_roman`). It is **not**:

- human relevance
- Success@5
- unseen naturalistic performance
- general real-world accuracy

**Supporting development comparators** (same pool; not Phase 12):

- Urdu-only BM25 (no Roman path): 0.5897 ExactSource Hit@5
- Roman subset Method A: 0/23
- Roman subset Method D: 22/23

Corpus: `data/clean_articles.csv`, n = 111,860.  
Evidence: `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`
