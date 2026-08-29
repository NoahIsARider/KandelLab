"""Vision: Gabor filters and orientation selectivity (simple-cell receptive fields).

Core concept #10a: sensory systems are tuned to features (visual orientation
selectivity).

Model
-----
    2D Gabor:
        g(x,y) = exp(−(x'² + γ²y'²)/(2σ²)) · cos(2π·f·x' + φ)
    where x' = x·cosθ + y·sinθ, y' = −x·sinθ + y·cosθ.

    Simple-cell response = inner product (dot product) of the receptive field
    and the image.

Verification anchors:
    the response peaks at the filter orientation θ;
    tuning-curve half-width ≈ the order of the orientation bandwidth (set by σ).
"""

from __future__ import annotations

import numpy as np

from .. import config


def gabor_2d(size=None, sf=None, sigma=None, theta=0.0, phi=None, kappa=None,
             gamma=None):
    """Generate a 2D Gabor filter kernel.

    Parameters
    ----------
    size : int
        Kernel side length (pixels).
    sf : float
        Spatial frequency (cycles/pixel).
    sigma : float
        Gaussian envelope standard deviation.
    theta : float
        Orientation (radians).
    phi : float
        Phase (radians).
    gamma : float
        Aspect ratio (γ); None uses kappa or the config default.
    """
    p = config.GABOR_DEFAULTS
    size = int(p["size"]) if size is None else int(size)
    sf = p["sf"] if sf is None else sf
    sigma = p["sigma"] if sigma is None else sigma
    phi = p["phi"] if phi is None else phi
    gamma = p["kappa"] if gamma is None else (kappa if gamma is None else gamma)

    half = (size - 1) / 2.0
    y, x = np.mgrid[0:size, 0:size].astype(float) - half
    xr = x * np.cos(theta) + y * np.sin(theta)
    yr = -x * np.sin(theta) + y * np.cos(theta)
    envelope = np.exp(-(xr ** 2 + gamma ** 2 * yr ** 2) / (2 * sigma ** 2))
    grating = np.cos(2 * np.pi * sf * xr + phi)
    kernel = envelope * grating
    return kernel - kernel.mean()


def gabor_bank(n_orientations=8, size=None, sf=None, sigma=None, phi=0.0,
               gamma=None):
    """Gabor filter bank with orientations uniformly spread over (0..π).

    Returns
    -------
    (orientations, filters) : orientation list and filter list.
    """
    thetas = np.linspace(0.0, np.pi, n_orientations, endpoint=False)
    filters = [gabor_2d(size, sf, sigma, th, phi, gamma=gamma)
               for th in thetas]
    return thetas, filters


def simple_cell_response(image, kernel):
    """Simple-cell response: inner product of image and kernel (linear filtering with absolute-value rectification)."""
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    return float(np.abs(np.sum(image * kernel)))


def orientation_tuning(image, thetas=None, filters=None, n_orientations=8,
                       **gabor_kwargs):
    """Compute the response of an image at each orientation → tuning curve.

    Returns
    -------
    (angles, responses) : orientations (radians) and responses.
    """
    if thetas is None or filters is None:
        thetas, filters = gabor_bank(n_orientations, **gabor_kwargs)
    responses = np.array([simple_cell_response(image, k) for k in filters])
    return np.asarray(thetas), responses


def tuning_halfwidth(angles, responses):
    """Tuning-curve half-width (degrees): FWHM at 1/√2 of the peak / 2.

    Locates, on either side of the peak, the angles where the response drops
    to 1/√2 of its peak via envelope interpolation, and takes half the distance
    between them.
    """
    angles = np.asarray(angles, dtype=float)
    responses = np.asarray(responses, dtype=float)
    deg = np.degrees(angles)
    resp = responses - responses.min()
    if resp.max() <= 0:
        return float("nan")
    resp = resp / resp.max()

    peak_idx = int(np.argmax(resp))
    target = 1.0 / np.sqrt(2.0)
    left = right = None

    # search left of the peak for the first interval crossing target and interpolate linearly
    for i in range(peak_idx, 0, -1):
        if min(resp[i - 1], resp[i]) <= target <= max(resp[i - 1], resp[i]):
            frac = (target - resp[i]) / (resp[i - 1] - resp[i])
            left = deg[i - 1] + frac * (deg[i] - deg[i - 1])
            break
    # search right of the peak
    for i in range(peak_idx, len(resp) - 1):
        if min(resp[i], resp[i + 1]) <= target <= max(resp[i], resp[i + 1]):
            frac = (target - resp[i]) / (resp[i + 1] - resp[i])
            right = deg[i] + frac * (deg[i + 1] - deg[i])
            break

    if left is None or right is None:
        return float("nan")
    return float(0.5 * (right - left))


def grating_image(size=(64, 64), sf=0.08, theta=np.pi / 4, phi=0.0,
                  contrast=1.0, mean=0.5):
    """Generate a sinusoidal grating image (for stimulating simple cells)."""
    h, w = size
    y, x = np.mgrid[0:h, 0:w].astype(float)
    xr = x * np.cos(theta) + y * np.sin(theta)
    return mean + contrast * mean * np.cos(2 * np.pi * sf * xr + phi)
