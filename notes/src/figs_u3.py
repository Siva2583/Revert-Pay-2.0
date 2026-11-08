"""Figures for Unit III."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Circle

from figlib import (canvas, box, arrow, circle_node, save, NAVY, TEAL, GOLD, ROSE,
                    GREEN, GREY, LIGHT, SAND, PINK, MINT, INK)


def fig_complexity():
    fig, ax = plt.subplots(figsize=(6.4, 2.55))
    fig.subplots_adjust(0.075, 0.17, 0.985, 0.97)
    x = np.linspace(0, 10, 400)
    tr = 0.62 * np.exp(-0.55 * x) + 0.05
    va = 0.30 + 0.055 * (x - 5.4) ** 2 / 3.0 + 0.30 * np.exp(-1.1 * x)
    ax.axvspan(0, 2.6, color=PINK, alpha=0.55, lw=0)
    ax.axvspan(2.6, 4.4, color=MINT, alpha=0.8, lw=0)
    ax.axvspan(4.4, 10, color=SAND, alpha=0.5, lw=0)
    ax.plot(x, tr, color=TEAL, lw=1.6, label=r"training error $J_{train}$")
    ax.plot(x, va, color=ROSE, lw=1.6, label=r"validation error $J_{val}$")
    i = np.argmin(va)
    ax.plot(x[i], va[i], "o", ms=4, color=ROSE, zorder=5)
    ax.annotate("best capacity\n(lowest $J_{val}$)", xy=(x[i], va[i]),
                xytext=(x[i] + 0.4, va[i] + 0.30), fontsize=7, color=ROSE,
                arrowprops=dict(arrowstyle="-", color=ROSE, lw=0.7))
    ax.text(1.25, 0.62, "underfitting\n(high bias)", ha="center", fontsize=7,
            color=ROSE)
    ax.text(8.0, 0.30, "overfitting\n(high variance)", ha="center", fontsize=7,
            color=GOLD)
    ax.set_xlabel("model capacity / effective parameters  (polynomial degree)")
    ax.set_ylabel("error")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(0, 0.85)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "fig3_complexity")


def fig_l1l2():
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.5))
    fig.subplots_adjust(0.03, 0.10, 0.985, 0.98, wspace=0.16)
    for ax, kind, ttl in zip(axes, ("l2", "l1"),
                             (r"$L_2$: $\|\theta\|_2\leq t$  (disk)",
                              r"$L_1$: $\|\theta\|_1\leq t$  (diamond)")):
        ax.set_aspect("equal")
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.4, 2.3)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ("top", "right", "left", "bottom"):
            ax.spines[s].set_visible(False)
        ax.axhline(0, color=GREY, lw=0.5, zorder=1)
        ax.axvline(0, color=GREY, lw=0.5, zorder=1)
        ax.plot(1.85, 1.25, "o", ms=4, color=NAVY, zorder=6)
        ax.text(1.95, 1.38, r"$\hat\theta$", fontsize=8, color=NAVY)
        for r in (0.35, 0.75, 1.15, 1.55):
            ax.add_patch(Ellipse((1.85, 1.25), 2 * r, 1.25 * r, angle=-20,
                                 fill=False, ec=GREY, lw=0.6, ls=(0, (2, 2)),
                                 zorder=2))
        if kind == "l2":
            ax.add_patch(Circle((0, 0), 1.0, fc=LIGHT, ec=TEAL, lw=1.2, zorder=3))
            p = np.array([0.72, 0.69])
        else:
            ax.add_patch(Polygon([(1.0, 0), (0, 1.0), (-1.0, 0), (0, -1.0)],
                                 closed=True, fc=LIGHT, ec=TEAL, lw=1.2, zorder=3))
            p = np.array([1.0, 0.0])
        ax.plot(*p, "o", ms=4.5, color=ROSE, zorder=6)
        ax.annotate(r"$\theta^\star$", xy=p, xytext=p + np.array([0.08, 0.22]),
                    fontsize=8, color=ROSE)
        ax.set_title(ttl, fontsize=8, color=INK, pad=4)
    axes[0].text(0, -2.25, "contact point is generic:\nboth weights shrink, neither is 0",
                 ha="center", va="bottom", fontsize=6.6, color=GREY)
    axes[1].text(0, -2.25, "contact point is a corner:\none weight becomes exactly 0",
                 ha="center", va="bottom", fontsize=6.6, color=ROSE)
    save(fig, "fig3_l1l2")


def fig_dropout():
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.45))
    fig.subplots_adjust(0.02, 0.02, 0.985, 0.92, wspace=0.10)
    drop = {0: [], 1: [1, 3, 4], 2: [2]}
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_axis_off()
        ax.set_title(("full network  (train and test)" if k == 0
                      else "one thinned network  (each mini-batch)"),
                     fontsize=7.6, color=INK, pad=2)
        coords = []
        for li, n in enumerate([4, 6, 4]):
            xs = 1.4 + li * 3.6
            ys = np.linspace(8.0, 2.0, n)
            coords.append([(xs, y) for y in ys])
        for li in range(2):
            for a in coords[li]:
                for b in coords[li + 1]:
                    dead = k == 1 and (li + 1 in drop and
                                       coords[li + 1].index(b) in drop[li + 1])
                    dead = dead or (k == 1 and li in drop and
                                    coords[li].index(a) in drop[li])
                    ax.plot([a[0], b[0]], [a[1], b[1]], lw=0.45,
                            color=("#DCE4EA" if dead else "#B9CBD8"), zorder=1)
        for li, layer in enumerate(coords):
            for ni, (x, y) in enumerate(layer):
                dead = k == 1 and li in drop and ni in drop[li]
                ax.add_patch(Circle((x, y), 0.42,
                                    fc=("white" if dead else LIGHT),
                                    ec=("#C9D3DA" if dead else TEAL), lw=0.8,
                                    ls=(":" if dead else "-"), zorder=3))
                if dead:
                    ax.plot([x - 0.3, x + 0.3], [y - 0.3, y + 0.3], lw=0.7,
                            color="#C0505E", zorder=4)
                    ax.plot([x - 0.3, x + 0.3], [y + 0.3, y - 0.3], lw=0.7,
                            color="#C0505E", zorder=4)
    fig.text(0.5, 0.015, r"each unit survives with probability $q$; at test time weights "
             r"are scaled by $q$ — a geometric-mean ensemble of $2^{n}$ sub-networks",
             ha="center", fontsize=6.6, color=GREY)
    save(fig, "fig3_dropout")


def fig_path():
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.55),
                             gridspec_kw={"width_ratios": [1.05, 1]})
    fig.subplots_adjust(0.03, 0.14, 0.985, 0.96, wspace=0.22)
    ax = axes[0]
    ax.set_aspect("equal")
    ax.set_xlim(-2.9, 2.9); ax.set_ylim(-2.7, 2.7)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.axhline(0, color=GREY, lw=0.45, zorder=0)
    ax.axvline(0, color=GREY, lw=0.45, zorder=0)
    th_hat = np.array([2.0, 1.25])
    for r in (0.5, 1.0, 1.5):
        ax.add_patch(Ellipse(th_hat, 2 * r, 1.25 * r, angle=-16, fill=False,
                             ec="#9BB0BF", lw=0.7, ls=(0, (2, 2)), zorder=2))
    ax.plot(*th_hat, "o", ms=4.2, color=NAVY, zorder=6)
    ax.text(th_hat[0] + 0.1, th_hat[1] + 0.16, r"$\hat\theta$", fontsize=8,
            color=NAVY)
    specs = [(0.45, "#7FB6BC", r"small $\lambda$"),
             (0.95, TEAL, r"medium $\lambda$"),
             (1.55, "#0A4C56", r"large $\lambda$")]
    for s_, col, lab in specs:
        ax.add_patch(Polygon([(s_, 0), (0, s_), (-s_, 0), (0, -s_)], closed=True,
                             fill=False, ec=col, lw=1.1, ls=(0, (4, 2)),
                             zorder=3, label=lab))
        pt = np.array([s_, 0.0])
        ax.plot(*pt, "o", ms=3.6, color=ROSE, zorder=6, clip_on=False)
    ax.legend(frameon=False, fontsize=6.2, loc="upper left", handlelength=1.5,
              borderpad=0.1, labelspacing=0.35)
    ax.set_title("geometry: growing diamond, fixed loss contours", fontsize=6.8,
                 color=INK, pad=2)
    ax.text(0, -2.55, "the contact point slides along the $\\theta_1$ axis",
            ha="center", fontsize=6.3, color=ROSE)

    bx = axes[1]
    lam = np.linspace(0, 2.0, 400)
    th1 = np.where(lam < 0.95, 1.9 - lam, 0.0)
    th2 = np.where(lam < 0.75, 1.25 - lam, 0.0)
    bx.plot(lam, th1, color=TEAL, lw=1.5, label=r"$\theta_1^\star$")
    bx.plot(lam, th2, color=ROSE, lw=1.5, label=r"$\theta_2^\star$")
    bx.axvline(0.75, color=GREY, lw=0.7, ls=(0, (3, 3)))
    bx.annotate(r"$\lambda=|y_2|$: $\theta_2$ hits 0", xy=(0.75, 0.0),
                xytext=(0.95, 0.55), fontsize=6.2, color=ROSE,
                arrowprops=dict(arrowstyle="-|>", color=ROSE, lw=0.7))
    bx.set_xlabel(r"regularisation strength $\lambda$", fontsize=7.5)
    bx.set_ylabel("weight value", fontsize=7.5)
    bx.set_xlim(0, 2.0); bx.set_ylim(-0.15, 2.1)
    bx.tick_params(labelsize=6.5)
    for sp in ("top", "right"):
        bx.spines[sp].set_visible(False)
    bx.legend(frameon=False, fontsize=6.4, loc="upper right")
    bx.set_title("the regularisation path is piecewise linear", fontsize=6.8,
                 color=INK, pad=2)
    save(fig, "fig3_path")


def fig_opt():
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    fig.subplots_adjust(0.04, 0.12, 0.98, 0.97)
    A = np.array([[1.0, 0.0], [0.0, 14.0]])
    xs = np.linspace(-6.4, 1.6, 300)
    ys = np.linspace(-2.4, 2.4, 300)
    X, Y = np.meshgrid(xs, ys)
    Z = 0.5 * (A[0, 0] * X ** 2 + A[1, 1] * Y ** 2)
    ax.contour(X, Y, Z, levels=[0.6, 2.0, 5.0, 11.0, 20.0, 34.0], colors="#B9CBD8",
               linewidths=0.7)
    ax.set_xlim(-6.4, 1.6); ax.set_ylim(-2.4, 2.4)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.plot(0, 0, "*", ms=9, color=INK, zorder=8)
    ax.text(0.18, 0.22, "minimum", fontsize=7, color=INK)

    def run(kind, steps=26):
        p = np.array([-5.9, 1.9])
        v = np.zeros(2); s = np.zeros(2); m = np.zeros(2)
        tr = [p.copy()]
        for t in range(1, steps + 1):
            g = A @ p
            if kind == "sgd":
                p = p - 0.075 * g
            elif kind == "mom":
                v = 0.86 * v - 0.075 * g
                p = p + v
            elif kind == "rms":
                s = 0.85 * s + 0.15 * g ** 2
                p = p - 0.28 * g / (np.sqrt(s) + 1e-8)
            else:
                m = 0.9 * m + 0.1 * g
                s = 0.999 * s + 0.001 * g ** 2
                mh = m / (1 - 0.9 ** t); sh = s / (1 - 0.999 ** t)
                p = p - 0.34 * mh / (np.sqrt(sh) + 1e-8)
            tr.append(p.copy())
        return np.array(tr)

    styles = {"sgd": ("#8494A2", "SGD", (0, (3, 2))), "mom": (GOLD, "momentum", "-"),
              "rms": (TEAL, "RMSProp", "-"), "adam": (ROSE, "Adam", "-")}
    for k in ("sgd", "mom", "rms", "adam"):
        tr = run(k)
        col, lab, ls = styles[k]
        ax.plot(tr[:, 0], tr[:, 1], color=col, lw=1.2, ls=ls, label=lab, zorder=5,
                marker="o", ms=1.4)
    ax.legend(frameon=False, fontsize=7, loc="upper right", ncol=4,
              handlelength=1.6, columnspacing=1.0)
    ax.set_xlabel(r"$\theta_1$  (shallow direction)", fontsize=8)
    ax.set_ylabel(r"$\theta_2$  (steep)", fontsize=8)
    save(fig, "fig3_opt")


def fig_early():
    fig, ax = plt.subplots(figsize=(6.3, 2.35))
    fig.subplots_adjust(0.09, 0.17, 0.975, 0.96)
    e = np.arange(1, 61)
    tr = 0.95 * np.exp(-e / 16) + 0.09
    va = 1.02 * np.exp(-e / 9) + 0.16 + 0.0016 * np.maximum(e - 22, 0) ** 2
    ax.plot(e, tr, color=TEAL, lw=1.5, label="training loss")
    ax.plot(e, va, color=ROSE, lw=1.5, label="validation loss")
    b = int(np.argmin(va)) + 1
    ax.axvline(b, color=GOLD, lw=0.9, ls=(0, (4, 3)))
    ax.plot(b, va[b - 1], "o", ms=4.5, color=GOLD, zorder=6)
    ax.annotate(f"stop here (epoch {b})\nreturn these weights",
                xy=(b, va[b - 1]), xytext=(b + 4, va[b - 1] + 0.42), fontsize=7,
                color=GOLD, arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.8))
    ax.fill_between(e, va, tr, where=(e > b), color=SAND, alpha=0.6, lw=0)
    ax.text(50, 0.30, "gap widens:\nmemorisation", fontsize=6.8, color=GOLD,
            ha="center")
    ax.set_xlabel("training epoch  $t$")
    ax.set_ylabel("loss")
    ax.set_xlim(0, 60); ax.set_ylim(0.05, 1.15)
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "fig3_early")


def main():
    fig_complexity()
    fig_l1l2()
    fig_dropout()
    fig_path()
    fig_opt()
    fig_early()
    print("unit III figures done")


if __name__ == "__main__":
    main()
