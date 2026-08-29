# Phase 12 query generation protocol

**Do this only after `PHASE12_SEALED_PROTOCOL.md` is approved.**  
**Still no retrieval. Still no labels. Still no M0 change.**

Write two files (not created in the design step):

- `queries_k.csv` — K001–K040  
- `queries_u.csv` — U001–U040  

Then compute SHA-256 of each file into `SEAL.json` **before** any search.

---

## Shared bans

While writing queries:

- Do not open H001–H040 lists, Phase 10C qrels, or `heldout_retrieval_template.csv`.
- Do not run BM25, MiniLM, or corpus keyword search to “find a good article” for subset U.
- Do not add terms to stress Roman failures you remember from earlier chats.
- Do not copy or paraphrase old H strings.
- Do not use the QTRN mixed template `Pakistan news update`.
- Do not look at Phase 11 M1 expansion lists to plant those tokens.

---

## Subset K — known-item (K001–K040)

**Columns:**  
`query_id,query_text,source_doc_id,article_category,notes`

**How to write one row:**

1. Sample a corpus row whose id is **not** a Phase 2 `QTRN_*` `source_doc_id`.  
2. Read headline (and lead if needed).  
3. Write a **title-like** query that a user might type if they wanted **that** article (shorten or light paraphrase; no extra facts from memory).  
4. Set `source_doc_id` to that row index **now**.  
5. Roman queries: character-romanize or use ordinary Roman Urdu of the **same** title; do not invent English-only queries disconnected from the headline.

**Target mix:** about 22 Urdu, 12 Roman, remainder MIXED only if both scripts appear naturally in the query. After the list is finished, run **detector counts** (script only, no search) and record them in `SEAL.json`. If MIXED is 0, that is acceptable; do not bolt on English templates to force MIXED.

**Reject a draft if:** you cannot point to one source row, or you needed retrieval to choose the source.

---

## Subset U — naturalistic (U001–U040)

**Columns:**  
`query_id,query_text,need_type,length_bin,script_intended,category,notes`

`source_doc_id` must be **empty**.

`need_type`: `factoid` | `explanatory` | `named_entity`  
`length_bin`: `short` | `medium` | `long` as in the sealed protocol.

**How to write:**

1. Pick a news **category** (sports, business, entertainment, science/tech, general).  
2. Write a query a bilingual Pakistani news user might type.  
3. Fill quota cells from the sealed protocol (§3.2).  
4. For the **4** temporal factoids, use `آج` / `aaj` / `موجودہ` / `mojooda` as a user would; do not write them to attack Method D.

**Reject a draft if:** it is a known headline copy with a hidden gold id, or it is a duplicate of another U/K string.

---

## Seal checklist (before retrieval)

- [ ] 40 K ids in order K001–K040  
- [ ] 40 U ids in order U001–U040  
- [ ] No `H` ids in these files  
- [ ] K: every `source_doc_id` in range, unique notes if two queries share a source (prefer unique sources)  
- [ ] U: all `source_doc_id` blank  
- [ ] SHA-256 written to `SEAL.json`  
- [ ] Detector counts logged **without** ranking  

**Stop.** Retrieval is a later approved step (`run_phase12.py` not written yet).
