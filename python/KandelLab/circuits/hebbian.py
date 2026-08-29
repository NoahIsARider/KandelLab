"""Hebbian learning: Hebb rule, Oja normalization, BCM sliding threshold and LTP/LTD curves.

Core concept #6: synaptic strength changes with use ("neurons that fire together
wire together").

Model
-----
    Hebb rule:   Δw = η · x · y          (associates input x with output y)
    Oja rule:    Δw = η · y · (x − y·w)  (includes weight normalization, prevents divergence)
    BCM:         Δw = η · x · y · (y − θ_M)
                 dθ_M/dt = (1/τ_θ) · (y² − θ_M)   (sliding threshold)

Verification anchors:
    training on correlated inputs → selective strengthening of weights;
    BCM curve: low activity y<θ_M → LTD, high activity y>θ_M → LTP.
"""

from __future__ import annotations

import numpy as np

from .. import config


def hebb_update(w, x, y, eta=None):
    """Single-step Hebb rule: Δw = η·x·y. Returns (new weight, weight change)."""
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    dw = eta * np.asarray(x, dtype=float) * float(y)
    return np.asarray(w, dtype=float) + dw, dw


def oja_update(w, x, y, eta=None):
    """Single-step Oja rule: Δw = η·y·(x − y·w)."""
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    w = np.asarray(w, dtype=float)
    dw = eta * float(y) * (np.asarray(x, dtype=float) - float(y) * w)
    return w + dw, dw


def run_hebb(x_train, y_train, w0=None, eta=None, rule="hebb"):
    """Offline training: apply the learning rule sample by sample.

    Parameters
    ----------
    x_train : np.ndarray (T, n_in)
    y_train : np.ndarray (T,)
    w0 : np.ndarray | None
    eta : float | None
    rule : str
        "hebb" / "oja" / "bcmoja"

    Returns
    -------
    w : trained weights
    w_history : (T, n_in)
    """
    x_train = np.asarray(x_train, dtype=float)
    y_train = np.asarray(y_train, dtype=float)
    n_in = x_train.shape[1]
    w = np.zeros(n_in) if w0 is None else np.asarray(w0, dtype=float).copy()
    hist = np.empty((x_train.shape[0], n_in))
    for i, (x, y) in enumerate(zip(x_train, y_train)):
        if rule == "hebb":
            w, _ = hebb_update(w, x, y, eta)
        elif rule == "oja":
            w, _ = oja_update(w, x, y, eta)
        else:
            raise ValueError(f"unknown rule: {rule}")
        hist[i] = w
    return w, hist


def correlated_inputs(pattern, noise_level=0.1, n_samples=500, seed=None):
    """A noisy input stream around a target pattern (for directed reinforcement training)."""
    from ..utils.neuro import rng
    r = rng(seed)
    pattern = np.asarray(pattern, dtype=float)
    pattern = (pattern - pattern.mean()) / (pattern.std() + 1e-9)
    x = pattern[None, :] + noise_level * r.standard_normal(
        (n_samples, pattern.size))
    y = x @ pattern   # dot product with the pattern as output activity
    return x, y


def lt_ltp_curve(y_range=(0.0, 3.0, 201), theta_M=None, eta=None, x=1.0):
    """BCM LTD/LTP curve: output activity y → weight change Δw.

    Returns
    -------
    (y, dW) : y sequence and corresponding weight changes (η·x·y·(y−θ_M)).
    """
    eta = config.HEBBIAN_DEFAULTS["eta"] if eta is None else eta
    theta_M = config.HEBBIAN_DEFAULTS["theta_M"] if theta_M is None else theta_M
    y = np.linspace(y_range[0], y_range[1], y_range[2])
    dW = eta * x * y * (y - theta_M)
    return y, dW


class BCM:
    """BCM sliding-threshold model."""

    def __init__(self, n_in, eta=None, tau_theta=None, theta_0=0.0):
        p = config.HEBBIAN_DEFAULTS
        self.eta = p["eta"] if eta is None else eta
        self.tau_theta = p["tau_theta"] if tau_theta is None else tau_theta
        self.w = np.zeros(n_in)
        self.theta = theta_0

    def step(self, x):
        """Single-step online update. Returns (output y, weight change Δw)."""
        x = np.asarray(x, dtype=float)
        y = float(self.w @ x)
        dw = self.eta * x * y * (y - self.theta)
        self.w = self.w + dw
        self.theta = self.theta + (1.0 / self.tau_theta) * (y ** 2 - self.theta)
        return y, dw

    def train(self, x_train, y_ref=None, n_epochs=5):
        """Loop training. Returns (y_history, theta_history)."""
        x_train = np.asarray(x_train, dtype=float)
        yh, th = [], []
        for _ in range(n_epochs):
            for x in x_train:
                y, _ = self.step(x)
                yh.append(y)
                th.append(self.theta)
        return np.array(yh), np.array(th)
