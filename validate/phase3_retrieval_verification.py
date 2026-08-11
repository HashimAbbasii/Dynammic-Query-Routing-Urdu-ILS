# -*- coding: utf-8 -*-
"""
Phase 3 — Retrieval ground-truth verification for the 5/6-word queries.

Run this LOCALLY, from your repo root (where data/clean_articles.csv,
data/embeddings.npy, and data/chromadb/ actually exist — these are the
large files not committed to GitHub).

Requires: pandas, numpy, chromadb, sentence-transformers, scikit-learn
    pip install pandas numpy chromadb sentence-transformers scikit-learn

What it does:
  For each of the 14 five/six-word queries from the 85-query test set,
  runs Keyword (TF-IDF cosine), Semantic (ChromaDB/embeddings), and
  Hybrid (weighted fusion) retrieval, computes P@5, P@10, P@15, MRR,
  nDCG@15 against a category-match relevance proxy (same convention as
  notebooks/04_retrieval.ipynb), then reports which retrieval mode wins
  for each query -- so we can check whether the existing Short/Long
  labels agree with retrieval behavior (per Phase 3 of the plan).

Output: prints a full table + saves results/phase3_retrieval_results.json
"""

import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------
# 1. Load data (EDIT PATHS if yours differ)
# ---------------------------------------------------------------------
print("[1/6] Loading clean_articles.csv (540MB, this can take ~30-60s)...", flush=True)
df = pd.read_csv("data/clean_articles.csv", encoding="utf-8-sig")
print(f"      Loaded {len(df)} rows. Columns: {list(df.columns)}", flush=True)

print("[2/6] Loading embeddings.npy...", flush=True)
embeddings = np.load("data/embeddings.npy")
print(f"      Loaded embeddings shape: {embeddings.shape}", flush=True)

print("[3/6] Connecting to ChromaDB...", flush=True)
import chromadb
client = chromadb.PersistentClient(path="data/chromadb")
collection = client.get_collection("urdu_news")
print(f"      Collection loaded, {collection.count()} documents.", flush=True)

print("[4/6] Loading SentenceTransformer model (downloads on first run, can take a few minutes)...", flush=True)
from sentence_transformers import SentenceTransformer
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
sem_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device)
print(f"      Model ready on device: {device}", flush=True)

# ---------------------------------------------------------------------
# 2. The 14 five/six-word queries from the 85-query Stage-C test set,
#    with an expected category as the relevance proxy. EDIT the
#    expected_category values below to match your df['category'] values
#    -- these are best guesses from the query topic, verify/correct them.
# ---------------------------------------------------------------------
target_queries = [
    ("ملتان میں ٹریفک حادثہ ہوا", "long", "Crime & Incidents"),
    ("کسانوں کو نیا قرض ملے گا", "long", "Business & Economics"),
    ("پشاور میں چوری کی واردات", "long", "Crime & Incidents"),
    ("نیا اسٹارٹ اپ فنڈنگ حاصل کرے", "long", "Business & Economics"),
    ("فیصل آباد میں پانی صاف نہیں", "long", "Environment"),
    ("multan mein traffic accident hua", "long", "Crime & Incidents"),
    ("kisano ko naya loan milega", "long", "Business & Economics"),
    ("peshawar mein chori ki waardaat", "long", "Crime & Incidents"),
    ("naya startup funding hasil karega", "long", "Business & Economics"),
    ("faisalabad mein pani saaf nahi", "long", "Environment"),
    ("نئے بینک اکاؤنٹ کھولنے کا طریقہ", "long", "Business & Economics"),
    ("عید سے پہلے بازاروں میں رش", "long", "Business & Economics"),
    ("naya bank account kholne ka tareeqa", "long", "Business & Economics"),
    ("scientists ne naya sitara dhoond liya", "long", "Science & Technology"),
]

# ---------------------------------------------------------------------
# 3. TF-IDF keyword index (char n-grams work better for Urdu than word-level)
#    Using actual column names from your CSV.
# ---------------------------------------------------------------------
print("[5/6] Building TF-IDF keyword index over headlines...", flush=True)
HEADLINE_COL = "Headline"
CATEGORY_COL = "Category"
corpus = df[HEADLINE_COL].fillna("").astype(str).tolist()
tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=50000)
tfidf_matrix = tfidf.fit_transform(corpus)
print(f"      TF-IDF matrix shape: {tfidf_matrix.shape}", flush=True)
print(f"      Unique categories in dataset: {sorted(df[CATEGORY_COL].dropna().unique().tolist())}", flush=True)


def keyword_search(query, top_k=15):
    qv = tfidf.transform([query])
    sims = cosine_similarity(qv, tfidf_matrix)[0]
    idx = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in idx]


def semantic_search(query, top_k=15):
    qemb = sem_model.encode(query).tolist()
    res = collection.query(query_embeddings=[qemb], n_results=top_k)
    # map chromadb ids back to df row indices -- adjust if your ids aren't row indices
    ids = [int(x) for x in res["ids"][0]]
    dists = res["distances"][0]
    sims = [1 - d for d in dists]  # convert distance to similarity
    return list(zip(ids, sims))


def hybrid_search(query, top_k=15, alpha=0.5):
    kw = dict(keyword_search(query, top_k=50))
    sem = dict(semantic_search(query, top_k=50))
    all_ids = set(kw) | set(sem)

    def norm(d):
        if not d:
            return {}
        vals = np.array(list(d.values()))
        lo, hi = vals.min(), vals.max()
        rng = hi - lo if hi > lo else 1.0
        return {k: (v - lo) / rng for k, v in d.items()}

    kw_n, sem_n = norm(kw), norm(sem)
    scores = {i: alpha * sem_n.get(i, 0) + (1 - alpha) * kw_n.get(i, 0) for i in all_ids}
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
    return ranked


# ---------------------------------------------------------------------
# 4. Metrics
# ---------------------------------------------------------------------
def relevance(idx, expected_cat):
    actual = str(df.iloc[idx][CATEGORY_COL])
    # Case-insensitive substring match (robust to exact-string mismatches
    # between our guessed expected_category and your actual category labels)
    return 1 if expected_cat.lower() in actual.lower() or actual.lower() in expected_cat.lower() else 0


def precision_at_k(ranked, expected_cat, k):
    top = ranked[:k]
    if not top:
        return 0.0
    return sum(relevance(i, expected_cat) for i, _ in top) / k


def mrr(ranked, expected_cat):
    for rank, (i, _) in enumerate(ranked, start=1):
        if relevance(i, expected_cat):
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked, expected_cat, k):
    top = ranked[:k]
    dcg = sum(relevance(i, expected_cat) / np.log2(r + 1) for r, (i, _) in enumerate(top, start=1))
    ideal_rels = sorted([relevance(i, expected_cat) for i, _ in top], reverse=True)
    idcg = sum(rel / np.log2(r + 1) for r, rel in enumerate(ideal_rels, start=1))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate(ranked, expected_cat):
    return {
        "P@5": precision_at_k(ranked, expected_cat, 5),
        "P@10": precision_at_k(ranked, expected_cat, 10),
        "P@15": precision_at_k(ranked, expected_cat, 15),
        "MRR": mrr(ranked, expected_cat),
        "nDCG@15": ndcg_at_k(ranked, expected_cat, 15),
    }


# ---------------------------------------------------------------------
# 5. Run everything
# ---------------------------------------------------------------------
print("[6/6] Running keyword/semantic/hybrid retrieval for all 14 queries...", flush=True)
results = []
print(f"{'Query':<40}{'True':<6}{'Best mode':<10}{'KW P@15':<9}{'SEM P@15':<9}{'HYB P@15':<9}")
for q, true_label, expected_cat in target_queries:
    kw_ranked = keyword_search(q, top_k=15)
    sem_ranked = semantic_search(q, top_k=15)
    hyb_ranked = hybrid_search(q, top_k=15)

    kw_metrics = evaluate(kw_ranked, expected_cat)
    sem_metrics = evaluate(sem_ranked, expected_cat)
    hyb_metrics = evaluate(hyb_ranked, expected_cat)

    # Which mode performs best overall (by nDCG@15)?
    scores = {"keyword": kw_metrics["nDCG@15"], "semantic": sem_metrics["nDCG@15"], "hybrid": hyb_metrics["nDCG@15"]}
    best_mode = max(scores, key=scores.get)
    # Map best mode to expected label convention: keyword-best -> short, semantic-best -> long, hybrid-best -> appropriate
    implied_label = {"keyword": "short", "semantic": "long", "hybrid": "long"}[best_mode]
    agrees = "YES" if implied_label == true_label else "NO"

    row = {
        "query": q, "true_label": true_label, "expected_category": expected_cat,
        "keyword": kw_metrics, "semantic": sem_metrics, "hybrid": hyb_metrics,
        "best_mode": best_mode, "implied_label": implied_label, "agrees_with_label": agrees,
    }
    results.append(row)
    print(f"{q[:38]:<40}{true_label:<6}{best_mode:<10}{kw_metrics['P@15']:<9.2f}{sem_metrics['P@15']:<9.2f}{hyb_metrics['P@15']:<9.2f}  agree={agrees}")

with open("results/phase3_retrieval_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

n_agree = sum(1 for r in results if r["agrees_with_label"] == "YES")
print(f"\nLabel-retrieval agreement: {n_agree}/{len(results)} = {n_agree/len(results):.2%}")
print("Saved full results to results/phase3_retrieval_results.json")
