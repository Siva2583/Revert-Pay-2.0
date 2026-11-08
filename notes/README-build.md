# Deep Learning (A40531) — 10-Mark Model Answer Booklets

Two deliverables, one per unit of the mid-examination syllabus:

| File | Contents | Pages |
|---|---|---|
| `Unit-I-10-Mark-Answers.pdf` | Unit I, Q1–Q8 (PCA, SVD, overflow/underflow, moments, gradient descent, constrained optimisation, least squares, PCA before a neural network) | 25 |
| `Unit-II-10-Mark-Answers.pdf` | Unit II, Q1–Q8 (bias/variance, validation strategy, batch vs stochastic GD, first intervention, MLE and losses, multiclass networks, depth/width/capacity, end-to-end workflow) | 24 |

Each answer follows the same 10-mark skeleton:

1. statement of the problem and notation
2. derivation with numbered equations (`n.m` = question *n*, equation *m*)
3. a vector diagram (`Fig. n.m`)
4. a comparison or design table
5. a worked numerical example where useful
6. **Examiner's checklist** box, **Golden line**, **Keywords** box

A contents page, a "unit at a glance" formula table and a final "rapid revision" grid
close each booklet.

## Rebuilding

The PDFs are generated (no hand layout):

```bash
python -m venv .venv-dl && .venv-dl/bin/pip install reportlab svglib matplotlib pymupdf
cd dl-notes/build
../.venv-dl/bin/python figs_u1.py        # Unit I diagrams  -> ../assets/figs/*.svg
../.venv-dl/bin/python figs_u2.py        # Unit II diagrams
../.venv-dl/bin/python build.py all      # writes both PDFs into ../ (dl-notes/)
```

Source layout:

- `framework.py` — typesetting engine: STIX fonts, LaTeX-subset maths rendered as
  vector SVG (matplotlib mathtext → svglib) for display equations and as
  baseline-aligned images for inline maths, plus callout boxes, tables, the cover
  and running headers.
- `content.py` — the small markup parser (`#A`, `##`, `$$`, `@fig`, `@table`, `@box`,
  `@mx`, `@kw`, ...).
- `content_u1.py`, `content_u2.py` — the answer scripts themselves.
- `figs_u1.py`, `figs_u2.py`, `figlib.py` — all diagrams as vector SVG.
- `build.py` — assembles cover + contents + answers + revision grid and runs a
  two-pass build so the table of contents carries real page numbers.
