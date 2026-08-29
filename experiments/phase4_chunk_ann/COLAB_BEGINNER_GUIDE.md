# Phase 4A on Google Colab (T4) — beginner steps

The local CPU index job is **stopped**. Incomplete files are in:

`experiments/phase4_chunk_ann/artifacts/_cpu_partial_backup/`

You will **not** train a new model. You will only **embed chunks on a GPU** and build the same chunk search index.

Time on T4: often **1–2 hours**. Keep the Colab tab open.

---

## What you need

1. A Google account
2. Google Drive with about **8 GB free**
3. The file `data/clean_articles.csv` on this PC (~515 MB)

---

## Part A — Put the corpus on Google Drive

1. On this PC, open File Explorer.
2. Go to:

   `C:\Users\User\OneDrive\Documents\ULTRA_Project\data`

3. Find `clean_articles.csv`.
4. In a browser, open [https://drive.google.com](https://drive.google.com) and sign in.
5. Click **New → New folder**. Name it exactly:

   `ULTRA_Phase4A`

6. Open that folder. Click **New → File upload**.
7. Choose `clean_articles.csv`. Wait until Drive shows the upload is finished (515 MB can take several minutes).

Do **not** start Colab until this upload is complete.

---

## Part B — Open the notebook on Colab

1. Open [https://colab.research.google.com](https://colab.research.google.com)
2. Sign in with the **same** Google account.
3. Click **File → Upload notebook**.
4. Choose this file from your PC:

   `C:\Users\User\OneDrive\Documents\ULTRA_Project\experiments\phase4_chunk_ann\Phase4A_Colab_T4.ipynb`

---

## Part C — Turn on the T4 GPU

1. In Colab: **Runtime → Change runtime type**
2. Hardware accelerator: **T4 GPU**
3. Click **Save**
4. Click **Runtime → Run all**

   Or run cells one by one with the play button on the left of each cell.

5. The **first code cell** will ask: *Permit this notebook to access your Google Drive?*  
   Click **Connect to Google Drive** → choose your account → **Allow**.

6. Cell 1 should print something like:

   `GPU: Tesla T4`

   If it prints `GPU: NONE`, go back to Part C and pick T4 again, then **Runtime → Restart session**, then **Run all**.

---

## Part D — While it runs

- You should see lines like: `articles 2000/111860 chunks=...`
- Progress is saved to Drive every 500 articles. If Colab disconnects, **Run all** again and it will **resume**.
- Do not close the browser tab. Do not shut the laptop lid if that sleeps the machine.
- Free Colab can disconnect. If it does, reconnect, check GPU is still T4, and Run all again.

**Done** looks like this printed at the end:

- `n_chunks`: **644100**
- `chroma_count`: **644100**
- a zip file on Drive: `ULTRA_Phase4A/phase4a_chunk_index.zip`

---

## Part E — Copy the index back to this PC

### Easier way (zip)

1. In Google Drive, open folder `ULTRA_Phase4A`.
2. Download **two** things:
   - `phase4a_chunk_index.zip` (about 1–3 GB)
   - `index_build.json` (small)
3. Wait until both downloads finish.
4. Unzip `phase4a_chunk_index.zip`. Inside you should see a folder named `artifacts`.
5. Copy the **contents** of that unzipped `artifacts` folder into:

   `C:\Users\User\OneDrive\Documents\ULTRA_Project\experiments\phase4_chunk_ann\artifacts\`

6. Copy `index_build.json` into:

   `C:\Users\User\OneDrive\Documents\ULTRA_Project\experiments\phase4_chunk_ann\`

   Do **not** copy into `_cpu_partial_backup`. Leave that folder alone.

After copying you should have:

```text
experiments/phase4_chunk_ann/index_build.json
experiments/phase4_chunk_ann/artifacts/chroma_chunks/     (the new GPU index)
experiments/phase4_chunk_ann/artifacts/chunk_embeddings.f32
experiments/phase4_chunk_ann/artifacts/chunk_article_ids.npy
experiments/phase4_chunk_ann/artifacts/index_progress.json
```

---

## Part F — Evaluate on this PC (not on Colab)

Eval needs your local Full Article index and Headline index. Those stay here.

Open PowerShell:

```powershell
cd C:\Users\User\OneDrive\Documents\ULTRA_Project\experiments\phase4_chunk_ann
$env:KMP_DUPLICATE_LIB_OK='TRUE'
python run_phase4a.py --stage eval
```

Do **not** run `--stage index` on this PC after Colab, unless Colab failed and you want to go back to the CPU backup.

---

## If something goes wrong

| Problem | What to do |
| --- | --- |
| `clean_articles.csv not found` | The Drive folder name must be `ULTRA_Phase4A` and the CSV must be inside it. Re-run the path cell. |
| `GPU: NONE` | Runtime → Change runtime type → T4 GPU → Restart session |
| Colab disconnected mid-way | Reconnect, check T4, Run all. It resumes from `index_progress.json` on Drive. |
| Want to cancel Colab and use this PC again | Tell me. We can restore `artifacts/_cpu_partial_backup` and resume CPU. |

You are **not** retraining the SVM. You are **not** using H001–H040. Colab only builds the chunk search index.
