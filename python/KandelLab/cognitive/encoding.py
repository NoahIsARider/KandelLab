"""Population coding: tuning curves, Fisher information and ML decoding (Cramér–Rao bound).

Core concept: populations of neurons encode stimulus features distributively
via tuning curves.

Model
-----
    Poisson firing-rate tuning curve of neuron i:
        f_i(θ) = r_max · exp(−(θ − θ_i)² / (2σ²))

    Fisher information (Poisson assumption):
        J(θ) = Σ_i  [f_i′(θ)]² / f_i(θ)

    ML decoding variance ≥ 1/J(θ) (Cramér–Rao bound).

Verification anchors:
    noise↑ → Fisher information↓ → decoding error↑, satisfying the CRB.
"""

from __future__ import annotations

import numpy as np


def tuning_curves(preferred, sigma, r_max=30.0, n_points=201, theta_range=(-np.pi, np.pi)):
    """Build the tuning-curve matrix.

    Returns
    -------
    (theta, tuning) : stimulus grid (n_points,) and firing rates (n_points, n_neurons).
    """
    preferred = np.asarray(preferred, dtype=float)
    theta = np.linspace(theta_range[0], theta_range[1], n_points)
    d = theta[:, None] - preferred[None, :]
    # handle circular (angular) distance
    d = np.angle(np.exp(1j * d))
    tuning = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    return theta, tuning


def population_response(theta_stim, preferred, sigma, r_max=30.0, seed=None):
    """Population response vector to stimulus θ_stim (Poisson sampling)."""
    from ..utils.neuro import rng
    d = np.angle(np.exp(1j * (theta_stim - np.asarray(preferred, dtype=float))))
    rates = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    r = rng(seed)
    return r.poisson(rates)


def fisher_info(theta_stim, preferred, sigma, r_max=30.0):
    """Fisher information J(θ) at stimulus θ_stim (Poisson assumption)."""
    pref = np.asarray(preferred, dtype=float)
    d = np.angle(np.exp(1j * (theta_stim - pref)))
    f = r_max * np.exp(-(d ** 2) / (2 * sigma ** 2))
    # f'(θ) = f · (−(θ−θ_i)/σ²)
    fp = f * (-d / sigma ** 2)
    return float(np.sum(fp ** 2 / (f + 1e-12)))


def cramer_rao_bound(J):
    """Cramér–Rao bound (variance lower bound) = 1/J."""
    return 1.0 / J


def ml_decode(response, preferred, sigma, r_max=30.0, n_points=501,
              theta_range=(-np.pi, np.pi)):
    """Maximum-likelihood decoding: find the θ maximizing the log-likelihood.

    Returns
    -------
    float : decoded stimulus angle.
    """
    theta, tuning = tuning_curves(preferred, sigma, r_max, n_points, theta_range)
    # Poisson log-likelihood: Σ r_i·log f_i(θ) − Σ f_i(θ) (constant terms ignored)
    log_like = response @ np.log(tuning + 1e-12) - tuning.sum(axis=1)
    return theta[int(np.argmax(log_like))]


def decode_error_var(theta_true, preferred, sigma, r_max, n_trials=200,
                     seed=0):
    """Variance of the ML decoding error over multiple trials (circular distance)."""
    rng = np.random.default_rng(seed)
    dec = np.empty(n_trials)
    for i in range(n_trials):
        resp = population_response(theta_true, preferred, sigma, r_max,
                                   seed=int(rng.integers(0, 2 ** 31)))
        dec[i] = ml_decode(resp, preferred, sigma, r_max)
    err = np.angle(np.exp(1j * (dec - theta_true)))
    return float(np.var(err))


def noise_scan(sigmas, n_neurons=16, n_trials=150, seed=0, r_max=30.0):
    """Scan tuning width σ → (Fisher information, decoding variance, CRB).

    Verification anchor: large σ (high noise) → small J → large variance.
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
