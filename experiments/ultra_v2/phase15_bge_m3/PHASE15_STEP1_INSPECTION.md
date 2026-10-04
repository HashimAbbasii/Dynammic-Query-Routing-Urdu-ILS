# PHASE15 — Step 1 Inspection Only (pre-preregistration)

**Status:** INSPECTION COMPLETE — do **not** score until preregistration (Step 2) is written and approved.  
**Date (local):** 2026-10-01  
**Frozen Phases 2–14 / TEST / PLOS/M0:** not modified.

---

## 1. Environment

| Item | Finding |
|---|---|
| Machine | Windows 11, 12th Gen Intel Core i5-1245U (10 cores / 12 logical) |
| RAM | **15.69 GB** total; **~1.8–1.9 GB free** at inspection time |
| GPU / CUDA | **None** — `nvidia-smi` unavailable; `torch.cuda.is_available() == False` |
| PyTorch | `2.13.0+cpu` |
| Python | 3.13.9 (`anaconda3`) |
| sentence-transformers | 5.7.0 (present) |
| FlagEmbedding | **Not installed** |
| Disk (C:) | **~32 GB free** |
| HF hub cache | ~1.37 GB (includes cached `intfloat/multilingual-e5-small` ~0.92 GB) |
| OpenMP note | Same Anaconda/Torch dual-`libiomp5md` conflict as Phase 3; Phase 3 used `MKL_THREADING_LAYER=SEQUENTIAL` (+ historically `KMP_DUPLICATE_LIB_OK`) |

---

## 2. Corpus SHA gate

| Item | Value |
|---|---|
| Path | `data/clean_articles.csv` |
| Computed SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Expected (all prior Program B phases) | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| **Result** | **MATCH** |
| n_docs (Phase 3 frozen) | 111,860 |

---

## 3. BGE-M3 loadability / model card (config download only — full weights not yet pulled)

Config/metadata downloaded successfully via `huggingface_hub` (no full `pytorch_model.bin` yet).

| Field | Documented / observed |
|---|---|
| HF id | `BAAI/bge-m3` |
| Main tip revision (pinned candidate) | `5617a9f61b028005a4858fdac845db406aefb181` |
| Architecture | XLM-RoBERTa (`XLMRobertaModel`), 24 layers, hidden **1024** |
| Dense embedding dim | **1024** (`1_Pooling/config.json` → `word_embedding_dimension`) |
| Pooling (model default — do not customize) | **CLS token** (`pooling_mode_cls_token=True`, `pooling_mode_mean_tokens=False`) — differs from Phase 3 e5-small **mean** pooling |
| ST modules | Transformer → Pooling → Normalize |
| Documented max sequence length | **8192** (model card / `max_position_embeddings=8194`) |
| Query instruction prefix | Model card FAQ: **BGE-M3 does not require** adding instructions to queries (unlike E5 `query:` / `passage:`) |
| Modes | Dense / sparse / multi-vector (ColBERT). **Phase 15 protocol target: DENSE-ONLY** (no sparse, no ColBERT scoring) |
| Weight file (not yet downloaded) | `pytorch_model.bin` (~2.27 GB class; model card / community size) |
| Dense-only via sentence-transformers | Supported (model card: “You also can use sentence-transformers … to generate dense embeddings”) — preferred here because FlagEmbedding is not installed and ST matches Phase 3 tooling |

**Download space check:** ~2.3 GB weights + ~0.44 GB float32 corpus matrix (111860 × 1024 × 4) + overhead ≈ **≤ 4 GB** needed. **32 GB free → disk OK.**

**RAM / load risk:** Full FP32 BGE-M3 weights alone are ~2+ GB; encode activations add more. With only **~1.9 GB free** on a 16 GB machine (CPU Torch), a local full load is **memory-tight / OOM-prone** and will compete with OS + OneDrive. Phase 3 e5-small peak RSS was ~652 MB — BGE-M3 is far larger.

---

## 4. Honest runtime estimate (CPU, this machine)

**Phase 3 reference (frozen):** e5-small corpus embed **30,948.2 s ≈ 8.6 h** on CPU (12 threads), batch 64, max_seq 512, n=111,860 (`dense_index_meta.json`).

**Scale basis (parameter count, same seq length):**  
multilingual-e5-small ≈ 118M params; BGE-M3 ≈ 568M params → **~4.8×**.

| Scenario | Estimate |
|---|---|
| CPU, max_seq=512 (Phase-3 protocol parity), param-count scale | **~40–45 hours** wall time (8.6 × 4.8 ≈ 41 h) |
| CPU, max_seq closer to BGE default 8192 on long news text | **Much worse** (often multi-day); model card itself warns to shorten max_length to speed encoding |
| Attention/width FLOPs (24L × 1024-d vs 12L × 384-d) | Can push CPU estimate **toward ~2–3× the param-only figure** → **~80–120 h** worst case if seq lengths inflate |

**GPU (Colab T4) estimate (order of magnitude):** embedding 111,860 passages on T4 with FP16 and max_length 512 is typically **tens of minutes to a few hours**, not tens of hours — exactly the use case where T4 helps.

### Recommendation

**This local machine is impractical for Phase 15 corpus embedding.** Reasons:

1. No CUDA (CPU-only Torch).  
2. ~41+ hour optimistic CPU wall time; realistically longer.  
3. ~16 GB RAM with ~1.9 GB free — high OOM / thrashing risk for BGE-M3.  
4. Dual OpenMP Anaconda/Torch conflict still present (survivable with Phase 3 launcher env, but not a reason to run a 40+ h job here).

**Recommend: Google Colab T4 (or equivalent GPU) for corpus + query embedding generation**, then score locally or on Colab against the same frozen corpus SHA and n=80 population. Keep **one** dense-only config (revision pinned, CLS pooling, dense-only, no tuning).

---

## 5. Protocol notes to carry into Step 2 preregistration (not yet written)

1. **Dense-only** mode; explicitly exclude sparse and ColBERT.  
2. Pooling: **CLS** (model default) — do not switch to mean.  
3. No E5-style `query:` / `passage:` prefixes (BGE-M3 documented behavior).  
4. Pin revision `5617a9f61b028005a4858fdac845db406aefb181` (main tip at inspection).  
5. Population: Phase 13 frozen Roman KN **n=80** (51 W1 + 29 LLM1).  
6. Honest expectation (verbatim into prereg): Phase 11 knowledge-representation gaps (FBR/CPEC/ADB/JLO; VOCAB paraphrase) are **not** expected to close the 55-point Hit@5 gap to 80%.  
7. One model, one run, no parameter search; TEST sealed.

---

## 6. Step 1 decision gate

| Check | Status |
|---|---|
| Corpus SHA matches prior phases | **PASS** |
| BGE-M3 config/metadata downloadable | **PASS** |
| Disk for weights + matrix | **PASS** (~32 GB free) |
| Local CPU runtime practical | **FAIL** (~41+ h optimistic; RAM tight) |
| Local GPU available | **FAIL** (none) |

**Proceed to Step 2 (preregistration) only after choosing execution venue** (strongly: Colab T4). Do **not** start corpus embedding on this laptop without an explicit override accepting multi-day CPU risk and possible OOM.

**STOP after Step 1 — awaiting review before Step 2.**
