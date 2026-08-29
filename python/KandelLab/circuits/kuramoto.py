"""Kuramoto 相位振荡器同步。

核心概念 #9：振荡与同步是神经节律（脑电/γ 振荡）的基础。

模型
----
    dθ_i/dt = ω_i + (K/N) · Σ_j sin(θ_j − θ_i)

序参量：
    R = |(1/N) Σ_j exp(i·θ_j)| ，衡量同步程度（0 ≤ R ≤ 1）。

验证锚点：
    K → 0 时 R ≈ 1/√N（去同步极限）；
    K → ∞ 时 R → 1（完全同步）；
    R(K) 随 K 单调上升（超临界相变）。
"""

from __future__ import annotations

import numpy as np

from .. import config


class Kuramoto:
    """Kuramoto 网络。默认参数来自 config.KURAMOTO_DEFAULTS。"""

    def __init__(self, N=None, omega_mean=None, omega_std=None, seed=None):
        p = config.KURAMOTO_DEFAULTS
        self.N = int(p["N"]) if N is None else int(N)
        omega_mean = p["omega_mean"] if omega_mean is None else omega_mean
        omega_std = p["omega_std"] if omega_std is None else omega_std
        self.rng = np.random.default_rng(seed)
        self.omega = self.rng.normal(omega_mean, omega_std, self.N)

    def vector_field(self, y, t, K):
        theta = np.asarray(y, dtype=float)
        diff = theta[None, :] - theta[:, None]   # sin(θ_j − θ_i)
        dtheta = self.omega + (K / self.N) * np.sum(np.sin(diff), axis=1)
        return dtheta

    def order_parameter(self, theta):
        """序参量 R。"""
        theta = np.asarray(theta, dtype=float)
        return float(np.abs(np.mean(np.exp(1j * theta))))

    def simulate(self, K, t_max=200.0, dt=0.01, theta0=None, burn=50.0,
                 method="euler"):
        """在耦合强度 K 下积分并返回稳态 R 及相位历史。

        Returns
        -------
        R : float （burn 之后的平均序参量）
        t : np.ndarray
        theta : np.ndarray (N_steps, N)
        R_t : np.ndarray （每一步的序参量）
        """
        from ..utils.neuro import integrate_ode
        if theta0 is None:
            theta0 = self.rng.uniform(0, 2 * np.pi, self.N)
        t, y = integrate_ode(self.vector_field, theta0, t_max, dt, method, K=K)
        R_t = np.array([self.order_parameter(row) for row in y])
        mask = t >= burn
        R = float(np.mean(R_t[mask]))
        return R, t, y, R_t

    def phase_transition(self, K_range, t_max=150.0, dt=0.01, burn=50.0,
                         seed=0):
        """扫描耦合强度 K → 平均序参量 R(K)。

        Returns
        -------
        (K, R) : 耦合强度序列与对应序参量。
        """
        rng = np.random.default_rng(seed)
        K = np.asarray(K_range, dtype=float)
        theta0 = rng.uniform(0, 2 * np.pi, self.N)
        R = np.empty_like(K)
        for i, k in enumerate(K):
            R[i], _, _, _ = self.simulate(k, t_max, dt, theta0=theta0, burn=burn)
        return K, R

    def snapshot_phases(self, K_list, t_max=100.0, dt=0.01, burn=80.0, seed=0):
        """不同耦合强度下的稳态相位分布（用于可视化）。

        Returns
        -------
        list[np.ndarray] : 每个 K 对应的相位数组。
        """
        rng = np.random.default_rng(seed)
        theta0 = rng.uniform(0, 2 * np.pi, self.N)
        out = []
        for k in K_list:
            _, _, y, _ = self.simulate(k, t_max, dt, theta0=theta0, burn=burn)
            out.append(y[-1])
        return out


def analytic_weak_coupling_r(n):
    """弱耦合（K→0）序参量的理论预测：R ≈ 1/√N。"""
    return 1.0 / np.sqrt(n)
