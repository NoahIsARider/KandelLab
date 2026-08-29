"""Synapse models: EPSP / IPSP and temporal & spatial summation.

Core concept #5: synaptic inputs integrate over time and space to determine
whether a neuron fires.

Model
-----
    PSP(t) = w · (t/τ) · exp(−t/τ)          (α function, t ≥ 0)

Responses to multiple synaptic events add linearly (approximately valid in the
subthreshold regime):
    V(t) = Σ_i  w_i · PSP(t − t_i)

Verification anchors:
    temporal summation: short ISI → double-pulse peak > single-pulse peak;
    spatial summation: many simultaneous inputs → amplitude grows roughly
    linearly with the number of inputs.
"""

from __future__ import annotations

import numpy as np

from .. import config


def psp_alpha(t, w=1.0, tau=None):
    """α-function postsynaptic potential.

    Parameters
    ----------
    t : array_like
        Time (ms).
    w : float
        Synaptic weight (amplitude; pass a negative value for IPSPs).
    tau : float | None
        Time constant (ms); None uses config.SYNAPSE_DEFAULTS["tau_decay"].

    Returns
    -------
    np.ndarray
    """
    tau = config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    pos = t >= 0
    out[pos] = w * (t[pos] / tau) * np.exp(-t[pos] / tau)
    return out


def psp_alpha_peak(w, tau):
    """Peak amplitude of the α function (normalized to w)."""
    return w * np.exp(-1.0)


def psp_peak_time(tau):
    """Time at which the α function reaches its peak (ms)."""
    return tau


def simulate_psp(spike_times, t, w=1.0, tau=None):
    """Temporal summation (linear superposition) of multiple spikes of a single input.

    Parameters
    ----------
    spike_times : array_like
        Spike times (ms).
    t : array_like
        Observation time grid (ms).
    w, tau : float
        Weight and time constant.

    Returns
    -------
    np.ndarray : V(t)
    """
    t = np.asarray(t, dtype=float)
    v = np.zeros_like(t)
    for st in np.atleast_1d(spike_times):
        v = v + psp_alpha(t - st, w, tau)
    return v


def temporal_sum_peak(isi, w=1.0, tau=None, dt=0.01):
    """Peak potential after temporal summation of two pulses separated by ISI.

    Returns
    -------
    float : summed peak (mV).
    """
    tau = config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau
    t = np.arange(0.0, max(8 * tau, isi + 6 * tau), dt)
    v = simulate_psp([0.0, isi], t, w, tau)
    return float(v.max())


def temporal_sum_scan(isis, w=1.0, tau=None, dt=0.01):
    """Scan the two-pulse interval: returns (ISI sequence, peak sequence, single-pulse peak)."""
    isis = np.asarray(isis, dtype=float)
    single = psp_alpha_peak(w, config.SYNAPSE_DEFAULTS["tau_decay"] if tau is None else tau)
    peaks = np.array([temporal_sum_peak(isi, w, tau, dt) for isi in isis])
    return isis, peaks, single


def spatial_sum(spike_times_list, t, weights=None, taus=None):
    """Spatial summation over multiple inputs (one spike-time sequence per input).

    Parameters
    ----------
    spike_times_list : list[array_like]
        Spike times for each input.
    t : array_like
        Time grid.
    weights : list[float] | None
        Weight of each input; None gives all weights 1.
    taus : list[float] | None
        Time constant of each input; None uses the default for all.

    Returns
    -------
    np.ndarray : V(t)
    """
    n_in = len(spike_times_list)
    if weights is None:
        weights = [1.0] * n_in
    if taus is None:
        taus = [None] * n_in
    t = np.asarray(t, dtype=float)
    v = np.zeros_like(t)
    for spikes, w, tau in zip(spike_times_list, weights, taus):
        v = v + simulate_psp(spikes, t, w, tau)
    return v


def spatial_sum_peak(spike_times_list, t, weights=None, taus=None):
    """Peak after spatial summation over multiple inputs."""
    return float(spatial_sum(spike_times_list, t, weights, taus).max())


def isi_to_firing(isi):
    """Convert an inter-spike interval (ms) to a firing rate (Hz)."""
    return 1000.0 / float(isi) if isi > 0 else np.inf
