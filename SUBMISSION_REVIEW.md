# Computers in Biology and Medicine submission review

Reviewed against the author-provided `guide.pdf` (saved 26 October 2026). Base manuscript: `6114100` ("re-review left"). The latest author-edited prose is preserved. This is a submission-format review, not certification of the scientific methods or results.

## Applied changes

- Retained the requested dual affiliations for Khan and Filkov and suppression of the generic preprint footer in PR #11.
- Added the missing `blei2003latent` bibliography entry without editing the citation or surrounding text. Metadata verified at https://www.jmlr.org/papers/v3/blei03a.html.
- Matched the supplementary title to the manuscript title.
- Updated Table S2 to the current objectives (1.3), extraction (2.3.4), limitations (4.3), and conclusion (4.4) sections. Replaced obsolete appendix references with the data availability statement and public repository. Distinguished CLAIM-informed reporting completeness from risk of bias.
- Clarified that human validation used 491 records and that the nearly 90% cardiac/neurologic share describes included studies. All five highlights remain within 85 characters.

## Author-edited lines left unchanged

1. **Abstract (`00-main.tex`, abstract):** approximately 265 whitespace-delimited words; the guide sets a maximum of 250. Shorten before submission. The entire paragraph was edited in `6114100`; it has not been changed here.
2. **AI disclosure (`00-main.tex`, final declaration):** the latest author wording mentions Claude assistance but omits OpenAI Codex assistance with manuscript editing and code. The guide requires disclosure of generative AI used in manuscript preparation. Supplement this account accurately before submission; existing author wording has not been changed. The guide's example heading is "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process."
3. **Figure reference (`03-analysis.tex`, first paragraph of Imaging Modalities and Anatomical Coverage):** `Figure \label{fig:anatomy_distribution}` should be `Figure~\ref{fig:anatomy_distribution}`. This author-edited line currently introduces a duplicate label and omits the number in that sentence; left unchanged.
4. **Unicode in Recurrent Theme Extraction (`02-methodology.tex`):** the current font drops curly quotes, apostrophes, dashes and the arrow in the author-edited paragraph. Convert these to equivalent LaTeX punctuation before submission. The wording has not been changed.
5. Other author-edited prose, including the restored Objectives subsection and revised discussion, is unchanged; remaining spelling and grammar issues need author review.

## Files and portal actions

- Upload editable LaTeX sources, bibliography, and all required figure/dependency files; a PDF alone is not an acceptable source submission.
- Upload `highlights.txt` separately (five bullets, each at most 85 characters).
- Upload the compiled supplementary material separately with a concise caption; the guide says supplementary files are published as supplied.
- Complete Elsevier's declarations tool even when there are no competing interests; upload its resulting Word document (.doc or .docx). This is separate from the manuscript declaration.
- Confirm corresponding-author details, author order, affiliations, CRediT roles, funding, permissions where applicable, and coauthor approval in the submission process. These factual confirmations have not been performed on the authors' behalf.
- A graphical abstract is encouraged, not mandatory. Double-column LaTeX is permitted. Seven keywords are within the allowed range. A data availability statement and funding statement are already present.

## Verification

Main manuscript and supplement compile successfully with Tectonic. The missing bibliography citation resolves. Title-page rendering and the updated checklist were visually checked. The build still reports the protected duplicate label, missing Unicode glyphs, and existing box warnings; compilation success does not mean the manuscript is submission-ready. Address the protected issues above before submission.
