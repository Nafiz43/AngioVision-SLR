# AngioVision SLR

Manuscript, screening data, extraction records, and analysis code for
*A Systematic Literature Review on AI Methods for Angiographic Sequence Analysis*.

This is the canonical repository for the paper and its reproducibility materials.

## Manuscript and Overleaf

Import this repository into Overleaf and select `00-main.tex` as the main document.
Use pdfLaTeX. The manuscript, `figs/`, and `tables/` retain their original paths.
The Python code and data folders are not needed for LaTeX compilation.
For an Overleaf project already connected to this repository, pull the GitHub changes
through Overleaf's GitHub synchronization menu. Synchronization is manual.
For an unconnected project, create a new project using Import from GitHub.
GitHub synchronization requires an eligible Overleaf subscription.

## Repository layout

- `00-main.tex`, `01-intro.tex` through `06-appendix.tex`: manuscript.
- `figs/`, `tables/`, `references.bib`: manuscript figures, tables, and bibliography.
- `supplementary/`: supplementary LaTeX material.
- `screening/`: screening decisions, human validation, and search/screening pipeline.
- `extraction/`: extraction instructions, schema, manifest, and 120 study records.
- `analysis/`: figure generation and statistical analysis.
- `REPRODUCIBILITY.md`: data descriptions, dependencies, and reproduction commands.
- `validation/`: manuscript's original screening validation materials.

Run `bash analysis/run_all.sh` from the repository root to regenerate analysis outputs.
Generated files go to ignored `results/` and `analysis-results/` directories;
this does not overwrite the manuscript's figures automatically.

## Provenance

The reproducibility materials were imported unchanged (apart from relocating their
README to `REPRODUCIBILITY.md`) from `Nafiz43/angiovision-slr-data` at commit
`9c1c441346224d595fe10e2465b1650e46bf936d`. The original repository is retained as an archived historical record.
Its former manuscript links now point to this repository.

The root `README` and `Makefile` belong to the bundled ACM template; the Makefile
is not the build entry point for this manuscript.

## Known reporting issue

The extraction instructions' operational CLAIM item definitions differ from the
official CLAIM 2024 checklist. Consolidating the repositories does not resolve that
methodological issue or change the scores. Reconcile definitions and reassess affected
items before describing the results as adherence to the official checklist.
