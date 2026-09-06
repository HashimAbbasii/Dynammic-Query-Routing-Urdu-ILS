# PLOS ONE figure audit

Date: 6 September 2026  
Branch: `publication/plos-one-final`  
Canonical manuscript: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
PLOS figures policy: https://journals.plos.org/plosone/s/figures (checked 6 September 2026)

**Status: FIGURE STAGE — PASS WITH MINOR FIXES**

`NO SCIENTIFIC VALUES OR RESULTS WERE CHANGED.`

---

## 1. Figure Inventory

PLOS LaTeX rule in this manuscript is correct: **no `\includegraphics`**. Captions live in the `.tex` file. Image files are uploaded separately to Editorial Manager.

| Manuscript Figure | Caption title (bold lead) | Referenced file (source PNG) | EM upload file | Format | Dimensions (px) | Tagged DPI | Used in text? | SI/Main? | Action |
| ----------------- | ------------------------- | ---------------------------- | -------------- | ------ | --------------- | ---------- | ------------- | -------- | ------ |
| Fig 1 (`fig1`) | Official frozen retriever M0. | `Fig1_m0_routing.png` | `Fig1.tif` | PNG source; TIFF derivative | PNG 2019×819 RGBA @ ~200 dpi → TIFF 2019×819 RGB @ 300 dpi | PNG ~200; TIFF 300 | Yes (`Fig~\ref{fig1}`) | Main | TIFF created; PNG preserved |
| Fig 2 (`fig2`) | ExactSource Hit@5 on the Phase 2 development/validation pool ($n = 78$). | `Fig2_development_comparators.png` | `Fig2.tif` | PNG source; TIFF derivative | 2160×1260 | 300 | Yes | Main | TIFF created; PNG preserved |
| Fig 3 (`fig3`) | Descriptive script splits of frozen M0, not used for tuning. | `Fig3_script_splits.png` | `Fig3.tif` | PNG source; TIFF derivative | PNG 2520×1200 → TIFF 2250×1071 | 300 | Yes (twice) | Main | Width scaled to PLOS max 2250 px; PNG preserved |
| Fig 4 (`fig4`) | Where sealed known-item misses sit. | `Fig4_k_miss_analysis.png` | `Fig4.tif` | PNG source; TIFF derivative | 2220×1260 | 300 | Yes | Main | TIFF created; PNG preserved |
| Fig 5 (`fig5`) | Label mass on the 200 judged U Top-5 documents. | `Fig5_u_label_distribution.png` | `Fig5.tif` | PNG source; TIFF derivative | 2220×1260 | 300 | Yes | Main | TIFF created; PNG preserved |

No Supporting Information figures. SI items are tables/files only (`S1 Table`–`S4 Table`, `S1 File`–`S3 File`, `S1 Text`).

Numbering is sequential Fig 1–5. First citations appear in read order before each caption block.

---

## 2. Manuscript-to-File Cross-check

| Check | Result |
| --- | --- |
| Every `\label{figN}` has a matching in-text `Fig~\ref{figN}` | Pass. Fig 3 is cited twice (script split, then U slices). |
| Every manuscript figure has a file | Pass. Five PNG sources and five TIFF uploads. |
| Unreferenced files in `Papers/PLOS_ONE/figures/` | After cleanup: only the five PNG sources and five TIFF derivatives. A crashed 0-byte `_test_deflate.tif` was deleted. |
| Duplicate/conflicting live versions | Historical `Fig2_u_script_split.png` (U-only Success@5) is **not** in the live figures folder. It is superseded by Fig 3. Archive copies remain under `archive/` and must not be uploaded. |
| `\includegraphics` in the live manuscript | None (only a commented PLOS template header example). Correct for PLOS LaTeX. |
| Figure generator in-tree | Live `generate_figures.py` is **not** in the current tree (`Papers/PLOS_ONE/FINAL/` was removed in cleanup). Historical `archive/historical_papers/PLOS_old/_make_m0_figures.py` drew Fig 1 plus the superseded U-only Fig 2 at 200 dpi. Current Fig 2–5 PNGs match the frozen table numbers and were retained as the source of record. |

Header comments in the `.tex` file now list TIFF upload names and PNG sources. Body text, captions, tables, and metrics were not rewritten.

---

## 3. Format/Resolution Assessment

Official PLOS production requirements (https://journals.plos.org/plosone/s/figures):

- Format: TIFF or EPS only (PNG is not a production format).
- Width 789–2250 px at 300 dpi; height ≤ 2625 px at 300 dpi.
- 300–600 dpi; file size &lt; 10 MB.
- RGB 8-bit, flattened, **no alpha**, LZW TIFF, single page.
- Upload names: `Fig1.tif`, `Fig2.tif`, …
- Text in figures: Arial, Times, or Symbol, 8–12 pt.
- Captions in the manuscript, not in the image.
- Formatting is **waived until a provisional Editorial Accept**, but Editorial Manager still documents TIFF/EPS upload. Submission-ready TIFFs were therefore prepared as **derivatives**, not as replacements of the PNG sources.

| File | Width vs 789–2250 | Height vs 2625 | DPI | Size | Alpha | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| PNG Fig1 | 2019 OK | 819 OK | ~200 tagged | 69 KB | RGBA | Print width at 200 dpi would be ~10.1 in (&gt; 7.5 in max). Same pixels at 300 dpi = 6.73 in (compliant). Not upsampled. |
| PNG Fig2 | 2160 OK | 1260 OK | 300 | 114 KB | RGBA | RGBA not allowed in PLOS TIFF. |
| PNG Fig3 | **2520 over** | 1200 OK | 300 | 104 KB | RGBA | Content bbox still ~2426 px wide; crop cannot meet 2250. |
| PNG Fig4 | 2220 OK | 1260 OK | 300 | 104 KB | RGBA | Flatten only. |
| PNG Fig5 | 2220 OK | 1260 OK | 300 | 84 KB | RGBA | Flatten only. |
| TIFF Fig1–5 | all in range | all in range | 300 | 96–225 KB | none | RGB, LZW, 1 page. Fig3 2250×1071. |

Vector EPS was **not** chosen: the live sources are raster matplotlib PNGs; PLOS prefers TIFF over EPS for production robustness; there is no vector source in-tree. Recreating plots from a new script would be an unnecessary scientific-risk step.

Fonts in the PNGs are matplotlib sans-serif (DejaVu Sans), not Arial/Times/Symbol. That is a **production** font issue, not a first-submission blocker under the format waiver. Regenerating plots solely to swap fonts was not done (would not change values, but is unnecessary risk before accept).

Color is not the only carrier of information: bar values are printed on the figures; Fig 1 labels every box in text.

---

## 4. Caption Audit

| Fig | Title ≤ 15 words? | Self-contained? | Abbreviations | Consistency | Caption rewrite? |
| --- | --- | --- | --- | --- | --- |
| 1 | Yes (4) | Yes: M0 routing, not SVM/MiniLM | M0, BM25, Method D defined in nearby Methods | Matches Methods | No |
| 2 | Yes (~8–11) | Yes: n=78 ExactSource Hit@5, not Phase 12 | ExactSource Hit@5 | Values match Table 2 for the five **run** systems | No |
| 3 | Yes (10) | Yes: two metrics, must not be averaged; mixed n=4 descriptive | Hit@5 vs Success@5 | 26/28, 1/12, 17/18, 6/18, 0/4 match Results | No |
| 4 | Yes (5) | Yes: K miss location | Top-50 | 26+2+0=28; 1+1+10=12; matches K text | No |
| 5 | Yes (9) | Yes: A–E on 200 U Top-5 docs | A–E defined in caption | 41, 26, 53, 80, 0 match Table 5 (official A1) | No |

Notes (no caption edits made):

- Fig 2 plots five comparators and omits the undeployed oracle row of Table 2 (0.9103). The caption points at Table 2 and states M0 is official. This is not a false number.
- Fig 3 is a two-panel figure described as Left/Right rather than (A)/(B). PLOS prefers lettered panels. Values are correct. Not redrawn.
- Fig 5 is official U (A1) label mass. It does not mention A2, which is correct: A2 is not a main-text figure.

No caption claims 87.18% as human usefulness, mixes A1/A2, or treats A2 as official.

---

## 5. Conversion Actions

**Decision:** convert PNG → submission TIFF derivatives. Do **not** overwrite PNG sources. Do **not** regenerate scientific plots.

Script: `experiments/publication_audit/convert_figures_to_tiff.py`

Method:

1. Flatten RGBA onto white → 8-bit RGB.
2. Write TIFF with LZW, photometric RGB, no extra samples, 300 dpi, one page.
3. Fig 3 only: proportional LANCZOS resize 2520×1200 → 2250×1071 (PLOS max width). No axis or value edits.
4. Figs 1, 2, 4, 5: **no resampling**. Fig 1 dpi tag 200→300 without adding pixels.

Pillow 12 on this Windows environment crashes on compressed TIFF write. LZW was written with `tifffile` + `imagecodecs`. Those packages are **not** part of the M0 `requirements.txt` pin and are not needed to reproduce retrieval scores.

PNG SHA-256 (unchanged sources):

| PNG | SHA-256 |
| --- | --- |
| `Fig1_m0_routing.png` | `9fc389cd55cbf1b758e70aa4f074cbf1ce0cc8c77754fdaaf438e9d5a9402fdc` |
| `Fig2_development_comparators.png` | `7c283f768f25ff6276e22ff90368989871767e2a7eb04dc68d59949f1558ab95` |
| `Fig3_script_splits.png` | `4f33896067424712efdee56b7f77f68fdde05b8749b31d1256ae57b1a6de5c6e` |
| `Fig4_k_miss_analysis.png` | `b60b4643c58446b0909201eba742d4b17d1570f1020a4636beab0999be539cbd` |
| `Fig5_u_label_distribution.png` | `21b5354e77c6a00a994e5150c5640fad26a5f8daad2ee114aac08c10b5d3d21f` |

Pixel verification after conversion:

- Fig 1, 2, 4, 5 TIFF = exact RGB flatten of the PNG.
- Fig 3 TIFF = exact LANCZOS resize of that flatten (max abs pixel difference 0 vs recomputed resize).

Visual check of TIFF content: same architecture, same Hit@5 bars, same K/U counts, same miss counts, same A–E counts.

---

## 6. Files Ready for PLOS Submission

Upload these **five** files to Editorial Manager (figure item type), named exactly:

| Upload name | Path | Bytes | Mode |
| --- | --- | --- | --- |
| `Fig1.tif` | `Papers/PLOS_ONE/figures/Fig1.tif` | 96,322 | RGB LZW 300 dpi 2019×819 |
| `Fig2.tif` | `Papers/PLOS_ONE/figures/Fig2.tif` | 149,236 | RGB LZW 300 dpi 2160×1260 |
| `Fig3.tif` | `Papers/PLOS_ONE/figures/Fig3.tif` | 225,263 | RGB LZW 300 dpi 2250×1071 |
| `Fig4.tif` | `Papers/PLOS_ONE/figures/Fig4.tif` | 137,081 | RGB LZW 300 dpi 2220×1260 |
| `Fig5.tif` | `Papers/PLOS_ONE/figures/Fig5.tif` | 129,671 | RGB LZW 300 dpi 2220×1260 |

Do **not** upload the PNG sources to EM unless staff ask for originals. Keep the PNGs in git as the unresampled source of record.

---

## 7. Files Excluded and Why

| Item | Why excluded from PLOS figure upload |
| --- | --- |
| `Fig1_m0_routing.png` … `Fig5_u_label_distribution.png` | Source of record; PNG is not a PLOS production figure format. |
| `data/clean_articles.csv`, `data/urdu_news.csv` | Third-party news text; not figures; gitignored. |
| SI CSVs / md / json | Supporting Information, not main figures. |
| `archive/**` historical figures (SVM/MiniLM, old U-only Fig 2, Layer A) | Not cited in this manuscript. |
| `experiments/phase5_roman_urdu/figures/` | Development method plots; not manuscript Figs 1–5. |
| Compiled `Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf` | Review PDF; not a figure file. |
| Conversion test leftovers | Removed (`_test.tif`, `_test_lzw.tif`, `_test_deflate.tif`). |

---

## 8. Scientific Freeze Verification

Plotted values checked against the frozen manuscript:

| Figure | Values in image | Manuscript / table |
| --- | --- | --- |
| Fig 1 | M0; Unicode detector; URDU/MIXED/OTHER → Urdu BM25; ROMAN → Method D; Top-50 retrieve, Top-5 cutoff | Methods |
| Fig 2 | 0.2564, 0.2821, 0.4487, 0.5897, 0.8718 | Table 2 Hit@5 (oracle 0.9103 not plotted) |
| Fig 3 | K 26/28 and 1/12; U 17/18, 6/18, 0/4 | Results / Table 6 |
| Fig 4 | Urdu 26 / 2 / 0; Roman 1 / 1 / 10 | K miss paragraph |
| Fig 5 | A 41, B 26, C 53, D 80, E 0 (n=200) | Table 5 official U (A1) |

No Phase 11 numbers. No A2 26/40 in any figure. No axis cropping that hides Roman failure. No new experiments.

`NO SCIENTIFIC VALUES OR RESULTS WERE CHANGED.`

---

## Remaining minor items (not blockers for this stage)

1. **Fonts:** DejaVu Sans in the raster, not Arial/Times/Symbol. Address at production if PLOS requests; do not retune science.
2. **Fig 3 panel letters:** Left/Right in the caption vs PLOS (A)/(B) preference. Optional at revision.
3. **In-figure chart titles:** graphs contain descriptive titles; they do not contain “Fig 1” captions. Acceptable; PLOS still uses the manuscript captions.

NAAS (PLOS figure checker) was not run in this environment.

---

## End status

`FIGURE STAGE — PASS WITH MINOR FIXES`

`NO SCIENTIFIC RESULTS CHANGED`
