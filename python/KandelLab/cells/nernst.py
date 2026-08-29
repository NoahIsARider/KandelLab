"""Nernst equation: ionic concentration gradients determine the equilibrium potential.

Core concept #1: ionic concentration gradients across the membrane plus
selective permeability → membrane potential.

Model
-----
    E = (RT / zF) · ln([X]_o / [X]_i)

where R is the gas constant, T the absolute temperature, z the ion valence,
F the Faraday constant, and [X]_o / [X]_i the external/internal concentrations.

Textbook anchors (37 °C, Kandel standard concentrations):
    K⁺  ≈ −90 mV, Na⁺ ≈ +60 mV, Cl⁻ ≈ −90 mV, Ca²⁺ ≈ +132 mV
"""

from __future__ import annotations

import numpy as np

from .. import config


def nernst_potential(z, c_out, c_in, T=None):
    """Compute the Nernst equilibrium potential for a single ion (mV).

    Parameters
    ----------
    z : int | float
        Ion valence (K⁺/Na⁺: +1, Ca²⁺: +2, Cl⁻: −1).
    c_out, c_in : float
        External / internal concentration (mM; any consistent unit).
    T : float | None
        Absolute temperature (K); None uses the config physiological 37 °C.

    Returns
    -------
    float : equilibrium potential (mV).
    """
    if z == 0:
        raise ValueError("z must not be 0")
    if c_in <= 0 or c_out <= 0:
        raise ValueError("concentrations must be positive")
    T = config.T_KELVIN if T is None else T
    rt_f = config.R * T / config.F   # units V
    return rt_f * 1000.0 / z * np.log(c_out / c_in)


def ion_equilibrium(ion, T=None):
    """Compute the equilibrium potential of an ion using config default concentrations (mV).

    Parameters
    ----------
    ion : str
        "K" / "Na" / "Ca" / "Cl".
    """
    if ion not in config.ION_CONCENTRATIONS:
        raise KeyError(f"unknown ion: {ion}")
    spec = config.ION_CONCENTRATIONS[ion]
    return nernst_potential(spec["z"], spec["o"], spec["i"], T)


def all_equilibria(T=None):
    """Return a dict of equilibrium potentials for all ions."""
    return {ion: ion_equilibrium(ion, T) for ion in config.ION_CONCENTRATIONS}


def concentration_scan(ion, c_out_range, T=None):
    """Scan the external concentration and return (concentration array, potential array).

    Used for experiment #1: varying [K⁺]_o → observe the resting potential
    (Nernst prediction).
    """
    spec = config.ION_CONCENTRATIONS[ion]
    c_out = np.asarray(c_out_range, dtype=float)
    E = np.array([nernst_potential(spec["z"], co, spec["i"], T) for co in c_out])
    return c_out, E


def temperature_scan(c_out, c_in, z=1, T_range=(280.0, 320.0, 41)):
    """Temperature scan: returns (temperature array, potential array)."""
    T = np.linspace(T_range[0], T_range[1], T_range[2])
    E = np.array([nernst_potential(z, c_out, c_in, Ti) for Ti in T])
    return T, E
