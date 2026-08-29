"""Kuramoto phase-oscillator synchronization.

Core concept #9: oscillation and synchronization underlie neural rhythms
(EEG / γ oscillations).

Model
-----
    dθ_i/dt = ω_i + (K/N) · Σ_j sin(θ_j − θ_i)

Order parameter:
    R = |(1/N) Σ_j exp(i·θ_j)| ，measures the degree of synchronization (0 ≤ R ≤ 1).

Verification anchors:
    K → 0: R ≈ 1/√N (desynchronized limit);
    K → ∞: R → 1 (full synchronization);
    R(K) rises monotonically with K (supercritical phase transition).
"""

from __future__ import annotations

import numpy as np

from .. import config


class Kuramoto:
    """Kuramoto network. Default parameters come from config.KURAMOTO_DEFAULTS."""

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
        """Order parameter R."""
        theta = np.asarray(theta, dtype=float)
        return float(np.abs(np.mean(np.exp(1j * theta))))

    def simulate(self, K, t_max=200.0, dt=0.01, theta0=None, burn=50.0,
                 method="euler"):
        """Integrate under coupling strength K and return the steady-state R and phase history.

        Returns
        -------
        R : float (mean order parameter after burn)
        t : np.ndarray
        theta : np.ndarray (N_steps, N)
        R_t : np.ndarray (order parameter at each step)
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
        """Scan coupling strength K → mean order parameter R(K).

        Returns
        -------
        (K, R) : coupling-strength sequence and corresponding order parameters.
        """
        rng = np.random.default_rng(seed)
        K = np.asarray(K_range, dtype=float)
        theta0 = rng.uniform(0, 2 * np.pi, self.N)
        R = np.empty_like(K)
        for i, k in enumerate(K):
            R[i], _, _, _ = self.simulate(k, t_max, dt, theta0=theta0, burn=burn)
        return K, R

    def snapshot_phases(self, K_list, t_max=100.0, dt=0.01, burn=80.0, seed=0):
        """Steady-state phase distributions at different coupling strengths (for visualization).

        Returns
        -------
        list[np.ndarray] : one phase array per K.
        """
        rng = np.random.default_rng(seed)
        theta0 = rng.uniform(0, 2 * np.pi, self.N)
        out = []
        for k in K_list:
            _, _, y, _ = self.simulate(k, t_max, dt, theta0=theta0, burn=burn)
            out.append(y[-1])
        return out


def analytic_weak_coupling_r(n):
    """Theoretical prediction of the order parameter under weak coupling (K→0): R ≈ 1/√N."""
    return 1.0 / np.sqrt(n)
