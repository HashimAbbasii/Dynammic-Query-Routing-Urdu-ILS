# data/

This folder is the **local** location of the frozen retrieval collection. The article-text CSV is **not** shipped in git.

Official freeze file (when present on disk): **`clean_articles.csv`** (n = 111,860; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`).

`data/*.csv` is gitignored. A clone of GitHub does not contain `clean_articles.csv` or `urdu_news.csv`. Those files are third-party news text. This project does not redistribute them. The repository MIT License covers original ULTRA code and documentation only; it does **not** license the news corpus. See `REPRODUCE.md`.

Other files that may appear here (embeddings, Chroma, reconstructed candidates) are generated or precursor artifacts. They are not required to *read* the official M0 metrics in `results/` and in the manuscript.

`training_queries_real.py` is Layer A SVM training data, not M0 routing.
