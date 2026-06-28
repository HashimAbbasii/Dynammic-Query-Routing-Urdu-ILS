# 🔍 Adaptive Dynamic Query Routing for Urdu Information Retrieval

[![Python](https://img.shields.io/badge/Python-3.11.15-blue?style=for-the-badge&logo=python)](https://python.org)
[![ML](https://img.shields.io/badge/ML-SVM-green?style=for-the-badge)](https://scikit-learn.org)
[![NLP](https://img.shields.io/badge/NLP-Urdu%20IR-orange?style=for-the-badge)](https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS)
[![Accuracy](https://img.shields.io/badge/Accuracy-100%25-brightgreen?style=for-the-badge)](https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS)
[![AUC-ROC](https://img.shields.io/badge/AUC--ROC-1.000-brightgreen?style=for-the-badge)](https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **MS Thesis Project** — The first dynamic query intent classifier for Urdu Information Retrieval, replacing static length-based routing with a learned semantic SVM approach that achieves **100% routing accuracy** versus 50% for the static baseline — at **zero cost** and **1000× faster** than LLMs.

---

## 📋 Table of Contents

1. [About](#-about)
2. [Problem Statement](#-problem-statement)
3. [System Architecture](#️-system-architecture)
4. [Novel Contributions](#-novel-contributions)
5. [Key Results](#-key-results)
6. [LLM Comparison](#-llm-comparison)
7. [Robustness Validation](#-robustness-validation)
8. [Dataset](#-dataset)
9. [Project Structure](#-project-structure)
10. [Setup & Installation](#️-setup--installation)
11. [How to Run](#-how-to-run)
12. [Results & Graphs](#-results--graphs)
13. [Examiner Q&A](#-examiner-qa-defense-ready)
14. [Citation](#-citation)
15. [Contact](#-contact)

---

## 👨‍💻 About

| Field          | Details                                           |
|----------------|---------------------------------------------------|
| **Author**     | Hashim Shazad (Roll: 243259)                      |
| **Program**    | MS Artificial Intelligence                        |
| **Supervisor** | Dr. Adnan Aslam                                   |
| **Base Paper** | ULTRA — Bashir, Qaiser, Hussain (PIEAS 2026)      |
| **GitHub**     | [@HashimAbbasii](https://github.com/HashimAbbasii)|

---

## ❗ Problem Statement

Urdu is Pakistan's national language with **230 million+ speakers**, yet existing Information Retrieval (IR) systems treat all queries the same way — using a **static length threshold (θ = 150 chars)** to decide search strategy.

**Problems with static routing:**
- Short queries → always keyword search (even if semantic is better)
- Long queries → always semantic search (even if keyword is better)
- **Result:** Only 50% correct routing decisions
- Roman Urdu (e.g., *"cricket match"* written in Latin script) is completely ignored

**Our Solution:** Replace the static threshold with a **learned SVM classifier** that reads 8 semantic features of each query and dynamically decides the best search strategy — with 100% accuracy.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY INPUT                             │
│              (Urdu Script  OR  Roman Urdu)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Roman Urdu Detection  │
              │  (Script Analysis)     │
              └────────────┬───────────┘
                           │
              ┌────────────▼───────────┐
              │   Roman Urdu?          │
              └──────┬─────────┬───────┘
                    YES        NO
                     │         │
                     ▼         │
        ┌────────────────────┐ │
        │ Dictionary         │ │
        │ Transliteration    │ │
        │ (179-word lexicon) │ │
        └────────┬───────────┘ │
                 │             │
                 └──────┬──────┘
                        │
                        ▼
          ┌─────────────────────────┐
          │   8-Feature Extraction  │
          │  ─────────────────────  │
          │  1. Character Count     │
          │  2. Word Count          │
          │  3. Avg Word Length     │
          │  4. Urdu Char Ratio     │
          │  5. Unique Word Ratio   │
          │  6. Stopword Ratio      │
          │  7. Punctuation Count   │
          │  8. Numeric Presence    │
          └────────────┬────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │  Dynamic SVM Classifier │
          │  (Trained on 369 queries│
          │   F1 = 1.00, AUC=1.000) │
          └────────────┬────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │   Confidence Score      │
          │   (0% ─────────── 100%) │
          └────────────┬────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    HIGH (≥85%)   MED (60-85%)  LOW (<60%)
         │             │             │
         ▼             ▼             ▼
    Full Semantic   Hybrid       Expand
       Search       Search        Query
         │             │             │
         └─────────────┴─────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │  ChromaDB Vector Search │
          │  (HNSW Cosine Similarity│
          │   111,860 Urdu articles)│
          └────────────┬────────────┘
                       │
                       ▼
          ┌─────────────────────────┐
          │   Top-15 Relevant       │
          │   Articles Returned     │
          └─────────────────────────┘
```

---

## 🚀 Novel Contributions

This thesis makes **6 original contributions** to Urdu IR:

| # | Contribution | Impact |
|---|-------------|--------|
| 1 | **Dynamic SVM Routing** | Replaces static θ=150 threshold; 100% vs 50% accuracy |
| 2 | **8-Feature Semantic Classifier** | Char, word, lexical, Urdu-ratio features — all validated |
| 3 | **Confidence-Based 3-Tier Routing** | HIGH / MEDIUM / LOW adaptive search strategy |
| 4 | **Roman Urdu Support Layer** | 179-word dictionary (6× expansion from 30) |
| 5 | **LLM Comparison Benchmark** | Validated against GPT-4, GPT-3.5, Claude, Gemini |
| 6 | **Ablation + Robustness Study** | Cohen's d=3.58, 12/12 robustness checks passed |

---

## 🏆 Key Results

| Experiment | Result |
|------------|--------|
| Baseline Precision@15 | **96%** |
| Roman Urdu Precision@15 | **92.5%** |
| Dynamic SVM Accuracy | **100%** |
| Static Threshold Accuracy | **50%** |
| F1 / Precision / Recall | **1.00 / 1.00 / 1.00** |
| AUC-ROC | **1.000** |
| Confidence Score (avg) | **98.18%** |
| Dictionary Expansion | **30 → 179 words (6×)** |
| Training Dataset | **369 real Urdu queries** |
| Topics Covered | **15+ domains** |

---

## 🤖 LLM Comparison

> Can an SVM beat expensive LLMs at query routing?

| Method | Accuracy | Latency | Cost |
|--------|----------|---------|------|
| Static Threshold | ❌ 50% | 0.0004 ms | Free |
| Gemini | ❌ 50% | ~900 ms | Paid |
| GPT-3.5 | ✅ 100% | ~600 ms | Paid |
| Claude | ✅ 100% | ~700 ms | Paid |
| GPT-4 | ✅ 100% | ~800 ms | Paid |
| **Our SVM** | ✅ **100%** | **0.45 ms** | **Free** |

**Conclusion:** Our SVM matches top-tier LLMs at **zero API cost** and is **~1,500× faster** than GPT-4.

---

## 🔬 Robustness Validation

All 4 examiner concerns addressed with statistical evidence:

### 1. Is 369 queries sufficient?
- **Cohen's d = 3.58** (Large effect — Cohen 1988)
- Large effect requires only 52 samples/class → we have 176+193 = **3.7× more**
- ✅ **PASS**

### 2. Is 100% accuracy = overfitting?
- Learning curve **train-validation gap = 0.00%**
- Both curves converge to 100% together
- Overfitting would show large gap — ours shows none
- ✅ **PASS**

### 3. Is SVM sensitive to hyperparameters?
- Tested C = {0.01, 0.1, 1, 10, 100, 1000}
- Accuracy range across all C values = **only 0.54%**
- ✅ **ROBUST**

### 4. External validation?
- 50 completely unseen Urdu queries (5 new topics)
- Result: **100% accuracy, 99.27% avg confidence**
- ✅ **PASS**

**Final Robustness Score: 12/12 checks PASSED ✅**

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| Total Corpus | 111,860 Urdu news articles |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Database | ChromaDB (HNSW, cosine similarity) |
| Training Queries | 369 (Urdu + Roman Urdu, manually labeled) |
| External Validation | 50 unseen queries (5 new topics) |
| Topics | Cricket, Politics, Economy, Education, Health, Technology, Sports, Weather, Crime, Entertainment, Agriculture, Defense, Judiciary, Science, Religion |

---

## 📁 Project Structure

```
ULTRA_Project/
│
├── 📓 notebooks/
│   ├── 01_preprocessing.ipynb          # Data cleaning & normalization
│   ├── 02_embeddings.ipynb             # Multilingual sentence embeddings
│   ├── 03_chromadb.ipynb               # ChromaDB vector database setup
│   ├── 04_retrieval.ipynb              # Top-15 article retrieval
│   ├── 05_roman_urdu.ipynb             # Roman Urdu detection layer
│   ├── 06_dynamic_classifier.ipynb     # SVM classifier training
│   ├── 07_evaluation.ipynb             # Results, metrics & charts
│   ├── 08_baseline_fix.ipynb           # Baseline comparison (ULTRA)
│   ├── 09_ablation.ipynb               # Ablation study (8 features)
│   ├── 10_llm_comparison.ipynb         # LLM vs SVM comparison
│   ├── 11_confidence_routing.ipynb     # 3-tier confidence routing
│   ├── 12_roman_urdu_expansion.ipynb   # Dictionary 30→179 expansion
│   ├── 13_*.ipynb                      # Additional experiments
│   ├── 14_robustness_validation.ipynb  # ✅ Final robustness study
│   └── DEMO_defense.ipynb              # 🎯 Live defense demo
│
├── 🧠 models/
│   ├── svm_classifier.pkl              # Trained SVM (369 queries)
│   ├── scaler.pkl                      # Feature StandardScaler
│   ├── training_info.json              # Training metadata
│   └── roman_urdu_dict_expanded.json   # 179-word transliteration dict
│
├── 📦 data/
│   ├── training_queries_real.py        # 369 labeled queries (tuples list)
│   ├── training_data.json              # 40 queries (reference only)
│   ├── urdu_news.csv                   # ⚠️ Large file — contact author
│   └── chromadb/                       # ⚠️ Large file — contact author
│
├── 📈 results/
│   ├── cohens_d_analysis.png
│   ├── learning_curves.png
│   ├── c_parameter_sensitivity.png
│   ├── external_validation.png
│   ├── robustness_final_report.png
│   ├── robustness_report.csv
│   ├── ablation_study.png
│   ├── llm_comparison.png
│   ├── confidence_routing.png
│   └── all_methods_comparison.png
│
├── .gitignore
├── .gitattributes
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Anaconda / Miniconda
- Python 3.11.15
- VS Code with Jupyter extension (recommended)

### Step 1 — Clone Repository

```bash
git clone https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS.git
cd Dynammic-Query-Routing-Urdu-ILS
```

### Step 2 — Create Conda Environment

```bash
conda create -n ultra_env python=3.11.15
conda activate ultra_env
```

### Step 3 — Install Dependencies

```bash
pip install sentence-transformers chromadb scikit-learn
pip install pandas numpy matplotlib seaborn joblib
pip install jupyter notebook ipykernel
```

### Step 4 — Large Files (Not on GitHub)

These files exceed GitHub's size limit. Contact the author for access:

```
data/urdu_news.csv         # 111,860 Urdu news articles (~500MB)
data/chromadb/             # Pre-built vector database
data/*.npy                 # Pre-computed embeddings
```

> 📧 Contact: See [Contact](#-contact) section below

---

## ▶️ How to Run

### ⚠️ Important: How to Load Training Data

```python
# CORRECT way to load training_queries_real.py
import training_queries_real as tqr

queries = [item[0] for item in tqr.training_queries]
labels  = [item[1] for item in tqr.training_queries]
```

> ⚠️ `training_queries_real.py` is a **tuples list, NOT a function**. Don't call it.

### Run Notebooks in Order

```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 14
```

### Load Pre-Trained Model (Shortcut)

```python
import joblib

svm  = joblib.load('models/svm_classifier.pkl')
scaler = joblib.load('models/scaler.pkl')

# Predict on a new query
features = extract_features("کرکٹ میچ کا نتیجہ")   # your feature extractor
features_scaled = scaler.transform([features])
prediction = svm.predict(features_scaled)
confidence = svm.predict_proba(features_scaled).max() * 100

print(f"Route: {prediction[0]}, Confidence: {confidence:.2f}%")
```

---

## 📈 Results & Graphs

All graphs are saved in the `results/` folder:

| File | Description |
|------|-------------|
| `cohens_d_analysis.png` | Effect size — Cohen's d = 3.58 (Large) |
| `learning_curves.png` | Train vs Val accuracy — gap = 0.00% |
| `c_parameter_sensitivity.png` | SVM C sensitivity — range = 0.54% |
| `external_validation.png` | 50 unseen queries — 100% accuracy |
| `robustness_final_report.png` | 12/12 robustness checks summary |
| `ablation_study.png` | All 8 features validated |
| `llm_comparison.png` | SVM vs GPT-4/Claude/Gemini |
| `confidence_routing.png` | 3-tier routing distribution |
| `all_methods_comparison.png` | Complete experiment comparison |

---

## 🎤 Examiner Q&A (Defense Ready)

**Q: Is 369 queries enough for training?**
> Cohen's d = 3.58 — this is a **Large Effect Size** (Cohen, 1988). Large effect requires only 52 samples per class. We have 176 + 193 = 369 — that is 3.7× more than required.

**Q: 100% accuracy means overfitting?**
> Our learning curve shows **train-validation gap = 0.00%**. Both curves converge to 100% together. Overfitting produces a large gap between them — ours shows none.

**Q: Can SVM overfit to specific hyperparameters?**
> We tested C = 0.01 to 1000 (6 orders of magnitude). Accuracy range across all values = **only 0.54%**. The model is highly robust to parameter choice.

**Q: No external validation was done?**
> We tested 50 completely unseen Urdu queries across 5 new topics never seen during training. Result: **100% accuracy, 99.27% average confidence**.

---

## 📝 Citation

If you use this work, please cite:

```bibtex
@mastersthesis{shazad2025dynamicurdu,
  author    = {Hashim Shazad},
  title     = {Adaptive Dynamic Query Routing for Urdu Information Retrieval},
  school    = {Air University Islamabad},
  year      = {2025},
  program   = {MS Artificial Intelligence},
  supervisor= {Dr. Adnan Aslam}
}
```

---

## 📬 Contact

**Hashim Shazad**
MS Artificial Intelligence

[![GitHub](https://img.shields.io/badge/GitHub-HashimAbbasii-black?style=flat-square&logo=github)](https://github.com/HashimAbbasii)

---

> ⭐ **Star this repo** if you find it useful for Urdu NLP research!

---

*Built with Python 3.11 · scikit-learn · ChromaDB · Sentence Transformers*
