"""KandelLab — 数值工具：积分器、发放检测、统计与通用数学工具。"""

from __future__ import annotations

import numpy as np

from .. import config


def euler_step(f, y, t, dt, *args, **kwargs):
    """Euler 显式积分单步。f(y, t, *args) -> dy/dt。"""
    return y + dt * np.asarray(f(y, t, *args, **kwargs), dtype=float)


def rk4_step(f, y, t, dt, *args, **kwargs):
    """经典 RK4 单步。f(y, t, *args) -> dy/dt。"""
    y = np.asarray(y, dtype=float)
    k1 = np.asarray(f(y, t, *args, **kwargs), dtype=float)
    k2 = np.asarray(f(y + 0.5 * dt * k1, t + 0.5 * dt, *args, **kwargs), dtype=float)
    k3 = np.asarray(f(y + 0.5 * dt * k2, t + 0.5 * dt, *args, **kwargs), dtype=float)
    k4 = np.asarray(f(y + dt * k3, t + dt, *args, **kwargs), dtype=float)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


INTEGRATORS = {"euler": euler_step, "rk4": rk4_step}


def integrate_ode(f, y0, t_max, dt=None, method="rk4", t0=0.0, **kwargs):
    """对一阶 ODE 组做数值积分。

    Parameters
    ----------
    f : callable
        f(y, t, **kwargs) -> dy/dt（y 为向量或标量）。
    y0 : array_like
        初值。
    t_max : float
        积分时长（单位与 dt 一致）。
    dt : float | None
        时间步长；None 时取 config.NUMERICS["default_dt"]。
    method : str
        "euler" 或 "rk4"。
    t0 : float
        初始时刻。

    Returns
    -------
    t : np.ndarray  (N,)
    y : np.ndarray  (N, ...) 维度与 y0 保持一致
    """
    dt = config.NUMERICS["default_dt"] if dt is None else dt
    stepper = INTEGRATORS[method]
    y0 = np.asarray(y0, dtype=float)
    n_steps = int(np.ceil(t_max / dt))
    t = np.linspace(t0, t0 + n_steps * dt, n_steps + 1)
    y = np.empty((n_steps + 1,) + y0.shape, dtype=float)
    y[0] = y0
    for i in range(n_steps):
        y[i + 1] = stepper(f, y[i], t[i], dt, **kwargs)
    return t, y


def detect_spikes(v, v_thresh=None, dt=None, refractory_ms=0.0,
                  grad_thresh=30.0):
    """从膜电位轨迹提取发放时刻。

    Parameters
    ----------
    v : np.ndarray
        膜电位序列（mV）。
    v_thresh : float | None
        检测阈值；None 时使用梯度法：以 dV/dt 超过 grad_thresh（默认
        30 mV/ms）的上升沿识别动作电位。梯度法可区分真正的 AP 与
        亚阈值去极化（如 HH 阈值下的小脉冲），也适用于 LIF 的瞬发放电。
    dt : float | None
        采样间隔（ms）；None 时按索引计时刻。
    refractory_ms : float
        最小发放间隔（用于去除检测毛刺）。
    grad_thresh : float
        梯度阈值（mV/ms），仅 v_thresh 为 None 时使用。

    Returns
    -------
    spike_times : np.ndarray
    """
    v = np.asarray(v, dtype=float)
    if v_thresh is not None:
        above = v > v_thresh
        # 上升沿触发
        cross = above[1:] & ~above[:-1]
        idx = np.flatnonzero(cross) + 1
    else:
        grad = np.diff(v)
        if dt is not None:
            grad = grad / dt
        rising = np.concatenate(([False], grad > grad_thresh))
        # 每段连续上升（rising 从 False→True）的起始位置
        starts = np.flatnonzero(rising[1:] & ~rising[:-1]) + 1
        idx = starts
        # 排除上升段起点之前的下降伪影：要求起点之后 v 确实显著高于起点
        if idx.size:
            keep = [i for i in idx if v[i] - v[0] > grad_thresh * (dt or 1.0)]
            idx = np.asarray(keep, dtype=int)
    # 不应期去重
    if refractory_ms > 0 and dt is not None:
        keep = [idx[0]] if idx.size else []
        for j in idx[1:]:
            if (j - keep[-1]) * dt >= refractory_ms:
                keep.append(j)
        idx = np.asarray(keep, dtype=int)
    if dt is None:
        return idx.astype(float)
    return idx * dt


def firing_rate(spike_times, duration):
    """由发放时刻列表与观测时长计算平均发放率（Hz）。"""
    spike_times = np.asarray(spike_times, dtype=float)
    return spike_times.size / float(duration) if duration > 0 else 0.0


def gaussian(x, mu, sigma):
    """高斯函数。"""
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def sigmoid(x, gain=1.0, threshold=0.0):
    """逻辑斯蒂 sigmoid：1 / (1 + exp(-gain*(x-threshold)))。"""
    x = np.asarray(x, dtype=float)
    z = gain * (x - threshold)
    z = np.clip(z, -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(-z))


def normalise(x, axis=None):
    """将数组线性缩放到 [0, 1]。"""
    x = np.asarray(x, dtype=float)
    mn = x.min(axis=axis, keepdims=True) if axis is not None else x.min()
    mx = x.max(axis=axis, keepdims=True) if axis is not None else x.max()
    span = mx - mn
    if np.all(span == 0):
        return np.zeros_like(x)
    return (x - mn) / span


def rng(seed=None):
    """返回带种子的 numpy 随机数生成器（默认使用全局配置种子）。"""
    if seed is None:
        seed = config.NUMERICS["seed"]
    return np.random.default_rng(int(seed))


def spike_times_to_raster(spike_times, n_trials, duration, dt=0.001):
    """把多次试验的发放时刻列表转为栅栏图二进制矩阵 (n_trials, n_bins)。

    Parameters
    ----------
    spike_times : list[np.ndarray]
        每次试验的发放时刻。
    n_trials : int
    duration : float
    dt : float
    """
    n_bins = int(np.ceil(duration / dt))
    raster = np.zeros((n_trials, n_bins), dtype=np.uint8)
    for i, times in enumerate(spike_times[:n_trials]):
        times = np.asarray(times, dtype=float)
        bins = np.clip((times / dt).astype(int), 0, n_bins - 1)
        raster[i, bins] = 1
    return raster
