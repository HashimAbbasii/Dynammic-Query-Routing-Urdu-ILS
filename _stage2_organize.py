# -*- coding: utf-8 -*-
"""Stage 2 file organization. No experiments. No git. Logs every action."""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG: list[str] = []


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def log(action: str, src: str, dest: str = "", reason: str = "") -> None:
    line = f"{action}\t{src}"
    if dest:
        line += f"\t->\t{dest}"
    if reason:
        line += f"\t# {reason}"
    LOG.append(line)
    print(line.encode("ascii", "replace").decode())


def ensure(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def move_path(src: Path, dest: Path, reason: str) -> None:
    if not src.exists():
        log("MISSING", rel(src), reason=reason)
        return
    ensure(dest.parent)
    if dest.exists():
        log("SKIP_EXISTS", rel(src), rel(dest), reason)
        return
    try:
        shutil.move(str(src), str(dest))
        log("MOVE", rel(src), rel(dest), reason)
    except Exception as e:
        try:
            if src.is_file():
                shutil.copy2(src, dest)
                log("COPY_LOCKED", rel(src), rel(dest), f"{reason}; original left ({e})")
            else:
                shutil.copytree(src, dest)
                log("COPYTREE_LOCKED", rel(src), rel(dest), f"{reason}; original left ({e})")
        except Exception as e2:
            log("FAIL", rel(src), rel(dest), str(e2))


def copy_file(src: Path, dest: Path, reason: str) -> None:
    if not src.exists():
        log("MISSING", rel(src), reason=reason)
        return
    ensure(dest.parent)
    shutil.copy2(src, dest)
    log("COPY", rel(src), rel(dest), reason)


def write_text(path: Path, text: str, reason: str) -> None:
    ensure(path.parent)
    path.write_text(text, encoding="utf-8")
    log("WRITE", rel(path), reason=reason)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rmdir_if_empty(p: Path) -> None:
    if p.exists() and p.is_dir() and not any(p.iterdir()):
        p.rmdir()
        log("RMDIR_EMPTY", rel(p))


def delete_path(p: Path, reason: str) -> None:
    if not p.exists():
        log("ALREADY_GONE", rel(p), reason=reason)
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
    log("DELETE", rel(p), reason=reason)


def main() -> None:
    # Directories
    for d in [
        ROOT / "Thesis" / "FINAL" / "figures",
        ROOT / "Papers" / "PLOS_ONE" / "FINAL" / "figures",
        ROOT / "Papers" / "PLOS_ONE" / "SUBMISSION_PACKAGE",
        ROOT / "Papers" / "IEEE" / "FINAL" / "figures",
        ROOT / "Papers" / "IEEE" / "SUBMISSION_PACKAGE",
        ROOT / "docs",
        ROOT / "archive" / "historical_thesis",
        ROOT / "archive" / "historical_papers" / "IEEE_MiniLM",
        ROOT / "archive" / "historical_papers" / "PLOS_old",
        ROOT / "archive" / "historical_experiments",
        ROOT / "archive" / "historical_figures" / "plos_unused_svm_minilm",
        ROOT / "archive" / "historical_figures" / "ieee_minilm",
        ROOT / "archive" / "historical_figures" / "results_layer_a",
    ]:
        ensure(d)

    # ---- Thesis FINAL (copy if locked, then try move) ----
    thesis_src = ROOT / "Thesis_Paper" / "Air_Thesis_Formate"
    thesis_dst = ROOT / "Thesis" / "FINAL"
    move_path(
        thesis_src / "Hashim_Shazad_243259_AU_Thesis_ULTRA.docx",
        thesis_dst / "Hashim_Shazad_243259_AU_Thesis_ULTRA.docx",
        "final thesis DOCX (21 images embedded; 0 external links)",
    )
    move_path(
        thesis_src / "ULTRA_THESIS_SUBMISSION_DRAFT.md",
        thesis_dst / "ULTRA_THESIS_SUBMISSION_DRAFT.md",
        "final thesis markdown",
    )
    move_path(
        thesis_src / "HOW_TO_UPDATE_WORD_THESIS.md",
        thesis_dst / "HOW_TO_UPDATE_WORD_THESIS.md",
        "Word TOC note",
    )

    write_text(
        thesis_dst / "figures" / "README.md",
        (
            "# Thesis figures\n\n"
            "The final DOCX embeds **21 PNG images** in `word/media/` "
            "(`image1.png` … `image21.png`). Document relationships use `r:embed` only; "
            "`r:link` count is 0 (no external image files).\n\n"
            "Images were **not** extracted or replaced. Opening the DOCX is sufficient.\n"
        ),
        "explain embedded thesis figures",
    )

    # thesis baks + repair scripts
    hist_th = ROOT / "archive" / "historical_thesis"
    for name in [
        "Hashim_Shazad_243259_AU_Thesis_ULTRA.pre_m0_cleanup.bak.docx",
        "Hashim_Shazad_243259_AU_Thesis_ULTRA.pre_consistency_audit.bak.docx",
    ]:
        move_path(thesis_src / name, hist_th / name, "obsolete thesis backup")

    for p in thesis_src.glob("_*"):
        move_path(p, hist_th / "repair_scripts" / p.name, "one-off Word repair/audit artifact")

    # ---- PLOS FINAL ----
    plos_src = ROOT / "Thesis_Paper" / "Clause_1_Formate" / "PLOS_ULTRA_paper"
    plos_dst = ROOT / "Papers" / "PLOS_ONE" / "FINAL"
    for name in ["main.tex", "references.bib", "plos2025.bst", "README.md"]:
        move_path(plos_src / name, plos_dst / name, "official M0 PLOS source")
    for fig in ["Fig1_m0_routing.png", "Fig2_u_script_split.png"]:
        move_path(
            plos_src / "figures" / fig,
            plos_dst / "figures" / fig,
            "PLOS includegraphics asset",
        )

    # unused PLOS figures (not referenced by live main.tex)
    unused_plos = ROOT / "archive" / "historical_figures" / "plos_unused_svm_minilm"
    figdir = plos_src / "figures"
    if figdir.exists():
        for p in figdir.iterdir():
            if p.is_file() and p.name not in ("Fig1_m0_routing.png", "Fig2_u_script_split.png"):
                move_path(p, unused_plos / p.name, "not referenced by M0 PLOS main.tex")

    for extra in ["_make_m0_figures.py", "_stitch_honest.py", "_honest_from_methods.tex", "main.pdf"]:
        move_path(plos_src / extra, ROOT / "archive" / "historical_papers" / "PLOS_old" / extra, "scratch or stale compile")

    # old PLOS zips/pdfs
    clause = ROOT / "Thesis_Paper" / "Clause_1_Formate"
    plos_old = ROOT / "archive" / "historical_papers" / "PLOS_old"
    for name in [
        "PLOS_ULTRA_paper_final.zip",
        "PLOS_ULTRA_paper_revised.zip",
        "PLOS_ULTRA_paper_source_Sample.zip",
        "Adaptive_Dynammic_Query_Clause1.zip",
        "Adaptive_Dynammic_Query.pdf",
        "Adaptive_Dynamic_Query_Routing_PLOS_ONE.pdf",
    ]:
        move_path(clause / name, plos_old / name, "obsolete PLOS package")

    move_path(
        ROOT / "Thesis_Paper" / "ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip",
        ROOT / "Papers" / "PLOS_ONE" / "SUBMISSION_PACKAGE" / "ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip",
        "clean PLOS submission zip",
    )

    # PLOS_ONE word drafts
    plos_word = ROOT / "Thesis_Paper" / "PLOS_ONE"
    if plos_word.exists():
        dest = ROOT / "archive" / "historical_papers" / "PLOS_ONE_word_draft"
        if not dest.exists():
            move_path(plos_word, dest, "pre-M0 PLOS Word draft")

    # ---- IEEE M0 FINAL (no includegraphics) ----
    ieee_src = ROOT / "Thesis_Paper" / "IEEE_M0"
    ieee_dst = ROOT / "Papers" / "IEEE" / "FINAL"
    for name in ["main.tex", "IEEEtran.cls", "README.md"]:
        move_path(ieee_src / name, ieee_dst / name, "official M0 IEEE source")
    write_text(
        ieee_dst / "figures" / "README.md",
        (
            "# IEEE M0 figures\n\n"
            "`main.tex` contains **no** `\\includegraphics` commands. "
            "No figure files are required to compile this manuscript.\n"
        ),
        "IEEE M0 has no figures",
    )
    move_path(
        ROOT / "Thesis_Paper" / "ULTRA_IEEE_M0_FINAL_SUBMISSION.zip",
        ROOT / "Papers" / "IEEE" / "SUBMISSION_PACKAGE" / "ULTRA_IEEE_M0_FINAL_SUBMISSION.zip",
        "clean IEEE submission zip",
    )

    # historical IEEE MiniLM (keep its figures beside the paper)
    ieee_old = ROOT / "Thesis_Paper" / "IEEE"
    if ieee_old.exists():
        move_path(
            ieee_old,
            ROOT / "archive" / "historical_papers" / "IEEE_MiniLM",
            "historical MiniLM dual-index IEEE paper (not M0)",
        )

    # remaining Thesis_Paper docs
    tp = ROOT / "Thesis_Paper"
    hist_docs = ROOT / "archive" / "historical_papers"
    for name in [
        "OUTDATED_DRAFTS.md",
        "FINALIZATION_REPORT.md",
        "README_FROZEN_RESULTS.md",
        "THESIS_CHAPTERS_5_6_FROZEN_M0.md",
        "FINAL_SUBMISSION_ZIP_MANIFEST.txt",
        "_build_final_submission_zips.py",
    ]:
        move_path(tp / name, hist_docs / name, "superseded thesis-paper folder note")

    # ---- docs ----
    move_path(
        ROOT / "CLEAN_FINALIZATION_MANIFEST.md",
        ROOT / "docs" / "PROJECT_STATUS.md",
        "project status / freeze manifest",
    )
    move_path(
        ROOT / "experiments" / "FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md",
        ROOT / "docs" / "FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md",
        "official interpretation (numbers unchanged)",
    )
    move_path(
        ROOT / "CLEANUP_PLAN.md",
        ROOT / "docs" / "CLEANUP_PLAN.md",
        "Stage 1 plan",
    )

    # ---- Layer A results figures ----
    res = ROOT / "results"
    la_fig = ROOT / "archive" / "historical_figures" / "results_layer_a"
    for name in ["CURRENT.txt", "CURRENT.json", "README.md", "robustness_report.csv",
                 "roman_urdu_results.json", "phase3_retrieval_results.json",
                 "phase4_retrieval_results.json", "_align_results_folder.py"]:
        move_path(res / name, la_fig / name, "Layer A / development results, not official M0")
    if (res / "figures").exists():
        move_path(res / "figures", la_fig / "figures", "Layer A MiniLM/SVM figures")
    if (res / "_archive_development_cv").exists():
        move_path(res / "_archive_development_cv", la_fig / "_archive_development_cv", "development 100%/P@15 archive")

    # ---- historical experiments (not Phase 8–12 / M0 impl) ----
    he = ROOT / "archive" / "historical_experiments"
    for name in ["notebooks", "validate", "artifacts"]:
        src = ROOT / name
        if src.exists():
            move_path(src, he / name, "Layer A / diagnostic history")
    for name in ["DEFENSE_DEMO.md", "INSTRUCTIONS_URDU.txt", "validation_response.py", "README (3).md", "results.zip"]:
        src = ROOT / name
        if src.exists():
            move_path(src, he / name, "obsolete root artifact")

    models = ROOT / "models"
    for p in models.iterdir() if models.exists() else []:
        if p.name.startswith("backup") or "PRE_GAPFIX" in p.name:
            move_path(p, he / "models_svm_backups" / p.name, "historical SVM snapshot")
    for name in ["svm_classifier.pkl", "scaler.pkl", "training_info.json", "training_data.json"]:
        move_path(models / name, he / "models_svm_layer_a" / name, "Layer A SVM; not M0")

    # early experiment folders (keep phase2,5,8,9,11,12,10c,4 in experiments)
    exp = ROOT / "experiments"
    for name in [
        "phase0_baseline",
        "phase1_forensic",
        "phase3_retrieval",
        "phase6_residual_diagnosis",
        "phase7_human_relevance",
        "phase10a_evidence",
        "phase10b_frozen_dump",
        "archive",
    ]:
        src = exp / name
        if src.exists():
            move_path(src, he / name, "historical/diagnostic experiment (not official M0 freeze path)")

    # leave phase4 in experiments (large gitignored zip + reports)
    # leave phase4b as supporting lexical baseline history — archive it
    if (exp / "phase4b_retrieval_benchmark").exists():
        move_path(
            exp / "phase4b_retrieval_benchmark",
            he / "phase4b_retrieval_benchmark",
            "historical retrieval benchmark reports",
        )

    # ---- pointer READMEs ----
    write_text(
        ROOT / "Thesis_Paper" / "README.md",
        (
            "This folder is a **path pointer** after repository cleanup.\n\n"
            "- Final thesis: `../Thesis/FINAL/`\n"
            "- Final PLOS ONE (M0): `../Papers/PLOS_ONE/FINAL/`\n"
            "- Final IEEE (M0): `../Papers/IEEE/FINAL/`\n"
            "- Historical MiniLM IEEE paper: `../archive/historical_papers/IEEE_MiniLM/`\n"
        ),
        "old Thesis_Paper path pointer",
    )
    write_text(
        ROOT / "src" / "README.md",
        (
            "# M0 source locations (not relocated)\n\n"
            "Python entry points were **not** moved, so documented paths still work.\n\n"
            "- Detector / BM25 / Method D routing: `experiments/phase5_roman_urdu/run_phase5.py`\n"
            "- Method D character table: `experiments/phase2_oracle/run_phase2_pipeline.py`\n"
            "- Phase 12 retrieval runner: `experiments/phase12_new_unseen_evaluation/run_phase12.py`\n"
        ),
        "src map only",
    )

    # ---- junk delete ----
    delete_path(ROOT / "Write-Host", "empty accidental file")
    vscode = ROOT / ".vscode"
    if vscode.exists():
        delete_path(vscode, "IDE metadata (gitignored)")
    scripts = ROOT / "scripts"
    if scripts.exists() and (not any(scripts.rglob("*")) or not any(scripts.iterdir())):
        delete_path(scripts, "empty directory")
    for pyc in ROOT.rglob("__pycache__"):
        if "archive" in pyc.parts:
            continue
        if pyc.is_dir():
            delete_path(pyc, "Python cache")

    # empty leftover dirs
    for leftover in [
        thesis_src,
        plos_src / "figures",
        plos_src,
        clause,
        ieee_src,
        tp,
    ]:
        # only if empty or only empty children — walk bottom-up later
        pass

    # prune empty dirs under Thesis_Paper
    if tp.exists():
        for child in sorted(tp.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if child.is_dir():
                try:
                    child.rmdir()
                    log("RMDIR_EMPTY", rel(child))
                except OSError:
                    pass

    (ROOT / "CLEANUP_STAGE2_ACTIONS.log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    log("WRITE", "CLEANUP_STAGE2_ACTIONS.log", reason="action log")


if __name__ == "__main__":
    main()
