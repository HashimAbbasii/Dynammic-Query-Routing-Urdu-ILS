#!/usr/bin/env python3
"""Create PLOS-upload TIFF derivatives from frozen PNG sources.

Does not overwrite PNG files. Does not recompute scientific values.

Pillow 12 on this Windows environment crashes when writing compressed
TIFF; LZW is written with tifffile + imagecodecs instead.

Flattens RGBA onto white. Writes 8-bit RGB TIFF, LZW, 300 dpi, single
page, no alpha. Fig3 is proportionally resized to PLOS max width 2250 px;
other figures are not resampled.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "Papers" / "PLOS_ONE" / "figures"
MAX_W = 2250
DPI = 300.0

SOURCES = [
    ("Fig1_m0_routing.png", "Fig1.tif", False),
    ("Fig2_development_comparators.png", "Fig2.tif", False),
    ("Fig3_script_splits.png", "Fig3.tif", True),
    ("Fig4_k_miss_analysis.png", "Fig4.tif", False),
    ("Fig5_u_label_distribution.png", "Fig5.tif", False),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def flatten_rgb(im: Image.Image) -> Image.Image:
    if im.mode == "RGB":
        return im
    rgba = im.convert("RGBA")
    bg = Image.new("RGB", rgba.size, (255, 255, 255))
    bg.paste(rgba, mask=rgba.split()[-1])
    return bg


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name, allow_resize in SOURCES:
        src = FIG / src_name
        dst = FIG / dst_name
        if not src.is_file():
            raise FileNotFoundError(src)
        rgb = flatten_rgb(Image.open(src))
        resized = False
        if allow_resize and rgb.size[0] > MAX_W:
            new_h = round(rgb.size[1] * MAX_W / rgb.size[0])
            rgb = rgb.resize((MAX_W, new_h), Image.Resampling.LANCZOS)
            resized = True
        elif (not allow_resize) and rgb.size[0] > MAX_W:
            raise ValueError(
                f"{src_name} width {rgb.size[0]} exceeds {MAX_W} and resize is not enabled"
            )
        arr = np.asarray(rgb)
        if arr.dtype != np.uint8 or arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(f"expected HxWx3 uint8 RGB, got {arr.shape} {arr.dtype}")
        tifffile.imwrite(
            dst,
            arr,
            compression="lzw",
            photometric="rgb",
            planarconfig="contig",
            resolution=(DPI, DPI),
            resolutionunit=2,
        )
        out = Image.open(dst)
        print(
            f"{src_name} {sha256(src)} -> {dst_name} "
            f"{out.mode} {out.size} dpi={out.info.get('dpi')} "
            f"compression={out.info.get('compression')} "
            f"bytes={dst.stat().st_size} resized={resized} "
            f"n_frames={getattr(out, 'n_frames', 1)}"
        )


if __name__ == "__main__":
    main()
