"""Reward learning: Rescorla–Wagner and TD(λ) temporal difference.

Core concept #11: learning depends on reward prediction errors (dopamine signal).

Model
-----
    Rescorla–Wagner: ΔV = α·(λ − V)
        expected value V gradually approaches the reward λ; a learned CS blocks
        learning about new cues.

    TD prediction error: δ = r + γ·V(s') − V(s)
        dopamine-like signal; after convergence δ → 0.

Verification anchors:
    conditioning V converges monotonically and asymptotically to λ;
    blocking: after learning A+ first, B acquires almost no value during AB+;
    TD: the error δ decays to 0 with learning.
"""

from __future__ import annotations

import numpy as np

from .. import config


def rescorla_wagner(alpha=None, lamb=1.0, n_trials=200, v0=0.0, reward=None):
    """Rescorla–Wagner conditioning learning.

    Parameters
    ----------
    alpha : float | None
        Learning rate.
    lamb : float
        Reward intensity (unconditioned stimulus, US).
    n_trials : int
        Number of trials.
    v0 : float
        Initial expected value.

    Returns
    -------
    (trial, V) : trial indices and expected-value history.
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    lamb = float(lamb)
    V = v0
    trials = np.arange(1, n_trials + 1)
    hist = np.empty(n_trials)
    for i in range(n_trials):
        delta = (lamb if reward is None else reward[i]) - V
        V = V + alpha * delta
        hist[i] = V
    return trials, hist


def blocking_experiment(alpha=None, lamb=1.0, n1=200, n2=200, v0=0.0):
    """Blocking-effect experiment.

    Phase 1: A+ paired alone with reward (V_A → λ).
    Phase 2: AB+ compound stimulus (V_A already saturated, learning about V_B
    is blocked).

    Returns
    -------
    (trial, V_A, V_B) : trial indices and expected values of both cues.
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    VA, VB = v0, v0
    trials = np.arange(1, n1 + n2 + 1)
    ha, hb = np.empty(n1 + n2), np.empty(n1 + n2)
    for i in range(n1):
        delta = lamb - VA
        VA = VA + alpha * delta
        ha[i], hb[i] = VA, VB
    for i in range(n2):
        total = VA + VB
        delta = lamb - total
        VA = VA + alpha * delta
        VB = VB + alpha * delta
        ha[n1 + i], hb[n1 + i] = VA, VB
    return trials, ha, hb


def td_sequence(alpha=None, gamma=None, lamb=1.0, n_steps=40, v0=0.0,
                reward_at=None):
    """TD learning trajectory for a single CS→US temporal sequence.

    At each time step: prediction error δ = reward + γ·V_next − V,
    updating V (here the value of the single-state CS predicting the value
    before US arrival).

    Returns
    -------
    (step, V, delta) : history records.
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    gamma = config.REWARD_DEFAULTS["gamma"] if gamma is None else gamma
    n = int(n_steps)
    V = np.zeros(n)
    delta = np.zeros(n)
    V[0] = v0
    reward = np.zeros(n)
    if reward_at is None:
        reward_at = [n - 1]
    for k in reward_at:
        reward[k] = lamb
    steps = np.arange(n)
    for i in range(n):
        r_next = reward[i]
        v_next = V[i + 1] if i + 1 < n else 0.0
        d = r_next + gamma * v_next - V[i]
        delta[i] = d
        if i + 1 < n:
            V[i + 1] = V[i] + alpha * d
    return steps, V, delta


def td_lambda(n_states=5, alpha=None, gamma=None, lam=None, lamb=1.0,
              n_episodes=300, seed=0):
    """Standard TD(λ) state-value learning (with eligibility traces).

    Scenario: a chain of states, US appears only at the end; learns state values V.

    Returns
    -------
    (episode, V_hist, delta_hist) : value and error of state 0 at the end of each episode.
    """
    alpha = config.REWARD_DEFAULTS["alpha"] if alpha is None else alpha
    gamma = config.REWARD_DEFAULTS["gamma"] if gamma is None else gamma
    if lam is None:
        lam = 0.9
    from ..utils.neuro import rng
    r = rng(seed)

    V = np.zeros(n_states)
    e = np.zeros(n_states)
    V_hist = np.empty(n_episodes)
    d_hist = np.empty(n_episodes)
    for ep in range(n_episodes):
        s = 0
        e[:] = 0.0
        while True:
            s_next = min(s + 1, n_states - 1)
            r_ = lamb if s_next == n_states - 1 else 0.0
            d = r_ + gamma * V[s_next] - V[s]
            e[s] += 1.0
            V = V + alpha * d * e
            e *= gamma * lam
            if s_next == n_states - 1:
                break
            s = s_next
        V_hist[ep] = V[0]
        d_hist[ep] = d
    return np.arange(n_episodes), V_hist, d_hist


def delta_converged(delta, tol=1e-2):
    """Check whether the TD error has converged to 0 (mean abs of last 10 < tol)."""
    tail = np.asarray(delta, dtype=float)[-10:]
    return bool(float(np.mean(np.abs(tail))) < tol)
