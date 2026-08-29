"""Hodgkin–Huxley（HH）模型：动作电位的电压门控离子通道动力学。

核心概念 #3：动作电位是电压门控 Na⁺/K⁺ 通道的协同动力学产物。

模型（经典 4 变量 ODE，HH 1952，单位 mV / ms / µA/cm²）
------------------------------------------------------
    C_m · dV/dt = −(g_Na·m³·h·(V−E_Na) + g_K·n⁴·(V−E_K) + g_L·(V−E_L)) + I_ext
    dm/dt = α_m(V)(1−m) − β_m(V)·m          （Na 激活）
    dh/dt = α_h(V)(1−h) − β_h(V)·h          （Na 失活）
    dn/dt = α_n(V)(1−n) − β_n(V)·n          （K 激活）

门控速率函数（V 以 mV 计，经典取值）：
    α_m = 0.1(V+40)/(1−exp(−(V+40)/10))      β_m = 4·exp(−(V+65)/18)
    α_h = 0.07·exp(−(V+65)/20)               β_h = 1/(1+exp(−(V+35)/10))
    α_n = 0.01(V+55)/(1−exp(−(V+55)/10))     β_n = 0.125·exp(−(V+65)/80)

验证锚点：静息 ≈ −65 mV、峰 ≈ +35 mV、阈值 ≈ −55 mV、绝对不应期 ≈ 2 ms。
"""

from __future__ import annotations

import numpy as np

from .. import config
from ..utils.neuro import integrate_ode, detect_spikes


# ---------------------------------------------------------------------------
# 门控速率函数
# ---------------------------------------------------------------------------
def alpha_m(v):
    v = np.asarray(v, dtype=float)
    z = (v + 40.0) / 10.0
    with np.errstate(over="ignore", invalid="ignore"):
        denom = 1.0 - np.exp(-z)
    zz = np.where(np.abs(z) < 1e-8, 1e-8, z)   # z→0 极限 = 1
    out = zz / denom
    return np.where(np.isfinite(out), out, 0.0)


def beta_m(v):
    return 4.0 * np.exp(-(np.asarray(v, dtype=float) + 65.0) / 18.0)


def alpha_h(v):
    return 0.07 * np.exp(-(np.asarray(v, dtype=float) + 65.0) / 20.0)


def beta_h(v):
    v = np.asarray(v, dtype=float)
    return 1.0 / (1.0 + np.exp(-(v + 35.0) / 10.0))


def alpha_n(v):
    v = np.asarray(v, dtype=float)
    z = (v + 55.0) / 10.0
    with np.errstate(over="ignore", invalid="ignore"):
        denom = 1.0 - np.exp(-z)
    zz = np.where(np.abs(z) < 1e-8, 1e-8, z)   # z→0 极限 = 0.1
    out = 0.1 * zz / denom
    return np.where(np.isfinite(out), out, 0.0)


def beta_n(v):
    return 0.125 * np.exp(-(np.asarray(v, dtype=float) + 65.0) / 80.0)


def gate_steady_state(v):
    """各门控的稳态值（m∞, h∞, n∞）与时间常数。"""
    v = np.asarray(v, dtype=float)
    a_m, b_m = alpha_m(v), beta_m(v)
    a_h, b_h = alpha_h(v), beta_h(v)
    a_n, b_n = alpha_n(v), beta_n(v)
    return {
        "m_inf": a_m / (a_m + b_m),
        "h_inf": a_h / (a_h + b_h),
        "n_inf": a_n / (a_n + b_n),
        "tau_m": 1.0 / (a_m + b_m),
        "tau_h": 1.0 / (a_h + b_h),
        "tau_n": 1.0 / (a_n + b_n),
    }


# ---------------------------------------------------------------------------
# HH 动力学
# ---------------------------------------------------------------------------
class HodgkinHuxley:
    """HH 模型封装。默认参数来自 config.HH_DEFAULTS。"""

    def __init__(self, **kwargs):
        p = dict(config.HH_DEFAULTS)
        p.update(kwargs)
        self.C_m = p["C_m"]
        self.g_Na = p["g_Na"]
        self.g_K = p["g_K"]
        self.g_L = p["g_L"]
        self.E_Na = p["E_Na"]
        self.E_K = p["E_K"]
        self.E_L = p["E_L"]
        self.V_rest = p["V_rest"]

    # -- 门控动力学（供 integrate_ode 使用的向量场） -------------------
    def dvdt(self, v, m, h, n, i_ext):
        i_na = self.g_Na * m ** 3 * h * (v - self.E_Na)
        i_k = self.g_K * n ** 4 * (v - self.E_K)
        i_l = self.g_L * (v - self.E_L)
        return (-(i_na + i_k + i_l) + i_ext) / self.C_m

    def vector_field(self, y, t, i_ext_fn=None):
        v, m, h, n = y
        i_ext = 0.0 if i_ext_fn is None else i_ext_fn(t)
        dm = alpha_m(v) * (1.0 - m) - beta_m(v) * m
        dh = alpha_h(v) * (1.0 - h) - beta_h(v) * h
        dn = alpha_n(v) * (1.0 - n) - beta_n(v) * n
        return np.array([self.dvdt(v, m, h, n, i_ext), dm, dh, dn])

    def initial_state(self):
        g = gate_steady_state(self.V_rest)
        return np.array([self.V_rest, g["m_inf"], g["h_inf"], g["n_inf"]])

    def simulate(self, t_max, dt=None, i_ext_fn=None, v0=None, method="rk4"):
        """模拟 HH 模型。

        Parameters
        ----------
        t_max : float
            仿真时长（ms）。
        dt : float | None
            时间步长。
        i_ext_fn : callable | None
            i_ext(t) 返回注入电流密度（µA/cm²）。
        v0 : array_like | None
            初值 [V, m, h, n]；None 用静息稳态。
        method : str
            "rk4" / "euler"。

        Returns
        -------
        t : np.ndarray
        y : np.ndarray (N, 4)，列为 V, m, h, n
        """
        y0 = self.initial_state() if v0 is None else np.asarray(v0, dtype=float)
        t, y = integrate_ode(self.vector_field, y0, t_max, dt, method,
                             i_ext_fn=i_ext_fn)
        return t, y

    def spikes(self, t, y, v_thresh=None, refractory_ms=1.0):
        v = y[:, 0]
        dt = t[1] - t[0]
        return detect_spikes(v, v_thresh, dt, refractory_ms)

    def fI_curve(self, currents, t_max=120.0, dt=0.01, t_stim=(10.0, 110.0),
                 method="rk4"):
        """不同注入电流下的发放率（Hz）。电流为恒定阶跃。

        Returns
        -------
        (I, f) : 电流序列与发放率序列。
        """
        I = np.asarray(currents, dtype=float)
        f = np.empty_like(I)
        for i, cur in enumerate(I):
            def i_ext_fn(tt):
                return cur if t_stim[0] <= tt <= t_stim[1] else 0.0
            t, y = self.simulate(t_max, dt, i_ext_fn=i_ext_fn, method=method)
            spikes = self.spikes(t, y)
            duration = t_stim[1] - t_stim[0]
            spikes = spikes[(spikes >= t_stim[0]) & (spikes <= t_stim[1])]
            f[i] = spikes.size / (duration / 1000.0)
        return I, f


def threshold_finder(hh, t_max=60.0, dt=0.01, amp_scan=(0.0, 12.0, 40),
                     pulse_ms=1.0, t_on=5.0, amp_tol=0.01):
    """用脉冲电流扫描确定发放阈值（mV）。

    做法：在静息电位基础上给一个短促电流脉冲，二分搜索临界电流幅度
    （恰好触发动作电位的注入电流），返回临界电流下亚阈值响应的
    峰值膜电位，作为阈值电压估计。对经典 HH 参数应 ≈ −55 mV。

    amp_tol : float
        二分搜索的电流精度（mV）；防止过度逼近临界点导致
        亚阈值峰值被 RK4 数值误差放大。
    """
    lo, hi = amp_scan[0], amp_scan[1]
    v_peak_sub = None
    for _ in range(amp_scan[2]):
        mid = 0.5 * (lo + hi)

        def i_ext_fn(tt):
            return mid if t_on <= tt <= t_on + pulse_ms else 0.0

        t, y = hh.simulate(t_max, dt, i_ext_fn=i_ext_fn, method="rk4")
        sp = hh.spikes(t, y, refractory_ms=0.5)
        has_spike = sp.size > 0
        if has_spike:
            hi = mid
        else:
            v_peak_sub = float(y[:, 0].max())
            lo = mid
        if hi - lo < amp_tol:
            break
    return v_peak_sub if v_peak_sub is not None else 0.5 * (lo + hi)


def step_current(amp, t_on=5.0, t_off=np.inf):
    """构造阶跃电流函数 i_ext(t)，在 [t_on, t_off) 注入恒定 amp。"""

    def fn(t):
        return amp if t_on <= t < t_off else 0.0

    return fn
