# Phase 11 inventory (no retrieval)

**Status:** inventory complete. System unmodified. Dictionary unmodified. No BM25. No H001–H040 mining. No H041+.

Evidence files in this folder: `TRAIN_SPLIT_SUMMARY.json`, `TRAIN_ROMAN_TOKEN_FREQ.csv`, `CANDIDATE_TRANSFORMATIONS.csv`, `DICT_DUPLICATE_VALUES.json`.

---

## 1. Allowed data (what was inspected)

| Source | Used how |
|---|---|
| `experiments/phase2_oracle/oracle_train.csv` (n=182) | Token counts; Roman / mixed / Urdu mix |
| `models/roman_urdu_dict_expanded.json` (198 keys) | Existing aliases; English loanword keys |
| `run_phase5.py` `_VARIANT_TO_DICT_KEY` | Existing Method C spelling map |
| Train `source_doc_id` headlines | Compare title_roman vs Method D `romanize_token` (string only, **not** BM25) |
| Phase 5 `TRANSLITERATION_AUDIT.md` | Existing eval documentation; **not** used to add H terms |
| Phase 6 taxonomy / Phase 8 `FUTURE_WORK.md` | Problem class only |

**Not opened for variant discovery:** `heldout_traps.py`, Phase 10C qrels, `heldout_retrieval_template.csv`.

Train contains **zero** `H*` IDs.

| language_type | n |
|---|---|
| urdu | 99 |
| roman_urdu (`title_roman`) | **64** |
| mixed (`mixed_short`) | 19 |

Roman train queries: **639** tokens, **417** unique. In frozen dict: 211 token occurrences. Not in dict: 428 (mostly naive character romanization: `krne`, `kilie`, `karkrdgi`, …).

---

## 2. Finding that controls the whole design

For all 64 train Roman queries, **naive headline romanization = Method D romanization** (0 differing pairs).

Phase 2 `title_roman` and Method D use the same char table + reverse dict. Train Roman queries are **already in Method D spelling**.

Therefore:

- **Replacing** `krne` with pretty Roman `karne` would **break** n=78 Roman known-item.
- M1/M2 must **expand** (keep original token **and** add aliases), never substitute-away the naive form.
- User-style Roman (`kya` vs `kiya`) barely appears in train title_roman. Aliases still come from the **frozen 198-key file** and `_VARIANT_TO_DICT_KEY`, not from H001–H040.

Phase 6: leftover n=78 misses are ambiguity / neighbours, not missing overlap. Phase 8 item 3: naturalistic Roman ≠ title_roman. This inventory agrees.

---

## 3. Candidate groups

### 3.1 Roman spelling / aliases (M1)

**A. Duplicate dict values** (same Urdu, several Latin keys). Method D `rev.setdefault` keeps the **first** JSON key as the document token. Queries using a later alias will miss.

| Urdu value | Keys (JSON order) | Method D canonical | Train Roman freq of aliases |
|---|---|---|---|
| کیا | kiya, kya | **kiya** | kiya=1, kya=0 |
| آج | aaj, aj, today | **aaj** | aj=1, aaj=0, today=0 |
| سے | se, sy | **se** | se=15, sy=0 |
| نے | ne, ny | **ne** | ne=7, ny=0 |
| گیا | gaya, geya | **gaya** | (gaya not in top list as content) |
| جیت | jeet, win | **jeet** | jeet=4, win=0 |
| شکست | loss, shikast | **loss** | loss=1, shikast=0 |
| حکومت | government, hukumat | **government** | both 0 in train Roman |
| عدالت | adalat, court | **adalat** | both 0 |

**Include** query expansion: every alias → add canonical (keep original).

**B. Existing `_VARIANT_TO_DICT_KEY`:** kia/kiya→kya, nahin/nai→nahi, mai→mein. Train Roman hit: **kiya=1 only**. Still **include** (already in repo). For Method D, map kia/kya/kiya → also **kiya**.

**C. Train nondict spellings of dict keys (freq ≥ 2, not false friends):**

| original | variant | freq | decision |
|---|---|---|---|
| pakstani | pakistan | 2 | INCLUDE (keep pakstani) |
| fridi | afridi | 2 | INCLUDE (keep fridi) |
| krne | karna | 4 | INCLUDE expand only; **never drop krne** |
| kilie | — | 3 | REJECT (no safe dict target) |
| qomi | qaum | 3 | REJECT (different stem; noisy edit match) |
| bad → bada | 3 | REJECT (false friend) |

### 3.2 English loanwords (M2)

**In train Roman queries** (already frozen dict keys): pakistan 7, cricket 3, economy 3, bank 2, dollar 2, market 2, match 2, film 2, batting/team/important/loss/internet/news = 1.

On Method D these **already match** if the document Urdu value reverse-maps to that key.

**Real M2 work** is the **English ↔ Roman alias** pairs already in the 198-key file: win↔jeet, loss↔shikast, government↔hukumat, court↔adalat, today↔aaj.

**Train mixed (19/19):** tokens `pakistan`, `news`, `update` from the `Pakistan news update` template. Mixed queries use **Urdu BM25**, not Method D. **Reject** turning `update` into a Roman rule.

**Train source headlines:** no Latin tokens (Urdu script). No new loanword list from headline ASCII.

**Reject (0 train Roman; not invent from later diagnostic sets):** diesel, temperature, iphone, kab-as-stop.  
football / petrol / score are **already dict keys** with 0 train Roman hits: **no new dictionary row**; exact-key identity remains if a future query uses that exact token.

### 3.3 Mixed tokens

Train mixed = Urdu fragment + English template `Pakistan news update`. Not Roman-path inventory. Unicode detector already sends MIXED → Urdu BM25. **No M1–M4 change for mixed.**

### 3.4 Function-word stoplist (M3)

Train Roman highest-df function words:

| token | freq | decision |
|---|---|---|
| ki | 27 | INCLUDE_M3 |
| mein | 26 | INCLUDE_M3 |
| ke | 22 | INCLUDE_M3 |
| se | 15 | INCLUDE_M3 |
| ka | 13 | INCLUDE_M3 |
| ko | 11 | INCLUDE_M3 |
| aur, ne, par | 7 | INCLUDE_M3 |
| hai, bhi | 3 | optional |
| nahi | 5 | REJECT_stop (negation) |
| aaj / kab | 0 / 0 | REJECT_stop (not train-justified; would be diagnostic leakage) |

**Proposed frozen M3 list (query-side, ROMAN path only):**  
`ka, ki, ke, ko, se, mein, ne, par, aur`  
Optional add-on (pre-register, default **off**): `hai, bhi`.

---

## 4. Frozen transformation set for Phase 11 (candidates only — not applied)

**M1 expansion table** (query token → extra tokens; original always kept):

- kya, kia → kiya  
- nahin, nai → nahi  
- mai → mein  
- aj, today → aaj  
- sy → se  
- ny → ne  
- geya → gaya  
- pakstani → pakistan  
- fridi → afridi  
- krne → karna  

**M2 extra expansions** (English/Roman dict aliases):

- win → jeet  
- shikast → loss  
- hukumat → government  
- court → adalat  

(If the query already is the canonical form, no extra token required.)

**M3 stoplist:** `ka ki ke ko se mein ne par aur`  
Remove from **query** tokens on ROMAN path only after expansion. Do not remove from documents.

No new rows in `roman_urdu_dict_expanded.json`.

---

## 5. Ablations M0–M4 (to run only after this inventory is approved)

Hard gate for **every** Mx: ExactSource Hit@5 on n=78 **≥ 68/78 (0.8718)**.  
Selection **only** on Phase 2 **train** (esp. 64 Roman). **Not** H001–H040. **No H041+.**

### What stays frozen in all Mx

Unicode `detect_script`; URDU/MIXED → Urdu BM25; ROMAN → Method D **document** index; k1=1.5; b=0.75; tokenizer; 198-key reverse dict used as **document** romanizer; corpus hash; no H-query rules.

### M0 — frozen baseline

**Change:** none.  
**Eval:** n=78 ExactSource Hit@5 / nDCG@5 / MRR; train Roman Hit@5 (smoke).  
**Accept:** this is the control. Must reproduce 68/78.

### M1 — Roman spelling normalization only

**Change:** ROMAN queries only: add M1 extra tokens (§4).  
**Eval:** same metrics; primary selection = train Roman ExactSource Hit@5; gate n=78.  
**Accept:** n=78 ≥ 0.8718 **and** train Roman Hit@5 ≥ M0.  
**Reject:** any n=78 drop, or train Roman drop.

### M2 — M1 + English loanword handling

**Change:** M1 + M2 alias expansions (§4). Still query-side, ROMAN only.  
**Eval / accept:** same as M1 vs M0; tie-break train Roman nDCG@5.  
**Reject:** n=78 < 0.8718.

### M3 — M1 + Roman function-word stoplist

**Change:** M1 expansions, then drop M3 stop tokens from the ROMAN **query**.  
**Eval / accept:** n=78 ≥ 0.8718 **and** train Roman Hit@5 ≥ M0.  
**Reject:** empty queries, or n=78 drop. If M3 fails the gate, M4 is not run as an official candidate (report M3 fail only).

### M4 — M2 + M3

**Change:** M1+M2 expansions, then M3 stops.  
**Eval / accept:** n=78 ≥ 0.8718 **and** train Roman Hit@5 ≥ M0.  
**Select winner:** among M0–M4 that pass the gate, highest train Roman Hit@5; tie nDCG@5.

No human Success@5 on H001–H040 for selection. No new IR score is computed **in this inventory step**.

---

## 6. What we did *not* do

- No BM25 / no index build  
- No dictionary file edit  
- No H001–H040 inspection for variants  
- No diesel / temperature / iphone / football **new** mappings  
- No H041+

---

## 7. Beginner: what we do after this inventory is approved

We still **do not** touch H001–H040 and we still **do not** make H041+.

Next implementation step (only if you say yes):

1. Save the small expansion list and stoplist as frozen JSON (still not searching).  
2. Run **M0, M1, M2, M3, M4** on **train Roman + the official n=78 set**.  
3. Throw away any version that scores below **68/78**.  
4. Pick the best remaining version using **train** only.  
5. Stop. Only later, with a new protocol, we would test that frozen winner on **new** queries (H041+).

If every M1–M4 fails the 68/78 gate, we **keep today’s frozen system** and the thesis reports 87.18% known-item plus the already-finished 62.5% human diagnostic — without pretending we reached 80% usefulness.
