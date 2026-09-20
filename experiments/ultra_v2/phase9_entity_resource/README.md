# ULTRA v2 Phase 9 — bilingual Wikipedia titles (resource)

Option 2 dump build + frozen v2 match rule. Scored once: **`PHASE9 PARTIALLY SUPPORTED`**.

- Dumps: `dumps/` (gitignored `.sql.gz`), dated `https://dumps.wikimedia.org/urwiki/20260901/`
- Table: `artifacts/bilingual_titles.csv` (gitignored; SHA in the prereg)
- Design freeze: `PHASE9_PREREGISTRATION.md` (§3.2a v2 rule)
- Report: `PHASE9_CONTROLLED_EXPERIMENT.md` / `PHASE9_PER_QUERY.csv`
- Common-word list: `resources/google-10000-english-no-swears.txt`
- Runner: `run_phase9.py` (Method-D BM25 only; no fusion)
