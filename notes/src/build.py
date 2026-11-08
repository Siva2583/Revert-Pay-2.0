"""Build the Mid-2 book (Units III, IV, V) or a single unit."""
import importlib
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (Paragraph, Spacer, PageBreak, CondPageBreak,
                                NextPageTemplate, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents

from framework import (NoteDoc, PartHead, QuestionHead, P, md, table, ST, NAVY,
                       TEAL, GOLD, GREY, RULE, INK, BODY, BOLD, ResetQ, Box,
                       TEAL_L)
from content import Ctx, parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "..", "..", "Revert-Pay-2.0", "notes")
os.makedirs(OUTDIR, exist_ok=True)


def contents_page():
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle('toc0', fontName=BOLD, fontSize=10.2, leading=17,
                       textColor=NAVY, spaceBefore=9, spaceAfter=2,
                       leftIndent=0, firstLineIndent=0),
        ParagraphStyle('toc1', fontName=BODY, fontSize=9.1, leading=13.6,
                       textColor=INK, leftIndent=16, firstLineIndent=0,
                       spaceAfter=1.5),
    ]
    toc.dotsMinLevel = 0
    head = Paragraph('<font name="Body-B" size="17" color="#123A5F">Contents</font>',
                     ParagraphStyle('ch', fontName=BOLD, fontSize=17, leading=21,
                                    textColor=NAVY, spaceAfter=2))
    sub = Paragraph(md("Twenty-four ten-mark answers, grouped by unit. Page numbers "
                       "refer to this document.", 8.6, "#5D6D7C"),
                    ParagraphStyle('cs', fontName=BODY, fontSize=8.6, leading=11,
                                   textColor=GREY, spaceAfter=10))
    return [head, sub, toc, PageBreak()]


def glance_table(rows):
    data = [["#", "Question", "Open with"]] + [[str(a), b, c] for a, b, c in rows]
    return table(data, [24, 240, 233], font=8.0, first_col_bold=True)


def revision_block(groups):
    head = Paragraph('<font name="Body-B" size="14" color="#123A5F">Rapid revision '
                     'grid</font>', ParagraphStyle('rh', fontName=BOLD, fontSize=14,
                                                   leading=17, textColor=NAVY,
                                                   spaceAfter=3))
    sub = Paragraph(md("If you have ten minutes before the paper, read only these "
                       "pages.", 8.6, "#5D6D7C"),
                    ParagraphStyle('rs', fontName=BODY, fontSize=8.6, leading=11,
                                   textColor=GREY, spaceAfter=8))
    out = [head, sub]
    for roman, rows in groups:
        out.append(Paragraph('<font name="Body-B" size="9.2" color="#0E6E7A">UNIT %s'
                             '</font>' % roman,
                             ParagraphStyle('rg', fontName=BOLD, fontSize=9.2,
                                            leading=12, textColor=TEAL,
                                            spaceBefore=8, spaceAfter=4)))
        data = [["Q", "The one line you must write", "Trap to avoid"]] + \
               [[str(a), b, c] for a, b, c in rows]
        out.append(table(data, [26, 268, 203], font=7.6, first_col_bold=True))
    out.append(Spacer(1, 14))
    out.append(Box("Last thing before you enter the hall", [
        P("Six sentences: regularise by diagnosis, not by reflex; a penalty is a "
          "constraint seen through a multiplier; a convolution is locality plus "
          "sharing; a pool is an invariance bought with position; a recurrence is a "
          "matrix applied $T$ times, which is why it needs a gate; an autoencoder is "
          "a bottleneck that learns the manifold.", 'boxp')],
        bg=TEAL_L, bar=TEAL, icon="\u25b6 "))
    return out


FORMULAE = {
    "UNIT III — regularisation and optimisation": [
        ("Regularised objective", r"\tilde{J}(\theta)=J(\theta)+\lambda\Omega(\theta)"),
        ("Weight decay update", r"\theta\leftarrow(1-\eta\lambda)\theta-\eta\nabla J(\theta)"),
        ("Penalty gradients", r"\nabla J+\lambda\theta\ \ (L_2);\qquad \nabla J+\lambda\,\mathrm{sgn}(\theta)\ \ (L_1)"),
        ("Soft threshold", r"w^{\star}=\mathrm{sign}(y)\max(|y|-\lambda,0)"),
        ("Ridge closed form", r"\hat{\theta}=(X^{\top}X+\lambda I)^{-1}X^{\top}y"),
        ("Elastic net", r"\Omega=\lambda_1\|\theta\|_1+\lambda_2\|\theta\|_2^{2}"),
        ("Momentum", r"v_t=\mu v_{t-1}-\eta g_t;\quad \theta_{t+1}=\theta_t+v_t"),
        ("Adam step", r"\theta\leftarrow\theta-\eta\,\hat{m}_t/(\sqrt{\hat{s}_t}+\epsilon)"),
        ("Bias correction", r"\hat{m}_t=m_t/(1-\beta_1^{t})"),
        ("He initialisation", r"W\sim\mathcal{N}(0,\,2/n_{in})"),
        ("Early stopping as L2", r"\lambda\approx 1/(\tau\eta)"),
        ("Dropout at test time", r"W_{test}=q\,W;\qquad \tilde{h}=m\odot h/q"),
    ],
    "UNIT IV — convolutional networks": [
        ("Output size", r"O=\lfloor (W-K+2P)/S\rfloor+1"),
        ("Parameters", r"K^{2}C_{in}C_{out}+C_{out}"),
        ("Cost", r"2\,H W K^{2}C_{in}C_{out}\ \mathrm{FLOPs}"),
        ("Receptive field", r"r_l=r_{l-1}+(K_l-1)\prod_{i<l}S_i"),
        ("Dilation", r"K_{eff}=K+(K-1)(d-1)"),
        ("Same padding", r"P=\lfloor K/2\rfloor,\ S=1"),
        ("Global average pool", r"g_c=\frac{1}{HW}\sum_{i,j}A_{i,j,c}"),
        ("Softmax + cross-entropy", r"\partial L/\partial z_c=\hat{y}_c-y_c"),
        ("Class activation map", r"M_c(i,j)=\sum_k w_{k,c}A_{i,j,k}"),
    ],
    "UNIT V — recurrent networks and autoencoders": [
        ("Simple RNN", r"h_t=\tanh(W_{xh}x_t+W_{hh}h_{t-1}+b)"),
        ("BPTT Jacobian", r"\partial h_i/\partial h_{i-1}=\mathrm{diag}(1-h_i^{2})W_{hh}"),
        ("Gradient bound", r"\|\partial L_t/\partial h_k\|\leq C\gamma^{\,t-k}"),
        ("Clipping", r"g\leftarrow g\cdot\min(1,\,c/\|g\|)"),
        ("LSTM state", r"c_t=f_t\odot c_{t-1}+i_t\odot\tilde{c}_t"),
        ("LSTM parameters", r"4\,d_h(d_h+d_x)"),
        ("Seq2seq likelihood", r"P(y\mid x)=\prod_t P(y_t\mid y_{<t},x)"),
        ("Attention", r"\alpha_{t,s}=\mathrm{softmax}_s(e_{t,s});\quad c_t=\sum_s\alpha_{t,s}h_s"),
        ("Autoencoder loss", r"\|x-D(E(x))\|^{2}"),
    ],
}


def appendix():
    story = [PageBreak(), ResetQ()]
    story.append(Paragraph('<font name="Body-B" size="16" color="#123A5F">Appendix A '
                           '· Formula sheet</font>',
                           ParagraphStyle('ah', fontName=BOLD, fontSize=16, leading=20,
                                          textColor=NAVY, spaceAfter=2)))
    story.append(Paragraph(md("Everything you are expected to write down, on three "
                              "pages. Derivations are in the answers; this is the "
                              "skeleton.", 8.6, "#5D6D7C"),
                           ParagraphStyle('as', fontName=BODY, fontSize=8.6, leading=11,
                                          textColor=GREY, spaceAfter=8)))
    for title, rows in FORMULAE.items():
        story.append(Paragraph('<font name="Body-B" size="10" color="#0E6E7A">%s</font>'
                               % title, ParagraphStyle('an', fontName=BOLD, fontSize=10,
                                                       leading=13, textColor=TEAL,
                                                       spaceBefore=9, spaceAfter=4)))
        data = [["Quantity", "Expression"]] + [[a, "$" + b + "$"] for a, b in rows]
        story.append(table(data, [150, 347], font=8.4, first_col_bold=True))
    return story


def how_to_write():
    story = [PageBreak(), ResetQ()]
    story.append(Paragraph('<font name="Body-B" size="16" color="#123A5F">Appendix B '
                           '· Writing a ten-mark answer</font>',
                           ParagraphStyle('bh', fontName=BOLD, fontSize=16, leading=20,
                                          textColor=NAVY, spaceAfter=6)))
    story.append(P("Ten marks are not awarded for volume. They are awarded for the "
                   "sequence *definition → mechanism → derivation → comparison → "
                   "consequence*, with the notation fixed in the first two lines. The "
                   "template below is the one used throughout this book; it fits any "
                   "of the twenty-four questions."))
    rows = [["Mark", "What the examiner looks for", "Where it appears in this book"],
            ["2", "A precise definition with the symbols declared",
             "the opening paragraph"],
            ["3", "The mechanism or derivation, one numbered equation per step",
             "the second section"],
            ["2", "A worked number, a figure or a table", "the middle of the answer"],
            ["2", "A comparison or an evaluation with trade-offs", "the closing table"],
            ["1", "A conclusion in one sentence", "the golden line"]]
    story.append(table(rows, [34, 250, 213], font=8.4, first_col_bold=True))
    story.append(Spacer(1, 10))
    story.append(P("**Four habits that cost marks when missing.**"))
    habits = ["Declare your symbols. $W$, $\\theta$, $\\lambda$ and $t$ must mean one "
              "thing each, from the first use.",
              "Answer the question that was asked. 'Underfitting caused by pooling' is "
              "not 'overfitting, so add dropout'.",
              "Put numbers in. A parameter count, a FLOP count or an output size is "
              "worth more than an adjective.",
              "Finish with the conclusion, not with a table. The last sentence is what "
              "the examiner remembers."]
    for htxt in habits:
        story.append(Paragraph(md(htxt, 9.6), ParagraphStyle(
            'hb', fontName=BODY, fontSize=9.6, leading=13.4, textColor=INK,
            leftIndent=14, bulletIndent=0, spaceAfter=3.5), bulletText='\u2022'))
    story.append(Spacer(1, 8))
    story.append(Paragraph('<font name="Body-B" size="10" color="#0E6E7A">The order in '
                           'which to spend twenty minutes</font>',
                           ParagraphStyle('bo2', fontName=BOLD, fontSize=10, leading=13,
                                          textColor=TEAL, spaceAfter=4)))
    steps = [["Minutes", "Do this"],
             ["0–2", "Write the definition and the symbols. Do not start with prose."],
             ["2–10", "Write the derivation, one equation per line, numbered."],
             ["10–15", "Draw the figure or write the numeric example."],
             ["15–18", "Write the comparison table — three rows is enough."],
             ["18–20", "Write the golden line and the keywords."]]
    story.append(table(steps, [80, 417], font=8.4, first_col_bold=True))
    story.append(Spacer(1, 12))
    story.append(Paragraph('<font name="Body-B" size="10" color="#0E6E7A">Notation used '
                           'throughout</font>',
                           ParagraphStyle('no', fontName=BOLD, fontSize=10, leading=13,
                                          textColor=TEAL, spaceBefore=4, spaceAfter=4)))
    notation = [["Symbol", "Meaning"],
                ["m, n", "number of examples; dimension of the input"],
                ["θ, W, b", "the parameter vector; the weight matrix and bias of a layer"],
                ["η, λ", "learning rate; regularisation strength (the KKT multiplier)"],
                ["K, S, P", "kernel size, stride and padding of a convolution"],
                ["H, W, C", "height, width and channel count of a feature map"],
                ["T", "sequence length, in time steps"],
                ["h, c", "hidden state and cell state of a recurrent layer"],
                ["L, J", "the loss or objective being minimised"]]
    story.append(table(notation, [86, 411], font=8.4, first_col_bold=True))
    return story


def build(units, out_pdf, book_title="MID-2 · Units III–V",
          header_right="UNITS III · IV · V", stats=None):
    doc = NoteDoc(out_pdf, book_title, header_right)
    doc.stats = stats or [("24", "model answers"), ("3", "units"),
                          ("20", "figures"), ("100", "syllabus marks")]
    story = [NextPageTemplate('body'), PageBreak()]
    story += contents_page()

    all_rev = []
    for u_i, mod_name in enumerate(units):
        mod = importlib.import_module(mod_name)
        info = mod.UNIT_INFO
        ctx = Ctx(info['unit'], info['label'])
        story.append(PartHead(info['label'], info['title'], info['subtitle']))
        story.append(Spacer(1, 8))
        story.append(Paragraph('<font name="Body-B" size="9.4" color="#0E6E7A">'
                               'UNIT AT A GLANCE</font>',
                               ParagraphStyle('gl', fontName=BOLD, fontSize=9.4,
                                              leading=12, textColor=TEAL,
                                              spaceAfter=5)))
        story.append(glance_table(mod.GLANCE))
        story.append(Spacer(1, 6))
        for num in sorted(mod.SCRIPTS):
            ans = parse(mod.SCRIPTS[num], ctx)
            story.append(CondPageBreak(160))
            story.append(QuestionHead(ans.num, ans.title, ans.meta, ans.short,
                                      key=f"u{info['unit']}q{ans.num}",
                                      unit=f"Unit {info['roman']}"))
            story.append(Spacer(1, 7))
            story.extend(ans.body)
            story.append(Spacer(1, 4))
        if u_i < len(units) - 1:
            story.append(PageBreak())
        all_rev.append((info['roman'], mod.REVISION))

    story += appendix()
    story += how_to_write()
    story.append(PageBreak())
    story += revision_block(all_rev)

    doc.multiBuild(story)
    print("wrote", out_pdf, "pages:", doc.page)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all":
        build(["content_u3", "content_u4", "content_u5"],
              os.path.join(OUTDIR, "Mid-2-Unit-III-IV-V-10-Mark-Answers.pdf"))
    elif which in ("u3", "u4", "u5"):
        mod = "content_" + which
        m = importlib.import_module(mod)
        build([mod], os.path.join(OUTDIR, f"scratch-{which}.pdf"),
              book_title=m.UNIT_INFO['label'], header_right=m.UNIT_INFO['roman'])
