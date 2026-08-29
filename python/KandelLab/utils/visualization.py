"""KandelLab — NeuroVisualizer: a unified academic-style figure generator.

All figures are saved as PNG (SVG is not used in the teaching context), with a
parchment-inspired vintage academic palette, serif fonts, no gridlines and
preserved borders, consistent with a "rigorous and minimalist academic" style.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({
    "font.family": "serif",
    "font.serif": ["Noto Serif CJK SC", "Noto Serif CJK", "DejaVu Serif"],
    "font.sans-serif": ["Noto Sans CJK SC", "Noto Sans CJK", "DejaVu Sans"],
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.edgecolor": "#3b2f1f",
    "axes.labelcolor": "#2a2018",
    "text.color": "#2a2018",
    "xtick.color": "#3b2f1f",
    "ytick.color": "#3b2f1f",
    "axes.linewidth": 0.8,
    "figure.dpi": 110,
    "savefig.dpi": 130,
    "axes.grid": False,
})

_PARCHMENT = "#f4ead0"
_INK = "#2a2018"
_FADED = "#8a7a5c"
_ACCENT1 = "#7a3b2e"   # ochre red (iron oxide)
_ACCENT2 = "#3d5a3a"   # ink green
_ACCENT3 = "#5a4a78"   # indigo


def _style_ax(ax, xlabel=None, ylabel=None, title=None):
    ax.set_facecolor("#fbf5e3")
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color(_FADED)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, pad=8)


def _save(fig, out_dir, name, fmt="png"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.{fmt}"
    fig.tight_layout()
    fig.savefig(path, facecolor=_PARCHMENT)
    plt.close(fig)
    return str(path)


class NeuroVisualizer:
    """Unified entry point for all plotting methods; each method returns the saved PNG path."""

    def __init__(self, out_dir="output/figures"):
        self.out_dir = str(out_dir)

    # ------------------------------------------------------------------
    # cells
    # ------------------------------------------------------------------
    def membrane_potential(self, t, v, gNa=None, gK=None, out="membrane_potential",
                           legend_v="V (mV)"):
        """Membrane potential waveform (optionally with gNa/gK conductances overlaid)."""
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.plot(t, v, color=_ACCENT1, lw=1.4, label=legend_v)
        if gNa is not None:
            ax.plot(t, gNa, color=_ACCENT2, lw=0.9, ls="--", label="g_Na")
        if gK is not None:
            ax.plot(t, gK, color=_ACCENT3, lw=0.9, ls=":", label="g_K")
        _style_ax(ax, "t (ms)", "mV" if gNa is None else "mV / mS·cm⁻²")
        ax.legend(frameon=False, loc="best")
        return _save(fig, self.out_dir, out)

    def raster(self, times_by_trial, out="raster"):
        """LIF raster plot (multiple trials overlaid)."""
        fig, ax = plt.subplots(figsize=(7, 3.2))
        for i, tt in enumerate(times_by_trial):
            ax.plot(tt, np.full_like(tt, i), color=_INK, marker="|", ms=3,
                    ls="none", alpha=0.8)
        _style_ax(ax, "t (ms)", "trial")
        return _save(fig, self.out_dir, out)

    def fi_curve(self, I, f, out="fi_curve"):
        """f-I curve."""
        fig, ax = plt.subplots(figsize=(5.4, 3.6))
        ax.plot(I, f, color=_ACCENT2, lw=1.8)
        ax.scatter(I, f, s=14, color=_ACCENT2, zorder=3)
        _style_ax(ax, "I (nA)", "f (Hz)")
        return _save(fig, self.out_dir, out)

    # ------------------------------------------------------------------
    # circuits
    # ------------------------------------------------------------------
    def dof_receptive_field(self, kernel2d, out="dof_receptive_field"):
        """DOG receptive-field heatmap."""
        fig, ax = plt.subplots(figsize=(4.4, 4.0))
        im = ax.imshow(kernel2d, cmap="RdBu_r", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        _style_ax(ax, None, None, "DOG receptive field")
        return _save(fig, self.out_dir, out)

    def edge_enhancement(self, original, processed, out="edge_enhancement"):
        """Edge-enhancement comparison (original / after lateral inhibition)."""
        fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4))
        for ax, img, title in zip(axes, (original, processed),
                                  ("Original luminance", "Lateral-inhibited output")):
            ax.imshow(img, cmap="gray", interpolation="nearest")
            ax.set_title(title)
            ax.set_xticks([]); ax.set_yticks([])
        return _save(fig, self.out_dir, out)

    def wc_phase_portrait(self, E, I, nullE, nullI, out="wc_phase_portrait"):
        """Wilson-Cowan phase portrait (nullclines + sampled trajectories)."""
        fig, ax = plt.subplots(figsize=(5.4, 5.0))
        ax.plot(E, nullE, color=_ACCENT1, lw=1.8, label="E nullcline")
        ax.plot(nullI, I, color=_ACCENT2, lw=1.8, label="I nullcline")
        ax.plot(E, I, color=_INK, lw=0.8, alpha=0.7, ls="--", label="trajectory")
        _style_ax(ax, "E", "I", "Wilson-Cowan phase plane")
        ax.legend(frameon=False, loc="best")
        return _save(fig, self.out_dir, out)

    def kuramoto_transition(self, K, R, out="kuramoto_transition"):
        """Kuramoto order-parameter R(K) phase-transition curve."""
        fig, ax = plt.subplots(figsize=(5.4, 3.6))
        ax.plot(K, R, color=_ACCENT3, lw=1.8)
        _style_ax(ax, "Coupling strength K", "Order parameter R")
        return _save(fig, self.out_dir, out)

    def kuramoto_snapshots(self, thetas_by_K, out="kuramoto_snapshots"):
        """Phase distributions at different coupling strengths (polar snapshots)."""
        n = len(thetas_by_K)
        fig, axes = plt.subplots(1, n, figsize=(2.4 * n, 2.2),
                                 subplot_kw={"projection": "polar"})
        if n == 1:
            axes = [axes]
        for ax, th in zip(axes, thetas_by_K):
            ax.scatter(th, np.ones_like(th), s=12, color=_ACCENT1, alpha=0.8)
            ax.set_ylim(0, 1.2); ax.set_yticks([])
            ax.set_xticks(np.linspace(0, 2 * np.pi, 5, endpoint=False))
        return _save(fig, self.out_dir, out)

    # ------------------------------------------------------------------
    # systems
    # ------------------------------------------------------------------
    def gabor_bank(self, gabors, out="gabor_bank"):
        """Gabor filter bank grid plot."""
        n = len(gabors)
        cols = min(6, n)
        rows = int(np.ceil(n / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(2.2 * cols, 2.2 * rows))
        axes = np.atleast_1d(axes).ravel()
        for ax, g in zip(axes, gabors):
            ax.imshow(g, cmap="RdBu_r", interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
        for ax in axes[n:]:
            ax.axis("off")
        return _save(fig, self.out_dir, out)

    def tuning_curve(self, angles, response, out="tuning_curve"):
        """Orientation tuning curve (polar + Cartesian)."""
        fig, (axp, axc) = plt.subplots(1, 2, figsize=(7.6, 3.4),
                                       subplot_kw=dict(projection="polar",
                                                       polar=True))
        axp.plot(angles, response, color=_ACCENT1, lw=1.6)
        axp.fill(angles, response, color=_ACCENT1, alpha=0.2)
        axp.set_ylim(0, max(response) * 1.15)
        _style_ax(axc, "Angle (°)", "Response")
        axc.plot(np.degrees(angles), response, color=_ACCENT2, lw=1.6)
        return _save(fig, self.out_dir, out)

    def tonotopy(self, freqs, response, out="tonotopy"):
        """Auditory frequency tuning curve (monotonic tonotopy arrangement)."""
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        ax.semilogx(freqs, response, color=_ACCENT3, lw=1.8, marker="o", ms=3)
        _style_ax(ax, "Frequency (Hz)", "Response")
        return _save(fig, self.out_dir, out)

    def adaptation_curve(self, trial, gain, target=None, out="adaptation_curve"):
        """VOR gain adaptation curve."""
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        ax.plot(trial, gain, color=_ACCENT2, lw=1.8)
        if target is not None:
            ax.axhline(target, color=_FADED, ls="--", lw=1.0,
                       label=f"target {target}")
        _style_ax(ax, "trial", "gain g")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)

    def memory_recall(self, original, corrupted, recovered, out="memory_recall"):
        """Hopfield associative memory retrieval (original / corrupted / recovered)."""
        fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.9))
        for ax, img, title in zip(axes, (original, corrupted, recovered),
                                  ("Stored pattern", "Corrupted input", "Recovered")):
            ax.imshow(img, cmap="binary", interpolation="nearest")
            ax.set_title(title)
            ax.set_xticks([]); ax.set_yticks([])
        return _save(fig, self.out_dir, out)

    def hopfield_energy(self, energy, out="hopfield_energy"):
        """Hopfield energy descent curve."""
        fig, ax = plt.subplots(figsize=(5.4, 3.4))
        ax.plot(energy, color=_ACCENT3, lw=1.6)
        _style_ax(ax, "Asynchronous update step", "Energy E")
        return _save(fig, self.out_dir, out)

    def rw_learning(self, trials, V, block2=None, out="rw_learning"):
        """Rescorla-Wagner learning curve (optionally showing the blocking phase)."""
        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        ax.plot(trials, V, color=_ACCENT1, lw=1.6)
        if block2 is not None:
            for start in block2:
                ax.axvline(start, color=_FADED, ls="--", lw=0.9)
        _style_ax(ax, "Trial", "Expected value V")
        return _save(fig, self.out_dir, out)

    def td_error(self, trial, delta, out="td_error"):
        """TD prediction error (dopamine-like signal)."""
        fig, ax = plt.subplots(figsize=(6.2, 3.4))
        ax.plot(trial, delta, color=_ACCENT2, lw=1.4)
        ax.axhline(0, color=_FADED, lw=0.8, ls=":")
        _style_ax(ax, "Time", "δ")
        return _save(fig, self.out_dir, out)

    def ddm_trajectories(self, t, x, boundary=None, out="ddm_trajectories"):
        """DDM decision trajectories."""
        fig, ax = plt.subplots(figsize=(6.4, 3.8))
        for i in range(min(x.shape[0], 15)):
            ax.plot(t, x[i], color=_ACCENT1, lw=0.8, alpha=0.8)
        if boundary is not None:
            ax.axhline(boundary, color=_FADED, ls="--", lw=0.9)
            ax.axhline(-boundary, color=_FADED, ls="--", lw=0.9)
        _style_ax(ax, "t (s)", "Accumulated evidence x")
        return _save(fig, self.out_dir, out)

    def rt_histogram(self, rt_correct, rt_error=None, out="rt_histogram"):
        """RT distribution histogram."""
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        if len(rt_correct) > 0:
            ax.hist(rt_correct, bins=30, color=_ACCENT2, alpha=0.75,
                    label="correct")
        if rt_error is not None and len(rt_error) > 0:
            ax.hist(rt_error, bins=30, color=_ACCENT1, alpha=0.65, label="error")
        _style_ax(ax, "RT (s)", "Count")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)

    def roc(self, fpr, tpr, auc=None, out="roc_curve"):
        """ROC curve."""
        fig, ax = plt.subplots(figsize=(4.6, 4.4))
        ax.plot(fpr, tpr, color=_ACCENT3, lw=1.8)
        ax.plot([0, 1], [0, 1], color=_FADED, ls="--", lw=0.9)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        title = "ROC"
        if auc is not None:
            title += f" (AUC={auc:.3f})"
        _style_ax(ax, "False-positive rate", "True-positive rate", title)
        return _save(fig, self.out_dir, out)

    def fisher_analysis(self, noise, fisher, var, out="fisher_analysis"):
        """Fisher information vs decoding variance comparison (Cramér-Rao)."""
        fig, ax = plt.subplots(figsize=(5.8, 3.6))
        ax.plot(noise, fisher, color=_ACCENT1, lw=1.6, label="Fisher information")
        ax.plot(noise, var, color=_ACCENT2, lw=1.6, ls="--", label="Decoding variance")
        _style_ax(ax, "Noise level", "Value")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)
