# Phase 15 step 1b — Colab cells

Paste these into a new Colab notebook. Runtime: **T4 GPU**. Do not run them on the local CPU machine.

This file does not change `step1_pilot_colab.py`. The optional cell is a later numerical check. It does not replace the timed 500-document run.

Do not open `experiments/ultra_v2/benchmark/test`. Do not encode queries. Do not compute Hit@k or any other retrieval score. One model only:

`ibm-granite/granite-embedding-311m-multilingual-r2` at `44399559930365213510b1ee2eb15ded83374f0e`.

## Script interface (quoted from `step1_pilot_colab.py`)

The docstring command is:

```text
python step1_pilot_colab.py --corpus /content/clean_articles.csv --out-dir /content/phase15_granite_step1
```

`argparse` defines two required arguments and no others:

- `--corpus` — "Path to the frozen clean_articles.csv copy."
- `--out-dir` — "Directory for the JSON summary. Must not be OneDrive or the git repo."

The only file the script writes is `step1_pilot_summary.json` inside `--out-dir`:

```text
out_path = os.path.join(args.out_dir, "step1_pilot_summary.json")
```

With the docstring paths, that file is `/content/phase15_granite_step1/step1_pilot_summary.json`. The script sets `"embeddings_written": False`. It does not write a `.npy`.

`--out-dir` must stay `/content/phase15_granite_step1`. The script exits if that path contains `onedrive` or sits inside a checkout that has both `.git` and `experiments/ultra_v2`. A clone under `/content/ULTRA_Project` is a checkout, so do not use a folder inside the clone as `--out-dir`.

`data/clean_articles.csv` is ignored by `.gitignore` (`data/*.csv`). A git clone does not contain the corpus. Copy it onto Colab local disk in cell 4.

Packages named in the script docstring (torch is already on Colab; do not pip-install it):

```text
pip install "sentence-transformers>=5.1.2" "transformers>=4.57.3" huggingface_hub pandas numpy
```

The script does not pin exact versions of `huggingface_hub`, `pandas`, or `numpy`. The `>=` floors match the model card's recorded `sentence-transformers` 5.1.2 and `transformers` 4.57.3.

---

## Cell 1 — confirm T4

```python
# Pehle yeh dekho: session T4 GPU par hai ya nahi.
# GPU nahi hai, ya naam T4 nahi hai, to yahin STOP.
# Colab menu: Runtime > Change runtime type > T4 GPU. Phir session restart.
# Local computer par yeh cell mat chalana. Wahan CUDA nahi hai.

import shutil
import torch

if not torch.cuda.is_available():
    raise SystemExit("STOP. CUDA nahi hai. CPU par embed mat karo.")

name = torch.cuda.get_device_name(0)
total = torch.cuda.get_device_properties(0).total_memory
print("GPU:", name)
print("VRAM_bytes:", total)
print("VRAM_GiB:", round(total / (1024 ** 3), 2))

with open("/proc/meminfo", encoding="utf-8") as f:
    for line in f:
        if line.startswith("MemTotal"):
            print(line.strip())
            break

disk = shutil.disk_usage("/content")
print("disk_total_bytes:", disk.total)
print("disk_free_bytes:", disk.free)
print("disk_free_GiB:", round(disk.free / (1024 ** 3), 2))

if "T4" not in name:
    raise SystemExit("STOP. GPU T4 nahi hai (%s). Runtime T4 par lao." % name)
print("T4 OK. Agle cell par jao.")
```

## Cell 2 — install the packages the script names

```python
# Torch ko pip se install ya upgrade mat karo. Colab ka CUDA wala torch rehne do.
# Neeche wali line script ke docstring se hai. Versions change mat karna.

!pip install "sentence-transformers>=5.1.2" "transformers>=4.57.3" huggingface_hub pandas numpy

import pandas
import numpy
import huggingface_hub
import transformers
import sentence_transformers

print("sentence_transformers", sentence_transformers.__version__)
print("transformers", transformers.__version__)
print("huggingface_hub", huggingface_hub.__version__)
print("pandas", pandas.__version__)
print("numpy", numpy.__version__)
```

## Cell 3 — get the script onto Colab

Use one option. Both put the same file on local disk. Neither option is a second model.

`data/clean_articles.csv` clone mein nahi aayega. Woh cell 4 ka kaam hai.

### Option A — git clone

The remote is `https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS.git`, branch `ultra-v2-phase15-granite`.

```python
# Sirf script lene ke liye clone hai. TEST folder mat kholna.
# Corpus is clone mein nahi hai, kyunki data/*.csv gitignore par hai.

!git clone --branch ultra-v2-phase15-granite --single-branch --depth 1 https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS.git /content/ULTRA_Project

from pathlib import Path
script = Path("/content/ULTRA_Project/experiments/ultra_v2/phase15_granite/step1_pilot_colab.py")
print("script_exists:", script.is_file())
if not script.is_file():
    raise SystemExit(
        "STOP. Clone mein step1_pilot_colab.py nahi hai. "
        "Yeh file abhi GitHub par push nahi hui. Option B: file upload karo."
    )
```

If this raises `STOP` because the file is missing, the branch on GitHub does not yet contain the local pilot script. Use option B. Do not clone a different branch and do not switch models.

### Option B — upload the file yourself

On your computer the file is:

`experiments/ultra_v2/phase15_granite/step1_pilot_colab.py`

```python
# Apne computer se sirf step1_pilot_colab.py upload karo.
# TEST ki koi file upload mat karna. Queries ki file bhi nahi.

from google.colab import files
from pathlib import Path

uploaded = files.upload()
if "step1_pilot_colab.py" not in uploaded:
    raise SystemExit("STOP. step1_pilot_colab.py upload nahi hui.")
Path("/content/step1_pilot_colab.py").write_bytes(uploaded["step1_pilot_colab.py"])
print("uploaded_bytes:", Path("/content/step1_pilot_colab.py").stat().st_size)
```

After option A the script path is `/content/ULTRA_Project/experiments/ultra_v2/phase15_granite/step1_pilot_colab.py`. After option B it is `/content/step1_pilot_colab.py`. Cell 5 uses one variable for that path.

## Cell 4 — corpus onto Colab local disk, then SHA-256

Expected SHA-256, the frozen Phase 3 value:

`8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

Step 1 measured the same file at 540,050,203 bytes. Copy to `/content/clean_articles.csv` (local disk). Do not leave it only on Drive, and do not put the pilot output under OneDrive.

Run **one** copy block, then the hash block.

### Copy option 1 — Drive, then copy to `/content`

Put `clean_articles.csv` in Google Drive first (from the PC file `data/clean_articles.csv`). Set `DRIVE_CSV` to that Drive path.

```python
# Drive sirf copy ke liye hai. Embed Drive path par mat likhna.
# DRIVE_CSV ko apni Drive wali file ke path se badlo.

from google.colab import drive
import shutil

drive.mount("/content/drive")
DRIVE_CSV = "/content/drive/MyDrive/clean_articles.csv"  # apna path yahan likho
shutil.copyfile(DRIVE_CSV, "/content/clean_articles.csv")
print("copied_to_/content/clean_articles.csv")
```

### Copy option 2 — browser upload

A 540 MB browser upload often fails midway. If it does, use the Drive copy instead. Do not hash a partial file and continue.

```python
from google.colab import files
from pathlib import Path

uploaded = files.upload()
if "clean_articles.csv" not in uploaded:
    raise SystemExit("STOP. clean_articles.csv upload nahi hui.")
Path("/content/clean_articles.csv").write_bytes(uploaded["clean_articles.csv"])
print("uploaded_bytes:", Path("/content/clean_articles.csv").stat().st_size)
```

### Hash block — mismatch means STOP

```python
# Yeh frozen corpus ka SHA hai. Match na ho to embed mat karna.
# TEST file yahan mat rakhna.

import hashlib
import os

path = "/content/clean_articles.csv"
expected = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
expected_bytes = 540050203

size = os.path.getsize(path)
print("bytes:", size)
if size != expected_bytes:
    raise SystemExit("STOP. File size %s hai, frozen size %s hai. Copy adhuri hai." % (size, expected_bytes))

h = hashlib.sha256()
with open(path, "rb") as f:
    while True:
        block = f.read(8 * 1024 * 1024)
        if not block:
            break
        h.update(block)
got = h.hexdigest()
print("sha256:", got)
if got != expected:
    raise SystemExit("STOP. SHA mismatch. Pilot mat chalana.")
print("SHA match. Cell 5 chala sakte ho.")
```

### If the model download returns 401

If `snapshot_download` in cell 5 or in an optional cell returns HTTP 401, set a Hugging Face token in Colab secrets, then rerun the download. Do not paste the token into the notebook.

Sidebar key icon → Add a secret named `HF_TOKEN` → enable notebook access. Then run:

```python
# Sirf tab chalana jab download 401 de. Token notebook mein mat likhna.
import os
from google.colab import userdata

os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")
os.environ["HUGGING_FACE_HUB_TOKEN"] = os.environ["HF_TOKEN"]
print("HF_TOKEN set:", bool(os.environ.get("HF_TOKEN")))
```

## Cell 5 — run the pilot

Set `SCRIPT` to the path from cell 3. This is the timed run. Let it finish. Do not start the optional cell while this cell is running.

The script has no batch-size flag. Batch size 8 and `random.seed(15)` are constants inside the file. Leave them for this first run.

```python
# Timed pilot. 500 docs, seed 15, max_length 32768, batch 8.
# Queries nahi. TEST nahi. Score nahi.
# Output folder clone ke andar mat rakhna, aur OneDrive par mat rakhna.

SCRIPT = "/content/ULTRA_Project/experiments/ultra_v2/phase15_granite/step1_pilot_colab.py"
# Agar option B use kiya tha, upar wali line hata kar yeh use karo:
# SCRIPT = "/content/step1_pilot_colab.py"

import subprocess
import sys

# Yeh wahi command hai jo script ke docstring mein hai.
# Colab shell magic Python variable expand nahi karti, is liye subprocess.
subprocess.check_call(
    [
        sys.executable,
        SCRIPT,
        "--corpus",
        "/content/clean_articles.csv",
        "--out-dir",
        "/content/phase15_granite_step1",
    ]
)
```

### If this cell dies with CUDA out of memory

`max_length` 32768 is a truncation ceiling. The script pads each batch to the longest document in that batch, not to 32768. A long article in a batch of 8 can still exhaust T4 memory. Token lengths are not known until this run's census.

If the log says CUDA out of memory:

1. Stop. Do not change the model id, the revision, `SAMPLE_SEED = 15`, `SAMPLE_N = 500`, or `CANDIDATE_MAX_LENGTH = 32768`.
2. In the Colab copy of `step1_pilot_colab.py`, change only `CANDIDATE_BATCH_SIZE = 8` to `4`. If it OOMs again, try `2`, then `1`.
3. Rerun this same cell. The new JSON's `candidate_batch_size` field is the batch that actually ran. Keep that file. Do not mix it with a crashed run.
4. If batch size 1 still OOMs, stop and bring the error back. Do not shorten `max_length` and do not switch models in this step.

## Cell 6 — print and download the pilot summary

The script writes one file: `step1_pilot_summary.json`. Download it before the Colab session ends. `/content` is wiped when the runtime is deleted.

```python
# Sirf summary JSON. Embedding matrix script ne disk par nahi likhi.
# Is file mein retrieval score nahi hai.

import json
from google.colab import files
from pathlib import Path

path = Path("/content/phase15_granite_step1/step1_pilot_summary.json")
if not path.is_file():
    raise SystemExit("STOP. step1_pilot_summary.json nahi mili.")
text = path.read_text(encoding="utf-8")
print(text)
files.download(str(path))
```

---

## Optional cell — fp16 vs fp32 on the first 30 of the same 500

Run this only after cell 5 has finished and cell 6 can see `step1_pilot_summary.json`. Skip it if you only need the timing file. This cell does not edit the pilot script and does not rerun the 500-document clock.

It is a numerical check of the **same** checkpoint (`44399559930365213510b1ee2eb15ded83374f0e`), once in fp16 and once in fp32, at the same `max_length` 32768. It is not a second model and not a retrieval comparison.

The 30 documents are `sample_index[:30]` from the pilot JSON (the first 30 draws from `random.seed(15)` / `random.sample` of 500). Do not call `random.sample` again. A new draw, or a different Python version, would not be the same 30 rows. Sanity-check batch size is 1 so this cell is less likely to OOM. That batch is not the pilot's batch of 8.

This cell writes a second file the pilot script does not write:

`/content/phase15_granite_step1/step1_fp16_fp32_sanity.json`

```python
# OPTIONAL. Main pilot ke BAAD chalana. Timing wali run ko dobara mat chalana.
# SAME model, SAME revision. fp16 aur fp32 sirf number check hai.
# Doosra model nahi. Query nahi. Hit@k nahi.
# Pehle 30 docs usi 500-doc sample ke hain jo summary JSON mein sample_index hai.

import gc
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

SUMMARY = Path("/content/phase15_granite_step1/step1_pilot_summary.json")
CORPUS = "/content/clean_articles.csv"
OUT = Path("/content/phase15_granite_step1/step1_fp16_fp32_sanity.json")
MODEL_ID = "ibm-granite/granite-embedding-311m-multilingual-r2"
REVISION = "44399559930365213510b1ee2eb15ded83374f0e"
MAX_LEN = 32768

summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
if summary.get("model_id") != MODEL_ID or summary.get("model_revision") != REVISION:
    raise SystemExit("STOP. Summary kisi aur model ki hai.")
if summary.get("sample_seed") != 15 or summary.get("sample_n") != 500:
    raise SystemExit("STOP. Sample seed 15 ya n=500 nahi hai.")
index30 = list(summary["sample_index"][:30])
if len(index30) != 30:
    raise SystemExit("STOP. sample_index mein 30 rows nahi hain.")

df = pd.read_csv(CORPUS, encoding="utf-8-sig")
if "combined_text" not in df.columns:
    raise SystemExit("STOP. combined_text column nahi hai.")
texts = df["combined_text"].fillna("").astype(str).tolist()
docs = [texts[i] for i in index30]

local_dir = snapshot_download(
    repo_id=MODEL_ID,
    revision=REVISION,
    ignore_patterns=["onnx/*", "openvino/*", "openvino_model.bin", "openvino_model.xml", "*.onnx"],
)

def embed(target):
    # Ek waqt par sirf ek copy GPU par rakho, taake T4 OOM na ho.
    model = None
    used_key = None
    for key in ("dtype", "torch_dtype"):
        try:
            model = SentenceTransformer(
                local_dir,
                device="cuda",
                model_kwargs={key: target},
            )
            used_key = key
            break
        except TypeError:
            model = None
    if model is None:
        raise SystemExit("STOP. Model load nahi hua.")
    want = "torch.float16" if target == torch.float16 else "torch.float32"
    seen = {str(p.dtype) for p in model.parameters()}
    if want not in seen:
        model = model.to(target)
        seen = {str(p.dtype) for p in model.parameters()}
    if int(model.max_seq_length) != MAX_LEN:
        model.max_seq_length = MAX_LEN
    prompts = getattr(model, "prompts", {}) or {}
    if prompts.get("query", "") not in ("", None) or prompts.get("document", "") not in ("", None):
        raise SystemExit("STOP. Prompts khali nahi hain.")
    arr = model.encode(
        docs,
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=True,
    )
    dtypes = sorted(seen)
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return np.asarray(arr), dtypes, used_key

fp16, fp16_dtypes, fp16_key = embed(torch.float16)
fp32, fp32_dtypes, fp32_key = embed(torch.float32)

def nan_inf(arr):
    return int(np.isnan(arr).sum()), int(np.isinf(arr).sum())

a = fp16.astype(np.float64)
b = fp32.astype(np.float64)
an = np.linalg.norm(a, axis=1)
bn = np.linalg.norm(b, axis=1)
cos = np.sum(a * b, axis=1) / np.maximum(an * bn, 1e-12)

fp16_nan, fp16_inf = nan_inf(fp16)
fp32_nan, fp32_inf = nan_inf(fp32)
report = {
    "label": "optional numerical check of the same checkpoint in fp16 and fp32",
    "same_model_not_a_variant": True,
    "model_id": MODEL_ID,
    "model_revision": REVISION,
    "queries_encoded": 0,
    "scores_computed": False,
    "hit_at_k": None,
    "n_docs": 30,
    "sample_seed": 15,
    "sample_index_first_30": index30,
    "max_length": MAX_LEN,
    "sanity_batch_size": 1,
    "note": "sanity batch is not the pilot batch; pilot timing is unchanged",
    "fp16_load_key": fp16_key,
    "fp32_load_key": fp32_key,
    "fp16_parameter_dtypes": fp16_dtypes,
    "fp32_parameter_dtypes": fp32_dtypes,
    "fp16_shape": list(fp16.shape),
    "fp32_shape": list(fp32.shape),
    "fp16_nan_count": fp16_nan,
    "fp16_inf_count": fp16_inf,
    "fp32_nan_count": fp32_nan,
    "fp32_inf_count": fp32_inf,
    "cosine_nan_count": int(np.isnan(cos).sum()),
    "cosine_min": None if np.isnan(cos).all() else float(np.nanmin(cos)),
    "cosine_mean": None if np.isnan(cos).all() else float(np.nanmean(cos)),
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
print("wrote", OUT)

from google.colab import files
files.download(str(OUT))
```

---

## Optional cell — five longest documents, one at a time

Run this only after cell 5 has written `step1_pilot_summary.json`. Skip it if you only need the timing file. It does not rerun the 500-document clock and it does not change `SAMPLE_SEED`, `SAMPLE_N`, or `CANDIDATE_MAX_LENGTH`.

This is a feasibility check on documents, not a retrieval test. It encodes the five longest corpus rows listed in `longest_5_full_corpus` (row index and token length only; the JSON has no document text). Same model, same revision, fp16, `max_length` 32768, batch size 1, one document per call. For each document it records peak VRAM, or the OOM error if that call fails, then continues. If the download returns 401, use the Colab secret `HF_TOKEN` note above before this cell.

This cell writes `/content/phase15_granite_step1/step1_longest5_vram.json`. The pilot script does not write that file.

```python
# OPTIONAL. Main pilot ke BAAD hi chalana. 500-doc wali timing dobara mat chalana.
# Yeh documents par feasibility check hai, retrieval test nahi.
# SAME model, SAME revision, fp16, max_length 32768, batch size 1.
# Paanch sab se lambe docs, ek ek karke. Query nahi. Hit@k nahi. Text print nahi.
# Agar download 401 de, upar wale HF_TOKEN secret wale note ko pehle chalao.

import gc
import json
from pathlib import Path

import pandas as pd
import torch
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

SUMMARY = Path("/content/phase15_granite_step1/step1_pilot_summary.json")
CORPUS = "/content/clean_articles.csv"
OUT = Path("/content/phase15_granite_step1/step1_longest5_vram.json")
MODEL_ID = "ibm-granite/granite-embedding-311m-multilingual-r2"
REVISION = "44399559930365213510b1ee2eb15ded83374f0e"
MAX_LEN = 32768

summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
if summary.get("model_id") != MODEL_ID or summary.get("model_revision") != REVISION:
    raise SystemExit("STOP. Summary kisi aur model ki hai.")
longest = list(summary.get("longest_5_full_corpus") or [])
if len(longest) != 5:
    raise SystemExit("STOP. longest_5_full_corpus mein 5 rows nahi hain.")
for row in longest:
    if set(row.keys()) != {"row_index", "token_length"}:
        raise SystemExit("STOP. longest_5 row mein text ya extra field hai.")

df = pd.read_csv(CORPUS, encoding="utf-8-sig")
if "combined_text" not in df.columns:
    raise SystemExit("STOP. combined_text column nahi hai.")
texts = df["combined_text"].fillna("").astype(str).tolist()

local_dir = snapshot_download(
    repo_id=MODEL_ID,
    revision=REVISION,
    ignore_patterns=["onnx/*", "openvino/*", "openvino_model.bin", "openvino_model.xml", "*.onnx"],
)

model = None
used_key = None
for key in ("dtype", "torch_dtype"):
    try:
        model = SentenceTransformer(
            local_dir,
            device="cuda",
            model_kwargs={key: torch.float16},
        )
        used_key = key
        break
    except TypeError:
        model = None
if model is None:
    raise SystemExit("STOP. fp16 model load nahi hua.")
seen = {str(p.dtype) for p in model.parameters()}
if "torch.float16" not in seen:
    model = model.to(torch.float16)
if int(model.max_seq_length) != MAX_LEN:
    model.max_seq_length = MAX_LEN
prompts = getattr(model, "prompts", {}) or {}
if prompts.get("query", "") not in ("", None) or prompts.get("document", "") not in ("", None):
    raise SystemExit("STOP. Prompts khali nahi hain.")

per_doc = []
for row in longest:
    idx = int(row["row_index"])
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    entry = {
        "row_index": idx,
        "token_length": int(row["token_length"]),
        "peak_vram_allocated_bytes": None,
        "peak_vram_reserved_bytes": None,
        "oom": False,
        "error": None,
    }
    try:
        model.encode(
            [texts[idx]],
            batch_size=1,
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        torch.cuda.synchronize()
        entry["peak_vram_allocated_bytes"] = int(torch.cuda.max_memory_allocated())
        entry["peak_vram_reserved_bytes"] = int(torch.cuda.max_memory_reserved())
    except RuntimeError as exc:
        message = str(exc)
        if "out of memory" not in message.lower():
            raise
        entry["oom"] = True
        entry["error"] = message
        torch.cuda.empty_cache()
    per_doc.append(entry)
    print(entry)
    gc.collect()

del model
gc.collect()
torch.cuda.empty_cache()

report = {
    "label": "optional feasibility check on the 5 longest documents",
    "feasibility_check_not_a_retrieval_test": True,
    "model_id": MODEL_ID,
    "model_revision": REVISION,
    "queries_encoded": 0,
    "scores_computed": False,
    "hit_at_k": None,
    "dtype": "float16",
    "fp16_load_key": used_key,
    "max_length": MAX_LEN,
    "batch_size": 1,
    "note": "one document per encode; peak VRAM is after a reset with the fp16 model already loaded; pilot timing is unchanged",
    "per_doc": per_doc,
}
OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("wrote", OUT)

from google.colab import files
files.download(str(OUT))
```

---

## What `step1_pilot_summary.json` will tell us

It reports whether the frozen CSV still matches the SHA-256, whether the row count is 111,860, token-length mean, sum, p50/p90/p99/p99.9/max and the counts above 512, 1024, 2048, 4096, 8192, and 32768 (full corpus and the 500-doc sample), the five longest corpus rows as row index plus token length with no document text, package versions (torch, transformers, sentence_transformers, huggingface_hub, pandas, numpy, and the CUDA version string), encode time for those 500 documents, a linear full-corpus hour estimate, embedding shape and dtype, NaN and inf counts, L2 norms, peak VRAM, GPU name, and the row indices drawn with `random.seed(15)`.

Inside `encode()`, sentence-transformers sorts by length. The hour figure is linear in document count. It excludes model load and the token census. It assumes the same batch size and the same max length, with batches padded to the longest row in the batch rather than to 32768.

## What it will not tell us

It will not tell us retrieval quality. It does not encode queries, does not read TEST, and does not compute Hit@k, MRR, or any rank metric. It does not say whether Granite is better or worse than the frozen Phase 3 encoder. The optional cosine file, if you run that cell, only says how close fp16 and fp32 vectors are for 30 documents. The optional five-document file only says whether those long documents fit in T4 memory one at a time. Neither cosine nor VRAM is a retrieval score.
