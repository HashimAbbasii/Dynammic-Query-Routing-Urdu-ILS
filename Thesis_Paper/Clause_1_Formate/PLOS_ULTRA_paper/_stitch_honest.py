# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(r"c:\Users\User\OneDrive\Documents\ULTRA_Project\Thesis_Paper\Clause_1_Formate\PLOS_ULTRA_paper")
main_path = ROOT / "main.tex"
tail_path = ROOT / "_honest_from_methods.tex"
bak = ROOT / "main.pre_honest.bak.tex"

text = main_path.read_text(encoding="utf-8")
if not bak.exists():
    bak.write_text(text, encoding="utf-8")

old_abs = text.split(r"\section*{Abstract}", 1)[1].split(r"\clearpage", 1)[0]
new_abs = r"""
Urdu search mixes native script with Roman Urdu. ULTRA still routes queries with one cutoff: 150 characters. A short question can need the article. A long question can be asking for a fact that already sits in a headline.

We keep SHORT and LONG but change the meaning. SHORT means a headline is probably enough. LONG means the user likely needs the body. An eight-feature SVM makes the call. Headlines and full articles live in two indexes. Confidence is a light: high searches one index, medium mixes both, low expands then mixes. The Roman Urdu word list on disk has 198 pairs (older drafts said 179).

Three tests are kept apart. On 50 frozen Phase~3B queries the SVM hit 86\% and a six-word rule hit 84\% (McNemar $p=1.0$). On 40 trap queries the SVM reached 60\%, word count 20\%, and $\theta=150$ 50\% (McNemar 16--0). That trap gain is almost entirely in 18 queries with why/how/fact wording; on the other 22 both systems score 27.27\%. Four hundred graded judgments on the same 40 queries do not reward the SVM at P@5 (word count 36.50\%, always-headline and $\theta=150$ 35.00\%, always-full 34.25\%, SVM 33.00\%). nDCG@5 is highest for always-headline (0.6868).

The character cutoff is a weak proxy for need. The SVM helps when the wording carries an obvious cue. On this news collection it does not improve early precision. We report that gap as part of the study.
"""

text = text.replace(r"\section*{Abstract}" + old_abs, r"\section*{Abstract}" + new_abs, 1)

# Research questions: retrieval claim
text = text.replace(
    r"in terms of retrieval precision (P@15) across both native Urdu and Roman Urdu queries?",
    r"on frozen need labels, and does that classification gain show up as P@5 when SHORT and LONG open two different indexes?",
)

text = text.replace(
    "(from 30 to 179 words) to improve retrieval precision for code-mixed and transliterated queries.",
    "(198 pairs on disk; older drafts said 179) to cover Roman Urdu queries.",
)
text = text.replace(
    "across a dataset of 369 real Urdu queries spanning 15+ topics.",
    "on frozen Phase 3B, trap classification, and dual-index P@5, without mixing development 100\\% into those tables.",
)

old_contrib = r"""\begin{enumerate}
    \item A dynamic SVM-based query routing model achieving 100\% routing accuracy on the evaluation dataset, compared to 50\% for the static threshold-based routing used in the base ULTRA framework \cite{bashir2026ultra}.
    \item An eight-feature semantic classifier engineered specifically for Urdu query characterization.
    \item A confidence-based three-tier routing architecture achieving an average confidence score of 98.18\% across the evaluation set.
    \item An expanded Roman Urdu transliteration dictionary (30 $\rightarrow$ 179 words, a 6$\times$ growth), improving Roman Urdu retrieval precision to 92.5\% (P@15).
    \item A comprehensive comparative evaluation against six retrieval methods, including large language models.
    \item An ablation study identifying the most robust and discriminative features for Urdu query routing.
\end{enumerate}"""

new_contrib = r"""\begin{enumerate}
    \item A restatement of SHORT/LONG as \emph{headline enough} vs.\ \emph{need the article}, not character length.
    \item Two retrieval indexes (headline vs.\ full article) plus HIGH/MEDIUM/LOW mixing on SVM confidence.
    \item Frozen Phase~3B: V2 SVM 86\% vs.\ word count 84\% (McNemar $p=1.0$).
    \item Frozen traps H001--H040: SVM 60\% vs.\ word count 20\% vs.\ $\theta=150$ 50\%, with a cue split that shows where the gain lives.
    \item Frozen dual-index P@5 on the same 40 queries: the classification win does not transfer (SVM 33.00\% vs.\ word count 36.50\%).
    \item A Roman Urdu dictionary of 198 pairs on disk, and an explicit refusal to quote development 100\% or 96\% as generalization.
\end{enumerate}"""

if old_contrib not in text:
    raise SystemExit("contributions block not found")
text = text.replace(old_contrib, new_contrib, 1)

text = text.replace("Roman Urdu dictionary (179 words)", "Roman Urdu dictionary (198 pairs)")
text = text.replace("SVM trained on 369 queries", "SVM trained on 409 V2 queries; frozen tests are separate")

cut = text.find(r"\section*{Materials and methods}")
if cut < 0:
    raise SystemExit("methods heading not found")
head = text[:cut]
tail = tail_path.read_text(encoding="utf-8")
# tail file starts with a comment then \section*{Materials and methods}
main_path.write_text(head + tail, encoding="utf-8")
print("wrote", main_path, "chars", main_path.stat().st_size)
