# Script detection report

Deterministic Unicode rule (not an SVM). Pre-registered in `METHODS_PREREGISTERED.md`.

```
urdu = count of U+0600..U+06FF
latin = count of ASCII letters
OTHER if both 0
MIXED if both > 0
URDU if only urdu
ROMAN if only latin
```

Evaluated on all **78** Phase 2 dev + internal_val queries. No H001–H040.

## Detector counts

| Label | n |
| --- | ---: |
| URDU | 46 |
| ROMAN | 23 |
| MIXED | 9 |
| OTHER | 0 |

## Oracle `language_type` (manual / generation labels)

| Label | n |
| --- | ---: |
| urdu → URDU | 46 |
| roman_urdu → ROMAN | 23 |
| mixed → MIXED | 9 |

## Agreement

Correct vs oracle labels: **78 / 78**.

Mismatches: **0**.

No mismatches. Oracle mixed queries all contain Urdu letters plus the Latin suffix `Pakistan news update`.

## Ambiguous cases

**Detector errors: 0.** Oracle and detector agree on all 78.

The nine MIXED queries are mixed-script **by construction** (Urdu title fragment + Latin suffix `Pakistan news update`). They are not detector failures and were not treated as Roman.

Ids: QTRN_054, QTRN_099, QTRN_108, QTRN_117, QTRN_153, QTRN_189, QTRN_207, QTRN_216, QTRN_225

The detector does not use the Roman dictionary and does not look at retrieval ranks.
