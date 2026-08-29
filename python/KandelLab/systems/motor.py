"""VOR (vestibulo-ocular reflex) gain adaptation: cerebellar Marr–Albus error-driven learning.

Core concept #10c (motor system): motor learning is driven by error signals;
gains are adaptable.

Model
-----
    VOR gain g: eye velocity = g × head velocity. For a stationary visual target
    the ideal gain is g* = 1.

    Error (retinal slip) = velocity of the target image on the retina:
        error = g_target − g

    Gain update (Marr–Albus style):
        Δg = η · error · (signal from co-activation of parallel fibers and
                          climbing fibers)

    This implementation simplifies it to: Δg = η · (g_target − g),
    converging to the target gain.

Verification anchors:
    after training the gain converges monotonically to the target value;
    the error decays to 0.
"""

from __future__ import annotations

import numpy as np

from .. import config


def update_gain(g, error, eta=None):
    """Single gain update: Δg = η·error."""
    eta = config.VOR_DEFAULTS["eta"] if eta is None else eta
    return g + eta * error


def simulate_adaptation(n_trials=200, g0=None, target_g=None, eta=None,
                        noise=0.0, seed=0):
    """Simulate VOR gain adaptation training.

    Parameters
    ----------
    n_trials : int
    g0 : float | None
        Initial gain.
    target_g : float | None
        Target gain.
    eta : float | None
        Learning rate.
    noise : float
        Standard deviation of the gain observation noise per trial.
    seed : int

    Returns
    -------
    (trial, gain_history, error_history) : record of the training process.
    """
    p = config.VOR_DEFAULTS
    g0 = p["g0"] if g0 is None else g0
    target_g = p["target_g"] if target_g is None else target_g
    eta = p["eta"] if eta is None else eta

    rng = np.random.default_rng(seed)
    g = g0
    trials = np.arange(n_trials)
    gains = np.empty(n_trials)
    errors = np.empty(n_trials)
    for i in range(n_trials):
        error = target_g - g
        g = update_gain(g, error, eta)
        observed = g + noise * rng.standard_normal()
        gains[i] = observed
        errors[i] = error
    return trials, gains, errors


def converged_gain(gains, target_g, tol=1e-2):
    """Check whether the terminal gain has converged to the target (final 20% mean within tol of target)."""
    tail = np.asarray(gains, dtype=float)[-int(len(gains) * 0.2):]
    return bool(abs(float(np.mean(tail)) - target_g) < tol)
