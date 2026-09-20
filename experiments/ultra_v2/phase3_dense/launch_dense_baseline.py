# -*- coding: utf-8 -*-
"""Process entrypoint for DENSE-BASELINE.

Sets a single-OpenMP runtime BEFORE numpy/torch import.

Conflict observed in the live encoder (PID 2092):
  conda MKL:  Library/bin/libiomp5md.dll
  PyTorch:    site-packages/torch/lib/libiomp5md.dll
That is Intel OMP Error #15 (two copies of libiomp5md).

Safer supported resolution (tested 2026-09-11, no KMP_DUPLICATE_LIB_OK):
  MKL_THREADING_LAYER=SEQUENTIAL
so MKL does not load a second Intel OpenMP. Torch keeps its OpenMP for encode.
NumPy search is 111860 x 384 and does not need MKL threading.

Do not start this launcher while another run_dense_baseline.py is already
embedding into artifacts/dense_doc_embeddings.memmap.
"""
from __future__ import annotations

import os
import runpy
import sys

os.environ.pop("KMP_DUPLICATE_LIB_OK", None)
os.environ["MKL_THREADING_LAYER"] = "SEQUENTIAL"
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
runpy.run_path(os.path.join(_DIR, "run_dense_baseline.py"), run_name="__main__")
