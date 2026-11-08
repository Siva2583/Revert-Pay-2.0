"""Tiny drawing helpers shared by the figure scripts (matplotlib -> SVG)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "figs")
os.makedirs(OUT, exist_ok=True)

NAVY = "#123A5F"
TEAL = "#0E6E7A"
GOLD = "#9A6A1B"
ROSE = "#9B2C3B"
GREEN = "#1F6B4E"
GREY = "#5D6D7C"
LIGHT = "#E8F3F4"
SAND = "#FBF3E2"
PINK = "#FCEFF0"
MINT = "#EDF6F1"
INK = "#1B2733"

matplotlib.rcParams.update({
    "mathtext.fontset": "stix",
    "font.family": "STIXGeneral",
    "font.size": 8,
    "axes.linewidth": 0.7,
    "axes.edgecolor": GREY,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "axes.labelcolor": INK,
    "svg.fonttype": "path",
})


def canvas(w, h, xlim=(0, 10), ylim=(0, 10)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def box(ax, x, y, w, h, text="", fc=LIGHT, ec=TEAL, fs=8, tc=INK, bold=False,
        r=0.12, lw=0.9):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, zorder=2)
    ax.add_patch(p)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                color=tc, zorder=3,
                fontweight="bold" if bold else "normal", linespacing=1.35)
    return p


def arrow(ax, p1, p2, color=GREY, lw=0.9, style="-|>", rad=0.0, ls="-", ms=6):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms, color=color,
                        lw=lw, linestyle=ls, zorder=4,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2)
    ax.add_patch(a)


def circle_node(ax, x, y, r=0.22, fc="white", ec=TEAL, lw=0.9, z=2):
    c = Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(c)
    return c


def save(fig, name, dpi=200):
    path = os.path.join(OUT, name + ".svg")
    fig.savefig(path, format="svg", transparent=True, bbox_inches="tight",
                pad_inches=0.02)
    if os.environ.get("FIGPNG"):
        fig.savefig(os.path.join(OUT, name + ".png"), dpi=200, facecolor="white",
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return path
