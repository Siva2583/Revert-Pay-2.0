"""Markup parser: answer scripts -> platypus flowables."""
import os
import re
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, KeepTogether,
                                CondPageBreak)
from reportlab.lib import colors

from framework import (P, md, Equation, Figure, Box, ST, NAVY, TEAL, GOLD, ROSE,
                      GREEN, TEAL_L, GOLD_BG, ROSE_BG, GREEN_BG, BG, GREY, RULE,
                      QuestionHead, SectionHead, PartHead)

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs")

BOX_STYLES = {
    'tip':  (GOLD_BG, GOLD, "\u25c6 "),
    'warn': (ROSE_BG, ROSE, "\u26a0 "),
    'key':  (TEAL_L, TEAL, "\u25b6 "),
    'note': (BG, GREY, "\u25aa "),
    'ok':   (GREEN_BG, GREEN, "\u2713 "),
}


class Ctx:
    """Counters shared by all answers of one unit."""

    def __init__(self, unit, label):
        self.unit = unit
        self.label = label
        self.eq = 0
        self.fig = 0


class Answer:
    def __init__(self, num, ctx, title, meta="", short=None):
        self.num = num
        self.ctx = ctx
        self.title, self.meta = title, meta
        self.short = short or title
        self.body = []

    def eq(self, tex):
        self.ctx.eq += 1
        self.body.append(Equation(tex, f"{self.ctx.unit}.{self.ctx.eq}"))

    def fig(self, key, caption):
        self.ctx.fig += 1
        path = os.path.join(FIGDIR, key + ".svg")
        cap = f"**Fig. {self.ctx.unit}.{self.ctx.fig}**   " + caption
        self.body.append(Figure(path, cap))


def _cells(line):
    """Split a table row on | or || occurring outside $...$ maths."""
    cells, buf, in_math, i = [], [], False, 0
    while i < len(line):
        ch = line[i]
        if ch == '$':
            in_math = not in_math
            buf.append(ch)
        elif ch == '|' and not in_math:
            while i + 1 < len(line) and line[i + 1] == '|':
                i += 1
            cells.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append(''.join(buf).strip())
    if cells and cells[0] == '':
        return [c for c in cells if c != '']
    return cells


def _build_table(items, widths=None):
    rows = []
    for kind, cells in items:
        para = []
        for c in cells:
            st = ST['cellh'] if kind == 'hdr' else ST['cell']
            para.append(Paragraph(md(c, 8.2), st))
        rows.append(para)
    ncol = max(len(r) for r in rows)
    avail = 497.0
    if widths and len(widths) == ncol:
        tot = sum(widths)
        widths = [w / tot * avail for w in widths]
    else:
        widths = [avail / ncol] * ncol
    t = Table(rows, colWidths=widths, repeatRows=1)
    cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('LINEBELOW', (0, 0), (-1, -1), 0.35, RULE)]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            cmds.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor("#F5F9FB")))
    t.setStyle(TableStyle(cmds))
    if len(rows) <= 8:
        return KeepTogether([t])
    return t


def parse(script, ctx):
    lines = script.split("\n")
    i = 0
    ans = None
    stack = []

    def target():
        return stack[-1][0] if stack else ans.body

    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line.strip():
            continue
        if line.startswith("#A "):
            parts = line[3:].split("::")
            num = parts[0].strip()
            title = parts[1].strip()
            meta = parts[2].strip() if len(parts) > 2 else ""
            short = parts[3].strip() if len(parts) > 3 else None
            ans = Answer(num, ctx, title, meta, short)
            continue
        if ans is None:
            raise ValueError("content before #A: " + line)
        if line.startswith("## "):
            target().append(SectionHead(line[3:].strip()))
            continue
        if line.startswith("### "):
            target().append(SectionHead(line[4:].strip(), level=3))
            continue
        if line.startswith("@@ ") or line.startswith("$$ "):
            tex = line[3:].strip()
            if stack:
                ctx.eq += 1
                stack[-1][0].append(Equation(tex, f"{ctx.unit}.{ctx.eq}"))
            else:
                ans.eq(tex)
            continue
        if line.startswith("@fig "):
            body = line[5:]
            key, cap = body.split("||", 1) if "||" in body else (body, "")
            ans.fig(key.strip(), cap.strip())
            continue
        if line.startswith("@box "):
            spec = line[5:].split("||")
            stack.append(([], ("box", spec[0].strip(),
                               spec[1].strip() if len(spec) > 1 else "")))
            continue
        if line.startswith("@table"):
            spec = line[6:].strip()
            widths = [float(x) for x in spec.split(",")] if spec else None
            stack.append(([], ("table", widths)))
            continue
        if line.startswith("@end"):
            content, kind = stack.pop()
            if kind[0] == "box":
                bg, bar, icon = BOX_STYLES[kind[1]]
                target().append(Box(kind[2], content, bg=bg, bar=bar, icon=icon))
            else:
                target().append(_build_table(content, kind[1]))
            continue
        if line.startswith("@hdr "):
            stack[-1][0].append(("hdr", _cells(line[5:])))
            continue
        if line.startswith("@row "):
            stack[-1][0].append(("row", _cells(line[5:])))
            continue
        if line.startswith("@kw "):
            kws = [k.strip() for k in line[4:].split(";") if k.strip()]
            txt = ' <font color="#8FBFC4">·</font> '.join(md(k, 8.8) for k in kws)
            kst = ParagraphStyle('kwp', parent=ST['boxp'], fontSize=8.8, leading=12,
                                 textColor=HexColor("#0B4F58"))
            target().append(Box("Keywords to write in the exam",
                                [Paragraph(txt, kst)], bg=TEAL_L, bar=TEAL, icon="",
                                space_before=4))
            continue
        if line.startswith("@key "):
            target().append(Box("Golden line", [P(line[5:].strip(), 'boxp')],
                                bg=GOLD_BG, bar=GOLD, icon="\u2605 "))
            continue
        if line.startswith("@sp "):
            target().append(Spacer(1, float(line[4:].strip())))
            continue
        if line.startswith("- "):
            target().append(Paragraph(md(line[2:].strip(), 10), ST['bullet'],
                                      bulletText='\u2022'))
            continue
        if line.startswith("+ "):
            lst = target()
            n = 0
            for f in reversed(lst):
                if (isinstance(f, Paragraph) and f.bulletText and
                        re.fullmatch(r'\d+\.', f.bulletText)):
                    n += 1
                else:
                    break
            lst.append(Paragraph(md(line[2:].strip(), 10), ST['num'],
                                 bulletText=f"{n + 1}."))
            continue
        target().append(P(line.strip()))
    return ans
