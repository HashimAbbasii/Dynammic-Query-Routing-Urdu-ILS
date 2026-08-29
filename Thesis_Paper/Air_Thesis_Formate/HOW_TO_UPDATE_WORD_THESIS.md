# How to update the Air University Word thesis

Scientific source of truth:

`Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md`

Live formatted file (keep certificates / signatures / TOC fields):

`Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`

## Do this in Word (no new experiments)

1. Replace the **Abstract** with the Abstract from the markdown draft.
2. Replace **§1.2–1.7, 1.8, 1.10** with the corresponding draft sections (keep acknowledgments).
3. Keep Chapter 2 largely, but add the ExactSource vs Success@5 paragraph from draft §2.3.
4. Add Chapter 3 sections 3.1–3.5 (M0 math). Label existing SVM equations as **Layer A / historical**.
5. Add Chapter 4 M0 architecture + Tables 1–2 and the Phase 8–12 protocol.
6. At the start of Chapter 5, paste the two-layer box, then **§5.16-style** official results (Tables 3–8) from the draft. Keep 5.1–5.15 only if each is labeled development/SVM/MiniLM, not official M0 Hit@5.
7. Replace **6.1 Conclusions** and **6.3 Limitations** with the draft text.
8. Paste **CLAIMS WE CAN / MUST NOT MAKE** as an appendix.
9. Update the dictionary figure **198 keys** wherever the text still says 179.

## Do not paste from

- Clause-1 PLOS `main.tex` (100% routing / ~90% P@15)
- IEEE `Thesis_Paper/IEEE/main.tex` MiniLM P@5 table as if it were M0 Success@5

Official M0 conference draft: `Thesis_Paper/IEEE_M0/main.tex`
