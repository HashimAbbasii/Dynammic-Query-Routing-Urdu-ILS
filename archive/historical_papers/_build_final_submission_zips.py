# -*- coding: utf-8 -*-
"""Build clean PLOS and IEEE submission ZIPs. No experiments. No git."""
from __future__ import annotations

import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLOS_DIR = HERE / "Clause_1_Formate" / "PLOS_ULTRA_paper"
IEEE_DIR = HERE / "IEEE_M0"
PLOS_ZIP = HERE / "ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip"
IEEE_ZIP = HERE / "ULTRA_IEEE_M0_FINAL_SUBMISSION.zip"

PLOS_FILES = [
    "main.tex",
    "references.bib",
    "plos2025.bst",
    "README.md",
    "figures/Fig1_m0_routing.png",
    "figures/Fig2_u_script_split.png",
]
IEEE_FILES = [
    "main.tex",
    "IEEEtran.cls",
    "README.md",
]


def write_zip(out: Path, base: Path, rels: list[str], prefix: str) -> list[str]:
    missing = [r for r in rels if not (base / r).exists()]
    if missing:
        raise SystemExit("missing: " + ", ".join(missing))
    names = []
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in rels:
            arc = f"{prefix}/{rel.replace(chr(92), '/')}"
            zf.write(base / rel, arcname=arc)
            names.append(arc)
        manifest = prefix + "/SUBMISSION_CONTENTS.txt"
        body = "Official frozen M0 submission package.\nDo not mix 87.18% / 67.50% / 57.50%.\n\n" + "\n".join(names) + "\n"
        zf.writestr(manifest, body)
        names.append(manifest)
    return names


def main() -> None:
    plos = write_zip(PLOS_ZIP, PLOS_DIR, PLOS_FILES, "ULTRA_PLOS_ONE_M0")
    ieee = write_zip(IEEE_ZIP, IEEE_DIR, IEEE_FILES, "ULTRA_IEEE_M0")
    report = HERE / "FINAL_SUBMISSION_ZIP_MANIFEST.txt"
    lines = [
        "PLOS ZIP: " + str(PLOS_ZIP),
        "size_bytes: " + str(PLOS_ZIP.stat().st_size),
        *["  " + n for n in plos],
        "",
        "IEEE ZIP: " + str(IEEE_ZIP),
        "size_bytes: " + str(IEEE_ZIP.stat().st_size),
        *["  " + n for n in ieee],
        "",
        "Excluded from both: .bak, old SVM/MiniLM sources, corpus, embeddings, Chroma, Git, experiment scratch.",
        "Scientific results unchanged.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
