#!/usr/bin/env python3
"""Deterministic conceptual figure: CIS computation + residual + null control.

Pure schematic -- no data are plotted, no results are depicted. Only the
frozen formulas and design are visualized (CIS definition, degree-matched
control, degree-preserving null arbitration). Grayscale-friendly, vector PDF.
Source-of-truth for notation: 10_REPORT/SUPPLEMENTARY_MATERIAL.md S3/S5/S7.

Usage (from 13_CROSS_SPECIES_CIS/):
    python SUBMISSION_PACKAGE/FIGURE_SOURCES/make_fig_cis_method.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import numpy as np, os

OUT = os.path.join("SUBMISSION_PACKAGE", "FINAL_MANUSCRIPT", "figures")
os.makedirs(OUT, exist_ok=True)

fig, axes = plt.subplots(1, 4, figsize=(7.05, 2.15))
GS = "#4a4a4a"; HL = "#000000"; FG = "#c9c9c9"

def small_graph(ax, seed, remove=None, highlight=None, title="", note=""):
    rng = np.random.default_rng(seed)
    pos = {}
    n_out, n_in = 9, 3  # outer ring + inner nodes
    for i in range(n_out):
        a = 2*np.pi*i/n_out
        pos[i] = (np.cos(a), np.sin(a))
    pos[n_out] = (0, 0); pos[n_out+1] = (0.5, 0.35); pos[n_out+2] = (-0.45, -0.3)
    edges = []
    for i in range(n_out):
        edges.append((i, (i+1) % n_out))
    edges += [(0, n_out), (2, n_out), (5, n_out), (4, n_out+1), (7, n_out+1),
              (3, n_out+2), (9, 10), (9, 11), (6, n_out+2), (1, 11)]
    shown = [(a, b) for (a, b) in edges if remove not in (a, b)]
    for a, b in shown:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
                color=GS, lw=0.8, zorder=1)
    for n, (x, y) in pos.items():
        if n == remove:
            ax.add_patch(Circle((x, y), 0.13, facecolor="white",
                                edgecolor=HL, lw=1.0, linestyle=(0, (2, 1.4)), zorder=3))
        else:
            fc = HL if n == highlight else "white"
            ax.add_patch(Circle((x, y), 0.13, facecolor=fc, edgecolor=GS,
                                lw=0.9, zorder=3))
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.35, 1.5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=7.6, pad=3)
    if note:
        ax.text(0, -1.32, note, ha="center", va="top", fontsize=6.3, color="#333333")

# (a) baseline graph
small_graph(axes[0], 7, title="(a) Connectome $G$",
            note=r"global efficiency $E(G)$")
# (b) node removed
small_graph(axes[1], 7, remove=9, highlight=9,
            title="(b) Remove node $i$",
            note=r"efficiency $E(G-i)$ on $G-i$")
# (c) matched control
ax = axes[2]
ax.add_patch(Rectangle((0.04, 0.30), 0.92, 0.30, facecolor="none",
                       edgecolor=GS, lw=0.8, zorder=1))
ax.add_patch(Rectangle((0.04, 0.02), 0.92, 0.22, facecolor="none",
                       edgecolor=GS, lw=0.8, zorder=1))
ax.text(0.50, 0.45, "target node $i$   (degree $d_i$)", ha="center", fontsize=6.6)
ax.text(0.50, 0.37, r"$\mathrm{CIS}(i)$", ha="center", fontsize=7.4)
ax.text(0.50, 0.13, "degree-matched control ($\\pm$10% $d_i$)", ha="center", fontsize=6.6)
ax.annotate("", xy=(0.50, 0.285), xytext=(0.50, 0.245),
            arrowprops=dict(arrowstyle="-|>", color=HL, lw=1.0))
ax.text(0.5, 0.255, r"residual $= \mathrm{CIS}(i)-\mathrm{CIS}(c_{\mathrm{match}})$",
        ha="center", fontsize=6.3, transform=ax.transData)
ax.text(0.5, -0.13, "1:1 greedy, no replacement;\nnearest-50 fallback (flagged)",
        ha="center", va="top", fontsize=6.3, color="#333333")
ax.set_xlim(0, 1); ax.set_ylim(-0.28, 0.68); ax.axis("off")
ax.set_title("(c) Degree/strength control", fontsize=7.6, pad=3)
# (d) null arbitration
small_graph(axes[3], 7, highlight=None,
            title="(d) Degree-preserving null",
            note="Maslov–Sneppen rewiring;\nidentical degree sequence")
axd = axes[3]
axd.text(0, -1.86, r"empirical $p$ (add-one) $\rightarrow$ Stouffer $z$ $\rightarrow$ BH-FDR",
         ha="center", va="top", fontsize=6.3, color="#333333")

# flow arrows between panels
for x0, x1 in [(0.965, 0.995), (0.665, 0.695), (0.365, 0.395)]:
    pass
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "fig02_cis_method.pdf"), format="pdf")
fig.savefig(os.path.join(OUT, "fig02_cis_method.png"), dpi=300)
print("wrote fig02_cis_method.pdf/.png")
