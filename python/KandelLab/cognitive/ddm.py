"""漂移扩散模型（Drift-Diffusion Model, DDM）。

核心概念 #12a：决策是证据累积到阈值的随机过程。

模型
----
    dx = μ·dt + σ·dW ，x 越过 +a → 选择 1（正确，若 μ>0）；
                        x 越过 −a → 选择 2（错误）。

验证锚点：
    漂移率 μ↑ → 正确率↑、反应时 RT↓；
    边界 a↑ → 正确率↑、反应时 RT↑（速度-准确性权衡）。
"""

from __future__ import annotations

import numpy as np

from .. import config


def simulate_trial(mu, sigma, boundary=None, dt=None, T_max=None, x0=0.0,
                   seed=None):
    """单次 DDM 决策。

    Returns
    -------
    (rt, choice) : 反应时（s）与选择（+1/−1）；超时返回 (T_max, 0)。
    """
    p = config.DDM_DEFAULTS
    boundary = p["boundary"] if boundary is None else boundary
    dt = p["dt"] if dt is None else dt
    T_max = p["T_max"] if T_max is None else T_max
    rng = np.random.default_rng(seed)
    x = x0
    n_steps = int(np.ceil(T_max / dt))
    for i in range(n_steps):
        x = x + mu * dt + sigma * np.sqrt(dt) * rng.standard_normal()
        if x >= boundary:
            return (i + 1) * dt, +1.0
        if x <= -boundary:
            return (i + 1) * dt, -1.0
    return T_max, 0.0


def simulate_experiment(mu, sigma, boundary=None, n_trials=1000, dt=None,
                        T_max=None, seed=None):
    """多次试验：返回 (RT 数组, 选择数组, 正确率, 平均 RT)。"""
    p = config.DDM_DEFAULTS
    boundary = p["boundary"] if boundary is None else boundary
    dt = p["dt"] if dt is None else dt
    T_max = p["T_max"] if T_max is None else T_max
    rng = np.random.default_rng(seed)
    rts = np.empty(n_trials)
    choices = np.empty(n_trials)
    for i in range(n_trials):
        rt, ch = simulate_trial(mu, sigma, boundary, dt, T_max,
                                seed=int(rng.integers(0, 2 ** 31)))
        rts[i], choices[i] = rt, ch
    decided = choices != 0
    acc = float(np.mean(choices[decided] == np.sign(mu))) if decided.any() else 0.0
    return rts, choices, acc, float(np.mean(rts))


def speed_accuracy_tradeoff(mu, sigma, boundaries, n_trials=500, seed=0):
    """扫描边界 a → (正确率, 平均 RT)。

    Returns
    -------
    (boundaries, accuracies, mean_rts)
    """
    accs, mrt = [], []
    for a in boundaries:
        _, _, acc, rt = simulate_experiment(mu, sigma, a, n_trials, seed=seed)
        accs.append(acc)
        mrt.append(rt)
    return (np.asarray(boundaries), np.asarray(accs), np.asarray(mrt))


def drift_scan(mus, sigma, boundary=None, n_trials=500, seed=0):
    """扫描漂移率 μ → (正确率, 平均 RT)。"""
    p = config.DDM_DEFAULTS
    boundary = p["boundary"] if boundary is None else boundary
    accs, mrt = [], []
    for m in mus:
        _, _, acc, rt = simulate_experiment(m, sigma, boundary, n_trials,
                                            seed=seed)
        accs.append(acc)
        mrt.append(rt)
    return (np.asarray(mus), np.asarray(accs), np.asarray(mrt))
