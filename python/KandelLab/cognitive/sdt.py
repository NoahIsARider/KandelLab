"""Signal Detection Theory (SDT).

Core concept: separation of sensitivity (d′) and criterion in perceptual decisions.

Model
-----
    Noise distribution N(0, 1), signal distribution N(d′, 1).
    Decision by criterion c: respond "signal" when evidence x > c.

    d′ = z(H) − z(FA)
    c  = −½(z(H) + z(FA))
    AUC = Φ(d′/√2)

Verification anchors:
    d′=0 → ROC is the diagonal;
    shifting c → response bias (H and FA move in the same direction);
    the analytic AUC agrees with numerical integration.
"""

from __future__ import annotations

import numpy as np


# -- standard normal quantile (Acklam approximation, error < 1e-9) -------------------------
_COEF_A = [-3.969683028665376e+01, 2.209460984245205e+02,
           -2.759285104469687e+02, 1.383577518672690e+02,
           -3.066479806614716e+01, 2.506628277459239e+00]
_COEF_B = [-5.447609879822406e+01, 1.615858368580409e+02,
           -1.556989798598866e+02, 6.680131188771972e+01,
           -1.328068155288572e+01]
_COEF_C = [-7.784894002430293e-03, -3.223964580411365e-01,
           -2.400758277161838e+00, -2.549732539343734e+00,
           4.374664141464968e+00, 2.938163982698783e+00]
_COEF_D = [7.784695709041462e-03, 3.224671290700398e-01,
           2.445134137142996e+00, 3.754408661907416e+00]
_P_LOW = 0.02425


def inv_norm(p):
    """Standard normal quantile Φ⁻¹(p), 0 < p < 1."""
    p = float(p)
    if not (0.0 < p < 1.0):
        raise ValueError(f"p must lie strictly in (0, 1), got {p}")
    if p < _P_LOW:
        q = np.sqrt(-2.0 * np.log(p))
        return (((((_COEF_C[0] * q + _COEF_C[1]) * q + _COEF_C[2]) * q
                  + _COEF_C[3]) * q + _COEF_C[4]) * q + _COEF_C[5]) / (
            ((((_COEF_D[0] * q + _COEF_D[1]) * q + _COEF_D[2]) * q
              + _COEF_D[3]) * q + 1.0))
    if p > 1 - _P_LOW:
        q = np.sqrt(-2.0 * np.log(1.0 - p))
        return -(((((_COEF_C[0] * q + _COEF_C[1]) * q + _COEF_C[2]) * q
                   + _COEF_C[3]) * q + _COEF_C[4]) * q + _COEF_C[5]) / (
            ((((_COEF_D[0] * q + _COEF_D[1]) * q + _COEF_D[2]) * q
              + _COEF_D[3]) * q + 1.0))
    q = p - 0.5
    r = q * q
    return (((((_COEF_A[0] * r + _COEF_A[1]) * r + _COEF_A[2]) * r
              + _COEF_A[3]) * r + _COEF_A[4]) * r + _COEF_A[5]) * q / (
        ((((_COEF_B[0] * r + _COEF_B[1]) * r + _COEF_B[2]) * r
          + _COEF_B[3]) * r + _COEF_B[4]) * r + 1.0)


def norm_cdf(x):
    """Standard normal CDF Φ(x) (via erf)."""
    return 0.5 * (1.0 + np.vectorize(_erf)(x / np.sqrt(2.0)))


def _erf(x):
    """erf approximation (numerically accurate enough for teaching verification)."""
    # Rational approximation (Cody-style), precision ~1e-7
    x = float(x)
    sign = 1.0 if x >= 0 else -1.0
    ax = abs(x)
    t = 1.0 / (1.0 + 0.3275911 * ax)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                 - 0.284496736) * t + 0.254829592) * t * np.exp(-ax * ax)
    return sign * y


def d_prime(hit_rate, fa_rate):
    """Sensitivity d′ = z(H) − z(FA)."""
    return inv_norm(hit_rate) - inv_norm(fa_rate)


def criterion_c(hit_rate, fa_rate):
    """Criterion c = −½(z(H) + z(FA))."""
    return -0.5 * (inv_norm(hit_rate) + inv_norm(fa_rate))


def roc_curve(d=1.0, n_points=101):
    """Theoretical ROC curve of the signal-plus-noise Gaussian model.

    Returns
    -------
    (fpr, tpr) : false-positive rate and true-positive rate sequences.
    """
    c = np.linspace(3.5, -3.5, n_points)
    fa = 1.0 - norm_cdf(c)          # Φ(−c)
    hit = 1.0 - norm_cdf(c - d)     # Φ(d − c)
    return fa, hit


def auc_analytic(d):
    """Analytic AUC value Φ(d′/√2)."""
    return norm_cdf(d / np.sqrt(2.0))


def auc_numeric(fpr, tpr):
    """Numerically integrate the AUC with the trapezoidal rule."""
    fpr = np.asarray(fpr, dtype=float)
    tpr = np.asarray(tpr, dtype=float)
    return float(np.trapz(tpr, fpr))


def simulate_trials(d, n_noise=2000, n_signal=2000, seed=0):
    """Simulated trials of the Gaussian model.

    Returns
    -------
    (evidence_noise, evidence_signal)
    """
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n_noise)
    signal = rng.standard_normal(n_signal) + d
    return noise, signal


def observed_rates(noise, signal, criterion):
    """Compute (H, FA) from simulated data using criterion c."""
    hit = float(np.mean(signal > criterion))
    fa = float(np.mean(noise > criterion))
    return hit, fa
