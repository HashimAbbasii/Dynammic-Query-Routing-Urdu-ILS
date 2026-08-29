# -*- coding: utf-8 -*-
"""
Phase 3 (revised) / Phase 4 -- corpus-supported 5/6-word queries.

64 queries across the 4 categories your retrieval corpus actually supports
(Business & Economics, Entertainment, Science & Technology, Sports), split:
  - 32 "short"  (headline-level single-fact lookup -- per your codebase's
                 own definition in notebooks/04_retrieval.ipynb:
                 "Short query: uses CLS pooling on headlines")
  - 32 "long"   (needs broader context/reasoning across article content --
                 "Long query: uses mean pooling on full content")
  - 16 Urdu-short, 16 Roman-short, 16 Urdu-long, 16 Roman-long
  - Balanced across all 4 categories and both 5-word / 6-word lengths

Labels here are GENUINE per the retrieval-strategy definition above, not
derived from word count -- word count is 5 or 6 for every query in this
set by design, so it cannot explain any label variation.

Run LOCALLY from repo root (needs data/clean_articles.csv, embeddings.npy,
chromadb/). Requires: pandas, numpy, chromadb, sentence-transformers,
scikit-learn, torch (already installed from the previous run).
"""

import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------
print("[1/6] Loading clean_articles.csv...", flush=True)
df = pd.read_csv("data/clean_articles.csv", encoding="utf-8-sig")
print(f"      Loaded {len(df)} rows.", flush=True)

print("[2/6] Loading embeddings.npy...", flush=True)
embeddings = np.load("data/embeddings.npy")
print(f"      Shape: {embeddings.shape}", flush=True)

print("[3/6] Connecting to ChromaDB...", flush=True)
import chromadb
client = chromadb.PersistentClient(path="data/chromadb")
collection = client.get_collection("urdu_news")
print(f"      {collection.count()} documents.", flush=True)

print("[4/6] Loading SentenceTransformer model...", flush=True)
from sentence_transformers import SentenceTransformer
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
sem_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device)
print(f"      Ready on {device}.", flush=True)

HEADLINE_COL = "Headline"
CATEGORY_COL = "Category"

print("[5/6] Building TF-IDF keyword index over headlines...", flush=True)
corpus = df[HEADLINE_COL].fillna("").astype(str).tolist()
tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=50000)
tfidf_matrix = tfidf.fit_transform(corpus)
print(f"      TF-IDF shape: {tfidf_matrix.shape}", flush=True)

# ---------------------------------------------------------------------
# 2. The 64 corpus-supported queries (genuine annotation-rule labels)
# ---------------------------------------------------------------------
target_queries = [
    {"q": 'اسٹاک مارکیٹ میں آج تیزی', "label": 'short', "category": 'Business & Economics'},
    {"q": 'نئی کمپنی نے منافع کمایا', "label": 'short', "category": 'Business & Economics'},
    {"q": 'بینک نے نئی شرح سود بڑھائی', "label": 'short', "category": 'Business & Economics'},
    {"q": 'اسٹارٹ اپ کو نئی فنڈنگ ملی', "label": 'short', "category": 'Business & Economics'},
    {"q": 'stock market mein aaj tezi', "label": 'short', "category": 'Business & Economics'},
    {"q": 'nai company ne munafa kamaya', "label": 'short', "category": 'Business & Economics'},
    {"q": 'bank ne nai shrah sood barhai', "label": 'short', "category": 'Business & Economics'},
    {"q": 'startup ko nai funding mili', "label": 'short', "category": 'Business & Economics'},
    {"q": 'مہنگائی کیوں کم نہیں ہوتی', "label": 'long', "category": 'Business & Economics'},
    {"q": 'چھوٹے کاروبار کیوں بند ہوتے', "label": 'long', "category": 'Business & Economics'},
    {"q": 'معیشت کیوں بہتر نہیں ہو رہی', "label": 'long', "category": 'Business & Economics'},
    {"q": 'سرمایہ کاری کیوں کم ہو رہی', "label": 'long', "category": 'Business & Economics'},
    {"q": 'mehngai kyun kam nahi hoti', "label": 'long', "category": 'Business & Economics'},
    {"q": 'chote karobar kyun band hote', "label": 'long', "category": 'Business & Economics'},
    {"q": 'economy kyun behtar nahi ho rahi', "label": 'long', "category": 'Business & Economics'},
    {"q": 'sarmaya kari kyun kam ho rahi', "label": 'long', "category": 'Business & Economics'},
    {"q": 'نئی فلم نے ریکارڈ توڑ دیا', "label": 'short', "category": 'Entertainment'},
    {"q": 'اداکارہ نے نیا گانا ریلیز کیا', "label": 'short', "category": 'Entertainment'},
    {"q": 'ڈرامہ کل رات نشر ہوگا', "label": 'short', "category": 'Entertainment'},
    {"q": 'گلوکار نے نیا البم لانچ کیا', "label": 'short', "category": 'Entertainment'},
    {"q": 'nai film ne record tor diya', "label": 'short', "category": 'Entertainment'},
    {"q": 'actress ne naya gana release kiya', "label": 'short', "category": 'Entertainment'},
    {"q": 'drama kal raat nashar hoga', "label": 'short', "category": 'Entertainment'},
    {"q": 'singer ne naya album launch kiya', "label": 'short', "category": 'Entertainment'},
    {"q": 'فلمیں کیوں کامیاب نہیں ہوتیں', "label": 'long', "category": 'Entertainment'},
    {"q": 'ڈرامے کا معیار کیوں گر گیا', "label": 'long', "category": 'Entertainment'},
    {"q": 'نئے اداکار کیوں مقبول نہیں ہوتے', "label": 'long', "category": 'Entertainment'},
    {"q": 'میوزک انڈسٹری کیوں پیچھے ہے', "label": 'long', "category": 'Entertainment'},
    {"q": 'filmein kyun kamyab nahi hotin', "label": 'long', "category": 'Entertainment'},
    {"q": 'drame ka miyar kyun gir gaya', "label": 'long', "category": 'Entertainment'},
    {"q": 'naye actors kyun maqbool nahi hote', "label": 'long', "category": 'Entertainment'},
    {"q": 'music industry kyun peeche hai', "label": 'long', "category": 'Entertainment'},
    {"q": 'سائنسدانوں نے نیا سیارہ دریافت کیا', "label": 'short', "category": 'Science & Technology'},
    {"q": 'نئی ٹیکنالوجی مارکیٹ میں آ گئی', "label": 'short', "category": 'Science & Technology'},
    {"q": 'کمپیوٹر کمپنی نے نیا چپ بنایا', "label": 'short', "category": 'Science & Technology'},
    {"q": 'محقق نے نئی تحقیق شائع کی', "label": 'short', "category": 'Science & Technology'},
    {"q": 'scientists ne naya sitara dhoond liya', "label": 'short', "category": 'Science & Technology'},
    {"q": 'nai technology market mein aa gayi', "label": 'short', "category": 'Science & Technology'},
    {"q": 'computer company ne naya chip banaya', "label": 'short', "category": 'Science & Technology'},
    {"q": 'researcher ne nai tehqeeq shaya ki', "label": 'short', "category": 'Science & Technology'},
    {"q": 'ٹیکنالوجی روزگار کم کیوں کرتی', "label": 'long', "category": 'Science & Technology'},
    {"q": 'خلائی تحقیق پر خرچ کیوں ضروری', "label": 'long', "category": 'Science & Technology'},
    {"q": 'نئی ایجادات سے خطرات کیوں بڑھتے', "label": 'long', "category": 'Science & Technology'},
    {"q": 'پاکستان سائنس میں پیچھے کیوں ہے', "label": 'long', "category": 'Science & Technology'},
    {"q": 'technology rozgar kam kyun karti', "label": 'long', "category": 'Science & Technology'},
    {"q": 'khalai tehqeeq par kharch kyun zaroori', "label": 'long', "category": 'Science & Technology'},
    {"q": 'nai ijadat se khatrat kyun barhte', "label": 'long', "category": 'Science & Technology'},
    {"q": 'pakistan science mein peeche kyun hai', "label": 'long', "category": 'Science & Technology'},
    {"q": 'پاکستانی ٹیم نے میچ جیت لیا', "label": 'short', "category": 'Sports'},
    {"q": 'کھلاڑی نے سنچری اسکور کی', "label": 'short', "category": 'Sports'},
    {"q": 'فٹبال ٹیم نے فائنل جیتا', "label": 'short', "category": 'Sports'},
    {"q": 'نیا کھلاڑی ٹیم میں شامل ہوا', "label": 'short', "category": 'Sports'},
    {"q": 'pakistani team ne match jeet liya', "label": 'short', "category": 'Sports'},
    {"q": 'player ne century score ki', "label": 'short', "category": 'Sports'},
    {"q": 'football team ne final jeeta', "label": 'short', "category": 'Sports'},
    {"q": 'naya player team mein shamil hua', "label": 'short', "category": 'Sports'},
    {"q": 'ٹیم کیوں ہار رہی ہے', "label": 'long', "category": 'Sports'},
    {"q": 'کھلاڑیوں کو مواقع کیوں نہیں ملتے', "label": 'long', "category": 'Sports'},
    {"q": 'نوجوان کھلاڑی کیوں پیچھے رہ جاتے', "label": 'long', "category": 'Sports'},
    {"q": 'کھیلوں میں سرمایہ کاری کیوں کم', "label": 'long', "category": 'Sports'},
    {"q": 'team kyun haar rahi hai', "label": 'long', "category": 'Sports'},
    {"q": 'players ko mauqe kyun nahi milte', "label": 'long', "category": 'Sports'},
    {"q": 'naujawan players kyun peeche reh jate', "label": 'long', "category": 'Sports'},
    {"q": 'khelon mein sarmaya kari kyun kam', "label": 'long', "category": 'Sports'},
]
print(f"\nLoaded {len(target_queries)} candidate queries "
      f"({sum(1 for r in target_queries if r['label']=='short')} short / "
      f"{sum(1 for r in target_queries if r['label']=='long')} long)")


# ---------------------------------------------------------------------
# 3. Retrieval functions
# ---------------------------------------------------------------------
def keyword_search(query, top_k=15):
    qv = tfidf.transform([query])
    sims = cosine_similarity(qv, tfidf_matrix)[0]
    idx = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in idx]


def semantic_search(query, top_k=15):
    qemb = sem_model.encode(query).tolist()
    res = collection.query(query_embeddings=[qemb], n_results=top_k)
    ids = [int(x) for x in res["ids"][0]]
    dists = res["distances"][0]
    sims = [1 - d for d in dists]
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
    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]


# ---------------------------------------------------------------------
# 4. Metrics (relevance = same category as query, exact match this time
#    since all 4 categories genuinely exist in the corpus)
# ---------------------------------------------------------------------
def relevance(idx, expected_cat):
    return 1 if df.iloc[idx][CATEGORY_COL] == expected_cat else 0


def precision_at_k(ranked, expected_cat, k):
    top = ranked[:k]
    return sum(relevance(i, expected_cat) for i, _ in top) / k if top else 0.0


def mrr(ranked, expected_cat):
    for rank, (i, _) in enumerate(ranked, start=1):
        if relevance(i, expected_cat):
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked, expected_cat, k):
    top = ranked[:k]
    dcg = sum(relevance(i, expected_cat) / np.log2(r + 1) for r, (i, _) in enumerate(top, start=1))
    ideal = sorted([relevance(i, expected_cat) for i, _ in top], reverse=True)
    idcg = sum(rel / np.log2(r + 1) for r, rel in enumerate(ideal, start=1))
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
print("[6/6] Running keyword/semantic/hybrid retrieval for 64 queries "
      "(this will take a few minutes, one embedding call per query)...", flush=True)

results = []
for n, row in enumerate(target_queries, start=1):
    q, true_label, cat = row["q"], row["label"], row["category"]
    kw_ranked = keyword_search(q, top_k=15)
    sem_ranked = semantic_search(q, top_k=15)
    hyb_ranked = hybrid_search(q, top_k=15)

    kw_m = evaluate(kw_ranked, cat)
    sem_m = evaluate(sem_ranked, cat)
    hyb_m = evaluate(hyb_ranked, cat)

    scores = {"keyword": kw_m["nDCG@15"], "semantic": sem_m["nDCG@15"], "hybrid": hyb_m["nDCG@15"]}
    best_mode = max(scores, key=scores.get)
    implied_label = {"keyword": "short", "semantic": "long", "hybrid": "long"}[best_mode]
    agrees = "YES" if implied_label == true_label else "NO"

    results.append({
        "query": q, "true_label": true_label, "category": cat,
        "keyword": kw_m, "semantic": sem_m, "hybrid": hyb_m,
        "best_mode": best_mode, "implied_label": implied_label, "agrees_with_label": agrees,
    })
    if n % 8 == 0:
        print(f"      ...{n}/{len(target_queries)} done", flush=True)

with open("results/phase4_retrieval_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------
n_agree = sum(1 for r in results if r["agrees_with_label"] == "YES")
print(f"\n{'='*70}")
print(f"OVERALL label-retrieval agreement: {n_agree}/{len(results)} = {n_agree/len(results):.2%}")
print(f"{'='*70}")

print(f"\n{'Query':<38}{'Cat':<22}{'True':<6}{'Best':<10}{'Agree'}")
for r in results:
    print(f"{r['query'][:36]:<38}{r['category'][:20]:<22}{r['true_label']:<6}{r['best_mode']:<10}{r['agrees_with_label']}")

# Breakdown by intended label
for lbl in ("short", "long"):
    sub = [r for r in results if r["true_label"] == lbl]
    n_ok = sum(1 for r in sub if r["agrees_with_label"] == "YES")
    print(f"\n{lbl.upper()} queries: {n_ok}/{len(sub)} agree = {n_ok/len(sub):.2%}")

# Breakdown by category
from collections import defaultdict
by_cat = defaultdict(list)
for r in results:
    by_cat[r["category"]].append(r)
print("\nBy category:")
for cat, sub in by_cat.items():
    n_ok = sum(1 for r in sub if r["agrees_with_label"] == "YES")
    print(f"  {cat:<25} {n_ok}/{len(sub)} = {n_ok/len(sub):.2%}")

print("\nSaved full results to results/phase4_retrieval_results.json")
