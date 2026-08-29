# PHASE 12 HUMAN RESULTS — U001–U040 relevance of frozen M0 Top-5

Human-relevance evaluation only. **Not** ExactSource Hit@5. **Not** a K evaluation. **Not** a Phase 9 rewrite. **Not** a system change.

Phase 9 development/validation known-item ExactSource Hit@5 remains **68/78 = 0.8718**.  
Phase 12 K ExactSource Hit@5 remains **27/40 = 0.6750**.  
Those numbers are **not** mixed with the figures below.

---

## A. Experiment identity

| | |
| --- | --- |
| Evaluation | Phase 12 human relevance (U only) |
| Retrieval artifact judged | `experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv` |
| Retrieval rerun | **no** |
| M0 modified | **no** |
| H001–H040 / Phase 10C qrels / held-out template | **not used** |
| U gold `source_doc_id` | **none** (by design) |

---

## B. Dataset

| | |
| --- | --- |
| Queries | U001–U040 |
| Documents labeled | 200 (40 × 5) |
| Empty / padded hits | none |
| U006 n_hits | 28 (still 5 judged) |
| Corpus | `data/clean_articles.csv` (frozen; unused for labeling) |

---

## C. Label distribution (200 documents)

| Label | Meaning | Count |
| --- | ---: | ---: |
| A | RELEVANT | 41 |
| B | PARTIALLY_RELEVANT | 26 |
| C | TOPICALLY_RELATED | 53 |
| D | NOT_RELEVANT | 80 |
| E | AMBIGUOUS | 0 |

A+B+C+D+E = 200.

---

## D. Primary metric — Success@5

A query succeeds if **at least one** retrieved Top-5 document is **A or B**.

**Success@5 = 23 / 40 = 0.5750**

This is **not** ExactSource Hit@5. It is **not** 87.18%.

---

## E. P@5

Conservative P@5: (count of **A**) / **5** per query, then mean over 40.

**Conservative P@5 = 0.2050**

Variable-denominator P@5: (count of **A**) / min(5, n_hits). Every query had ≥5 hits, so this equals conservative P@5.

**Variable P@5 = 0.2050**

---

## F. nDCG@5

Gain mapping (Phase 12 sealed protocol, optional graded metric):

| Label | Gain |
| --- | ---: |
| A | 3 |
| B | 2 |
| C | 1 |
| D | 0 |
| E | 0 |

Mean nDCG@5 over 40 queries:

**nDCG@5 = 0.6460**

**Caveat:** C has gain 1, so a Top-5 of only topical neighbours can score **nDCG@5 = 1.0** with **zero** A/B (see U018, U035, U037–U039). Do **not** treat nDCG@5 as usefulness. Use Success@5 and MRR for that.

---

## G. MRR

Reciprocal rank of the **first A or B** document; 0 if none.

**MRR = 0.4542**

---

## H. Per-query results

| ID | Query | 1 | 2 | 3 | 4 | 5 | Succ | 1st A/B |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| U001 | آج قومی اسمبلی کا اجلاس ہے کیا | A | B | B | B | C | yes | 1 |
| U002 | aaj pakistan ka cricket match kis se hai | A | D | D | D | D | yes | 1 |
| U003 | موجودہ وزیراعظم پاکستان کون ہیں | A | A | A | C | B | yes | 1 |
| U004 | mojooda dollar rate pakistan mein kya hai | D | D | D | D | D | no | — |
| U005 | سونے کی قیمت کتنی ہے | A | A | A | A | A | yes | 1 |
| U006 | psl points table | D | D | D | D | D | no | — |
| U007 | کراچی میں رات بجلی کٹے گی | D | B | C | C | C | yes | 2 |
| U008 | lahore se islamabad train ticket price | D | D | D | D | D | no | — |
| U009 | عالمی کپ کرکٹ شیڈول پاکستان | C | B | C | C | B | yes | 2 |
| U010 | netflix pakistan subscription charges | D | D | D | D | D | no | — |
| U011 | وفاقی بجٹ کب پیش ہوگا | A | A | A | A | A | yes | 1 |
| U012 | karachi stock market closing | A | D | D | C | A | yes | 1 |
| U013 | چاند گرہن کب لگے گا | A | A | A | A | A | yes | 1 |
| U014 | 5G kab aye ga pakistan | D | D | D | D | D | no | — |
| U015 | پاکستان میں مہنگائی کیوں بڑھ رہی ہے | C | C | B | D | B | yes | 3 |
| U016 | pakistan mein berozgari kyun barh rahi hai | D | D | D | D | D | no | — |
| U017 | پاکستان کی کرکٹ ٹیم عالمی مقابلوں میں بار بار خراب کارکردگی کیوں دکھاتی ہے | B | C | B | C | D | yes | 1 |
| U018 | pakistan mein har saal flood ke baad faslon ka nuqsan itna zyada kyun hota hai | C | C | C | D | D | no | — |
| U019 | سوشل میڈیا کے غلط استعمال سے نوجوانوں کی ذہنی صحت پر کیا فرق پڑتا ہے | B | A | A | B | A | yes | 1 |
| U020 | mobile apps phone ki battery kyun jaldi khatam karti hain aur iska hall kya hai | D | D | D | D | D | no | — |
| U021 | پاکستان کی یونیورسٹیوں میں سائنس کی تحقیق دوسرے ممالک سے کیوں پیچھے رہ گئی ہے | C | C | C | B | C | yes | 4 |
| U022 | internet speed pakistan mein slow kyun rehti hai aur isko kaise behtar kiya ja sakta hai | D | C | C | B | B | yes | 4 |
| U023 | فلم انڈسٹری پاکستان میں کیوں ترقی نہیں کر پا رہی اور اس کی کیا وجہ ہے | B | D | B | D | D | yes | 1 |
| U024 | drama industry mein original stories kam kyun banti hain aur audience kya chahti hai | D | B | C | C | C | yes | 2 |
| U025 | کراچی میں روزانہ ٹریفک جام کم کرنے کے لیے کیا اقدامات کیے جا سکتے ہیں | C | C | B | C | C | yes | 3 |
| U026 | larkion ki higher education ke liye ghar walon ka support kyun zaroori hota hai | D | D | D | D | D | no | — |
| U027 | بجلی کے بحران کی وجہ سے چھوٹی صنعتوں کو کیا نقصان ہو رہا ہے | B | B | B | B | C | yes | 1 |
| U028 | foreign students pakistan ke universities mein admission kyun kam lete hain aur iski wajah kya hai | D | D | D | D | D | no | — |
| U029 | محمد رضوان | A | A | A | A | A | yes | 1 |
| U030 | virat kohli | A | A | A | A | A | yes | 1 |
| U031 | شاہ رخ خان نئی فلم | A | C | C | A | A | yes | 1 |
| U032 | mahira khan ka naya drama kab aa raha hai | D | D | D | D | D | no | — |
| U033 | عمران خان کے تازہ سیاسی بیانات | A | B | D | D | C | yes | 1 |
| U034 | wasim akram ki commentary kab start hogi | D | D | D | D | D | no | — |
| U035 | نادیہ خان کے شو میں کون آیا | C | C | C | C | D | no | — |
| U036 | nasa mars mission kab launch hoga | C | B | A | D | A | yes | 2 |
| U037 | بابر اعظم کی PSL میں کارکردگی کیسی رہی | C | C | C | C | C | no | — |
| U038 | نرگس فخری کی Hollywood فلم کون سی ہے | C | C | C | C | C | no | — |
| U039 | حریم شاہ کی YouTube ویڈیو کہاں دیکھی جائے | C | C | C | C | C | no | — |
| U040 | قائد اعظم University میں داخلے کب شروع ہیں | D | D | D | D | D | no | — |

---

## I. Breakdowns (Success@5)

| Slice | Hits | n | Rate |
| --- | ---: | ---: | ---: |
| URDU | 17 | 18 | 0.9444 |
| ROMAN | 6 | 18 | 0.3333 |
| MIXED | 0 | 4 | 0.0000 |
| factoid | 9 | 14 | 0.6429 |
| explanatory | 9 | 14 | 0.6429 |
| named_entity | 5 | 12 | 0.4167 |
| short | 9 | 12 | 0.7500 |
| medium | 6 | 16 | 0.3750 |
| long | 8 | 12 | 0.6667 |
| temporal (آج/aaj/موجودہ/mojooda) | 3 | 4 | 0.7500 |
| non-temporal | 20 | 36 | 0.5556 |

Script slices use the **detector** on the sealed query (same as retrieval). They are descriptive. They are **not** a licence to retune Method D.

---

## J. Complete failures (no A/B in Top-5)

U004, U006, U008, U010, U014, U016, U018, U020, U026, U028, U032, U034, U035, U037, U038, U039, U040.

All-D lists: U004, U006, U008, U010, U014, U016, U020, U026, U028, U032, U034, U040.

---

## K. What frozen M0 achieved on this unseen U set

On **new naturalistic queries** with human labels, frozen M0 put at least one useful (A or B) document in the Top-5 for **23 of 40** queries (**57.5%**).

Urdu-script queries were usually useful (**17/18**). Roman Method D queries were useful much less often (**6/18**). The four MIXED queries had no A/B.

This is a genuine unseen usefulness result. It does **not** support claiming ~80% or 87.18% on natural queries. Conservative P@5 is **0.205** because many successes are a single B, not five A’s.

---

## L. Valid vs invalid claims

**Valid**

- “On sealed U001–U040, frozen M0 human Success@5 = 23/40 = 0.575.”
- “On sealed K001–K040, frozen M0 ExactSource Hit@5 = 27/40.”
- “On Phase 2 development/validation known-item queries, ExactSource Hit@5 = 68/78 = 0.8718.”

**Invalid**

- Calling 23/40 ExactSource Hit@5.
- Averaging 0.575 with 0.8718 or 0.675.
- “The system achieved ~80% on unseen queries.”
- Using these 17 failures to change M0, the dictionary, or Method D (that would burn this test set).

---

## M. Stop

Human annotation of U is complete. Do not tune. Do not start a new retrieval. Do not create H041+.
