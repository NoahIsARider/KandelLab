"""KandelLab — NeuroVisualizer：统一的学术风图表生成器。

所有图以 PNG 保存（教学场景不使用 SVG），采用仿羊皮纸的复古学术配色，
衬线字体，去网格线、保边框，符合"学术场景严谨极简"风格。
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
_ACCENT1 = "#7a3b2e"   # 赭红（氧化铁）
_ACCENT2 = "#3d5a3a"   # 墨绿
_ACCENT3 = "#5a4a78"   # 靛青


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
    """所有绘图方法的统一入口；每个方法返回保存后的 PNG 路径。"""

    def __init__(self, out_dir="output/figures"):
        self.out_dir = str(out_dir)

    # ------------------------------------------------------------------
    # cells
    # ------------------------------------------------------------------
    def membrane_potential(self, t, v, gNa=None, gK=None, out="membrane_potential",
                           legend_v="V (mV)"):
        """膜电位波形（可选叠加 gNa/gK 电导）。"""
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
        """LIF 栅栏图（多次试验叠加）。"""
        fig, ax = plt.subplots(figsize=(7, 3.2))
        for i, tt in enumerate(times_by_trial):
            ax.plot(tt, np.full_like(tt, i), color=_INK, marker="|", ms=3,
                    ls="none", alpha=0.8)
        _style_ax(ax, "t (ms)", "trial")
        return _save(fig, self.out_dir, out)

    def fi_curve(self, I, f, out="fi_curve"):
        """f-I 曲线。"""
        fig, ax = plt.subplots(figsize=(5.4, 3.6))
        ax.plot(I, f, color=_ACCENT2, lw=1.8)
        ax.scatter(I, f, s=14, color=_ACCENT2, zorder=3)
        _style_ax(ax, "I (nA)", "f (Hz)")
        return _save(fig, self.out_dir, out)

    # ------------------------------------------------------------------
    # circuits
    # ------------------------------------------------------------------
    def dof_receptive_field(self, kernel2d, out="dof_receptive_field"):
        """DOG 感受野热图。"""
        fig, ax = plt.subplots(figsize=(4.4, 4.0))
        im = ax.imshow(kernel2d, cmap="RdBu_r", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        _style_ax(ax, None, None, "DOG 感受野")
        return _save(fig, self.out_dir, out)

    def edge_enhancement(self, original, processed, out="edge_enhancement"):
        """边缘增强对比（原图 / 侧抑制后）。"""
        fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4))
        for ax, img, title in zip(axes, (original, processed),
                                  ("原始亮度", "侧抑制输出")):
            ax.imshow(img, cmap="gray", interpolation="nearest")
            ax.set_title(title)
            ax.set_xticks([]); ax.set_yticks([])
        return _save(fig, self.out_dir, out)

    def wc_phase_portrait(self, E, I, nullE, nullI, out="wc_phase_portrait"):
        """Wilson-Cowan 相图（零等斜线 + 采样轨迹）。"""
        fig, ax = plt.subplots(figsize=(5.4, 5.0))
        ax.plot(E, nullE, color=_ACCENT1, lw=1.8, label="E nullcline")
        ax.plot(nullI, I, color=_ACCENT2, lw=1.8, label="I nullcline")
        ax.plot(E, I, color=_INK, lw=0.8, alpha=0.7, ls="--", label="trajectory")
        _style_ax(ax, "E", "I", "Wilson-Cowan 相平面")
        ax.legend(frameon=False, loc="best")
        return _save(fig, self.out_dir, out)

    def kuramoto_transition(self, K, R, out="kuramoto_transition"):
        """Kuramoto 序参量 R(K) 相变曲线。"""
        fig, ax = plt.subplots(figsize=(5.4, 3.6))
        ax.plot(K, R, color=_ACCENT3, lw=1.8)
        _style_ax(ax, "耦合强度 K", "序参量 R")
        return _save(fig, self.out_dir, out)

    def kuramoto_snapshots(self, thetas_by_K, out="kuramoto_snapshots"):
        """不同耦合强度下的相位分布（极坐标快照）。"""
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
        """Gabor 滤波器组网格图。"""
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
        """方位调谐曲线（极坐标 + 直角坐标）。"""
        fig, (axp, axc) = plt.subplots(1, 2, figsize=(7.6, 3.4),
                                       subplot_kw=dict(projection="polar",
                                                       polar=True))
        axp.plot(angles, response, color=_ACCENT1, lw=1.6)
        axp.fill(angles, response, color=_ACCENT1, alpha=0.2)
        axp.set_ylim(0, max(response) * 1.15)
        _style_ax(axc, "角度 (°)", "响应")
        axc.plot(np.degrees(angles), response, color=_ACCENT2, lw=1.6)
        return _save(fig, self.out_dir, out)

    def tonotopy(self, freqs, response, out="tonotopy"):
        """听觉频率调谐曲线（tonotopy 单调排列）。"""
        fig, ax = plt.subplots(figsize=(5.6, 3.6))
        ax.semilogx(freqs, response, color=_ACCENT3, lw=1.8, marker="o", ms=3)
        _style_ax(ax, "频率 (Hz)", "响应")
        return _save(fig, self.out_dir, out)

    def adaptation_curve(self, trial, gain, target=None, out="adaptation_curve"):
        """VOR 增益适应曲线。"""
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        ax.plot(trial, gain, color=_ACCENT2, lw=1.8)
        if target is not None:
            ax.axhline(target, color=_FADED, ls="--", lw=1.0,
                       label=f"目标 {target}")
        _style_ax(ax, "trial", "增益 g")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)

    def memory_recall(self, original, corrupted, recovered, out="memory_recall"):
        """Hopfield 联想记忆恢复（原模式/损坏/恢复）。"""
        fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.9))
        for ax, img, title in zip(axes, (original, corrupted, recovered),
                                  ("存储模式", "损坏输入", "恢复结果")):
            ax.imshow(img, cmap="binary", interpolation="nearest")
            ax.set_title(title)
            ax.set_xticks([]); ax.set_yticks([])
        return _save(fig, self.out_dir, out)

    def hopfield_energy(self, energy, out="hopfield_energy"):
        """Hopfield 能量下降曲线。"""
        fig, ax = plt.subplots(figsize=(5.4, 3.4))
        ax.plot(energy, color=_ACCENT3, lw=1.6)
        _style_ax(ax, "异步更新步", "能量 E")
        return _save(fig, self.out_dir, out)

    def rw_learning(self, trials, V, block2=None, out="rw_learning"):
        """Rescorla-Wagner 学习曲线（可含阻塞期）。"""
        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        ax.plot(trials, V, color=_ACCENT1, lw=1.6)
        if block2 is not None:
            for start in block2:
                ax.axvline(start, color=_FADED, ls="--", lw=0.9)
        _style_ax(ax, "试验次数", "预期值 V")
        return _save(fig, self.out_dir, out)

    def td_error(self, trial, delta, out="td_error"):
        """TD 预测误差（多巴胺样信号）。"""
        fig, ax = plt.subplots(figsize=(6.2, 3.4))
        ax.plot(trial, delta, color=_ACCENT2, lw=1.4)
        ax.axhline(0, color=_FADED, lw=0.8, ls=":")
        _style_ax(ax, "时间", "δ")
        return _save(fig, self.out_dir, out)

    def ddm_trajectories(self, t, x, boundary=None, out="ddm_trajectories"):
        """DDM 决策轨迹。"""
        fig, ax = plt.subplots(figsize=(6.4, 3.8))
        for i in range(min(x.shape[0], 15)):
            ax.plot(t, x[i], color=_ACCENT1, lw=0.8, alpha=0.8)
        if boundary is not None:
            ax.axhline(boundary, color=_FADED, ls="--", lw=0.9)
            ax.axhline(-boundary, color=_FADED, ls="--", lw=0.9)
        _style_ax(ax, "t (s)", "累积证据 x")
        return _save(fig, self.out_dir, out)

    def rt_histogram(self, rt_correct, rt_error=None, out="rt_histogram"):
        """RT 分布直方图。"""
        fig, ax = plt.subplots(figsize=(5.6, 3.4))
        if len(rt_correct) > 0:
            ax.hist(rt_correct, bins=30, color=_ACCENT2, alpha=0.75,
                    label="correct")
        if rt_error is not None and len(rt_error) > 0:
            ax.hist(rt_error, bins=30, color=_ACCENT1, alpha=0.65, label="error")
        _style_ax(ax, "RT (s)", "频数")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)

    def roc(self, fpr, tpr, auc=None, out="roc_curve"):
        """ROC 曲线。"""
        fig, ax = plt.subplots(figsize=(4.6, 4.4))
        ax.plot(fpr, tpr, color=_ACCENT3, lw=1.8)
        ax.plot([0, 1], [0, 1], color=_FADED, ls="--", lw=0.9)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        title = "ROC"
        if auc is not None:
            title += f" (AUC={auc:.3f})"
        _style_ax(ax, "假阳性率", "真阳性率", title)
        return _save(fig, self.out_dir, out)

    def fisher_analysis(self, noise, fisher, var, out="fisher_analysis"):
        """Fisher 信息与解码方差对比（Cramér-Rao）。"""
        fig, ax = plt.subplots(figsize=(5.8, 3.6))
        ax.plot(noise, fisher, color=_ACCENT1, lw=1.6, label="Fisher 信息")
        ax.plot(noise, var, color=_ACCENT2, lw=1.6, ls="--", label="解码方差")
        _style_ax(ax, "噪声水平", "值")
        ax.legend(frameon=False)
        return _save(fig, self.out_dir, out)
