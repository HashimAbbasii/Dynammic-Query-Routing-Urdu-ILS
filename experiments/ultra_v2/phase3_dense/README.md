# ULTRA v2 Phase 3 — dense retrieval baseline

Isolated directory. Does **not** edit frozen M0, R2 artifacts, PLOS, or TEST.

Protocol (written before evaluation): `DENSE_PREREGISTRATION.md`  
Report (after evaluation): `DENSE_CONTROLLED_EXPERIMENT.md`

The original CPU encode was left running after a chat interrupt and completed in-process from a valid 4,096-doc checkpoint.

```text
python experiments/ultra_v2/phase3_dense/launch_dense_baseline.py
```

`launch_dense_baseline.py` sets `MKL_THREADING_LAYER=SEQUENTIAL` before numpy/torch import (one OpenMP runtime). Do not start a second encoder while a memmap write is in progress.

Opens TRAIN/DEV only. Refuses `benchmark/test/`.
