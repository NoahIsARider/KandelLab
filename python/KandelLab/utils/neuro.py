"""KandelLab — numerical tools: integrators, spike detection, statistics and general math utilities."""

from __future__ import annotations

import numpy as np

from .. import config


def euler_step(f, y, t, dt, *args, **kwargs):
    """Single explicit Euler integration step. f(y, t, *args) -> dy/dt."""
    return y + dt * np.asarray(f(y, t, *args, **kwargs), dtype=float)


def rk4_step(f, y, t, dt, *args, **kwargs):
    """Classic RK4 single step. f(y, t, *args) -> dy/dt."""
    y = np.asarray(y, dtype=float)
    k1 = np.asarray(f(y, t, *args, **kwargs), dtype=float)
    k2 = np.asarray(f(y + 0.5 * dt * k1, t + 0.5 * dt, *args, **kwargs), dtype=float)
    k3 = np.asarray(f(y + 0.5 * dt * k2, t + 0.5 * dt, *args, **kwargs), dtype=float)
    k4 = np.asarray(f(y + dt * k3, t + dt, *args, **kwargs), dtype=float)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


INTEGRATORS = {"euler": euler_step, "rk4": rk4_step}


def integrate_ode(f, y0, t_max, dt=None, method="rk4", t0=0.0, **kwargs):
    """Numerically integrate a first-order ODE system.

    Parameters
    ----------
    f : callable
        f(y, t, **kwargs) -> dy/dt (y may be a vector or scalar).
    y0 : array_like
        Initial value.
    t_max : float
        Integration duration (same units as dt).
    dt : float | None
        Time step; None uses config.NUMERICS["default_dt"].
    method : str
        "euler" or "rk4".
    t0 : float
        Initial time.

    Returns
    -------
    t : np.ndarray  (N,)
    y : np.ndarray  (N, ...) with the same shape as y0
    """
    dt = config.NUMERICS["default_dt"] if dt is None else dt
    stepper = INTEGRATORS[method]
    y0 = np.asarray(y0, dtype=float)
    n_steps = int(np.ceil(t_max / dt))
    t = np.linspace(t0, t0 + n_steps * dt, n_steps + 1)
    y = np.empty((n_steps + 1,) + y0.shape, dtype=float)
    y[0] = y0
    for i in range(n_steps):
        y[i + 1] = stepper(f, y[i], t[i], dt, **kwargs)
    return t, y


def detect_spikes(v, v_thresh=None, dt=None, refractory_ms=0.0,
                  grad_thresh=30.0):
    """Extract spike times from a membrane-potential trace.

    Parameters
    ----------
    v : np.ndarray
        Membrane potential sequence (mV).
    v_thresh : float | None
        Detection threshold; None uses the gradient method: rising edges with
        dV/dt above grad_thresh (default 30 mV/ms) are identified as action
        potentials. The gradient method distinguishes true APs from subthreshold
        depolarizations (e.g. small pulses below the HH threshold) and also
        works for transient LIF firing.
    dt : float | None
        Sampling interval (ms); None times the spikes by index.
    refractory_ms : float
        Minimum inter-spike interval (removes detection glitches).
    grad_thresh : float
        Gradient threshold (mV/ms); used only when v_thresh is None.

    Returns
    -------
    spike_times : np.ndarray
    """
    v = np.asarray(v, dtype=float)
    if v_thresh is not None:
        above = v > v_thresh
        # trigger on rising edges
        cross = above[1:] & ~above[:-1]
        idx = np.flatnonzero(cross) + 1
    else:
        grad = np.diff(v)
        if dt is not None:
            grad = grad / dt
        rising = np.concatenate(([False], grad > grad_thresh))
        # start positions of each contiguous rising run (rising False→True)
        starts = np.flatnonzero(rising[1:] & ~rising[:-1]) + 1
        idx = starts
        # exclude falling artifacts before the rising run: require v after the start to be clearly above the start
        if idx.size:
            keep = [i for i in idx if v[i] - v[0] > grad_thresh * (dt or 1.0)]
            idx = np.asarray(keep, dtype=int)
    # refractory dedup
    if refractory_ms > 0 and dt is not None:
        keep = [idx[0]] if idx.size else []
        for j in idx[1:]:
            if (j - keep[-1]) * dt >= refractory_ms:
                keep.append(j)
        idx = np.asarray(keep, dtype=int)
    if dt is None:
        return idx.astype(float)
    return idx * dt


def firing_rate(spike_times, duration):
    """Average firing rate (Hz) from a spike-time list and observation duration."""
    spike_times = np.asarray(spike_times, dtype=float)
    return spike_times.size / float(duration) if duration > 0 else 0.0


def gaussian(x, mu, sigma):
    """Gaussian function."""
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def sigmoid(x, gain=1.0, threshold=0.0):
    """Logistic sigmoid: 1 / (1 + exp(-gain*(x-threshold)))."""
    x = np.asarray(x, dtype=float)
    z = gain * (x - threshold)
    z = np.clip(z, -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(-z))


def normalise(x, axis=None):
    """Linearly scale an array to [0, 1]."""
    x = np.asarray(x, dtype=float)
    mn = x.min(axis=axis, keepdims=True) if axis is not None else x.min()
    mx = x.max(axis=axis, keepdims=True) if axis is not None else x.max()
    span = mx - mn
    if np.all(span == 0):
        return np.zeros_like(x)
    return (x - mn) / span


def rng(seed=None):
    """Return a seeded numpy random number generator (defaults to the global config seed)."""
    if seed is None:
        seed = config.NUMERICS["seed"]
    return np.random.default_rng(int(seed))


def spike_times_to_raster(spike_times, n_trials, duration, dt=0.001):
    """Convert spike-time lists from multiple trials into a raster binary matrix (n_trials, n_bins).

    Parameters
    ----------
    spike_times : list[np.ndarray]
        Spike times of each trial.
    n_trials : int
    duration : float
    dt : float
    """
    n_bins = int(np.ceil(duration / dt))
    raster = np.zeros((n_trials, n_bins), dtype=np.uint8)
    for i, times in enumerate(spike_times[:n_trials]):
        times = np.asarray(times, dtype=float)
        bins = np.clip((times / dt).astype(int), 0, n_bins - 1)
        raster[i, bins] = 1
    return raster
