# Deep Learning (A40531) — 10-Mark Model Answer Books

| File | Contents | Pages |
|---|---|---|
| `Unit-I-10-Mark-Answers.pdf` | Unit I, Q1–Q8 (PCA, SVD, overflow/underflow, moments, gradient descent, constrained optimisation, least squares, PCA before a neural network) | 25 |
| `Unit-II-10-Mark-Answers.pdf` | Unit II, Q1–Q8 (bias/variance, validation strategy, batch vs stochastic GD, first intervention, MLE and losses, multiclass networks, depth/width/capacity, end-to-end workflow) | 24 |
| `Mid-2-Unit-III-IV-V-10-Mark-Answers.pdf` | **Mid-2 book**: Units III, IV and V, Q1–Q24 in one document — regularisation and optimisation, convolutional networks, recurrent networks and autoencoders | 56 |

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

## The Mid-2 book (Units III–V)

`Mid-2-Unit-III-IV-V-10-Mark-Answers.pdf` is a single 56-page document covering
all twenty-four Mid-2 questions:

- Unit III — regularisation plans, L1/L2 and sparsity, dropout, norm constraints
  and the KKT multiplier, the optimiser ladder, deep vs pure optimisation,
  AdaGrad/RMSProp/Adam, early stopping vs dropout vs augmentation.
- Unit IV — CNN design, output-size and cost formulas with worked numbers,
  fully connected vs convolutional, priors, pooling and localisation,
  flatten vs global average pooling, underfitting from pooling, architecture
  justification for a real application.
- Unit V — unfolded RNN and weight sharing, vanishing/exploding gradients,
  RNN variants, LSTM gates and cell state, long-sequence strategy,
  encoder–decoder seq2seq, autoencoders for dimensionality reduction and
  representation learning.

Front matter: cover, contents with page numbers, one "unit at a glance" table per
unit. Back matter: Appendix A (one-page-per-unit formula sheet), Appendix B (how
to write a ten-mark answer, with notation), and the rapid revision grid with the
one line and the trap for each of the twenty-four answers.

Equations are numbered per unit (`(3.1)`, `(4.1)`, `(5.1)`) and figures likewise
(`Fig. 3.1` … `Fig. 5.7`), so a question can be cited unambiguously across units.

The generator sources for this book sit in `notes/src/` (`framework.py`,
`content.py`, `content_u3.py`, `content_u4.py`, `content_u5.py`, `figs_u3.py`,
`figs_u4.py`, `figs_u5.py`, `figlib.py`, `build.py`, `validate.py`). To rebuild:

```bash
python -m venv .venv && .venv/bin/pip install reportlab svglib matplotlib pymupdf
mkdir -p build/fonts && cp <matplotlib>/mpl-data/fonts/ttf/STIXGeneral*.ttf build/fonts/
cp notes/src/*.py build/ && cd build
../.venv/bin/python validate.py          # parse-checks every equation
../.venv/bin/python figs_u3.py           # figures -> ../assets/figs/*.svg
../.venv/bin/python figs_u4.py
../.venv/bin/python figs_u5.py
../.venv/bin/python build.py all         # writes the PDF
```
