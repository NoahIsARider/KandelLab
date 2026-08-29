"""群体编码：调谐曲线、Fisher 信息与 ML 解码（Cramér–Rao 界）。

核心概念：群体神经元以调谐曲线分布式编码刺激特征。

模型
----
    神经元 i 的泊松发放率调谐曲线：
        f_i(θ) = r_max · exp(−(θ − θ_i)² / (2σ²))

    Fisher 信息（泊松假设）：
        J(θ) = Σ_i  [f_i′(θ)]² / f_i(θ)

    ML 解码方差 ≥ 1/J(θ)（Cramér–Rao 界）。

验证锚点：
    噪声↑ → Fisher 信息↓ → 解码误差↑，满足 CRB。
"""

from __future__ import annotations

import numpy as np


def tuning_curves(preferred, sigma, r_max=30.0, n_points=201, theta_range=(-np.pi, np.pi)):
    """构建调谐曲线矩阵。

    Returns
    -------
    (theta, tuning) : 刺激网格 (n_points,) 与发放率 (n_points, n_neurons)。
    """
    preferred = np.asarray(preferred, dtype=float)
    theta = np.linspace(theta_range[0], theta_range[1], n_points)
    d = theta[:, None] - preferred[None, :]
    # 处理环形（角度）距离
    d = np.angle(np.exp(1j * d))
    tuning = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    return theta, tuning


def population_response(theta_stim, preferred, sigma, r_max=30.0, seed=None):
    """刺激 θ_stim 下的群体响应向量（泊松采样）。"""
    from ..utils.neuro import rng
    d = np.angle(np.exp(1j * (theta_stim - np.asarray(preferred, dtype=float))))
    rates = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    r = rng(seed)
    return r.poisson(rates)


def fisher_info(theta_stim, preferred, sigma, r_max=30.0):
    """刺激处 θ_stim 的 Fisher 信息 J(θ)（泊松假设）。"""
    pref = np.asarray(preferred, dtype=float)
    d = np.angle(np.exp(1j * (theta_stim - pref)))
    f = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    # f'(θ) = f · (−(θ−θ_i)/σ²)
    fp = f * (-d / sigma ** 2)
    return float(np.sum(fp ** 2 / (f + 1e-12)))


def cramer_rao_bound(J):
    """Cramér–Rao 界（方差下界）= 1/J。"""
    return 1.0 / J


def ml_decode(response, preferred, sigma, r_max=30.0, n_points=501,
              theta_range=(-np.pi, np.pi)):
    """最大似然解码：寻找使对数似然最大的 θ。

    Returns
    -------
    float : 解码出的刺激角度。
    """
    theta, tuning = tuning_curves(preferred, sigma, r_max, n_points, theta_range)
    # 泊松对数似然：Σ r_i·log f_i(θ) − Σ f_i(θ)（忽略常数项）
    log_like = response @ np.log(tuning + 1e-12) - tuning.sum(axis=1)
    return theta[int(np.argmax(log_like))]


def decode_error_var(theta_true, preferred, sigma, r_max, n_trials=200,
                     seed=0):
    """多次试验 ML 解码误差的方差（环形距离）。"""
    rng = np.random.default_rng(seed)
    dec = np.empty(n_trials)
    for i in range(n_trials):
        resp = population_response(theta_true, preferred, sigma, r_max,
                                   seed=int(rng.integers(0, 2 ** 31)))
        dec[i] = ml_decode(resp, preferred, sigma, r_max)
    err = np.angle(np.exp(1j * (dec - theta_true)))
    return float(np.var(err))


def noise_scan(sigmas, n_neurons=16, n_trials=150, seed=0, r_max=30.0):
    """扫描调谐宽度 σ → (Fisher 信息, 解码方差, CRB)。

    验证锚点：σ 大（噪声大）→ J 小 → 方差大。
    """
    pref = np.linspace(-np.pi, np.pi, n_neurons, endpoint=False)
    J, var, crb = [], [], []
    for s in sigmas:
        Ji = fisher_info(0.0, pref, s, r_max)
        v = decode_error_var(0.0, pref, s, r_max, n_trials, seed)
        J.append(Ji)
        var.append(v)
        crb.append(cramer_rao_bound(Ji))
    return (np.asarray(sigmas), np.asarray(J), np.asarray(var),
            np.asarray(crb))
