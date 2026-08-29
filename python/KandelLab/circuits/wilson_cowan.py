"""Wilson–Cowan 兴奋-抑制群体动力学。

核心概念 #8：皮层兴奋-抑制平衡维持网络稳定。

模型（双群体 ODE）
------------------
    τ_E · dE/dt = −E + S(w_EE·E − w_EI·I + P_E − θ_E)
    τ_I · dI/dt = −I + S(w_IE·E − w_II·I + P_I − θ_I)

其中 S(x) = 1/(1+exp(−x)) 为群体发放率 sigmoid，
w_xy 为群体间连接强度，P 为外部输入，θ 为发放阈值。

验证锚点：
    静息态不动点存在且 Jacobian 特征值实部为负（稳定）；
    强输入可把系统推到高活动（双稳态）不动点。
"""

from __future__ import annotations

import numpy as np

from .. import config
from ..utils.neuro import sigmoid, integrate_ode


class WilsonCowan:
    """Wilson-Cowan 双群体模型。默认参数来自 config。"""

    def __init__(self, **kwargs):
        p = dict(config.WILSON_COWAN_DEFAULTS)
        p.update(kwargs)
        self.tau_E = p["tau_E"]
        self.tau_I = p["tau_I"]
        self.w_EE = p["w_EE"]
        self.w_EI = p["w_EI"]
        self.w_IE = p["w_IE"]
        self.w_II = p["w_II"]
        self.theta_E = p["theta_E"]
        self.theta_I = p["theta_I"]

    def transfer(self, z):
        """sigmoid 转移函数 S(z)。"""
        return sigmoid(z, gain=1.0, threshold=0.0)

    def rates(self, E, I, P_E=0.0, P_I=0.0):
        """由活动 (E, I) 与外部输入计算驱动量并返回 (dE/dt, dI/dt)。"""
        E = np.asarray(E, dtype=float)
        I = np.asarray(I, dtype=float)
        drive_E = self.w_EE * E - self.w_EI * I + P_E - self.theta_E
        drive_I = self.w_IE * E - self.w_II * I + P_I - self.theta_I
        return self.transfer(drive_E), self.transfer(drive_I)

    def vector_field(self, y, t, P_E=0.0, P_I=0.0):
        E, I = y
        rE, rI = self.rates(E, I, P_E, P_I)
        return np.array([(-E + rE) / self.tau_E, (-I + rI) / self.tau_I])

    def simulate(self, t_max, dt=0.1, E0=0.05, I0=0.05, P_E=0.0, P_I=0.0,
                 method="euler"):
        """从初值积分相轨迹。返回 (t, E, I)。"""
        t, y = integrate_ode(self.vector_field, [E0, I0], t_max, dt, method,
                             P_E=P_E, P_I=P_I)
        return t, y[:, 0], y[:, 1]

    # -- 不动点与稳定性 -------------------------------------------------
    def _e_nullcline_I(self, E, P_E, P_I):
        """E-nullcline 上给定 E 对应的 I（闭式解）。

        E = S(w_EE·E − w_EI·I + P_E − θ_E)
        => I = (w_EE·E + P_E − θ_E − S⁻¹(E)) / w_EI
        S⁻¹(E) = ln(E/(1−E))，仅在 0 < E < 1 有定义。
        """
        E = float(E)
        if E <= 0.0 or E >= 1.0:
            return np.nan
        return (self.w_EE * E + P_E - self.theta_E
                - np.log(E / (1.0 - E))) / self.w_EI

    def _i_nullcline_I(self, E, P_E, P_I):
        """I-nullcline 上给定 E 对应的 I（单调方程，二分求解）。

        I = S(w_IE·E − w_II·I + P_I − θ_I)
        """
        def g(I):
            return I - self.transfer(self.w_IE * E - self.w_II * I
                                     + P_I - self.theta_I)
        return _bisect(g, 0.0, 1.5)

    def fixed_points(self, P_E=0.0, P_I=0.0, grid=400):
        """数值搜索不动点（零等斜线交点）。

        Returns
        -------
        list[(E, I)] : 不动点列表。
        """
        eps = 1e-4
        E_grid = np.linspace(eps, 1.0 - eps, grid)
        nullE = np.array([self._e_nullcline_I(E, P_E, P_I) for E in E_grid])
        nullI = np.array([self._i_nullcline_I(E, P_E, P_I) for E in E_grid])

        diff = nullE - nullI
        fpts = []
        for k in range(grid - 1):
            a, b = diff[k], diff[k + 1]
            if np.isnan(a) or np.isnan(b) or a * b >= 0:
                continue
            t = abs(a) / (abs(a) + abs(b))
            E_star = E_grid[k] + t * (E_grid[k + 1] - E_grid[k])
            I_star = 0.5 * (nullE[k] + nullI[k]
                            + t * (nullE[k + 1] - nullE[k]
                                   + nullI[k + 1] - nullI[k]))
            fpts.append((float(E_star), float(I_star)))
        return fpts

    def _solve_E_nullcline(self, E, P_E, P_I):
        """E-nullcline 上给定 E 的 I（兼容旧接口，闭式解）。"""
        return self._e_nullcline_I(E, P_E, P_I)

    def jacobian(self, E, I, P_E=0.0, P_I=0.0):
        """不动点处 Jacobian（关于 E, I）。"""
        sE = self.transfer(self.w_EE * E - self.w_EI * I + P_E - self.theta_E)
        sI = self.transfer(self.w_IE * E - self.w_II * I + P_I - self.theta_I)
        # sigmoid 导数 S'(z) = S(1−S)
        J = np.array([
            [(self.w_EE * sE * (1 - sE) - 1) / self.tau_E,
             (-self.w_EI * sE * (1 - sE)) / self.tau_E],
            [(self.w_IE * sI * (1 - sI)) / self.tau_I,
             (-self.w_II * sI * (1 - sI) - 1) / self.tau_I],
        ])
        return J

    def is_stable(self, E, I, P_E=0.0, P_I=0.0):
        """判断不动点是否线性稳定（Jacobian 实部全为负）。"""
        eig = np.linalg.eigvals(self.jacobian(E, I, P_E, P_I))
        return bool(np.all(eig.real < 0))

    def nullclines(self, P_E=0.0, P_I=0.0, grid=300):
        """返回零等斜线数组 (E_grid, nullE, nullI)。"""
        eps = 1e-4
        E_grid = np.linspace(eps, 1.0 - eps, grid)
        nullE = np.array([self._e_nullcline_I(E, P_E, P_I) for E in E_grid])
        nullI = np.array([self._i_nullcline_I(E, P_E, P_I) for E in E_grid])
        return E_grid, nullE, nullI


def _bisect(f, lo, hi, tol=1e-8, max_iter=200):
    """单变量零点搜索（假设 f 单调跨零）。"""
    f_lo, f_hi = f(lo), f(hi)
    if f_lo * f_hi > 0:
        return np.nan
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if abs(f_mid) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return 0.5 * (lo + hi)
