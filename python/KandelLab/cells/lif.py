"""漏电积分发放（Leaky Integrate-and-Fire, LIF）模型。

核心概念 #4：神经元以脉冲序列（频率编码）传递信息。

模型
----
    τ_m · dV/dt = −(V − E_L) + R_m · I(t)

V ≥ V_th 时发放一次并复位到 V_reset（含绝对不应期 τ_ref）。

解析发放率（恒定电流 I，V∞ = E_L + R·I）：
    f = 1 / (τ_ref + τ_m · ln((V∞ − V_reset) / (V∞ − V_th)))

验证锚点：数值模拟的 f-I 曲线与解析公式逐点吻合。
"""

from __future__ import annotations

import numpy as np

from .. import config
from ..utils.neuro import detect_spikes


class LIF:
    """LIF 神经元。默认参数来自 config.LIF_DEFAULTS。"""

    def __init__(self, **kwargs):
        p = dict(config.LIF_DEFAULTS)
        p.update(kwargs)
        self.tau_m = p["tau_m"]
        self.R_m = p["R_m"]
        self.E_L = p["E_L"]
        self.V_th = p["V_th"]
        self.V_reset = p["V_reset"]
        self.V_peak = p["V_peak"]
        self.tau_ref = p["tau_ref"]

    # -- 数值模拟 -------------------------------------------------------
    def simulate(self, I, t_max, dt=0.01, v0=None):
        """恒定/时变电流下的仿真。

        Parameters
        ----------
        I : float | np.ndarray
            恒定电流（nA）或与 t 对齐的电流序列。
        t_max : float
            时长（ms）。
        dt : float
            步长（ms）。
        v0 : float | None
            初始电位；None 用 E_L。

        Returns
        -------
        t : np.ndarray
        v : np.ndarray
        spike_times : np.ndarray
        """
        n = int(np.ceil(t_max / dt)) + 1
        t = np.arange(n) * dt
        v = np.empty(n)
        if np.isscalar(I):
            I = np.full(n, float(I))
        I = np.asarray(I, dtype=float)
        if I.ndim == 0:
            I = np.full(n, float(I))

        v[0] = self.E_L if v0 is None else v0
        spike_times = []
        ref_end = -1.0
        for i in range(n - 1):
            tt = t[i]
            if i < ref_end:
                v[i] = self.V_reset
                v[i + 1] = self.V_reset
                continue
            v_inf = self.E_L + self.R_m * I[i]
            dv = (-(v[i] - self.E_L) + self.R_m * I[i]) / self.tau_m
            v[i + 1] = v[i] + dt * dv
            if v[i + 1] >= self.V_th:
                v[i + 1] = self.V_peak
                spike_times.append(tt + dt)
                ref_end = i + 1 + int(np.ceil(self.tau_ref / dt))
        return t, v, np.array(spike_times)

    # -- 解析 -----------------------------------------------------------
    def analytical_rate(self, I):
        """恒定电流下的解析发放率（Hz）。I 低于阈时返回 0。"""
        v_inf = self.E_L + self.R_m * float(I)
        if v_inf <= self.V_th:
            return 0.0
        t_s = self.tau_m * np.log((v_inf - self.V_reset) / (v_inf - self.V_th))
        if t_s < 0:
            return 0.0
        return 1.0 / ((self.tau_ref + t_s) / 1000.0)

    def rheobase(self):
        """基强度电流（nA）：恰好使 V∞ = V_th。"""
        return (self.V_th - self.E_L) / self.R_m

    def fI_curve(self, currents, t_max=1000.0, dt=0.01, burn_ms=100.0):
        """数值 f-I 曲线（Hz），burn_ms 用于丢弃起始瞬态。"""
        I = np.asarray(currents, dtype=float)
        f_num = np.empty_like(I)
        for k, cur in enumerate(I):
            t, v, sp = self.simulate(float(cur), t_max, dt)
            sp = sp[sp >= burn_ms]
            f_num[k] = sp.size / ((t_max - burn_ms) / 1000.0)
        f_ana = np.array([self.analytical_rate(float(c)) for c in I])
        return I, f_num, f_ana


def raster_simulation(currents, n_trials=20, t_max=300.0, dt=0.01, seed=None,
                      **lif_kwargs):
    """多次试验的栅栏图模拟：返回 {电流: spike_times 列表}。

    通过在每个 trial 添加微小高斯噪声模拟响应变异性。
    """
    from ..utils.neuro import rng
    r = rng(seed)
    lif = LIF(**lif_kwargs)
    out = {}
    for cur in currents:
        trial_spikes = []
        for _ in range(n_trials):
            noisy = cur + r.normal(0.0, abs(cur) * 0.05 + 0.1)
            t, v, sp = lif.simulate(noisy, t_max, dt)
            trial_spikes.append(sp)
        out[float(cur)] = trial_spikes
    return out
