# 🔍 Adaptive Dynamic Query Routing for Urdu Information Retrieval

<!-- TOC -->
## 📑 Table of Contents
- [About](#-about)
- [Overview](#-overview)
- [Key Results](#-key-results)
- [System Architecture](#️-system-architecture)
- [Project Structure](#-project-structure)
- [Setup Instructions](#️-setup-instructions)
- [Novel Contributions](#-novel-contributions)
- [Dataset](#-dataset)
- [Phase 2.5 — Human Retrieval Validation](#-phase-25--human-retrieval-validation-pilot)
- [Phase 3A — Feature Pipeline Verification](#-phase-3a--feature-pipeline-verification)
- [Phase 3B — Final Frozen Evaluation](#-phase-3b--final-frozen-evaluation)
- [§5b — Statistical Comparisons: Which Test Means What](#-5b--statistical-comparisons-which-test-means-what)
- [Examiner Q&A](#-examiner-qa)
- [Contact](#-contact)

---

[![Python](https://img.shields.io/badge/Python-3.11.15-blue?style=for-the-badge&logo=python)]()
[![ML](https://img.shields.io/badge/ML-SVM-green?style=for-the-badge)]()
[![NLP](https://img.shields.io/badge/NLP-Urdu%20IR-orange?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)]()
[![Earlier CV Result](https://img.shields.io/badge/Earlier%20Training%2FCV-100%25%20Accuracy%2C%20AUC%201.000-lightgrey?style=for-the-badge)]()
[![Frozen Evaluation](https://img.shields.io/badge/Frozen%20Phase%203B%20Eval-86.00%25%20Accuracy-blueviolet?style=for-the-badge)]()

---

## 👨‍🎓 About

|                |                                              |
| -------------- | -------------------------------------------- |
| **Student**    | Hashim Shazad                                |
| **Program**    | MS Artificial Intelligence                   |
| **Supervisor** | Dr. Adnan Aslam                              |
| **Base Paper** | ULTRA — Bashir, Qaiser, Hussain (PIEAS 2026) |

---

## 📌 Overview

This project proposes a **dynamic query intent classifier for Urdu Information Retrieval**, replacing the static length-based routing of ULTRA with a learned semantic SVM approach.

> *"We propose a dynamic query intent classifier for Urdu IR, replacing static length-based routing with a learned semantic approach. Earlier training/cross-validation experiments showed 100% routing accuracy versus 50% for the static baseline. On a later, held-out, frozen 50-query evaluation set built specifically to test generalization, the SVM-based router achieved 86.00% accuracy compared with 84.00% for a fixed word-count baseline — a small, non-statistically-significant improvement (exact McNemar p = 1.0000). Separately, human retrieval judgments indicate that word count alone is an imperfect proxy for retrieval need, particularly in the 5-word boundary region."*

---

## 🏆 Key Results

### Earlier training / cross-validation results

These were obtained during model development and internal cross-validation, **before** the frozen, independent Phase 3B evaluation described below. They demonstrate the approach is learnable, not that it generalizes at this level — see the Phase 3B section for the generalization test.

| Experiment                | Result                  |
| ------------------------- | ----------------------- |
| Baseline Precision@15     | **96%**                 |
| Roman Urdu Precision@15   | **92.5%**               |
| Dynamic SVM Accuracy (CV) | **100%**                |
| Static Threshold Accuracy | **50%**                 |
| Confidence Score (avg)    | **98.18%**              |
| Dictionary Expansion      | **30 → 179 words (6x)** |
| Dataset Size              | **369 real queries**    |

### 🧊 Final frozen evaluation (Phase 3B) — held-out generalization test

This is the final, methodologically strongest result: a trained V2 SVM and a word-count baseline evaluated against a **frozen 60-query set (50 primary + 10 secondary)** that neither model saw during training.

| Metric              | SVM (V2)   | Word-count baseline |
| -------------------- | ---------- | -------------------- |
| Correct (of 50)      | 43         | 42                   |
| Accuracy              | **86.00%** | 84.00%               |
| Macro Precision       | 84.29%     | 81.62%                |
| Macro Recall          | 83.09%     | 81.62%                |
| Macro F1              | 83.64%     | 81.62%                |

**Difference:** +1 correct query, +2.00 percentage points accuracy, +2.02 macro-F1 points — a small descriptive advantage for the SVM that is **not statistically significant** (see [§5b](#-5b--statistical-comparisons-which-test-means-what)).

### 🤖 LLM Comparison (earlier experiment)

| Method           | Accuracy   | Speed      | Cost     |
| ---------------- | ---------- | ---------- | -------- |
| Static Threshold | ❌ 50%      | 0.0004ms   | Free     |
| GPT-4 Style      | ✅ 100%     | ~800ms     | Paid     |
| GPT-3.5 Style    | ✅ 100%     | ~600ms     | Paid     |
| Claude Style     | ✅ 100%     | ~700ms     | Paid     |
| Gemini Style     | ❌ 50%      | ~900ms     | Paid     |
| **Our SVM**      | ✅ **100%** | **0.45ms** | **Free** |

> Note: this comparison predates the frozen Phase 3B evaluation and reflects the earlier training/CV setup, not the held-out generalization test.

---

## 🏗️ System Architecture

```
User Query (Urdu / Roman Urdu)
         ↓
Roman Urdu Detection
         ↓
   [Roman Urdu?] ──Yes──→ Dictionary Transliteration (179 words)
         │                         ↓
         No                  Urdu Script Query
         ↓                         ↓
8-Feature Extraction ←────────────┘
         ↓
Dynamic SVM Classifier
         ↓
Confidence Score (0-100%)
         ↓
┌────────────────────────────────┐
│ HIGH (≥85%) → Full Semantic   │
│ MED  (60%)  → Hybrid Search   │
│ LOW  (<60%) → Expand Query    │
└────────────────────────────────┘
         ↓
ChromaDB Vector Search (HNSW)
         ↓
Top-15 Relevant Articles
```

---

## 📁 Project Structure

```
ULTRA_Project/
├── notebooks/
│   ├── 01_preprocessing.ipynb      # Data cleaning
│   ├── 02_embeddings.ipynb         # Sentence embeddings
│   ├── 03_chromadb.ipynb           # Vector database
│   ├── 04_retrieval.ipynb          # Top-15 retrieval
│   ├── 05_roman_urdu.ipynb         # Roman Urdu layer
│   ├── 06_dynamic_classifier.ipynb # SVM classifier
│   ├── 07_evaluation.ipynb         # Results & charts
│   ├── 08_baseline_fix.ipynb       # Baseline comparison
│   ├── 09_ablation.ipynb           # Ablation study
│   ├── 10_llm_comparison.ipynb     # LLM comparison
│   ├── 11_confidence_routing.ipynb # Confidence routing
│   ├── 12_roman_urdu_expansion.ipynb # Dictionary expansion
│   └── DEMO_defense.ipynb          # Live demo
├── models/
│   ├── svm_classifier.pkl          # Trained SVM model
│   ├── scaler.pkl                  # Feature scaler
│   ├── training_info.json          # Training metadata
│   └── roman_urdu_dict_expanded.json # 179-word dictionary
├── data/
│   └── training_queries_real.py    # 369 training queries
├── validate/
│   ├── phase2_5/                   # Human retrieval validation pilot
│   ├── phase3/
│   │   ├── phase3a_extractor.py            # Canonical 8-feature extractor
│   │   ├── phase3_evaluation_set.csv       # Frozen 60-query eval set
│   │   ├── phase3b_svm_predictions.csv     # Frozen SVM predictions
│   │   └── phase3b_wordcount_predictions.csv # Frozen baseline predictions
│   ├── phase3_retrieval_verification.py
│   └── phase4_retrieval_verification.py
├── results/
│   ├── ablation_study.png
│   ├── llm_comparison.png
│   ├── confidence_routing.png
│   └── all_methods_comparison.png
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository
```
git clone https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS.git
cd Dynammic-Query-Routing-Urdu-ILS
```

### 2. Create Environment
```
conda create -n ultra_env python=3.11.15
conda activate ultra_env
```

### 3. Install Dependencies
```
pip install sentence-transformers chromadb scikit-learn
pip install pandas numpy matplotlib seaborn joblib
```

### 4. Large Files (Contact Author)
These files exceed GitHub limits — contact for access:
```
data/urdu_news.csv        # 111,860 Urdu articles
data/chromadb/            # Vector database
data/*.npy                # Embeddings
```

### 5. Run Notebooks in Order
```
01 → 02 → 03 → 04 → 05 → 06 → 07
```

---

## 🔬 Novel Contributions

1. **Dynamic SVM Routing** — replaces static θ=150 threshold
2. **8-Feature Semantic Classifier** — char, word, lexical, Urdu ratio features
3. **Confidence-Based 3-Tier Routing** — HIGH/MEDIUM/LOW adaptive search
4. **Roman Urdu Support** — 179-word dictionary (6x expansion)
5. **LLM Comparison** — validated against GPT-4, GPT-3.5, Claude, Gemini
6. **Ablation Study** — all 8 features validated as collectively robust
7. **Independent Frozen Evaluation** — Phase 3B tests generalization on a 60-query held-out set never used in training or feature verification
8. **Human Retrieval Validation** — Phase 2.5 empirically tests the 5–6 word SHORT/LONG boundary with real human relevance judgments rather than assumption

---

## 📊 Dataset

| Property         | Value                                 |
| ---------------- | ------------------------------------- |
| Total Articles   | 111,860 Urdu news articles            |
| Embedding Model  | paraphrase-multilingual-MiniLM-L12-v2 |
| Vector DB        | ChromaDB (HNSW cosine similarity)     |
| Training Queries | 369 (Urdu + Roman Urdu)               |
| Topics Covered   | 15+ (Cricket, Politics, Economy...)   |

---

## 🧪 Phase 2.5 — Human Retrieval Validation (Pilot)

**Status: Complete.**

A pilot of **33 queries** (5w=4, 6w=6, 7w=9, 8w=6, 9w=4 bare-event queries, plus 4 anchor queries; 18 Urdu / 15 Roman Urdu) was retrieved under `HEADLINE` and `FULL_CONTENT` modes and independently human-judged at ranks 1–5, producing **330 judgment rows**.

**Human relevance distribution:**

| Label               | Count |
| -------------------- | ----- |
| Not relevant          | 199   |
| Relevant              | 86    |
| Partially relevant    | 45    |

**Key finding:** the 5-word bare-event bucket (n = 4) showed a decision-rule verdict of **SHORT** with 75% query-level agreement — this **contradicts** the provisional §4 rule that had defaulted bare-event queries to LONG. The 6-word bucket, and the 5–6 word combination overall, were **query-dependent / inconclusive**.

**Important caveat:** retrieval exported top-15 results, but judgments were only collected for ranks 1–5. Any reported nDCG@15 / P@10 / P@15 in this project is therefore based on **judged depth 5**, not full depth 15 — this should be stated explicitly wherever those metrics are cited.

`HYBRID` and `HEADLINE_KEYWORD_TFIDF` modes were **not** human-judged in this pilot. A separate 8-row LLM-judging smoke test (1 query, HEADLINE only) exists but is **not** pilot-scale and must not be presented as human validation.

---

## 🧪 Phase 3A — Feature Pipeline Verification

**Status: Complete.**

A standalone canonical feature extractor (`validate/phase3/phase3a_extractor.py`) was built and verified against the deployed scaler and SVM, using the exact 8-feature order:

```
urdu_ratio, roman_ratio, has_urdu, has_roman,
query_len, char_len, mixed, urdu_chars
```

Verification confirmed:
- Scaler expects 8 features; SVM expects 8 features; extractor outputs 8 — no schema mismatch.
- `scaler.transform()` succeeds on extractor output.
- Recomputed feature means across all 409 training queries match `scaler.mean_` with **deviation = 0.0**.

No fitting or retraining occurred in this phase — it is inference-pipeline verification only, confirming the deployed model receives exactly the features it was trained on.

---

## 🧪 Phase 3B — Final Frozen Evaluation

**Status: Complete.**

A frozen 60-query evaluation set (`validate/phase3/phase3_evaluation_set.csv`, 50 primary with gold labels + 10 secondary) was scored by the trained V2 SVM and a word-count baseline. This file is frozen and must not be modified — its committed MD5 is `faef0d264ec2915baf1f3948a9b78e66` (GitHub-normalized; original freeze-time MD5 was `b442ab2ffbd85a98734d49e62450aaa9`, differing only by BOM/line-ending representation, with content independently re-verified identical: 60 rows, 13 columns, P3_001–P3_060, matching bucket/script/label distributions and word counts).

**Results (primary 50):**

| Metric              | SVM     | Word-count |
| -------------------- | ------- | ----------- |
| Accuracy              | 86.00%  | 84.00%      |
| Macro Precision       | 84.29%  | 81.62%      |
| Macro Recall          | 83.09%  | 81.62%      |
| Macro F1              | 83.64%  | 81.62%      |

**Confusion matrices:**

SVM:
```
              Pred SHORT   Pred LONG
True SHORT        12           4
True LONG          3          31
```

Word-count:
```
              Pred SHORT   Pred LONG
True SHORT        12           4
True LONG          4          30
```

**Paired comparison:** both correct = 41, both wrong = 6, SVM-only correct = 2, WC-only correct = 1, discordant pairs = 3. Exact McNemar p = **1.0000** — not statistically significant, and the small discordant count means this comparison has low statistical power. The +2 percentage point difference should be read as descriptive, not as evidence of general SVM superiority.

**Strongest defensible conclusion:**
> "The SVM-based dynamic router achieved 86.0% accuracy on a frozen 50-query primary evaluation set, compared with 84.0% for the fixed word-count baseline. Although the SVM obtained a small descriptive improvement (+2 percentage points), the difference was not statistically significant (exact McNemar p=1.0000). Separately, human retrieval judgments indicated that word count alone is an imperfect proxy for retrieval need, particularly in the 5-word boundary region."

---

## 📐 §5b — Statistical Comparisons: Which Test Means What

This project reports **two different McNemar's tests**, comparing different things. They must not be conflated:

| Test | Compares | Result |
| ---- | -------- | ------ |
| Earlier Stage-C evaluation | Old (pre-relabel) model vs. new (post-relabel, V2) model, on an external Stage-C test set, following the Phase 2 label-audit fix | p = 0.000002 (statistically significant improvement from fixing the mislabeled training data) |
| Phase 3B frozen evaluation | New V2 SVM vs. word-count baseline, on the frozen 60-query held-out set | Exact p = 1.0000 (not statistically significant) |

The first test shows that **fixing the training data labels mattered a great deal** — it is a before/after comparison of the same model family. The second test shows that, on the final frozen generalization benchmark, **the SVM's edge over a simple word-count baseline is small and not statistically demonstrated** at this sample size. Both are legitimate, independently true findings; they answer different questions and neither one supersedes the other.

---

## 🎓 Examiner Q&A

**Q: Your README says 100% accuracy in one place and 86% in another — which is correct?**
A: Both are correct, for different experiments, at different stages. 100% (with AUC 1.000) reflects earlier training/cross-validation results, which show the approach is learnable. 86.00% is the result on a later, independent, frozen 50-query evaluation set designed to test generalization to unseen queries — this is the number that should be treated as the project's headline generalization result.

**Q: Is the SVM statistically better than the word-count baseline?**
A: Not demonstrably, on the frozen Phase 3B set. The SVM is descriptively ahead by 2 percentage points (86.00% vs 84.00%), but the exact McNemar test on the 3 discordant query pairs gives p = 1.0000 — not significant. With only 50 primary queries, the test has low power to detect a difference this small.

**Q: Why are there two different McNemar p-values in this project (0.000002 and 1.0000)?**
A: They test different comparisons. p = 0.000002 is from an earlier Stage-C test comparing the old, mislabeled-data model against the new, relabeled V2 model — it shows the label-audit fix produced a real improvement. p = 1.0000 is from the Phase 3B frozen evaluation, comparing the new V2 SVM against a word-count baseline — a different pair of models, a different question. See [§5b](#-5b--statistical-comparisons-which-test-means-what).

**Q: What did the human relevance judgments (Phase 2.5) add beyond the automatic metrics?**
A: They tested whether the SHORT/LONG routing boundary near 5–6 words matches how a human would judge retrieval need. The 5-word bare-event bucket empirically behaved like SHORT (contradicting the provisional rule that assumed LONG), while 6-word and combined 5–6 word buckets were query-dependent. This is real evidence that word count alone is an imperfect signal near the boundary — motivating, but not itself constituting, the case for a learned router.

**Q: Are the Phase 2.5 nDCG@15/P@10/P@15 numbers trustworthy at full depth?**
A: They should be reported with the caveat that they are computed from rank-1–5 human judgments only, even though retrieval exported top-15. Treat them as depth-5-judged approximations, not true depth-15/10 metrics.

**Q: Why keep the older 100%/50% and LLM-comparison results in the README at all if they're superseded?**
A: They are not fabricated, and they document real earlier experiments in the project's development history. They are clearly labeled as earlier training/CV results and distinguished from the final frozen Phase 3B evaluation, which is the methodologically stronger, held-out result an examiner should weight most heavily.

---

## 📬 Contact

**Hashim Shazad**  
MS Artificial Intelligence  
GitHub: [@HashimAbbasii](https://github.com/HashimAbbasii)

---

⭐ Star this repo if you find it useful!
