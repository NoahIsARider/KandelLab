"""VOR（前庭眼动反射）增益适应：小脑 Marr–Albus 误差驱动学习。

核心概念 #10c（运动系统）：运动学习由误差信号驱动，增益可适应。

模型
----
    VOR 增益 g：眼速 = g × 头速。视觉目标静止时理想增益 g* = 1。

    误差（视网膜滑移）= 目标像在视网膜上的速度：
        error = g_target − g

    增益更新（Marr–Albus 风格）：
        Δg = η · error · (平行纤维与攀缘纤维共激活的信号)

    本实现简化为：Δg = η · (g_target − g)，收敛到目标增益。

验证锚点：
    训练后增益单调收敛到目标值；误差衰减到 0。
"""

from __future__ import annotations

import numpy as np

from .. import config


def update_gain(g, error, eta=None):
    """单次增益更新：Δg = η·error。"""
    eta = config.VOR_DEFAULTS["eta"] if eta is None else eta
    return g + eta * error


def simulate_adaptation(n_trials=200, g0=None, target_g=None, eta=None,
                        noise=0.0, seed=0):
    """模拟 VOR 增益适应训练。

    Parameters
    ----------
    n_trials : int
    g0 : float | None
        初始增益。
    target_g : float | None
        目标增益。
    eta : float | None
        学习率。
    noise : float
        每次 trial 增益观测噪声标准差。
    seed : int

    Returns
    -------
    (trial, gain_history, error_history) : 训练过程记录。
    """
    p = config.VOR_DEFAULTS
    g0 = p["g0"] if g0 is None else g0
    target_g = p["target_g"] if target_g is None else target_g
    eta = p["eta"] if eta is None else eta

    rng = np.random.default_rng(seed)
    g = g0
    trials = np.arange(n_trials)
    gains = np.empty(n_trials)
    errors = np.empty(n_trials)
    for i in range(n_trials):
        error = target_g - g
        g = update_gain(g, error, eta)
        observed = g + noise * rng.standard_normal()
        gains[i] = observed
        errors[i] = error
    return trials, gains, errors


def converged_gain(gains, target_g, tol=1e-2):
    """判断末端增益是否收敛到目标（末 20% 均值与目标差 < tol）。"""
    tail = np.asarray(gains, dtype=float)[-int(len(gains) * 0.2):]
    return bool(abs(float(np.mean(tail)) - target_g) < tol)
