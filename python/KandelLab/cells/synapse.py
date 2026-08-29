"""突触模型：EPSP / IPSP 与时间、空间总和。

核心概念 #5：突触输入在时间与空间上整合，决定神经元是否发放。

模型
----
    PSP(t) = w · (t/τ) · exp(−t/τ)          （α 函数，t ≥ 0）

多突触事件的响应线性叠加（在亚阈值范围内近似成立）：
    V(t) = Σ_i  w_i · PSP(t − t_i)

验证锚点：
    时间总和：ISI 短 → 双脉冲峰值 > 单脉冲峰值；
    空间总和：多输入同刻 → 幅度随输入数近似线性增长。
"""

from __future__ import annotations

import numpy as np

from .. import config


def psp_alpha(t, w=1.0, tau=None):
    """α 函数型突触后电位。

    Parameters
    ----------
    t : array_like
        时间（ms）。
    w : float
        突触权重（幅度；IPSP 传负值）。
    tau : float | None
        时间常数（ms）；None 用 config.SYNAPSE_DEFAULTS["tau_decay"]。

    Returns
    -------
    np.ndarray
    """
    tau = config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    pos = t >= 0
    out[pos] = w * (t[pos] / tau) * np.exp(-t[pos] / tau)
    return out


def psp_alpha_peak(w, tau):
    """α 函数峰值幅度（归一化到 w）。"""
    return w * np.exp(-1.0)


def psp_peak_time(tau):
    """α 函数到达峰值的时间（ms）。"""
    return tau


def simulate_psp(spike_times, t, w=1.0, tau=None):
    """对单一输入的多次发放做时间总和（线性叠加）。

    Parameters
    ----------
    spike_times : array_like
        发放时刻（ms）。
    t : array_like
        观测时间网格（ms）。
    w, tau : float
        权重与时间常数。

    Returns
    -------
    np.ndarray : V(t)
    """
    t = np.asarray(t, dtype=float)
    v = np.zeros_like(t)
    for st in np.atleast_1d(spike_times):
        v = v + psp_alpha(t - st, w, tau)
    return v


def temporal_sum_peak(isi, w=1.0, tau=None, dt=0.01):
    """双脉冲（间隔 ISI）时间总和后的峰值电位。

    Returns
    -------
    float : 叠加后峰值（mV）。
    """
    tau = config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau
    t = np.arange(0.0, max(8 * tau, isi + 6 * tau), dt)
    v = simulate_psp([0.0, isi], t, w, tau)
    return float(v.max())


def temporal_sum_scan(isis, w=1.0, tau=None, dt=0.01):
    """扫描双脉冲间隔：返回 (ISI 序列, 峰值序列, 单脉冲峰值)。"""
    isis = np.asarray(isis, dtype=float)
    single = psp_alpha_peak(w, config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau)
    peaks = np.array([temporal_sum_peak(isi, w, tau, dt) for isi in isis])
    return isis, peaks, single


def spatial_sum(spike_times_list, t, weights=None, taus=None):
    """多输入（每条输入一个发放时刻序列）的空间总和。

    Parameters
    ----------
    spike_times_list : list[array_like]
        每条输入对应的发放时刻。
    t : array_like
        时间网格。
    weights : list[float] | None
        各输入权重；None 全为 1。
    taus : list[float] | None
        各输入时间常数；None 全用默认。

    Returns
    -------
    np.ndarray : V(t)
    """
    n_in = len(spike_times_list)
    if weights is None:
        weights = [1.0] * n_in
    if taus is None:
        taus = [None] * n_in
    t = np.asarray(t, dtype=float)
    v = np.zeros_like(t)
    for spikes, w, tau in zip(spike_times_list, weights, taus):
        v = v + simulate_psp(spikes, t, w, tau)
    return v


def spatial_sum_peak(spike_times_list, t, weights=None, taus=None):
    """多输入空间总和后的峰值。"""
    return float(spatial_sum(spike_times_list, t, weights, taus).max())


def isi_to_firing(isi):
    """由发放间隔（ms）换算发放率（Hz）。"""
    return 1000.0 / float(isi) if isi > 0 else np.inf
