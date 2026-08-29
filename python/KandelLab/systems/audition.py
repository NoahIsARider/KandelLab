"""Audition: γ-tone filter bank and frequency tuning (tonotopy).

Core concept #10b: sensory systems are tuned to features (auditory frequency
selectivity).

Model
-----
    γ-tone impulse response (Patterson & Holdsworth):
        g(t) = t^(n−1) · exp(−2π·b·t) · cos(2π·f·t + φ)，t ≥ 0

    Channel bandwidth is taken as the equivalent rectangular bandwidth (ERB):
        ERB(f) = 24.7 · (4.37·f/1000 + 1)

    Channel response = energy (RMS) of the signal after channel filtering.

Verification anchors:
    for a pure tone, the channel whose characteristic frequency equals the
    stimulus frequency responds most strongly;
    channel characteristic frequencies increase monotonically along the cochlea
    (tonotopy).
"""

from __future__ import annotations

import numpy as np

from .. import config


def erb(f):
    """Equivalent rectangular bandwidth ERB(f) (Hz)."""
    f = np.asarray(f, dtype=float)
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def gammatone_impulse(t, f, order=4, bw=None, phi=0.0):
    """γ-tone impulse response g(t).

    Parameters
    ----------
    t : array_like
        Time (s).
    f : float
        Characteristic frequency (Hz).
    order : int
        γ order (n=4 is the classic value).
    bw : float | None
        Bandwidth (Hz); None uses ERB(f).
    phi : float
        Phase.
    """
    bw = erb(f) if bw is None else bw
    t = np.asarray(t, dtype=float)
    pos = t >= 0
    out = np.zeros_like(t)
    tp = t[pos]
    env = tp ** (order - 1) * np.exp(-2 * np.pi * bw * tp)
    out[pos] = env * np.cos(2 * np.pi * f * tp + phi)
    return out


def gammatone_filterbank(fmin=None, fmax=None, n_channels=None, fs=None,
                         order=None, dur=0.02):
    """Generate a γ-tone filter bank (characteristic frequencies uniformly spaced on the ERB scale).

    Returns
    -------
    (cf, filters) : characteristic-frequency array and (n, len(t)) kernel matrix.
    """
    p = config.AUDITION_DEFAULTS
    fmin = p["fmin"] if fmin is None else fmin
    fmax = p["fmax"] if fmax is None else fmax
    n = int(p["n_channels"]) if n_channels is None else int(n_channels)
    fs = p["fs"] if fs is None else fs
    order = p["order"] if order is None else order

    # ERB scale: n_channels channels with monotonically increasing ERB number
    n_erb = np.linspace(0.0, 1.0, n)
    # uniform on the ERB scale: f(i) = fmin + (fmax - fmin) * via the monotonic ERB mapping
    cf = _erb_spaced(fmin, fmax, n)
    t = np.arange(0.0, dur, 1.0 / fs)
    filters = np.array([gammatone_impulse(t, fc, order) for fc in cf])
    return cf, filters


def _erb_spaced(fmin, fmax, n):
    """Characteristic frequencies uniformly spaced on the ERB-number scale (log-like monotonic)."""
    # ERB number: 21.4·log10(4.37·f/1000 + 1)
    def num(f):
        return 21.4 * np.log10(4.37 * f / 1000.0 + 1.0)

    lo, hi = num(fmin), num(fmax)
    nums = np.linspace(lo, hi, n)
    # inverse function: f = 1000/4.37·(10^(nums/21.4) − 1)
    f = 1000.0 / 4.37 * (10.0 ** (nums / 21.4) - 1.0)
    return f


def channel_response(signal, filters, fs):
    """Response of each channel to the signal (RMS energy)."""
    signal = np.asarray(signal, dtype=float)
    return np.sqrt(np.mean(
        np.array([np.convolve(signal, f, mode="same") ** 2 for f in filters]),
        axis=1))


def pure_tone_response(f_stim, fs=None, dur=0.05, fmin=None, fmax=None,
                       n_channels=None, order=None):
    """Pure-tone stimulus → per-channel response → (cf, response).

    Verification anchor: the channel whose cf is closest to f_stim responds most.
    """
    p = config.AUDITION_DEFAULTS
    fs = p["fs"] if fs is None else fs
    dur = float(dur)
    t = np.arange(0.0, dur, 1.0 / fs)
    signal = np.sin(2 * np.pi * f_stim * t)
    cf, filters = gammatone_filterbank(fmin, fmax, n_channels, fs, order)
    resp = channel_response(signal, filters, fs)
    return cf, resp


def tonotopy_curve(f_stim_list, fs=None, dur=0.05, **fb_kwargs):
    """Scan stimulus frequencies: returns (stimulus frequencies, best channel frequencies, best responses)."""
    best = []
    for f_stim in f_stim_list:
        cf, resp = pure_tone_response(f_stim, fs, dur, **fb_kwargs)
        i = int(np.argmax(resp))
        best.append((float(f_stim), float(cf[i]), float(resp[i])))
    best = np.array(best)
    return best[:, 0], best[:, 1], best[:, 2]
