"""KandelLab global configuration — all tunable parameters live here.

All simulation parameters (ion concentrations, channel parameters, network
sizes, time steps, etc.) are defined in this single file. Modules read them
on demand via :func:`get`, ensuring cross-module consistency and allowing
whole-system tuning in one place.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Fundamental physical constants
# ---------------------------------------------------------------------------
R = 8.314462618                       # gas constant J/(mol·K)
F = 96485.33212                       # Faraday constant C/mol
T_CELSIUS = 37.0                      # physiological temperature (celsius)
T_KELVIN = T_CELSIUS + 273.15         # physiological temperature (kelvin)

# ---------------------------------------------------------------------------
# Ion concentrations (millimolar, textbook Kandel standard values)
# ---------------------------------------------------------------------------
ION_CONCENTRATIONS = {
    "K":  {"o": 5.0,  "i": 140.0, "z": 1},
    "Na": {"o": 145.0, "i": 15.0, "z": 1},
    "Ca": {"o": 2.0, "i": 0.0001, "z": 2},
    "Cl": {"o": 120.0, "i": 4.2, "z": -1},
}

# Relative permeabilities (Gerstner Neuronal Dynamics standard values, PK normalized)
PERMEABILITIES = {"K": 1.0, "Na": 0.04, "Cl": 0.45}

# ---------------------------------------------------------------------------
# Hodgkin-Huxley (HH 1952, units mV / ms / µA/cm²)
# ---------------------------------------------------------------------------
HH_DEFAULTS = {
    "C_m":   1.0,        # membrane capacitance µF/cm²
    "g_Na":  120.0,      # sodium conductance mS/cm²
    "g_K":   36.0,       # potassium conductance mS/cm²
    "g_L":   0.3,        # leak conductance mS/cm²
    "E_Na":  +50.0,      # sodium equilibrium potential mV
    "E_K":   -77.0,      # potassium equilibrium potential mV
    "E_L":   -54.387,    # leak equilibrium potential mV
    "V_rest": -65.0,     # resting potential mV
}

# ---------------------------------------------------------------------------
# Leaky integrate-and-fire (LIF)
# ---------------------------------------------------------------------------
LIF_DEFAULTS = {
    "tau_m": 20.0,        # membrane time constant ms
    "R_m":   100.0,       # membrane resistance MΩ
    "E_L":   -70.0,       # leak equilibrium potential mV
    "V_th":  -55.0,       # threshold mV
    "V_reset": -70.0,     # reset potential mV
    "V_peak": 30.0,       # peak potential (used only in the analytic f-I formula)
    "tau_ref": 2.0,       # absolute refractory period ms
}

# ---------------------------------------------------------------------------
# Synapse (α-function PSP)
# ---------------------------------------------------------------------------
SYNAPSE_DEFAULTS = {
    "tau_rise": 1.0,      # rise time constant ms
    "tau_decay": 10.0,    # decay time constant ms
}

# ---------------------------------------------------------------------------
# Hebbian / BCM
# ---------------------------------------------------------------------------
HEBBIAN_DEFAULTS = {
    "eta": 0.01,          # learning rate
    "theta_M": 1.0,       # BCM sliding threshold reference value
    "tau_theta": 1.0,     # threshold sliding time constant
}

# ---------------------------------------------------------------------------
# Wilson-Cowan excitatory-inhibitory population
# ---------------------------------------------------------------------------
WILSON_COWAN_DEFAULTS = {
    "tau_E": 8.0, "tau_I": 8.0,
    "a_E": 1.2, "b_E": 0.0, "theta_E": 4.0,
    "a_I": 1.0, "b_I": 0.0, "theta_I": 1.5,
    "w_EE": 16.0, "w_EI": 12.0, "w_IE": 15.0, "w_II": 3.0,
}

# ---------------------------------------------------------------------------
# Kuramoto synchronization
# ---------------------------------------------------------------------------
KURAMOTO_DEFAULTS = {
    "N": 100,             # number of oscillators
    "omega_mean": 1.0,    # mean natural frequency rad/s
    "omega_std": 0.1,     # natural frequency standard deviation
}

# ---------------------------------------------------------------------------
# Gabor / vision
# ---------------------------------------------------------------------------
GABOR_DEFAULTS = {
    "size": 64,           # receptive field size (pixels)
    "sf": 0.1,            # spatial frequency cycles/pixel
    "sigma": 8.0,         # Gaussian envelope standard deviation
    "phi": 0.0,           # phase
    "kappa": 1.0,         # aspect ratio
}

# ---------------------------------------------------------------------------
# γ-tone / audition
# ---------------------------------------------------------------------------
AUDITION_DEFAULTS = {
    "n_channels": 24,     # number of filter channels
    "fmin": 100.0,        # lowest characteristic frequency Hz
    "fmax": 8000.0,       # highest characteristic frequency Hz
    "ERB_scale": 1.0,     # equivalent rectangular bandwidth coefficient
    "order": 4,           # γ-tone order
    "fs": 20000.0,        # sampling rate Hz
}

# ---------------------------------------------------------------------------
# VOR / motor
# ---------------------------------------------------------------------------
VOR_DEFAULTS = {
    "g0": 0.6,            # initial gain
    "target_g": 1.0,      # target gain
    "eta": 0.05,          # learning rate
}

# ---------------------------------------------------------------------------
# Hopfield associative memory
# ---------------------------------------------------------------------------
HOPFIELD_DEFAULTS = {
    "N": 256,             # number of neurons (16×16 pixels)
    "T_max": 200,         # maximum asynchronous update iterations
}

# ---------------------------------------------------------------------------
# Reward learning RW / TD
# ---------------------------------------------------------------------------
REWARD_DEFAULTS = {
    "alpha": 0.1,         # RW learning rate
    "gamma": 0.9,         # TD discount factor
}

# ---------------------------------------------------------------------------
# Drift-diffusion model (DDM)
# ---------------------------------------------------------------------------
DDM_DEFAULTS = {
    "dt": 0.001,          # time step s
    "T_max": 3.0,         # maximum decision time s
    "boundary": 1.0,      # absorbing boundary ±a
}

# ---------------------------------------------------------------------------
# Numerical integration
# ---------------------------------------------------------------------------
NUMERICS = {
    "default_dt": 0.01,   # ms (default step for ODEs such as HH)
    "seed": 42,           # global random seed (deterministic)
}


def get(section: str, key: str, default=None):
    """Read a configuration item; return default if the section or key is missing."""
    table = globals().get(section.upper(), None)
    if isinstance(table, dict) and key in table:
        return table[key]
    return default


def update(section: str, key: str, value):
    """Update a configuration item; raise TypeError if the section is not a dict."""
    table = globals().get(section.upper(), None)
    if not isinstance(table, dict):
        raise KeyError(f"unknown config section: {section}")
    table[key] = value
