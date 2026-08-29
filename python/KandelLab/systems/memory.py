"""Hopfield associative memory network.

Core concept #12b: associative memory — the brain stores and retrieves patterns
distributively.

Model
-----
    Storage (Hebbian outer-product sum):
        w_ij = (1/N) · Σ_p ξᵢᵖ ξⱼᵖ ，w_ii = 0

    Update (asynchronous random, s ∈ {+1, −1}):
        sᵢ ← sign(Σ_j w_ij s_j)

    Energy function:
        E = −1/2 · Σ_ij w_ij s_i s_j  (monotonically non-increasing under updates)

Verification anchors:
    energy is monotonically non-increasing under asynchronous updates;
    corrupted patterns recover to stored attractors;
    capacity α ≈ 0.138N (measured capacity for small N < theoretical value).
"""

from __future__ import annotations

import numpy as np

from .. import config


def train(patterns):
    """Build the weight matrix via the Hebbian outer-product sum.

    Parameters
    ----------
    patterns : np.ndarray (P, N), row vectors s ∈ {±1}.

    Returns
    -------
    W : np.ndarray (N, N), with zero diagonal.
    """
    P = np.asarray(patterns, dtype=float)
    N = P.shape[1]
    W = (P.T @ P) / N
    np.fill_diagonal(W, 0.0)
    return W


def energy(W, state):
    """Energy function E = −½ Σ w_ij s_i s_j."""
    state = np.asarray(state, dtype=float)
    return -0.5 * float(state @ W @ state)


def async_update(W, state, n_steps=None, seed=None):
    """Asynchronous random-order update.

    Parameters
    ----------
    W : np.ndarray (N, N)
    state : np.ndarray (N,)
    n_steps : int | None
        Maximum number of update steps; None uses config.HOPFIELD_DEFAULTS["T_max"].
    seed : int | None

    Returns
    -------
    state : updated state
    energy_history : np.ndarray
    converged : bool
    """
    from ..utils.neuro import rng
    N = W.shape[0]
    T_max = config.HOPFIELD_DEFAULTS["T_max"] if n_steps is None else int(n_steps)
    r = rng(seed)
    state = np.asarray(state, dtype=float).copy()
    history = np.empty(T_max + 1)
    history[0] = energy(W, state)
    order = r.permutation(N)
    converged = False
    for step in range(T_max):
        i = order[step % N]
        h = float(W[i] @ state)
        new_val = 1.0 if h >= 0 else -1.0
        state[i] = new_val
        history[step + 1] = energy(W, state)
        if step > 0 and abs(history[step + 1] - history[step]) < 1e-12:
            # no change over one full pass (check a full round without flips)
            converged = True
    return state, history, converged


def recall(W, corrupted, max_steps=None, seed=None):
    """Recover a stored pattern from a corrupted state. Returns (state, energy history, converged)."""
    return async_update(W, corrupted, max_steps, seed)


def overlap(a, b):
    """Overlap of two ±1 states (normalized inner product, ∈ [−1, 1])."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(a @ b) / a.size


def random_patterns(N, n_patterns, seed=None):
    """Random set of ±1 patterns."""
    from ..utils.neuro import rng
    r = rng(seed)
    return 2.0 * (r.random((n_patterns, N)) > 0.5) - 1.0


def corrupt(pattern, flip_frac, seed=None):
    """Randomly flip a fraction of bits (corruption)."""
    from ..utils.neuro import rng
    r = rng(seed)
    mask = r.random(pattern.size) < flip_frac
    out = pattern.copy()
    out[mask] = -out[mask]
    return out


def capacity_estimate(N=128, P_range=None, n_trials=10, flip_frac=0.2,
                      seed=0):
    """Measured storage capacity: for each P, the fraction of corrupted patterns successfully recovered.

    Returns
    -------
    (P_values, success_rates) : pattern counts and recovery success rates.
    """
    if P_range is None:
        P_range = np.arange(1, max(2, int(N * 0.15)))
    rates = []
    for P in P_range:
        ok = 0
        for t in range(n_trials):
            pat = random_patterns(N, int(P), seed=seed + t)
            W = train(pat)
            # corrupt and recall each stored pattern
            all_ok = True
            for p in pat:
                c = corrupt(p, flip_frac, seed=seed + t + 7)
                rec, _, _ = recall(W, c, seed=seed + t + 3)
                if overlap(rec, p) < 0.9:
                    all_ok = False
                    break
            ok += int(all_ok)
        rates.append(ok / n_trials)
    return np.asarray(P_range), np.asarray(rates)


# ---------------------------------------------------------------------------
# Letter patterns (for visualization, 16×16 bitmaps)
# ---------------------------------------------------------------------------
_LETTER_BITS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}


def letter_bitmap(letter, size=16):
    """Generate the ±1 bitmap of a single letter (N = size×size, flattened to a vector)."""
    if letter.upper() not in _LETTER_BITS:
        raise KeyError(f"unsupported letter: {letter}")
    rows = _LETTER_BITS[letter.upper()]
    bit = np.array([[1.0 if c == "1" else -1.0 for c in r] for r in rows])
    # upscale (each pixel 2×2 → 14×10), then pad to size×size and center
    big = np.kron(bit, np.ones((2, 2)))
    h, w = big.shape
    canvas = np.full((size, size), -1.0)
    y0, x0 = (size - h) // 2, (size - w) // 2
    canvas[y0:y0 + h, x0:x0 + w] = big
    return canvas.reshape(-1)


def letters_bitmaps(letters, size=16):
    """Bitmap matrix of several letters (P, N)."""
    return np.array([letter_bitmap(L, size) for L in letters])


def reshape_square(state, size=16):
    """Reshape a flattened state into a square image (for visualization)."""
    return np.asarray(state).reshape(size, size)
