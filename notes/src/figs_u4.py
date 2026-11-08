"""Figures for Unit IV."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

from figlib import (canvas, box, arrow, save, NAVY, TEAL, GOLD, ROSE, GREEN, GREY,
                    LIGHT, SAND, PINK, MINT, INK)


def _grid(ax, x0, y0, n, cell, fc="white", ec="#9FB3C2", lw=0.6, labels=None,
          fs=6.5):
    for r in range(n):
        for c in range(n):
            ax.add_patch(Rectangle((x0 + c * cell, y0 + (n - 1 - r) * cell), cell,
                                   cell, fc=fc, ec=ec, lw=lw, zorder=2))
            if labels is not None:
                ax.text(x0 + c * cell + cell / 2, y0 + (n - 1 - r) * cell + cell / 2,
                        str(labels[r][c]), ha="center", va="center", fontsize=fs,
                        color=GREY, zorder=3)
    return x0, y0, n * cell


def fig_conv():
    fig, ax = canvas(6.5, 2.35, (0, 13), (0, 4.7))
    cell = 0.52
    lab = [[(r + c) % 6 for c in range(6)] for r in range(6)]

    _grid(ax, 0.2, 1.15, 6, cell, labels=lab)
    ax.add_patch(Rectangle((0.2 + 1 * cell, 1.15 + 3 * cell), 3 * cell, 3 * cell,
                           fc=GOLD, ec=GOLD, alpha=0.28, lw=1.1, zorder=3))
    ax.text(0.2 + 3.0 * cell, 0.72, r"input  $6\times 6$", ha="center", fontsize=7,
            color=INK)
    ax.text(0.2 + 2.5 * cell, 1.15 + 6 * cell + 0.16, r"$3\times 3$ receptive field",
            ha="center", fontsize=6.6, color=GOLD)

    arrow(ax, (4.35, 2.35), (5.15, 2.35), color=GREY, lw=1.0)

    kc = 0.74
    kx, ky = 5.25, 1.15 + 3 * cell + 0.1
    _grid(ax, kx, ky, 3, kc, fc=LIGHT, ec=TEAL, lw=0.8,
          labels=[["w", "", "w"], ["", "w", ""], ["w", "", "w"]], fs=6.0)
    ax.text(kx + 1.5 * kc, ky - 0.30, "kernel $K=3$\n(shared everywhere)",
            ha="center", fontsize=6.6, color=TEAL)
    ax.text(kx + 1.5 * kc, ky + 3 * kc + 0.14, r"$\sum_{i,j}w_{ij}x_{ij}+b$",
            ha="center", fontsize=7.2, color=TEAL)

    arrow(ax, (7.55, 2.35), (8.35, 2.35), color=GREY, lw=1.0)

    ox, oy = 8.45, 1.45
    oc = 0.55
    vals = [[5, 3, 2, 1], [4, 7, 3, 0], [2, 4, 6, 2], [1, 2, 3, 5]]
    _grid(ax, ox, oy, 4, oc, fc=MINT, ec=TEAL, lw=0.6, labels=vals)
    ax.add_patch(Rectangle((ox, oy + 2 * oc), oc, oc, fc=ROSE, ec=ROSE, alpha=0.30,
                           lw=1.0, zorder=3))
    ax.text(ox + 2 * oc, oy - 0.28, r"feature map  $4\times 4$", ha="center",
            fontsize=7, color=INK)
    ax.text(ox + 2 * oc, oy + 4 * oc + 0.14, "one value per position", ha="center",
            fontsize=6.6, color=GREY)
    ax.text(6.6, 0.18, r"$O=(W-K+2P)/S+1=(6-3+0)/1+1=4$   with "
            r"$W{=}6$, $K{=}3$, $P{=}0$, $S{=}1$", ha="center", fontsize=6.4,
            color=GREY)
    save(fig, "fig4_conv")


def fig_sizes():
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.45))
    fig.subplots_adjust(0.02, 0.12, 0.985, 0.90, wspace=0.10)
    specs = [("valid, $S=1$, $P=0$", 1, 0, 4, r"$O=\frac{6-3+0}{1}+1=4$"),
             ("valid, $S=2$, $P=0$", 2, 0, 2, r"$O=\frac{6-3+0}{2}+1=2$"),
             ("same, $S=1$, $P=1$", 1, 1, 6, r"$O=\frac{6-3+2}{1}+1=6$")]
    for ax, (ttl, S, P, O, tex) in zip(axes, specs):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_axis_off()
        ax.set_title(ttl, fontsize=7.4, color=INK, pad=2)
        cell = 1.0
        x0, y0 = 1.5, 4.3
        if P:
            ax.add_patch(Rectangle((x0 - P * cell, y0 - P * cell),
                                   (6 + 2 * P) * cell, (6 + 2 * P) * cell,
                                   fc=SAND, ec=GOLD, lw=0.9, ls=(0, (3, 2)),
                                   zorder=1))
            ax.text(x0 + 3 * cell, y0 + 7 * cell + 0.15, "$P=1$ ring of zeros",
                    ha="center", fontsize=6.0, color=GOLD)
        for r in range(6):
            for c in range(6):
                ax.add_patch(Rectangle((x0 + c * cell, y0 + (5 - r) * cell), cell,
                                       cell, fc="white", ec="#9FB3C2", lw=0.5,
                                       zorder=2))
        for k in range(min(O, 2)):
            ax.add_patch(Rectangle((x0 + k * S * cell, y0 + (6 - 3 - k * S) * cell),
                                   3 * cell, 3 * cell, fc=(TEAL if k == 0 else ROSE),
                                   alpha=0.20, lw=0.9,
                                   ec=(TEAL if k == 0 else ROSE), zorder=3))
        oc = 0.62
        ox, oy = 5.55, 0.75
        for r in range(O):
            for c in range(O):
                ax.add_patch(Rectangle((ox + c * oc, oy + (O - 1 - r) * oc), oc, oc,
                                       fc=MINT, ec=TEAL, lw=0.5))
        ax.text(ox + O * oc / 2, oy + O * oc + 0.18, f"$O\\times O={O}\\times{O}$",
                ha="center", fontsize=6.4, color=TEAL)
        ax.text(5, 0.15, tex, ha="center", fontsize=7.6, color=INK)
    fig.text(0.5, 0.01, "same $6\\times6$ input and $3\\times3$ kernel: stride and "
             "padding decide the output size", ha="center", fontsize=6.6, color=GREY)
    save(fig, "fig4_sizes")


def fig_fc_cnn():
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.5))
    fig.subplots_adjust(0.02, 0.06, 0.985, 0.92, wspace=0.08)
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_axis_off()
        ax.set_title(("fully connected: $n_{in}n_{out}$ weights" if k == 0 else
                      "convolutional: 9 weights, shared at every position"),
                     fontsize=7.4, color=INK, pad=2)
        n = 5
        left = [(1.6, 1.4 + i * 1.65) for i in range(n)]
        right = [(6.6, 1.4 + i * 1.65) for i in range(n)]
        for a in left:
            for b in right:
                if k == 0:
                    ax.plot([a[0], b[0]], [a[1], b[1]], lw=0.35, color="#D3DFE7")
                elif left.index(a) == right.index(b) or abs(left.index(a) -
                                                             right.index(b)) <= 1:
                    same = left.index(a) == right.index(b)
                    ax.plot([a[0], b[0]], [a[1], b[1]], lw=1.5 if same else 0.5,
                            color=TEAL if same else "#B9CBD8")
        for i, (x, y) in enumerate(left):
            ax.add_patch(Rectangle((x, y - 0.55), 0.9, 1.1, fc=LIGHT, ec=TEAL,
                                   lw=0.7, zorder=3))
        for i, (x, y) in enumerate(right):
            ax.add_patch(Rectangle((x, y - 0.55), 0.9, 1.1, fc=MINT, ec=TEAL,
                                   lw=0.7, zorder=3))
        if k == 0:
            ax.text(5, 0.35, "every input touches every output\n"
                    "$5\\times5=25$ independent parameters",
                    ha="center", fontsize=6.4, color=ROSE)
        else:
            ax.text(5, 0.35, "local 3-tap window, one shared $w$ (bold)\n"
                    "$3$ parameters reused at all positions",
                    ha="center", fontsize=6.4, color=TEAL)
        ax.text(2.05, 9.0, "input\nlayer", ha="center", fontsize=6.4, color=GREY)
        ax.text(7.05, 9.0, "output\nlayer", ha="center", fontsize=6.4, color=GREY)
    save(fig, "fig4_fc_cnn")


def fig_pool():
    fig, ax = canvas(6.4, 2.45, (0, 13), (0, 4.9))
    fmap = [[1, 2, 3, 0],
            [4, 9, 1, 2],
            [0, 1, 5, 3],
            [2, 0, 1, 4]]
    cell = 0.78
    x0, y0 = 0.4, 1.25
    for r in range(4):
        for c in range(4):
            v = fmap[r][c]
            ax.add_patch(Rectangle((x0 + c * cell, y0 + (3 - r) * cell), cell, cell,
                                   fc=("#BFE3E6" if v >= 5 else "white"),
                                   ec="#9FB3C2", lw=0.6, zorder=2))
            ax.text(x0 + c * cell + cell / 2, y0 + (3 - r) * cell + cell / 2, str(v),
                    ha="center", va="center", fontsize=7, color=INK, zorder=3)
    for i in range(0, 4, 2):
        for j in range(0, 4, 2):
            ax.add_patch(Rectangle((x0 + i * cell, y0 + (2 - j) * cell), 2 * cell,
                                   2 * cell, fc="none", ec=GOLD, lw=1.0,
                                   ls=(0, (3, 2)), zorder=4))
    ax.text(x0 + 2 * cell, y0 - 0.35, r"$4\times4$ activation map", ha="center",
            fontsize=6.8, color=INK)
    arrow(ax, (4.0, 2.35), (5.1, 2.35), color=GREY, lw=1.0)
    ax.text(4.55, 2.52, "max-pool\n$2\\times2$, $S{=}2$", ha="center", fontsize=6.2,
            color=GOLD)
    pooled = [[9, 3], [2, 5]]
    oc = 0.95
    ox, oy = 5.3, 1.6
    for r in range(2):
        for c in range(2):
            ax.add_patch(Rectangle((ox + c * oc, oy + (1 - r) * oc), oc, oc,
                                   fc=MINT, ec=TEAL, lw=0.7, zorder=2))
            ax.text(ox + c * oc + oc / 2, oy + (1 - r) * oc + oc / 2, str(pooled[r][c]),
                    ha="center", va="center", fontsize=7.5, color=INK, zorder=3)
    ax.text(ox + oc, oy - 0.35, r"$2\times2$ pooled map", ha="center", fontsize=6.8,
            color=INK)
    ax.text(9.6, 3.35, "the peak has moved\nby up to 2 pixels, but the\n"
            "pooled value is unchanged\n→ translation tolerance",
            fontsize=6.5, color=TEAL, va="center")
    ax.text(9.6, 1.5, "the exact location of\nthe maximum is no\nlonger recoverable",
            fontsize=6.5, color=ROSE, va="center")
    save(fig, "fig4_pool")


def fig_gap():
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.35))
    fig.subplots_adjust(0.02, 0.06, 0.985, 0.92, wspace=0.06)
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_axis_off()
        ax.set_title(("flatten → dense" if k == 0 else
                      "global average pooling → dense"),
                     fontsize=7.4, color=INK, pad=2)
        nf = 4
        for c in range(nf):
            for r in range(3):
                for cc in range(3):
                    ax.add_patch(Rectangle((0.6 + c * 0.95 + cc * 0.20,
                                            3.6 + r * 0.20), 0.18, 0.18,
                                           fc="#BFE3E6", ec=TEAL, lw=0.3))
        ax.text(2.1, 3.1, f"{nf} maps, each $3\\times3$", ha="center", fontsize=6.4,
                color=GREY)
        if k == 0:
            ax.text(4.0, 6.6, r"$36$" + "\nvalues", ha="center", fontsize=6.6,
                    color=ROSE)
            for i in range(nf):
                ax.plot([3.4 + i * 0.25, 6.0], [4.2 + i * 0.25, 5.9], lw=0.4,
                        color="#C9D8E2")
            box(ax, 6.5, 5.0, 1.9, 1.0, "dense\n36→10", fc=PINK, ec=ROSE, fs=6.2)
            ax.text(8.6, 5.5, "$36\\times10=360$\nweights\nposition-dependent",
                    fontsize=6.0, color=ROSE, va="center")
        else:
            for i in range(nf):
                ax.add_patch(Rectangle((5.6, 3.9 + i * 0.55), 0.55, 0.42, fc=SAND,
                                       ec=GOLD, lw=0.6))
                ax.plot([3.5, 5.5], [4.2 + i * 0.25, 4.11 + i * 0.55], lw=0.4,
                        color="#C9D8E2")
            ax.text(5.85, 3.35, "average\nper map", ha="center", fontsize=6.2,
                    color=GOLD)
            box(ax, 6.9, 5.0, 1.5, 1.0, "dense\n4→10", fc=MINT, ec=TEAL, fs=6.2)
            ax.text(8.6, 5.5, "$4\\times10=40$\nweights\nlocation-free",
                    fontsize=6.0, color=TEAL, va="center")
    fig.text(0.5, 0.005, "GAP averages each channel into one number, so the "
             "classifier sees evidence, not coordinates", ha="center", fontsize=6.5,
             color=GREY)
    save(fig, "fig4_gap")


def fig_arch():
    fig, ax = canvas(6.6, 2.0, (0, 13.4), (0, 4.0))
    blocks = [("input\n$224{\\times}224{\\times}3$", LIGHT, TEAL, 1.55),
              ("conv 3×3\n32, S1 P1\n+ReLU", MINT, TEAL, 1.55),
              ("maxpool\n2×2, S2\n112²×32", MINT, TEAL, 1.55),
              ("conv 3×3\n64\n+ ReLU", MINT, TEAL, 1.45),
              ("maxpool\n2×2 → 56²", MINT, TEAL, 1.45),
              ("conv 3×3\n128 + pool\n→ 28²×128", MINT, TEAL, 1.55),
              ("GAP\n128", SAND, GOLD, 1.0),
              ("softmax\n10", PINK, ROSE, 1.05)]
    x = 0.1
    ys, h = 1.35, 1.45
    for i, (txt, fc, ec, w) in enumerate(blocks):
        box(ax, x, ys, w, h, txt, fc=fc, ec=ec, fs=5.9)
        if i < len(blocks) - 1:
            arrow(ax, (x + w, ys + h / 2), (x + w + 0.34, ys + h / 2), color=GREY,
                  lw=0.8, ms=5)
        x += w + 0.34
    ax.text(6.7, 0.72, "feature extraction  ($3.0$ M parameters)", ha="center",
            fontsize=6.4, color=TEAL)
    ax.text(11.7, 0.72, "classifier  ($1.3$ K)", ha="center", fontsize=6.4,
            color=ROSE)
    ax.plot([0.1, 9.35], [1.02, 1.02], lw=0.7, color=TEAL)
    ax.plot([9.5, 13.2], [1.02, 1.02], lw=0.7, color=ROSE)
    ax.text(6.6, 3.35, "spatial size shrinks, channel depth grows, parameter count "
            "stays small", ha="center", fontsize=6.5, color=GREY)
    save(fig, "fig4_arch")


def fig_prior():
    fig, ax = canvas(6.6, 3.05, (0, 13.2), (0, 6.55))
    cell = 0.44
    n = 6

    def grid(x0, y0, n_, obj=None, peak=None, fc="white", ec="#9FB3C2"):
        for r in range(n_):
            for c in range(n_):
                fill = fc
                if obj and (r, c) in obj:
                    fill = "#8FCBD1"
                ax.add_patch(Rectangle((x0 + c * cell, y0 + (n_ - 1 - r) * cell),
                                       cell, cell, fc=fill, ec=ec, lw=0.45, zorder=2))
        if peak:
            ax.add_patch(Rectangle((x0 + peak[1] * cell,
                                    y0 + (n_ - 1 - peak[0]) * cell), cell, cell,
                                   fc=ROSE, ec=ROSE, lw=0.5, zorder=3))

    W = n * cell
    obj_a = [(1, 0), (1, 1), (2, 0), (2, 1)]
    obj_b = [(1, 1), (1, 2), (2, 1), (2, 2)]

    y1 = 3.35
    grid(0.5, y1, n, obj=obj_a)
    ax.text(0.5 + W / 2, y1 - 0.28, "input", ha="center", fontsize=6.2, color=GREY)
    arrow(ax, (0.5 + W + 0.12, y1 + W / 2), (3.05, y1 + W / 2), color=GREY, lw=0.9,
          ms=5)
    grid(3.2, y1, n, peak=(1, 0))
    ax.text(3.2 + W / 2, y1 - 0.28, "feature map", ha="center", fontsize=6.2,
            color=GREY)

    grid(7.4, y1, n, obj=obj_b)
    ax.text(7.4 + W / 2, y1 - 0.28, "input shifted by 1", ha="center", fontsize=6.2,
            color=GREY)
    arrow(ax, (7.4 + W + 0.12, y1 + W / 2), (9.95, y1 + W / 2), color=GREY, lw=0.9,
          ms=5)
    grid(10.1, y1, n, peak=(1, 1))
    ax.text(10.1 + W / 2, y1 - 0.28, "response shifted by 1", ha="center",
            fontsize=6.2, color=ROSE)

    y2 = 0.75
    grid(3.2, y2, 3, peak=(0, 0), fc="#EDF6F1", ec=TEAL)
    grid(10.1, y2, 3, peak=(0, 0), fc="#EDF6F1", ec=TEAL)
    arrow(ax, (3.2 + W / 2, y1 - 0.55), (3.2 + W / 2, y2 + 3 * cell + 0.12),
          color=TEAL, lw=0.8, ms=5)
    arrow(ax, (10.1 + W / 2, y1 - 0.55), (10.1 + W / 2, y2 + 3 * cell + 0.12),
          color=TEAL, lw=0.8, ms=5)
    ax.text(3.2 + 1.5 * cell, y2 - 0.28, "pooled", ha="center", fontsize=6.2,
            color=TEAL)
    ax.text(10.1 + 1.5 * cell, y2 - 0.28, "pooled", ha="center", fontsize=6.2,
            color=TEAL)
    ax.text(6.85, 1.35, "identical", ha="center", fontsize=6.6, color=TEAL,
            fontweight="bold")

    ax.text(6.6, 6.25, "convolution: the response travels with the object "
            "(equivariance)", ha="center", fontsize=6.5, color=INK)
    ax.text(6.6, 0.12, "pooling: a shift smaller than the stride disappears "
            "(invariance)", ha="center", fontsize=6.5, color=TEAL)
    save(fig, "fig4_prior")


def main():
    fig_conv()
    fig_sizes()
    fig_fc_cnn()
    fig_pool()
    fig_gap()
    fig_arch()
    fig_prior()
    print("unit IV figures done")


if __name__ == "__main__":
    main()
