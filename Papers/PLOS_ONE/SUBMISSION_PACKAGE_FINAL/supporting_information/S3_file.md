# S3 File. Dataset provenance and reconstruction notes

This note describes how the frozen retrieval collection used in this study relates to a third-party Urdu news compilation. It does **not** contain article text.

The full corpus files `data/clean_articles.csv` and `data/urdu_news.csv` are **not** included in Supporting Information. They are not redistributed in the project GitHub repository. Redistribution permission for the underlying news article text has not been independently verified.

## Frozen collection used for all official M0 scores

| Item | Value |
| --- | --- |
| Local filename | `data/clean_articles.csv` |
| Articles | 111,860 |
| Bytes | 540,050,203 |
| SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Document identifier | CSV row index (`source_doc_id`) |
| Indexed field | concatenated headline and body (`combined_text`) |

## Third-party source

The local precursor `data/urdu_news.csv` (111,861 records) is schema- and size-consistent with Shahane, Urdu News Dataset, Kaggle Version 1, file `urdu-news-dataset-1M.csv`. That Kaggle listing cites Hussain, Mughal, Ali, Hassan, and Daudpota, Urdu News Dataset 1M, Mendeley Data, V3, doi:10.17632/834vsxnb99.3.

A SHA-256 identity check between a fresh provider download and the local precursor was not completed. Researchers should obtain the source dataset from Kaggle and/or Mendeley under those providers’ terms.

The compilation title uses “1M”. The file used here has 111,861 precursor records and 111,860 frozen articles. The string “1M” is the public dataset title and a depositor description claim; it is not a verified row count of the local file.

## Precursor to frozen file (111,861 → 111,860)

The only documented transform is: drop incomplete rows, then concatenate headline and news text into `combined_text`, then write `clean_articles.csv`.

The local precursor has 111,860 well-formed eight-field records plus **one truncated last record** (three fields only). That incomplete row is dropped. Deduplication was not used.

A complete, non-truncated public file, if one exists, would not necessarily drop a row. Identity of a reconstruction still depends on matching this truncated precursor or matching the frozen SHA-256 above.

Local precursor (not uploaded): 276,791,832 bytes; SHA-256 `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062`; 111,861 CSV records.

## How to verify a reconstructed corpus

After obtaining a third-party copy and applying the same drop-null / concatenate-text step:

1. Confirm 111,860 articles.
2. Compute SHA-256 of the reconstructed `clean_articles.csv`.
3. Compare to `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.

A Python helper that performs only this check (it does not modify the dataset) is in the project repository: `experiments/publication_audit/verify_corpus_hash.py`.

pandas `to_csv` bit-identity is not guaranteed across library versions. The SHA-256 of the frozen file is the identity used in this study.

## Freeze parameters (unchanged)

These values are recorded in S1 File and were not altered for this package:

- BM25 k1 = 1.5, b = 0.75
- Retrieve 50 documents; official cutoff 5
- Routing: URDU and MIXED → Urdu BM25; ROMAN → Method D (romanized-document BM25)
- Roman Urdu dictionary: `models/roman_urdu_dict_expanded.json`, 198 keys, SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`
- Development/validation ExactSource Hit@5: 68/78 = 87.18%; nDCG@5 = 0.8107; MRR = 0.797

S1 File is a historical freeze JSON. Its `test_set` field still names H001–H040. Official unseen evaluations reported in the article are K001–K040 and U001–U040, not a replacement of the freeze hashes or BM25 parameters.

## Code and labels that are shared

The project GitHub repository provides M0 code, the Roman Urdu dictionary, sealed query files, Annotator-1 qrels, and these Supporting Information files. It does not provide the third-party article CSV.

Official metrics in the article were copied from sealed Phase 8–12 reports and were not recomputed for this package.
