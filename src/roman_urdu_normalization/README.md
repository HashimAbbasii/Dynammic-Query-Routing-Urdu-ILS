# Module 1 — Generic Roman Urdu normalization

## 1. Purpose

This package is an **isolated, reusable surface-form normalizer** for Latin-script text that may include Roman Urdu. Future research modules may optionally call it. It is **not** part of frozen M0 and is **not** used by Phase 12 evaluation.

## 2. Scientific hypothesis

Generic Roman Urdu surface-form normalization *may* reduce lexical mismatch caused by spelling variation (case, spacing, punctuation, informal letter elongation) while remaining independent of individual test queries.

This module does **not** claim that the hypothesis is true. It only implements a candidate intervention that can later be tested on **new, separated** development data.

## 3. What “normalization” means here

A deterministic string → string transform with independently switchable layers. No retrieval, no corpus I/O, no dictionary lookup, no Method D, no routing.

Public API:

```python
from src.roman_urdu_normalization import normalize_roman_urdu, NormalizationConfig, explain_roman_urdu_normalization

normalize_roman_urdu("MERA   dost!!")
# "mera dost"

explain_roman_urdu_normalization("mera   dost").transformations
# ["whitespace"]
```

## 4–5. Rules implemented and why

| Layer | Default | What it does | Why |
| --- | --- | --- | --- |
| Unicode NFKC | on | Compatibility composition; ZWNJ/ZWJ → space | Stable string identity; matches the repo's existing leakage-check convention for joiners |
| Lowercase | on | Latin case fold | Informal Roman Urdu and English IR typically ignore case |
| Punctuation spacing | on | Non-word punctuation → space; hyphens/apostrophes kept | Separates tokens without deleting letters |
| Whitespace | on | Collapse runs; strip | Generic cleanup |
| Repeated ASCII letters (3+ → 2) | **off** | Optional informal elongation | Conservative: `good`/`book` unchanged; `soooo` → `soo` when enabled |
| Vowel/surface mapping | **off / unimplemented** | Flag only | See exclusions |

URLs and emails are masked before later layers so they are not split or lowercased internally.

## 6. Deliberately not implemented

- **No use of `roman_urdu_dict_expanded.json`.** Dictionary expansion is a future candidate experiment, not Module 1.
- **No vowel deletion or grapheme rewriting** (`boht`↔`bohot`, `aa`↔`a`). Too easy to merge distinct English/Roman tokens and names.
- **No Method C `_VARIANT_TO_DICT_KEY` aliases** (`kia`→`kya`). Those live in frozen Phase 5 Method C, not this module.
- **No Phase-12-derived word mappings.**
- **No collapsing all repeated characters to one** (would damage `good`, `book`).
- **Not wired into M0 retrieval.**

## 7. Known risks

- Lowercasing changes visual form of acronyms (`CPEC` → `cpec`) while preserving letter sequence.
- Punctuation spacing can split `hello,world` (intended) but would also split unusual punctuation in code-like strings if they are not URLs.
- Repeat collapse to two letters does **not** produce canonical dictionary spellings (`boooht` → `booht`, not `boht`).
- Aggressive future vowel rules could harm names and English.

## 8. Usage

From the repository root (no install required):

```python
from src.roman_urdu_normalization import NormalizationConfig, normalize_roman_urdu

normalize_roman_urdu("MERA   dost!!")

cfg = NormalizationConfig(repeated_character_normalization=True)
normalize_roman_urdu("soooo", cfg)
```

## 9. Tests

```text
python -m unittest tests.test_roman_urdu_normalization
```

## 10. Later experimental evaluation (not done here)

A future module should:

1. Freeze this code.
2. Build a **new** development query sample that is not K001–K040 or U001–U040.
3. Ablate layers (repeat on/off, etc.) against a lexical mismatch diagnostic — still not Phase 12.
4. Only then, if justified, run a **new sealed** retrieval test. Do not retune on U001–U040.
