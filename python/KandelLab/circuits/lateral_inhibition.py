"""Lateral inhibition and center-surround receptive fields (Difference of Gaussians, DOG).

Core concept #7: lateral inhibition enhances sensory contrast (edge enhancement,
Mach band phenomenon).

Model
-----
    DOG kernel (center excitation − surround inhibition):
        K(r) = A_c · exp(−r² / 2σ_c²) − A_s · exp(−r² / 2σ_s²)

    Convolving an image with the DOG kernel → flat response on uniform regions,
    enhanced responses at edges.

Verification anchors:
    uniform-luminance input → output ≈ 0 (flat);
    step edge → bright/dark bands on either side of the edge (Mach bands).
"""

from __future__ import annotations

import numpy as np


def dog_1d(r, sigma_c, sigma_s, A_c=1.0, A_s=None):
    """1D DOG response. A_s defaults to A_c·(σ_s/σ_c)² to conserve volume (zero DC component)."""
    if A_s is None:
        A_s = A_c * (sigma_s / sigma_c) ** 2
    r = np.asarray(r, dtype=float)
    return A_c * np.exp(-r ** 2 / (2 * sigma_c ** 2)) \
        - A_s * np.exp(-r ** 2 / (2 * sigma_s ** 2))


def dog_kernel_2d(size, sigma_c, sigma_s, A_c=1.0):
    """2D DOG convolution kernel (zero-mean normalized)."""
    half = size // 2
    y, x = np.mgrid[-half:half + 1, -half:half + 1]
    r2 = x ** 2 + y ** 2
    center = A_c * np.exp(-r2 / (2 * sigma_c ** 2))
    surround = A_c * (sigma_c / sigma_s) ** 2 * np.exp(-r2 / (2 * sigma_s ** 2))
    kernel = center - surround
    return kernel - kernel.mean()


def apply_kernel(image, kernel):
    """Zero-padded 2D convolution (FFT-based; more stable for large kernels)."""
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    kh, kw = kernel.shape
    ih, iw = image.shape
    out_size = (ih + kh - 1, iw + kw - 1)
    fft_img = np.fft.fft2(image, s=out_size)
    fft_k = np.fft.fft2(kernel, s=out_size)
    conv = np.fft.ifft2(fft_img * fft_k).real
    # crop back to the original size ('same' semantics, including boundary padding)
    top = kh // 2
    left = kw // 2
    return conv[top:top + ih, left:left + iw]


def step_edge_image(size=(64, 128), left_value=0.2, right_value=0.8,
                    edge_col=None):
    """Build an image with a vertical step edge (for the Mach band demo)."""
    h, w = size
    img = np.full((h, w), left_value)
    if edge_col is None:
        edge_col = w // 2
    img[:, edge_col:] = right_value
    return img


def mach_bands(size=(64, 128), sigma_c=2.0, sigma_s=6.0, left=0.2, right=0.8):
    """Complete Mach band demo: returns (original image, output, DOG kernel)."""
    img = step_edge_image(size, left, right)
    kernel = dog_kernel_2d(max(3, int(size[0] * 0.3)) * 2 + 1, sigma_c, sigma_s)
    out = apply_kernel(img, kernel)
    return img, out, kernel


def lateral_inhibit(image, sigma_c=2.0, sigma_s=6.0, gain=1.0, subtract=0.0):
    """Apply lateral inhibition to an image: output = original luminance + gain·(DOG convolution − subtract).

    subtract removes the offset on uniform regions so that flat areas stay flat.
    """
    img = np.asarray(image, dtype=float)
    kernel = dog_kernel_2d(max(3, int(min(img.shape) * 0.3)) * 2 + 1,
                           sigma_c, sigma_s)
    filtered = apply_kernel(img, kernel)
    return img + gain * (filtered - subtract)
