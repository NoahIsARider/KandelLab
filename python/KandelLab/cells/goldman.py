"""Goldman–Hodgkin–Katz (GHK) equation: permeability-weighted resting potential.

Core concept #2: the resting potential is jointly determined by the relative
permeabilities of multiple ions.

Model
-----
    V = (RT/F) · ln((P_K[K]_o + P_Na[Na]_o + P_Cl[Cl]_i)
                  / (P_K[K]_i + P_Na[Na]_i + P_Cl[Cl]_o))

P_X is the relative permeability; Cl⁻ is swapped between in/out because of its
−1 valence.

Verification anchors:
    single-ion limit (all other P = 0) → reduces to the Nernst equation;
    resting potential under physiological permeabilities ≈ −70 mV.
"""

from __future__ import annotations

import numpy as np

from .. import config


def goldman_voltage(permeabilities, c_out, c_in, T=None, z=None):
    """Compute the resting potential with the GHK equation (mV).

    Parameters
    ----------
    permeabilities : dict[str, float]
        {"K": P_K, "Na": P_Na, "Cl": P_Cl, ...}, values are relative permeabilities.
    c_out, c_in : dict[str, float]
        {"K": …, "Na": …, "Cl": …} external/internal concentrations (mM).
    T : float | None
        Absolute temperature (K).
    z : dict[str, int] | None
        Valence of each ion; None uses the valences in config.ION_CONCENTRATIONS.

    Returns
    -------
    float : resting potential (mV).
    """
    T = config.T_KELVIN if T is None else T
    rt_f = config.R * T / config.F * 1000.0   # mV

    if z is None:
        z = {ion: config.ION_CONCENTRATIONS[ion]["z"] for ion in permeabilities}

    numer = 0.0
    denom = 0.0
    for ion, P in permeabilities.items():
        zi = z[ion]
        co = c_out[ion]
        ci = c_in[ion]
        if zi > 0:
            numer += P * co
            denom += P * ci
        else:
            numer += P * ci
            denom += P * co

    if numer <= 0 or denom <= 0:
        raise ValueError("GHK numerator/denominator must be positive (undefined if all P are 0)")
    return rt_f * np.log(numer / denom)


def resting_potential(T=None):
    """Compute the resting potential using config physiological concentrations and default permeabilities (mV)."""
    perm = dict(config.PERMEABILITIES)
    conc = config.ION_CONCENTRATIONS
    c_out = {ion: conc[ion]["o"] for ion in perm}
    c_in = {ion: conc[ion]["i"] for ion in perm}
    return goldman_voltage(perm, c_out, c_in, T)


def single_ion_limit(ion, T=None):
    """Compute the limit potential when only one ion is permeable; it should equal that ion's Nernst potential."""
    conc = config.ION_CONCENTRATIONS
    perm = {ion: 1.0}
    c_out = {ion: conc[ion]["o"]}
    c_in = {ion: conc[ion]["i"]}
    return goldman_voltage(perm, c_out, c_in, T)


def permeability_scan(na_frac, T=None, cl_perm=None):
    """Scan the relative Na⁺ permeability (PK=1) and its effect on the resting potential.

    Parameters
    ----------
    na_frac : array_like
        Sequence of P_Na values.
    T : float | None
    cl_perm : float | None
        Fixed P_Cl value; None uses the config default of 0.45.

    Returns
    -------
    (na_frac, V) : permeability sequence and corresponding potentials.
    """
    conc = config.ION_CONCENTRATIONS
    c_out = {ion: conc[ion]["o"] for ion in ("K", "Na", "Cl")}
    c_in = {ion: conc[ion]["i"] for ion in ("K", "Na", "Cl")}
    if cl_perm is None:
        cl_perm = config.PERMEABILITIES["Cl"]
    na_frac = np.asarray(na_frac, dtype=float)
    V = np.array([
        goldman_voltage({"K": 1.0, "Na": p, "Cl": cl_perm}, c_out, c_in, T)
        for p in na_frac
    ])
    return na_frac, V
