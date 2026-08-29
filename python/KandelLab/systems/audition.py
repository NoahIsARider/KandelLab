"""听觉：γ-tone 滤波器组与频率调谐（tonotopy）。

核心概念 #10b：感觉系统按特征调谐（听觉频率选择性）。

模型
----
    γ-tone 冲激响应（Patterson & Holdsworth）：
        g(t) = t^(n−1) · exp(−2π·b·t) · cos(2π·f·t + φ)，t ≥ 0

    通道带宽取等效矩形带宽（ERB）：
        ERB(f) = 24.7 · (4.37·f/1000 + 1)

    通道响应 = 信号经通道滤波后的能量（RMS）。

验证锚点：
    纯音刺激在特征频率等于刺激频率的通道响应最大；
    通道特征频率沿耳蜗从低到高单调排列（tonotopy）。
"""

from __future__ import annotations

import numpy as np

from .. import config


def erb(f):
    """等效矩形带宽 ERB(f)（Hz）。"""
    f = np.asarray(f, dtype=float)
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def gammatone_impulse(t, f, order=4, bw=None, phi=0.0):
    """γ-tone 冲激响应 g(t)。

    Parameters
    ----------
    t : array_like
        时间（s）。
    f : float
        特征频率（Hz）。
    order : int
        γ 阶数（n=4 为经典值）。
    bw : float | None
        带宽（Hz）；None 用 ERB(f)。
    phi : float
        相位。
    """
    bw = erb(f) if bw is None else bw
    t = np.asarray(t, dtype=float)
    pos = t >= 0
    out = np.zeros_like(t)
    tp = t[pos]
    env = tp ** (order - 1) * np.exp(-2 * np.pi * bw * tp)
    out[pos] = env * np.cos(2 * np.pi * f * tp + phi)
    return out


def gammatone_filterbank(fmin=None, fmax=None, n_channels=None, fs=None,
                         order=None, dur=0.02):
    """生成 γ-tone 滤波器组（特征频率在 ERB 尺度上均匀分布）。

    Returns
    -------
    (cf, filters) : 特征频率数组与 (n, len(t)) 滤波器核矩阵。
    """
    p = config.AUDITION_DEFAULTS
    fmin = p["fmin"] if fmin is None else fmin
    fmax = p["fmax"] if fmax is None else fmax
    n = int(p["n_channels"]) if n_channels is None else int(n_channels)
    fs = p["fs"] if fs is None else fs
    order = p["order"] if order is None else order

    # ERB 尺度：n_channels 个通道，ERB 数单调递增
    n_erb = np.linspace(0.0, 1.0, n)
    # 在 ERB 尺度均匀：f(i) = fmin + (fmax - fmin) * 用 ERB 单调映射
    cf = _erb_spaced(fmin, fmax, n)
    t = np.arange(0.0, dur, 1.0 / fs)
    filters = np.array([gammatone_impulse(t, fc, order) for fc in cf])
    return cf, filters


def _erb_spaced(fmin, fmax, n):
    """在 ERB 数尺度上均匀分布的特征频率（对数-like 单调）。"""
    # ERB number: 21.4·log10(4.37·f/1000 + 1)
    def num(f):
        return 21.4 * np.log10(4.37 * f / 1000.0 + 1.0)

    lo, hi = num(fmin), num(fmax)
    nums = np.linspace(lo, hi, n)
    # 反函数：f = 1000/4.37·(10^(nums/21.4) − 1)
    f = 1000.0 / 4.37 * (10.0 ** (nums / 21.4) - 1.0)
    return f


def channel_response(signal, filters, fs):
    """每个通道对信号的响应（RMS 能量）。"""
    signal = np.asarray(signal, dtype=float)
    return np.sqrt(np.mean(
        np.array([np.convolve(signal, f, mode="same") ** 2 for f in filters]),
        axis=1))


def pure_tone_response(f_stim, fs=None, dur=0.05, fmin=None, fmax=None,
                       n_channels=None, order=None):
    """纯音刺激 → 各通道响应 → (cf, response)。

    验证锚点：cf 最接近 f_stim 的通道响应最大。
    """
    p = config.AUDITION_DEFAULTS
    fs = p["fs"] if fs is None else fs
    dur = float(dur)
    t = np.arange(0.0, dur, 1.0 / fs)
    signal = np.sin(2 * np.pi * f_stim * t)
    cf, filters = gammatone_filterbank(fmin, fmax, n_channels, fs, order)
    resp = channel_response(signal, filters, fs)
    return cf, resp


def tonotopy_curve(f_stim_list, fs=None, dur=0.05, **fb_kwargs):
    """扫描刺激频率：返回 (刺激频率, 最优通道频率, 最优响应)。"""
    best = []
    for f_stim in f_stim_list:
        cf, resp = pure_tone_response(f_stim, fs, dur, **fb_kwargs)
        i = int(np.argmax(resp))
        best.append((float(f_stim), float(cf[i]), float(resp[i])))
    best = np.array(best)
    return best[:, 0], best[:, 1], best[:, 2]
