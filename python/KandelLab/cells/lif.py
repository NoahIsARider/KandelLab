"""Leaky Integrate-and-Fire (LIF) model.

Core concept #4: neurons transmit information as spike trains (rate coding).

Model
-----
    τ_m · dV/dt = −(V − E_L) + R_m · I(t)

When V ≥ V_th the neuron fires and resets to V_reset (with absolute refractory
period τ_ref).

Analytic firing rate (constant current I, V∞ = E_L + R·I):
    f = 1 / (τ_ref + τ_m · ln((V∞ − V_reset) / (V∞ − V_th)))

Verification anchor: the numerically simulated f-I curve matches the analytic
formula point by point.
"""

from __future__ import annotations

import numpy as np

from .. import config
from ..utils.neuro import detect_spikes


class LIF:
    """LIF neuron. Default parameters come from config.LIF_DEFAULTS."""

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

    # -- numerical simulation -------------------------------------------------------
    def simulate(self, I, t_max, dt=0.01, v0=None):
        """Simulate under constant or time-varying current.

        Parameters
        ----------
        I : float | np.ndarray
            Constant current (nA) or a current sequence aligned with t.
        t_max : float
            Duration (ms).
        dt : float
            Time step (ms).
        v0 : float | None
            Initial potential; None uses E_L.

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

    # -- analytic -----------------------------------------------------------
    def analytical_rate(self, I):
        """Analytic firing rate (Hz) under constant current. Returns 0 when I is subthreshold."""
        v_inf = self.E_L + self.R_m * float(I)
        if v_inf <= self.V_th:
            return 0.0
        t_s = self.tau_m * np.log((v_inf - self.V_reset) / (v_inf - self.V_th))
        if t_s < 0:
            return 0.0
        return 1.0 / ((self.tau_ref + t_s) / 1000.0)

    def rheobase(self):
        """Rheobase current (nA): the current that makes V∞ = V_th exactly."""
        return (self.V_th - self.E_L) / self.R_m

    def fI_curve(self, currents, t_max=1000.0, dt=0.01, burn_ms=100.0):
        """Numerical f-I curve (Hz); burn_ms discards the initial transient."""
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
    """Multi-trial raster simulation: returns {current: list of spike_times}.

    Response variability is mimicked by adding small Gaussian noise to each trial.
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
