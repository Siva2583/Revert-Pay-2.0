"""Typesetting framework: STIX serif, vector maths, callouts, running heads."""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.mathtext import MathTextParser
from matplotlib.font_manager import FontProperties

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Flowable, KeepTogether, CondPageBreak,
                                PageBreak, NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import HRFlowable
from svglib.svglib import svg2rlg

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
CACHE = os.path.join(HERE, "..", "assets", "cache")
os.makedirs(CACHE, exist_ok=True)

INK = HexColor("#1B2733")
NAVY = HexColor("#123A5F")
NAVY_D = HexColor("#0C2740")
TEAL = HexColor("#0E6E7A")
TEAL_L = HexColor("#E8F3F4")
GREY = HexColor("#5D6D7C")
RULE = HexColor("#C9D8E2")
BG = HexColor("#F4F8FB")
GOLD = HexColor("#9A6A1B")
GOLD_BG = HexColor("#FBF3E2")
ROSE = HexColor("#9B2C3B")
ROSE_BG = HexColor("#FCEFF0")
GREEN = HexColor("#1F6B4E")
GREEN_BG = HexColor("#EDF6F1")

BODY, BOLD, ITAL = "Body", "Body-B", "Body-I"


def _reg(name, file):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, file)))


_reg("Body", "STIXGeneral.ttf")
_reg("Body-B", "STIXGeneralBol.ttf")
_reg("Body-I", "STIXGeneralItalic.ttf")
_reg("Body-BI", "STIXGeneralBolIta.ttf")
registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I",
                   boldItalic="Body-BI")

matplotlib.rcParams.update({
    "mathtext.fontset": "stix",
    "font.family": "STIXGeneral",
    "svg.fonttype": "path",
    "figure.dpi": 200,
})

SYMS = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
    'varepsilon': 'ε', 'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι',
    'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'pi': 'π',
    'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ', 'phi': 'φ',
    'varphi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω', 'Gamma': 'Γ',
    'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ', 'Pi': 'Π',
    'Sigma': 'Σ', 'Upsilon': 'Υ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω',
    'le': '≤', 'leq': '≤', 'ge': '≥', 'geq': '≥', 'neq': '≠', 'ne': '≠',
    'approx': '≈', 'sim': '∼', 'simeq': '≃', 'propto': '∝', 'equiv': '≡',
    'times': '×', 'cdot': '·', 'pm': '±', 'mp': '∓', 'div': '÷',
    'to': '→', 'rightarrow': '→', 'leftarrow': '←', 'Rightarrow': '⇒',
    'Leftarrow': '⇐', 'leftrightarrow': '↔', 'longrightarrow': '⟶',
    'iff': '⇔', 'Leftrightarrow': '⇔', 'Longrightarrow': '⟹',
    'in': '∈', 'notin': '∉', 'subset': '⊂', 'subseteq': '⊆', 'cup': '∪',
    'cap': '∩', 'emptyset': '∅', 'forall': '∀', 'exists': '∃',
    'sum': 'Σ', 'prod': 'Π', 'int': '∫', 'partial': '∂', 'nabla': '∇',
    'infty': '∞', 'sqrt': '√', 'ldots': '…', 'dots': '…', 'cdots': '⋯',
    'top': '<super size="6.9" rise="3.4">T</super>', 'circ': '∘', 'ast': '∗',
    '|': '‖', 'mid': '|', 'lVert': '‖', 'rVert': '‖', 'lvert': '|',
    'rvert': '|', 'langle': '⟨', 'rangle': '⟩', 'odot': '⊙', 'oplus': '⊕',
    'ell': 'ℓ', 'quad': '  ', 'qquad': '    ', ',': '\u2009', ';': '\u2005',
    ':': '\u2005', ' ': ' ', '{': '{', '}': '}', '%': '%', '&': '&amp;',
    '#': '#', '_': '_',
    'log': 'log', 'exp': 'exp', 'ln': 'ln', 'max': 'max', 'min': 'min',
    'lim': 'lim', 'det': 'det', 'tr': 'tr', 'diag': 'diag', 'sgn': 'sgn',
    'Var': 'Var', 'Cov': 'Cov', 'E': 'E',
}


def _group(s, i):
    depth, j = 0, i
    while j < len(s):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def tex_inline(tex):
    """LaTeX subset -> ReportLab inline markup (fallback only)."""
    out, i, n = [], 0, len(tex)
    while i < n:
        ch = tex[i]
        if ch == '\\':
            m = re.match(r'\\([A-Za-z]+)', tex[i:])
            if m:
                cmd = m.group(1)
                i += len(m.group(0))
                if cmd in ('mathbb', 'mathcal', 'mathbf', 'mathrm', 'text', 'mathit'):
                    if i < n and tex[i] == '{':
                        inner, i = _group(tex, i)
                        if cmd == 'mathbb':
                            out.append({'R': 'ℝ', 'E': 'E', '1': '1'}.get(inner, inner))
                        elif cmd == 'mathbf':
                            out.append('<b>' + tex_inline(inner) + '</b>')
                        elif cmd in ('mathit', 'mathcal'):
                            out.append('<i>' + tex_inline(inner) + '</i>')
                        else:
                            out.append(tex_inline(inner))
                    continue
                if cmd in ('hat', 'bar', 'tilde', 'vec', 'dot'):
                    if i < n and tex[i] == '{':
                        inner, i = _group(tex, i)
                        mark = {'hat': '\u0302', 'bar': '\u0304', 'tilde': '\u0303',
                                'vec': '\u20d7', 'dot': '\u0307'}[cmd]
                        out.append(tex_inline(inner) + mark)
                    continue
                if cmd == 'frac':
                    num = den = ''
                    if i < n and tex[i] == '{':
                        num, i = _group(tex, i)
                    if i < n and tex[i] == '{':
                        den, i = _group(tex, i)
                    out.append(tex_inline(num) + '/' + tex_inline(den))
                    continue
                if cmd == 'sqrt':
                    if i < n and tex[i] == '{':
                        inner, i = _group(tex, i)
                        out.append('√(' + tex_inline(inner) + ')')
                    continue
                if cmd in SYMS:
                    out.append(SYMS[cmd])
                    continue
                out.append(cmd)
                continue
            nxt = tex[i + 1] if i + 1 < n else ''
            out.append({'\\': '<br/>', '|': '‖'}.get(nxt, nxt))
            i += 2
            continue
        if ch in '^_':
            tag = 'super' if ch == '^' else 'sub'
            i += 1
            if i < n and tex[i] == '{':
                inner, i = _group(tex, i)
                out.append(f'<{tag}>{tex_inline(inner)}</{tag}>')
            elif i < n:
                out.append(f'<{tag}>{tex_inline(tex[i])}</{tag}>')
                i += 1
            continue
        out.append({'&': '&amp;', '<': '&lt;', '>': '&gt;'}.get(ch, ch))
        i += 1
    return ''.join(out)


_parser = MathTextParser("path")
_inl_cache = {}
_eq_cache = {}

BIGOPS = [(chr(92) + 'sum', chr(92) + 'Sigma'), (chr(92) + 'prod', chr(92) + 'Pi')]


def _flat_frac(tex):
    pat = re.compile(r'\\frac\{([^{}]*)\}\{([^{}]*)\}')

    def rep(m):
        num, den = m.group(1), m.group(2)
        if re.search(r'[+\-\s]', den) or len(den) > 3:
            den = '(' + den + ')'
        return num + '/' + den
    for _ in range(3):
        tex, k = pat.subn(rep, tex)
        if not k:
            break
    return tex


def _shrink_ops(tex):
    for a, b in BIGOPS:
        tex = tex.replace(a + '_{', b + '_{').replace(a + '^', b + '^')
        tex = re.sub(re.escape(a) + r'(?![A-Za-z])', lambda m, b=b: b, tex)
    return tex


def math_img(tex, size=10, color="#1B2733"):
    tex = _shrink_ops(_flat_frac(tex))
    key = (tex, round(size, 1), color)
    if key in _inl_cache:
        return _inl_cache[key]
    expr = tex if tex.strip().startswith('$') else '$' + tex + '$'
    props = FontProperties(size=size)
    try:
        w, h, d, _, _ = _parser.parse(expr, dpi=72, prop=props)
    except Exception:
        return None
    pad = 0.5
    W, H = w + 2 * pad, h + 2 * pad
    dpi = 520
    fig = plt.figure(figsize=(W / 72.0, H / 72.0), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_axis_off()
    ax.text(pad, pad + d, expr, fontsize=size, va='baseline', ha='left', color=color)
    fname = os.path.join(CACHE, f"inl_{abs(hash(key))}.png")
    fig.savefig(fname, dpi=dpi, transparent=True, pad_inches=0)
    plt.close(fig)
    markup = (f'<img src="{fname}" width="{W:.2f}" height="{H:.2f}" '
              f'valign="{-d - pad:.2f}"/>')
    _inl_cache[key] = markup
    return markup


def tex_drawing(tex, fontsize=10.5):
    key = (tex, fontsize)
    if key in _eq_cache:
        return _eq_cache[key]
    fig = plt.figure(figsize=(0.01, 0.01))
    body = tex.replace(chr(92) + 'frac', chr(92) + 'dfrac')
    fig.text(0, 0, '$' + body + '$', fontsize=fontsize)
    fname = os.path.join(CACHE, f"eq_{abs(hash(key))}.svg")
    fig.savefig(fname, bbox_inches="tight", pad_inches=0.03, transparent=True,
                format="svg")
    plt.close(fig)
    d = svg2rlg(fname)
    _eq_cache[key] = d
    return d


TOKEN = re.compile(r'(\$[^$]+\$|\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`)')


def md(text, size=None, color=None):
    if size is None:
        size = 10.0
    parts = TOKEN.split(text)
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith('$') and p.endswith('$') and len(p) > 2:
            img = math_img(p[1:-1], size, color or "#1B2733")
            out.append(img if img else tex_inline(p[1:-1]))
        elif p.startswith('**') and p.endswith('**'):
            out.append('<b>' + md(p[2:-2], size, color) + '</b>')
        elif p.startswith('*') and p.endswith('*') and len(p) > 2:
            out.append('<i>' + md(p[1:-1], size, color) + '</i>')
        elif p.startswith('`') and p.endswith('`'):
            out.append('<font name="Body-I" color="#0E6E7A">' + p[1:-1] + '</font>')
        else:
            out.append(p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
    return ''.join(out)


class Equation(Flowable):
    def __init__(self, tex, number=None, fontsize=10.5, space_before=4,
                 space_after=6):
        Flowable.__init__(self)
        self.tex, self.number, self.fs = tex, number, fontsize
        self.sb, self.sa = space_before, space_after

    def wrap(self, aw, ah):
        self.aw = aw
        self.d = tex_drawing(self.tex, self.fs)
        self.nw = (pdfmetrics.stringWidth(f"({self.number})", BODY, 9) + 12
                   if self.number else 0)
        self.s = min(1.0, (aw - self.nw - 8) / max(self.d.width, 1))
        self.height = self.d.height * self.s + self.sb + self.sa
        return aw, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        w = self.d.width * self.s
        x = (self.aw - w) / 2
        if self.number:
            x = max(2, x - self.nw / 2)
        c.translate(x, self.sa)
        if self.s != 1.0:
            c.scale(self.s, self.s)
        self.d.drawOn(c, 0, 0)
        c.restoreState()
        if self.number:
            c.setFont(BODY, 9)
            c.setFillColor(GREY)
            c.drawRightString(self.aw - 2, self.sa + 1, f"({self.number})")


class Figure(Flowable):
    def __init__(self, path, caption="", width=None, space_before=8, space_after=4):
        Flowable.__init__(self)
        self.path, self.caption = path, caption
        self.w_target = width
        self.sb, self.sa = space_before, space_after
        self.d = svg2rlg(path)

    def wrap(self, aw, ah):
        self.aw = aw
        self.s = (self.w_target / self.d.width) if self.w_target else min(
            1.0, aw / self.d.width)
        self.ih = self.d.height * self.s
        cap_h = 0
        if self.caption:
            self.cap = Paragraph(md(self.caption, 8.3, "#5D6D7C"), ST['caption'])
            cw, cap_h = self.cap.wrap(aw, ah)
        self.cap_h = cap_h
        self.height = self.sb + self.ih + cap_h + self.sa
        return aw, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate((self.aw - self.d.width * self.s) / 2, self.sa + self.cap_h)
        c.scale(self.s, self.s)
        self.d.drawOn(c, 0, 0)
        c.restoreState()
        if self.caption:
            self.cap.drawOn(c, 0, self.sa)


class Box(Flowable):
    def __init__(self, title, flowables, bg=TEAL_L, bar=TEAL, width=None, pad=6,
                 space_before=6, space_after=6, icon=""):
        Flowable.__init__(self)
        self.title = title
        self.items = flowables
        self.bg, self.bar = bg, bar
        self.pad = pad
        self.sb, self.sa = space_before, space_after
        self.icon = icon

    def wrap(self, aw, ah):
        self.aw = aw
        self.inner_w = aw - 2 * self.pad - 5
        self.hs = []
        total = 0
        for f in self.items:
            w, h = f.wrap(self.inner_w, ah)
            self.hs.append(h)
            total += h
        self.title_h = 0
        if self.title:
            self.ts = Paragraph(
                '<font name="Body-B" size="8.6" color="%s">%s</font>' %
                ('#' + self.bar.hexval()[2:], self.icon + md(self.title).upper()),
                ParagraphStyle('bt', fontName=BODY, fontSize=8.6, leading=11))
            _, self.title_h = self.ts.wrap(self.inner_w, 40)
            self.title_h += 3
        self.body_h = total + self.title_h
        self.height = self.sb + self.body_h + 2 * self.pad + self.sa
        return aw, self.height

    def draw(self):
        c = self.canv
        h = self.body_h + 2 * self.pad
        c.saveState()
        c.setFillColor(self.bg)
        c.setStrokeColor(self.bg)
        c.roundRect(0, self.sa, self.aw, h, 2.5, stroke=0, fill=1)
        c.setFillColor(self.bar)
        c.rect(0, self.sa, 2.6, h, stroke=0, fill=1)
        y = self.sa + h - self.pad
        if self.title:
            y -= self.title_h
            self.ts.drawOn(c, self.pad + 3, y + 2)
        for f, hh in zip(self.items, self.hs):
            y -= hh
            f.drawOn(c, self.pad + 3, y)
        c.restoreState()


class QuestionHead(Flowable):
    def __init__(self, num, title, meta="", short=None, key=None, unit=""):
        Flowable.__init__(self)
        self.num, self.title, self.meta = num, title, meta
        self.short = short or title[:60]
        self.key = key or f"q{num}"
        self.unit = unit

    def wrap(self, aw, ah):
        self.aw = aw
        self.qt = Paragraph(md(self.title, 11.4, "#FFFFFF"),
                            ParagraphStyle('qt', fontName=BOLD, fontSize=11.4,
                                           leading=14.6, textColor=colors.white))
        tw, th = self.qt.wrap(aw - 64, ah)
        self.th = th
        self.mt = Paragraph(md(self.meta, 8, "#9FC3D8"),
                            ParagraphStyle('mt', fontName=BODY, fontSize=8, leading=10,
                                           textColor=HexColor("#9FC3D8")))
        mw, mh = self.mt.wrap(aw - 64, 40)
        self.height = th + (mh + 6 if self.meta else 0) + 22
        return aw, self.height

    def draw(self):
        c = self.canv
        c.bookmarkPage(self.key)
        try:
            c.addOutlineEntry(f"Q{self.num}.  {self.short}", self.key, level=1,
                              closed=0)
        except Exception:
            pass
        c.saveState()
        h = self.height
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.aw, h - 6, 3, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(0, 0, 4, h - 6, stroke=0, fill=1)
        c.setFillColor(HexColor("#0A2036"))
        c.roundRect(8, h - 6 - 8 - 26, 40, 26, 2, stroke=0, fill=1)
        c.setFont(BOLD, 12)
        c.setFillColor(HexColor("#7FD3DB"))
        c.drawCentredString(28, h - 6 - 8 - 18, f"Q{self.num}")
        self.qt.drawOn(c, 54, h - 6 - 9 - self.th)
        if self.meta:
            self.mt.drawOn(c, 54, 8)
        c.restoreState()


class PartHead(Flowable):
    def __init__(self, label, title, subtitle, blurb=""):
        Flowable.__init__(self)
        self.label, self.title, self.subtitle, self.blurb = label, title, subtitle, blurb

    def wrap(self, aw, ah):
        self.aw = aw
        self.t1 = Paragraph(md(self.label, 9), ParagraphStyle(
            'p1', fontName=BOLD, fontSize=9, leading=12,
            textColor=HexColor("#7FD3DB"), spaceAfter=6))
        self.t2 = Paragraph(md(self.title, 22), ParagraphStyle(
            'p2', fontName=BOLD, fontSize=22, leading=26, textColor=colors.white))
        self.t3 = Paragraph(md(self.subtitle, 11), ParagraphStyle(
            'p3', fontName=ITAL, fontSize=11, leading=15,
            textColor=HexColor("#BBD5E4"), spaceBefore=4))
        h1 = self.t1.wrap(aw - 40, 40)[1]
        h2 = self.t2.wrap(aw - 40, 80)[1]
        h3 = self.t3.wrap(aw - 40, 60)[1]
        self.hs = (h1, h2, h3)
        self.height = 34 + h1 + h2 + h3 + 34
        return aw, self.height

    def draw(self):
        c = self.canv
        key = "part" + re.sub(r'\W+', '', self.label)
        c.bookmarkPage(key)
        try:
            c.addOutlineEntry(f"{self.label} — {self.title}", key, level=0, closed=0)
        except Exception:
            pass
        c.saveState()
        h = self.height
        c.setFillColor(NAVY_D)
        c.roundRect(0, 0, self.aw, h, 3, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(0, 0, self.aw, 5, stroke=0, fill=1)
        y = h - 34
        y -= self.hs[0]
        self.t1.drawOn(c, 20, y)
        y -= self.hs[1]
        self.t2.drawOn(c, 20, y)
        y -= self.hs[2]
        self.t3.drawOn(c, 20, y)
        c.restoreState()


class ResetQ(Flowable):
    """Zero-height marker that clears the running question label."""

    _reset_q = True

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        pass


class SectionHead(Flowable):
    def __init__(self, text, level=2):
        Flowable.__init__(self)
        self.text = text
        self.level = level

    def wrap(self, aw, ah):
        self.aw = aw
        st = ST['h3'] if self.level == 3 else ST['h2']
        self.p = Paragraph(md(self.text), st)
        w, h = self.p.wrap(aw - 10, ah)
        self.height = h + (4 if self.level == 2 else 2)
        return aw, self.height

    def draw(self):
        c = self.canv
        col = TEAL if self.level == 2 else GOLD
        c.setFillColor(col)
        if self.level == 2:
            c.rect(0, self.height - 11, 2.4, 9, stroke=0, fill=1)
        else:
            c.circle(2.2, self.height - 6, 1.6, stroke=0, fill=1)
        self.p.drawOn(c, 8, 0)


ST = {}
ST['body'] = ParagraphStyle('body', fontName=BODY, fontSize=10, leading=14.6,
                            alignment=TA_LEFT, textColor=INK, spaceAfter=5.0)
ST['h2'] = ParagraphStyle('h2', fontName=BOLD, fontSize=11, leading=14,
                          textColor=NAVY, spaceBefore=10, spaceAfter=4,
                          keepWithNext=1)
ST['h3'] = ParagraphStyle('h3', fontName='Body-BI', fontSize=10, leading=13,
                          textColor=TEAL, spaceBefore=7, spaceAfter=3,
                          keepWithNext=1)
ST['bullet'] = ParagraphStyle('bullet', parent=ST['body'], leftIndent=14,
                              bulletIndent=0, spaceAfter=3.2)
ST['num'] = ParagraphStyle('num', parent=ST['body'], leftIndent=16,
                           bulletIndent=0, spaceAfter=3.2)
ST['caption'] = ParagraphStyle('caption', fontName=BODY, fontSize=8.3, leading=10.6,
                               textColor=GREY, alignment=TA_CENTER, spaceBefore=3)
ST['cell'] = ParagraphStyle('cell', fontName=BODY, fontSize=8.2, leading=10.7,
                            textColor=INK)
ST['cellh'] = ParagraphStyle('cellh', fontName='Body-B', fontSize=8.2, leading=10.7,
                             textColor=colors.white)
ST['boxp'] = ParagraphStyle('boxp', parent=ST['body'], fontSize=9.2, leading=13,
                            spaceAfter=2.5)


def P(text, style='body'):
    return Paragraph(md(text), ST[style])


def table(data, widths, header=True, font=8.2, zebra=True, first_col_bold=False):
    rows = []
    for r_i, row in enumerate(data):
        cells = []
        for c_i, cell in enumerate(row):
            if isinstance(cell, str):
                if header and r_i == 0:
                    cells.append(Paragraph(md(cell, font), ParagraphStyle(
                        'th', parent=ST['cellh'], fontSize=font, leading=font * 1.3)))
                else:
                    st = ParagraphStyle('td', parent=ST['cell'], fontSize=font,
                                        leading=font * 1.3)
                    txt = md(cell, font)
                    if first_col_bold and c_i == 0:
                        txt = '<b>' + txt + '</b>'
                    cells.append(Paragraph(txt, st))
            else:
                cells.append(cell)
        rows.append(cells)
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.35, RULE)]
    if header:
        cmds += [('BACKGROUND', (0, 0), (-1, 0), NAVY),
                 ('LINEBELOW', (0, 0), (-1, 0), 0.6, NAVY_D)]
        start = 1
    else:
        start = 0
    if zebra:
        for i in range(start, len(rows)):
            if (i - start) % 2 == 1:
                cmds.append(('BACKGROUND', (0, i), (-1, i), HexColor("#F5F9FB")))
    t.setStyle(TableStyle(cmds))
    return t


class NoteDoc(BaseDocTemplate):
    def __init__(self, filename, book_title, header_right, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=A4, leftMargin=52,
                                 rightMargin=46, topMargin=58, bottomMargin=52,
                                 title=book_title, author="G. Pullaiah College of "
                                 "Engineering & Technology",
                                 subject="A40531 Deep Learning — 10-mark model "
                                 "answers", **kw)
        self.book_title = book_title
        self.header_right = header_right
        self.current_q = ""
        self.current_q_page = 10 ** 6
        self.stats = None

        fw, fh = self.width, self.height
        cover = PageTemplate(id='cover', frames=[Frame(52, 56, A4[0] - 98, A4[1] - 56,
                                                      leftPadding=0, rightPadding=0,
                                                      topPadding=0, bottomPadding=0,
                                                      id='cf')],
                             onPage=self.draw_cover)
        body = PageTemplate(id='body', frames=[Frame(self.leftMargin, self.bottomMargin,
                                                     fw, fh, id='bf', leftPadding=0,
                                                     rightPadding=0, topPadding=0,
                                                     bottomPadding=0)],
                            onPage=self.draw_header, onPageEnd=self.draw_footer)
        self.addPageTemplates([cover, body])

    def draw_cover(self, c, doc):
        W, H = A4
        c.setFillColor(NAVY_D)
        c.rect(0, H - 320, W, 320, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(0, H - 326, W, 6, stroke=0, fill=1)
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont(BOLD, 9)
        c.drawString(52, H - 60,
                     "G. PULLAIAH COLLEGE OF ENGINEERING AND TECHNOLOGY")
        c.setFont(BODY, 8.2)
        c.setFillColor(HexColor("#A8C4D8"))
        c.drawString(52, H - 74, "Autonomous  ·  Affiliated to JNTUA, Anantapur  ·  Kurnool")
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont(BODY, 9.5)
        c.drawString(52, H - 118, "A40531  ·  DEEP LEARNING  ·  IV B.Tech CSE  ·  I Semester")
        c.setFont(BOLD, 42)
        c.drawString(52, H - 178, "MID-2")
        c.setFont(BOLD, 20)
        c.setFillColor(HexColor("#7FD3DB"))
        c.drawString(52, H - 210, "Units III · IV · V")
        c.setFont(BODY, 11.5)
        c.setFillColor(HexColor("#BBD5E4"))
        c.drawString(52, H - 240, "Model Answers for the 10-Mark Question Bank")
        c.setFont(ITAL, 10)
        c.setFillColor(HexColor("#8FB4CB"))
        c.drawString(52, H - 262,
                     "Regularisation  ·  optimisation  ·  CNNs  ·  recurrent networks")

        cards = [("UNIT III", "Regularisation and\nOptimisation", "answers 1 – 8",
                  "overfitting · penalties\ndropout · optimisers"),
                 ("UNIT IV", "Convolutional\nNetworks", "answers 9 – 16",
                  "kernels · strides\npooling · priors"),
                 ("UNIT V", "Recurrent Networks,\nLSTM and Autoencoders",
                  "answers 17 – 24", "unrolling · gates\nseq2seq · autoencoders")]
        cx = 52
        for lab, ttl, cnt, desc in cards:
            c.setFillColor(HexColor("#F4F8FB"))
            c.setStrokeColor(HexColor("#DCE7EE"))
            c.roundRect(cx, 300, 152, 128, 3, stroke=1, fill=1)
            c.setFillColor(TEAL)
            c.setFont(BOLD, 8)
            c.drawString(cx + 12, 404, lab)
            c.setFillColor(NAVY)
            c.setFont(BOLD, 11.5)
            for i, ln in enumerate(ttl.split("\n")):
                c.drawString(cx + 12, 386 - i * 15, ln)
            c.setFont(ITAL, 7.4)
            c.setFillColor(HexColor("#8FA6B6"))
            for i, ln in enumerate(desc.split("\n")):
                c.drawString(cx + 12, 352 - i * 10, ln)
            c.setFillColor(GREY)
            c.setFont(BODY, 7.8)
            c.drawString(cx + 12, 314, cnt)
            cx += 168

        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.line(52, 268, W - 46, 268)
        c.setFont(BODY, 8.4)
        c.setFillColor(GREY)
        c.drawString(52, 250, "Every answer carries a numbered derivation, a vector "
                     "figure, an examiner's checklist and a one-line golden statement.")
        c.drawString(52, 236, "Prepared for the Mid-2 examination · A40531 Deep "
                     "Learning · 2025–26")
        c.setFont(ITAL, 8.4)
        c.setFillColor(HexColor("#8FA6B6"))
        c.drawString(52, 210, "G. Pullaiah College of Engineering and Technology, "
                     "Kurnool · Department of CSE (Data Science)")

        if getattr(self, 'stats', None):
            x = 52
            for val, lab in self.stats:
                c.setFont(BOLD, 15)
                c.setFillColor(NAVY)
                c.drawString(x, 120, val)
                c.setFont(BODY, 7.2)
                c.setFillColor(GREY)
                c.drawString(x, 106, lab.upper())
                x += 124

    def draw_header(self, c, doc):
        W, H = A4
        c.saveState()
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(52, H - 42, W - 46, H - 42)
        c.setFont(BODY, 7.4)
        c.setFillColor(GREY)
        c.drawString(52, H - 38, "A40531  DEEP LEARNING  ·  MID-2 MODEL ANSWERS")
        c.drawRightString(W - 46, H - 38, self.header_right)
        c.restoreState()

    def draw_footer(self, c, doc):
        W, H = A4
        c.saveState()
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(52, 40, W - 46, 40)
        c.setFont(BODY, 7.4)
        c.setFillColor(GREY)
        if doc.page >= self.current_q_page and self.current_q:
            c.drawString(52, 29, self.current_q[:80])
        c.setFont(BOLD, 8)
        c.setFillColor(NAVY)
        c.drawRightString(W - 46, 29, str(doc.page))
        c.restoreState()

    def afterFlowable(self, flowable):
        if getattr(flowable, '_reset_q', False):
            self.current_q = ""
            return
        if isinstance(flowable, PartHead):
            self.notify('TOCEntry', (0, f"{flowable.label} — {flowable.title}",
                                     self.page, "part" +
                                     re.sub(r'\W+', '', flowable.label)))
            self.current_q = flowable.label
        elif isinstance(flowable, QuestionHead):
            pre = (flowable.unit + "  ·  ") if flowable.unit else ""
            self.current_q = f"{pre}Q{flowable.num}  ·  {flowable.short}"
            self.current_q_page = self.page
            self.notify('TOCEntry', (1, f"Q{flowable.num}.  {flowable.short}",
                                     self.page, flowable.key))
