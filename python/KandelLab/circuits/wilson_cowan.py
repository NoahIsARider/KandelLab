"""Wilson–Cowan excitatory-inhibitory population dynamics.

Core concept #8: cortical excitation-inhibition balance maintains network stability.

Model (two-population ODE)
------------------
    τ_E · dE/dt = −E + S(w_EE·E − w_EI·I + P_E − θ_E)
    τ_I · dI/dt = −I + S(w_IE·E − w_II·I + P_I − θ_I)

where S(x) = 1/(1+exp(−x)) is the population firing-rate sigmoid,
w_xy the inter-population connection strength, P the external input,
and θ the firing threshold.

Verification anchors:
    a rest fixed point exists and the Jacobian eigenvalues have negative real
    parts (stable);
    strong input can push the system to a high-activity (bistable) fixed point.
"""

from __future__ import annotations

import numpy as np

from .. import config
from ..utils.neuro import sigmoid, integrate_ode


class WilsonCowan:
    """Wilson-Cowan two-population model. Default parameters come from config."""

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
        """Sigmoid transfer function S(z)."""
        return sigmoid(z, gain=1.0, threshold=0.0)

    def rates(self, E, I, P_E=0.0, P_I=0.0):
        """Compute the drives from activities (E, I) and external input, returning (dE/dt, dI/dt)."""
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
        """Integrate the phase trajectory from initial values. Returns (t, E, I)."""
        t, y = integrate_ode(self.vector_field, [E0, I0], t_max, dt, method,
                             P_E=P_E, P_I=P_I)
        return t, y[:, 0], y[:, 1]

    # -- fixed points and stability -------------------------------------------
    def _e_nullcline_I(self, E, P_E, P_I):
        """I on the E-nullcline for a given E (closed-form solution).

        E = S(w_EE·E − w_EI·I + P_E − θ_E)
        => I = (w_EE·E + P_E − θ_E − S⁻¹(E)) / w_EI
        S⁻¹(E) = ln(E/(1−E)), defined only for 0 < E < 1.
        """
        E = float(E)
        if E <= 0.0 or E >= 1.0:
            return np.nan
        return (self.w_EE * E + P_E - self.theta_E
                - np.log(E / (1.0 - E))) / self.w_EI

    def _i_nullcline_I(self, E, P_E, P_I):
        """I on the I-nullcline for a given E (monotonic equation, solved by bisection).

        I = S(w_IE·E − w_II·I + P_I − θ_I)
        """
        def g(I):
            return I - self.transfer(self.w_IE * E - self.w_II * I
                                     + P_I - self.theta_I)
        return _bisect(g, 0.0, 1.5)

    def fixed_points(self, P_E=0.0, P_I=0.0, grid=400):
        """Numerically search for fixed points (intersections of the nullclines).

        Returns
        -------
        list[(E, I)] : list of fixed points.
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
        """I on the E-nullcline for a given E (legacy interface, closed-form solution)."""
        return self._e_nullcline_I(E, P_E, P_I)

    def jacobian(self, E, I, P_E=0.0, P_I=0.0):
        """Jacobian at a fixed point (with respect to E, I)."""
        sE = self.transfer(self.w_EE * E - self.w_EI * I + P_E - self.theta_E)
        sI = self.transfer(self.w_IE * E - self.w_II * I + P_I - self.theta_I)
        # sigmoid derivative S'(z) = S(1−S)
        J = np.array([
            [(self.w_EE * sE * (1 - sE) - 1) / self.tau_E,
             (-self.w_EI * sE * (1 - sE)) / self.tau_E],
            [(self.w_IE * sI * (1 - sI)) / self.tau_I,
             (-self.w_II * sI * (1 - sI) - 1) / self.tau_I],
        ])
        return J

    def is_stable(self, E, I, P_E=0.0, P_I=0.0):
        """Check whether a fixed point is linearly stable (all Jacobian real parts negative)."""
        eig = np.linalg.eigvals(self.jacobian(E, I, P_E, P_I))
        return bool(np.all(eig.real < 0))

    def nullclines(self, P_E=0.0, P_I=0.0, grid=300):
        """Return the nullcline arrays (E_grid, nullE, nullI)."""
        eps = 1e-4
        E_grid = np.linspace(eps, 1.0 - eps, grid)
        nullE = np.array([self._e_nullcline_I(E, P_E, P_I) for E in E_grid])
        nullI = np.array([self._i_nullcline_I(E, P_E, P_I) for E in E_grid])
        return E_grid, nullE, nullI


def _bisect(f, lo, hi, tol=1e-8, max_iter=200):
    """One-dimensional root search (assumes f is monotonic and crosses zero)."""
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
