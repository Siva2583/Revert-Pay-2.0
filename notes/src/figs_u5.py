"""Figures for Unit V."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

from figlib import (canvas, box, arrow, circle_node, save, NAVY, TEAL, GOLD, ROSE,
                    GREEN, GREY, LIGHT, SAND, PINK, MINT, INK)


def fig_unfold():
    fig, ax = canvas(6.6, 2.5, (0, 13.2), (0, 5.0))
    cols = [1.4, 5.4, 9.4]
    labels = ["$t-1$", "$t$", "$t+1$"]
    for i, (x, lab) in enumerate(zip(cols, labels)):
        ax.add_patch(FancyBboxPatch((x, 2.05), 2.3, 1.35,
                                    boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=(LIGHT if i != 1 else MINT), ec=TEAL,
                                    lw=1.0, zorder=2))
        ax.text(x + 1.15, 2.72, "$h_{t}$" if i != 1 else "$h_t$", ha="center",
                va="center", fontsize=9.5, color=INK, zorder=3)
        ax.text(x + 1.15, 0.95, "$x_{" + lab.replace('$', '') + "}$" if i == 0 else
                "$x_t$" if i == 1 else "$x_{t+1}$", ha="center", fontsize=8.5,
                color=GREY)
        ax.text(x + 1.15, 3.62, lab, ha="center", fontsize=7, color=NAVY)
        arrow(ax, (x + 1.15, 1.35), (x + 1.15, 2.0), color=GREY, lw=0.9)
    for i in range(2):
        arrow(ax, (cols[i] + 2.35, 2.72), (cols[i + 1] - 0.05, 2.72), color=TEAL,
              lw=1.3)
        ax.text((cols[i] + cols[i + 1] + 2.3) / 2, 2.95, "$W_{hh}$", ha="center",
                fontsize=7.2, color=TEAL)
    ax.text(cols[1] + 1.45, 3.9, "$y_t$", fontsize=8, color=GREY)
    arrow(ax, (cols[1] + 1.15, 3.45), (cols[1] + 1.15, 3.85), color=GREY, lw=0.9)
    for i, x in enumerate(cols):
        ax.text(x + 1.15, 1.62, "$W_{xh}$", ha="center", fontsize=6.6, color=GREY)
    ax.text(6.6, 0.35, "one cell, one set of weights $W_{xh}, W_{hh}, W_{hy}$ and "
            "bias $b_h$ reused at every step  →  $T$ steps, $O(1)$ parameters",
            ha="center", fontsize=6.8, color=INK)
    save(fig, "fig5_unfold")


def fig_vanish():
    fig, ax = plt.subplots(figsize=(6.4, 2.45))
    fig.subplots_adjust(0.11, 0.18, 0.975, 0.96)
    t = np.arange(1, 41)
    ax.semilogy(t, 0.75 ** t, color=ROSE, lw=1.6,
                label=r"vanilla RNN: $\|\partial h_t/\partial h_{t-k}\|\sim\gamma^{k}$")
    ax.semilogy(t, 1.35 ** t / 1.35 ** 40 * 0.02 + 1e-9, color=GOLD, lw=1.6,
                ls="-", label=r"exploding: $\gamma>1$ (clipping needed)")
    ax.semilogy(t, 0.97 ** t, color=TEAL, lw=1.6,
                label="LSTM / GRU with forget gate near 1")
    ax.axhline(1e-3, color=GREY, lw=0.6, ls=(0, (3, 3)))
    ax.text(38, 1.3e-3, "information lost", fontsize=6.5, color=GREY, ha="right")
    ax.set_xlabel("distance $k$ between the two time steps (steps)")
    ax.set_ylabel(r"gradient magnitude")
    ax.set_ylim(1e-9, 1e2)
    ax.set_xlim(0, 40)
    ax.legend(frameon=False, fontsize=6.6, loc="lower left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "fig5_vanish")


def fig_variants():
    fig, axes = plt.subplots(1, 4, figsize=(6.6, 2.15))
    fig.subplots_adjust(0.01, 0.13, 0.99, 0.90, wspace=0.12)
    titles = ["vanilla\n(one direction)", "bidirectional",
              "deep (stacked)", "LSTM cell"]
    for ax, ttl in zip(axes, titles):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_axis_off()
        ax.set_title(ttl, fontsize=6.9, color=INK, pad=2)
    ax = axes[0]
    for i, x in enumerate([1.6, 4.1, 6.6]):
        box(ax, x, 4.2, 1.7, 1.4, "$h$", fc=LIGHT, ec=TEAL, fs=7)
        if i < 2:
            arrow(ax, (x + 1.7, 4.9), (x + 2.4, 4.9), color=TEAL, lw=0.9)
    ax = axes[1]
    xs = [1.4, 4.0, 6.6]
    for x in xs:
        box(ax, x, 5.6, 1.7, 1.2, r"$\overrightarrow{h}$", fc=MINT, ec=TEAL, fs=6.6)
        box(ax, x, 3.4, 1.7, 1.2, r"$\overleftarrow{h}$", fc=SAND, ec=GOLD, fs=6.6)
    for i in range(2):
        arrow(ax, (xs[i] + 1.7, 6.2), (xs[i + 1] - 0.05, 6.2), color=TEAL, lw=0.8)
        arrow(ax, (xs[i + 1], 4.0), (xs[i] + 1.75, 4.0), color=GOLD, lw=0.8)
    ax.text(4.8, 1.9, "two passes,\nconcatenate", ha="center", fontsize=5.8,
            color=GREY)
    ax = axes[2]
    for layer, (yy, fc, ec) in enumerate([(2.6, LIGHT, TEAL), (4.5, MINT, TEAL),
                                          (6.4, SAND, GOLD)]):
        for i, x in enumerate([1.5, 4.0, 6.5]):
            box(ax, x, yy, 1.6, 1.2, "$h^{%d}$" % (layer + 1), fc=fc, ec=ec, fs=6.2)
            if i < 2:
                arrow(ax, (x + 1.6, yy + 0.6), (x + 2.4, yy + 0.6), color=ec, lw=0.7)
    ax = axes[3]
    box(ax, 1.8, 3.9, 6.0, 2.4, "", fc=LIGHT, ec=TEAL)
    ax.text(4.8, 5.6, r"$c_{t-1}\ \longrightarrow\ c_t$", ha="center", fontsize=6.6,
            color=INK)
    ax.text(4.0, 4.6, r"gates: $f_t,\ i_t,\ o_t$", ha="center", fontsize=6.2,
            color=TEAL)
    ax.text(4.8, 8.4, "additive state path\n(no repeated $W$ product)",
            ha="center", fontsize=5.6, color=GREY)
    fig.text(0.5, 0.015, "all four share weights across time; they differ in "
             "direction, depth and in how the state is updated", ha="center",
             fontsize=6.3, color=GREY)
    save(fig, "fig5_variants")


def fig_lstm():
    fig, ax = canvas(6.7, 3.15, (0, 13.4), (0, 6.3))
    ax.plot([0.5, 12.9], [4.55, 4.55], color=INK, lw=1.3, zorder=1)
    ax.text(0.55, 4.85, "$c_{t-1}$", fontsize=8.2, color=INK)
    ax.text(12.2, 4.85, "$c_t$", fontsize=8.2, color=INK)

    def mul(x, y):
        ax.add_patch(Circle((x, y), 0.28, fc="white", ec=INK, lw=1.0, zorder=4))
        ax.plot([x - 0.2, x + 0.2], [y - 0.2, y + 0.2], color=INK, lw=0.9, zorder=5)
        ax.plot([x - 0.2, x + 0.2], [y + 0.2, y - 0.2], color=INK, lw=0.9, zorder=5)

    def plus(x, y):
        ax.add_patch(Circle((x, y), 0.28, fc="white", ec=INK, lw=1.0, zorder=4))
        ax.plot([x - 0.19, x + 0.19], [y, y], color=INK, lw=0.9, zorder=5)
        ax.plot([x, x], [y - 0.19, y + 0.19], color=INK, lw=0.9, zorder=5)

    mul(3.0, 4.55); plus(6.6, 4.55); mul(10.0, 4.55)

    box(ax, 1.7, 2.55, 2.6, 0.95, r"$f_t=\sigma(W_f[h_{t-1},x_t]+b_f)$",
        fc=PINK, ec=ROSE, fs=5.6)
    arrow(ax, (3.0, 3.5), (3.0, 4.27), color=ROSE, lw=0.9)
    box(ax, 4.35, 2.55, 1.9, 0.95, r"$i_t=\sigma(\cdot)$", fc=MINT, ec=TEAL, fs=6.2)
    box(ax, 5.55, 1.35, 1.9, 0.95, r"$\tilde{c}_t=\tanh(\cdot)$", fc=MINT,
        ec=TEAL, fs=6.2)
    mul(5.0, 1.85)
    arrow(ax, (5.3, 3.02), (5.05, 2.13), color=TEAL, lw=0.8)
    arrow(ax, (6.5, 1.82), (6.55, 2.14), color=TEAL, lw=0.8)
    arrow(ax, (6.6, 2.5), (6.6, 4.27), color=TEAL, lw=0.9)
    ax.text(6.85, 3.5, r"$i_t\odot\tilde{c}_t$", fontsize=6.2, color=TEAL)
    box(ax, 8.35, 2.55, 1.9, 0.95, r"$o_t=\sigma(\cdot)$", fc=SAND, ec=GOLD, fs=6.2)
    box(ax, 8.55, 1.35, 1.9, 0.95, r"$\tanh$", fc=SAND, ec=GOLD, fs=6.6)
    arrow(ax, (10.0, 4.27), (9.9, 3.5), color=GOLD, lw=0.9)
    arrow(ax, (9.5, 1.82), (9.9, 2.24), color=GOLD, lw=0.8)
    ax.text(10.2, 3.5, r"$\tanh(c_t)$", fontsize=6.2, color=GOLD)
    ax.text(0.55, 1.35, "$h_{t-1}$", fontsize=8.2, color=GREY)
    ax.text(0.55, 0.95, "$x_t$", fontsize=8.2, color=GREY)
    ax.plot([1.0, 1.35], [1.4, 1.4], color=GREY, lw=1.0)
    ax.plot([1.0, 1.35], [1.0, 1.0], color=GREY, lw=1.0)
    ax.plot([1.35, 1.35], [1.0, 1.4], color=GREY, lw=1.0)
    for x in (3.0, 5.3, 9.3):
        ax.plot([1.35, x], [1.2, 1.2], color=GREY, lw=0.6, ls=(0, (2, 2)),
                zorder=1)
        arrow(ax, (x, 1.2), (x, 1.32), color=GREY, lw=0.7)
    arrow(ax, (10.0, 4.55), (11.5, 4.55), color=INK, lw=1.3)
    ax.plot([11.5, 11.5], [4.55, 5.55], color=INK, lw=1.1)
    ax.plot([11.5, 12.6], [5.55, 5.55], color=INK, lw=1.1)
    ax.text(12.2, 5.8, "$h_t$", fontsize=8.2, color=INK)
    ax.text(6.6, 0.55, r"$\sigma$ gates decide what to throw away, what to write, "
            "and what to expose", ha="center", fontsize=6.3, color=GREY)
    save(fig, "fig5_lstm")


def fig_seq2seq():
    fig, ax = canvas(6.6, 2.6, (0, 13.2), (0, 5.2))
    enc = [(1.0, "$h_1$"), (3.0, "$h_2$"), (5.0, "$h_T$")]
    dec = [(8.2, "$s_1$"), (10.2, "$s_2$"), (12.2, "$s_{T'}$")]
    for x, lab in enc:
        box(ax, x, 2.5, 1.45, 1.1, lab, fc=LIGHT, ec=TEAL, fs=7)
    for i in range(2):
        arrow(ax, (enc[i][0] + 1.45, 3.05), (enc[i + 1][0] - 0.05, 3.05), color=TEAL,
              lw=0.9)
    for x, lab in dec:
        box(ax, x, 2.5, 1.45, 1.1, lab, fc=MINT, ec=GREEN, fs=7)
    for i in range(2):
        arrow(ax, (dec[i][0] + 1.45, 3.05), (dec[i + 1][0] - 0.05, 3.05),
              color=GREEN, lw=0.9)
    ax.add_patch(FancyBboxPatch((6.55, 2.35), 1.3, 1.4,
                                boxstyle="round,pad=0,rounding_size=0.1",
                                fc=SAND, ec=GOLD, lw=1.0, zorder=2))
    ax.text(7.2, 3.05, "$c$", ha="center", va="center", fontsize=8, color=GOLD,
            zorder=3)
    arrow(ax, (6.4, 3.05), (6.52, 3.05), color=GOLD, lw=1.1)
    arrow(ax, (7.88, 3.05), (8.14, 3.05), color=GOLD, lw=1.1)
    ax.text(7.2, 1.98, "context $c=h_T$", ha="center", fontsize=6.0, color=GOLD)
    ins = ["the", "cat", "sat"]
    outs = ["<sos>", "le", "chat"]
    for (x, _), tok in zip(enc, ins):
        ax.text(x + 0.72, 2.1, tok, ha="center", fontsize=6.2, color=GREY)
        arrow(ax, (x + 0.72, 2.25), (x + 0.72, 2.45), color=GREY, lw=0.7)
    for (x, _), tok in zip(dec, outs):
        ax.text(x + 0.72, 4.0, tok, ha="center", fontsize=6.2, color=GREEN)
        arrow(ax, (x + 0.72, 3.65), (x + 0.72, 3.95), color=GREEN, lw=0.7)
    ax.text(3.0, 4.55, r"encoder: $h_t=f(h_{t-1},x_t)$", ha="center", fontsize=6.8,
            color=TEAL)
    ax.text(10.4, 4.55, r"decoder: $P(y_{t'}\mid y_{<t'},c)$", ha="center",
            fontsize=6.8, color=GREEN)
    ax.text(6.6, 0.72, r"objective: maximise $\sum_{t'}\log P(y_{t'}\mid y_{<t'},c)$"
            "  — teacher forcing; weights shared within each direction",
            ha="center", fontsize=6.4, color=INK)
    save(fig, "fig5_seq2seq")


def fig_ae():
    fig, ax = canvas(6.5, 2.4, (0, 13.4), (0, 4.8))
    widths = [1.7, 1.1, 0.55, 1.1, 1.7]
    xs = [0.3, 3.0, 5.6, 7.7, 10.6]
    hts = [2.6, 1.7, 0.9, 1.7, 2.6]
    cols = [LIGHT, MINT, PINK, MINT, LIGHT]
    ecs = [TEAL, TEAL, ROSE, TEAL, TEAL]
    labs = ["input\n$x\\in\\mathbb{R}^{8}$", "encoder\n$E$", "$z$\n$2$-d",
            "decoder\n$D$", "reconstruction\n$\\hat{x}=D(E(x))$"]
    for x, w, h, fc, ec, lab in zip(xs, widths, hts, cols, ecs, labs):
        box(ax, x, 2.4 - h / 2 + 0.35, w, h, lab, fc=fc, ec=ec, fs=6.0)
    for i in range(4):
        arrow(ax, (xs[i] + widths[i], 2.75), (xs[i + 1] - 0.04, 2.75), color=GREY,
              lw=0.9)
    ax.text(6.0, 3.85, "bottleneck", ha="center", fontsize=6.4, color=ROSE)
    ax.annotate("", xy=(5.85, 3.72), xytext=(5.6, 3.15),
                arrowprops=dict(arrowstyle="-|>", color=ROSE, lw=0.8))
    ax.text(6.7, 0.5, r"minimise $\|x-D(E(x))\|^{2}$   —   if $E,D$ are linear and "
            r"the loss is squared error, the optimum spans the same subspace as PCA",
            ha="center", fontsize=6.4, color=GREY)
    ax.text(0.3, 3.85, "capacity is squeezed at $z$: the network must keep only\n"
            "the factors that allow reconstruction", fontsize=6.2, color=INK)
    save(fig, "fig5_ae")


def fig_long():
    fig, ax = canvas(6.6, 2.5, (0, 13.4), (0, 5.1))
    xs = [0.7 + i * 1.12 for i in range(9)]
    for i, x in enumerate(xs):
        ax.add_patch(Circle((x, 2.55), 0.26, fc=(MINT if i >= 5 else LIGHT), ec=TEAL,
                            lw=0.9, zorder=3))
        ax.text(x, 2.55, f"$h_{{{i + 1}}}$", ha="center", va="center", fontsize=5.6,
                color=INK, zorder=4)
        if i:
            arrow(ax, (xs[i - 1] + 0.27, 2.55), (x - 0.28, 2.55), color=TEAL, lw=0.7,
                  ms=4)
    ax.plot([xs[5] - 0.34, xs[8] + 0.34], [3.28, 3.28], color=ROSE, lw=0.8)
    ax.plot([xs[5] - 0.34, xs[5] - 0.34], [3.28, 3.08], color=ROSE, lw=0.8)
    ax.plot([xs[8] + 0.34, xs[8] + 0.34], [3.28, 3.08], color=ROSE, lw=0.8)
    ax.text((xs[5] + xs[8]) / 2, 3.42, "truncated BPTT window ($k=4$)", ha="center",
            fontsize=6.2, color=ROSE)
    ax.add_patch(FancyBboxPatch((11.1, 2.2), 1.5, 0.72,
                                boxstyle="round,pad=0,rounding_size=0.1",
                                fc=SAND, ec=GOLD, lw=0.9, zorder=3))
    ax.text(11.85, 2.56, "decoder $s_t$", ha="center", va="center", fontsize=5.9,
            color=GOLD, zorder=4)
    ax.text(0.7, 1.72, "chain: path length $T$", fontsize=6.0, color=GREY)
    arrow(ax, (xs[1], 2.28), (11.3, 2.2), color=GOLD, lw=1.2, rad=0.28, ls=(0, (4, 2)))
    ax.text(6.3, 0.55, "attention path from step 2: length 1", fontsize=6.2,
            color=GOLD, ha="center")
    ax.text(6.6, 4.45, "bound the path length instead of hoping the gradient survives it",
            ha="center", fontsize=6.4, color=INK)
    ax.text(6.9, 1.72, "gradient flows only inside the window", fontsize=6.0,
            color=ROSE, ha="center")
    save(fig, "fig5_long")


def main():
    fig_unfold()
    fig_vanish()
    fig_variants()
    fig_lstm()
    fig_seq2seq()
    fig_ae()
    fig_long()
    print("unit V figures done")


if __name__ == "__main__":
    main()
