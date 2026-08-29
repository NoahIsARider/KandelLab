"""奖赏学习：Rescorla–Wagner 与 TD(λ) 时序差分。

核心概念 #11：学习依赖奖赏预测误差（多巴胺信号）。

模型
----
    Rescorla–Wagner：ΔV = α·(λ − V)
        预期值 V 逐步逼近奖赏 λ；已学会的 CS 阻塞新线索的学习。

    TD 预测误差：δ = r + γ·V(s') − V(s)
        多巴胺样信号；收敛后 δ → 0。

验证锚点：
    条件反射 V 单调渐近收敛到 λ；
    blocking：先学会 A+ 后，B 在 AB+ 阶段几乎不获得价值；
    TD：误差 δ 随学习衰减到 0。
"""

from __future__ import annotations

import numpy as np

from .. import config


def rescorla_wagner(alpha=None, lamb=1.0, n_trials=200, v0=0.0, reward=None):
    """Rescorla–Wagner 条件反射学习。

    Parameters
    ----------
    alpha : float | None
        学习率。
    lamb : float
        奖赏强度（无条件刺激 US）。
    n_trials : int
        试验次数。
    v0 : float
        初始预期值。

    Returns
    -------
    (trial, V) : 试验序号与预期值历史。
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    lamb = float(lamb)
    V = v0
    trials = np.arange(1, n_trials + 1)
    hist = np.empty(n_trials)
    for i in range(n_trials):
        delta = (lamb if reward is None else reward[i]) - V
        V = V + alpha * delta
        hist[i] = V
    return trials, hist


def blocking_experiment(alpha=None, lamb=1.0, n1=200, n2=200, v0=0.0):
    """阻塞效应实验。

    Phase 1：A+ 单独与奖赏配对（V_A → λ）。
    Phase 2：AB+ 复合刺激（V_A 已饱和，V_B 学习被阻塞）。

    Returns
    -------
    (trial, V_A, V_B) : 全程试验序号与两个线索的预期值。
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    VA, VB = v0, v0
    trials = np.arange(1, n1 + n2 + 1)
    ha, hb = np.empty(n1 + n2), np.empty(n1 + n2)
    for i in range(n1):
        delta = lamb - VA
        VA = VA + alpha * delta
        ha[i], hb[i] = VA, VB
    for i in range(n2):
        total = VA + VB
        delta = lamb - total
        VA = VA + alpha * delta
        VB = VB + alpha * delta
        ha[n1 + i], hb[n1 + i] = VA, VB
    return trials, ha, hb


def td_sequence(alpha=None, gamma=None, lamb=1.0, n_steps=40, v0=0.0,
                reward_at=None):
    """单次 CS→US 时序的 TD 学习轨迹。

    每个时间步：V 的预测误差 δ = reward + γ·V_next − V，
    更新 V（此处以单状态 CS 的价值预测 US 到达前的值）。

    Returns
    -------
    (step, V, delta) : 历史记录。
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    gamma = config.REWARD_DEFAULTS["gamma"] if gamma is None else gamma
    n = int(n_steps)
    V = np.zeros(n)
    delta = np.zeros(n)
    V[0] = v0
    reward = np.zeros(n)
    if reward_at is None:
        reward_at = [n - 1]
    for k in reward_at:
        reward[k] = lamb
    steps = np.arange(n)
    for i in range(n):
        r_next = reward[i]
        v_next = V[i + 1] if i + 1 < n else 0.0
        d = r_next + gamma * v_next - V[i]
        delta[i] = d
        if i + 1 < n:
            V[i + 1] = V[i] + alpha * d
    return steps, V, delta


def td_lambda(n_states=5, alpha=None, gamma=None, lam=None, lamb=1.0,
              n_episodes=300, seed=0):
    """标准 TD(λ) 状态价值学习（带资格迹）。

    场景：一条链式状态，US 仅在末端出现；学习状态值 V。

    Returns
    -------
    (episode, V_hist, delta_hist) : 每 episode 末尾状态 0 的价值与误差。
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    gamma = config.REWARD_DEFAULTS["gamma"] if gamma is None else gamma
    if lam is None:
        lam = 0.9
    from ..utils.neuro import rng
    r = rng(seed)

    V = np.zeros(n_states)
    e = np.zeros(n_states)
    V_hist = np.empty(n_episodes)
    d_hist = np.empty(n_episodes)
    for ep in range(n_episodes):
        s = 0
        e[:] = 0.0
        while True:
            s_next = min(s + 1, n_states - 1)
            r_ = lamb if s_next == n_states - 1 else 0.0
            d = r_ + gamma * V[s_next] - V[s]
            e[s] += 1.0
            V = V + alpha * d * e
            e *= gamma * lam
            if s_next == n_states - 1:
                break
            s = s_next
        V_hist[ep] = V[0]
        d_hist[ep] = d
    return np.arange(n_episodes), V_hist, d_hist


def delta_converged(delta, tol=1e-2):
    """判断 TD 误差是否收敛到 0（末 10 个均值绝对值 < tol）。"""
    tail = np.asarray(delta, dtype=float)[-10:]
    return bool(float(np.mean(np.abs(tail))) < tol)
