# -*- coding: utf-8 -*-
from pathlib import Path
from docx import Document

HERE = Path(__file__).resolve().parent
d = Document(str(HERE / "Hashim_Shazad_243259_AU_Thesis_ULTRA.docx"))
needles = (
    "Contributions 1 through 3",
    "3.6 Retrieval Scoring",
    "Layer A dual-index (not official M0)",
    "Official IR contribution of this thesis is script-aware BM25",
    "Historical Layer A keeps ULTRA",
    "These application remarks concern routing patterns",
    "If a live system is built from this thesis",
    "The complexity bounds below describe Layer A",
)
lines = []
for i, p in enumerate(d.paragraphs):
    t = p.text or ""
    if any(n in t for n in needles):
        lines.append("[%d|%s] %s" % (i, (p.style.name if p.style else "")[:20], t[:280].replace("\n", " ")))
Path(HERE / "_audit_spot.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
