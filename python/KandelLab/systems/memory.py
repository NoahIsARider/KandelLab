"""Hopfield 联想记忆网络。

核心概念 #12b：联想记忆 —— 大脑以分布式方式存储并恢复模式。

模型
----
    存储（Hebbian 外积和）：
        w_ij = (1/N) · Σ_p ξᵢᵖ ξⱼᵖ ，w_ii = 0

    更新（异步随机，s ∈ {+1, −1}）：
        sᵢ ← sign(Σ_j w_ij s_j)

    能量函数：
        E = −1/2 · Σ_ij w_ij s_i s_j  （随更新单调不增）

验证锚点：
    能量随异步更新单调不增；
    损坏的模式能恢复到存储的吸引子；
    容量 α ≈ 0.138N（小 N 实测容量 < 理论值）。
"""

from __future__ import annotations

import numpy as np

from .. import config


def train(patterns):
    """Hebbian 外积和构造权重矩阵。

    Parameters
    ----------
    patterns : np.ndarray (P, N)，行向量 s ∈ {±1}。

    Returns
    -------
    W : np.ndarray (N, N)，对角置零。
    """
    P = np.asarray(patterns, dtype=float)
    N = P.shape[1]
    W = (P.T @ P) / N
    np.fill_diagonal(W, 0.0)
    return W


def energy(W, state):
    """能量函数 E = −½ Σ w_ij s_i s_j。"""
    state = np.asarray(state, dtype=float)
    return -0.5 * float(state @ W @ state)


def async_update(W, state, n_steps=None, seed=None):
    """异步随机顺序更新。

    Parameters
    ----------
    W : np.ndarray (N, N)
    state : np.ndarray (N,)
    n_steps : int | None
        最大更新步数；None 用 config.HOPFIELD_DEFAULTS["T_max"]。
    seed : int | None

    Returns
    -------
    state : 更新后的状态
    energy_history : np.ndarray
    converged : bool
    """
    from ..utils.neuro import rng
    N = W.shape[0]
    T_max = config.HOPFIELD_DEFAULTS["T_max"] if n_steps is None else int(n_steps)
    r = rng(seed)
    state = np.asarray(state, dtype=float).copy()
    history = np.empty(T_max + 1)
    history[0] = energy(W, state)
    order = r.permutation(N)
    converged = False
    for step in range(T_max):
        i = order[step % N]
        h = float(W[i] @ state)
        new_val = 1.0 if h >= 0 else -1.0
        state[i] = new_val
        history[step + 1] = energy(W, state)
        if step > 0 and abs(history[step + 1] - history[step]) < 1e-12:
            # 一轮未改变（检查一整轮无翻转）
            converged = True
    return state, history, converged


def recall(W, corrupted, max_steps=None, seed=None):
    """从损坏状态恢复存储模式。返回 (状态, 能量历史, 是否收敛)。"""
    return async_update(W, corrupted, max_steps, seed)


def overlap(a, b):
    """两个 ±1 状态的重叠度（归一化内积，∈ [−1, 1]）。"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(a @ b) / a.size


def random_patterns(N, n_patterns, seed=None):
    """随机 ±1 模式集。"""
    from ..utils.neuro import rng
    r = rng(seed)
    return 2.0 * (r.random((n_patterns, N)) > 0.5) - 1.0


def corrupt(pattern, flip_frac, seed=None):
    """按比例随机翻转位（损坏）。"""
    from ..utils.neuro import rng
    r = rng(seed)
    mask = r.random(pattern.size) < flip_frac
    out = pattern.copy()
    out[mask] = -out[mask]
    return out


def capacity_estimate(N=128, P_range=None, n_trials=10, flip_frac=0.2,
                      seed=0):
    """实测存储容量：对每个 P，统计损坏模式成功恢复的比例。

    Returns
    -------
    (P_values, success_rates) : 模式数与恢复成功率。
    """
    if P_range is None:
        P_range = np.arange(1, max(2, int(N * 0.15)))
    rates = []
    for P in P_range:
        ok = 0
        for t in range(n_trials):
            pat = random_patterns(N, int(P), seed=seed + t)
            W = train(pat)
            # 对每个存储模式损坏后召回
            all_ok = True
            for p in pat:
                c = corrupt(p, flip_frac, seed=seed + t + 7)
                rec, _, _ = recall(W, c, seed=seed + t + 3)
                if overlap(rec, p) < 0.9:
                    all_ok = False
                    break
            ok += int(all_ok)
        rates.append(ok / n_trials)
    return np.asarray(P_range), np.asarray(rates)


# ---------------------------------------------------------------------------
# 字母模式（可视化用，16×16 位图）
# ---------------------------------------------------------------------------
_LETTER_BITS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


def letter_bitmap(letter, size=16):
    """生成单个字母的 ±1 位图（N = size×size，展平为向量）。"""
    if letter.upper() not in _LETTER_BITS:
        raise KeyError(f"不支持的字幕: {letter}")
    rows = _LETTER_BITS[letter.upper()]
    bit = np.array([[1.0 if c == "1" else -1.0 for c in r] for r in rows])
    # 放大（每像素 2×2 → 14×10），再 pad 到 size×size 居中
    big = np.kron(bit, np.ones((2, 2)))
    h, w = big.shape
    canvas = np.full((size, size), -1.0)
    y0, x0 = (size - h) // 2, (size - w) // 2
    canvas[y0:y0 + h, x0:x0 + w] = big
    return canvas.reshape(-1)


def letters_bitmaps(letters, size=16):
    """多个字母的位图矩阵（P, N）。"""
    return np.array([letter_bitmap(L, size) for L in letters])


def reshape_square(state, size=16):
    """把展平状态重塑为方形图像（可视化）。"""
    return np.asarray(state).reshape(size, size)
