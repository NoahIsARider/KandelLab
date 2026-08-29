/** Physical and biological constants for neuroscience simulations */

/** Universal gas constant (J/(mol·K)) */
export const R = 8.314;

/** Faraday constant (C/mol) */
export const F = 96485;

/** Default temperature (Celsius) */
export const DEFAULT_TEMP_C = 37;

/** Convert Celsius to Kelvin */
export function celsiusToKelvin(c: number): number {
  return c + 273.15;
}

/** Default temperature in Kelvin */
export const DEFAULT_TEMP_K = celsiusToKelvin(DEFAULT_TEMP_C);

/** RT/F at 37°C (mV) */
export function thermalVoltage(tempK: number = DEFAULT_TEMP_K): number {
  return (R * tempK) / F * 1000; // in mV
}

/** Ion concentrations (mM) - typical mammalian neuron */
export const ION_CONCENTRATIONS = {
  K_out: 5.0,
  K_in: 140.0,
  Na_out: 145.0,
  Na_in: 15.0,
  Ca_out: 2.0,
  Ca_in: 0.0001,
  Cl_out: 110.0,
  Cl_in: 10.0,
};

/** Ion valences */
export const ION_VALENCES: Record<string, number> = {
  K: 1,
  Na: 1,
  Ca: 2,
  Cl: -1,
};

/** Default membrane permeabilities (relative) */
export const DEFAULT_PERMEABILITIES = {
  P_K: 1.0,
  P_Na: 0.04,
  P_Cl: 0.45,
};

/** HH model default parameters */
export const HH_PARAMS = {
  V_rest: -65,     // mV
  V_thresh: -55,   // mV
  V_peak: 35,      // mV
  E_Na: 55,        // mV
  E_K: -90,        // mV
  E_L: -54.4,      // mV
  g_Na: 120,       // mS/cm²
  g_K: 36,         // mS/cm²
  g_L: 0.3,        // mS/cm²
  C_m: 1,          // µF/cm²
};

/** LIF model default parameters */
export const LIF_PARAMS = {
  tau: 20,         // ms - membrane time constant
  E_L: -70,        // mV - resting potential
  V_thresh: -50,   // mV - threshold
  V_reset: -80,    // mV - reset potential
  R: 10,           // MΩ - membrane resistance
  t_ref: 2,        // ms - refractory period
};

/** Synapse default parameters */
export const SYNAPSE_PARAMS = {
  tau_epsp: 5,     // ms - EPSP time constant
  tau_ipsp: 10,    // ms - IPSP time constant
  w_epsp: 1.0,     // EPSP weight
  w_ipsp: -0.5,    // IPSP weight
};

/** Hebbian learning defaults */
export const HEBBIAN_PARAMS = {
  eta: 0.01,       // learning rate
  theta_M: 0,      // BCM sliding threshold
};

/** Wilson-Cowan defaults */
export const WC_PARAMS = {
  tau_E: 1,
  tau_I: 2,
  w_EE: 12,
  w_EI: 4,
  w_IE: 13,
  w_II: 11,
  theta_E: 4,
  theta_I: 3.5,
  P_ext: 0,
  Q_ext: 0,
};

/** Kuramoto defaults */
export const KURAMOTO_PARAMS = {
  N: 50,           // number of oscillators
  K: 2,            // coupling strength
  omega_mean: 1,   // mean natural frequency
  omega_std: 0.5,  // std of natural frequencies
};

/** Hopfield network defaults */
export const HOPFIELD_PARAMS = {
  N: 100,          // number of neurons
  alpha: 0.1,      // load parameter
};

/** Reward learning defaults */
export const REWARD_PARAMS = {
  alpha_RW: 0.1,   // RW learning rate
  gamma: 0.95,     // discount factor
  lambda: 0.8,     // eligibility trace decay
};

/** DDM defaults */
export const DDM_PARAMS = {
  drift: 0.5,      // drift rate
  boundary: 1.0,   // decision boundary
  sigma: 1.0,      // noise
  dt: 0.01,        // time step
  max_time: 5,     // max decision time
};

/** SDT defaults */
export const SDT_PARAMS = {
  d_prime: 1.5,
  criterion: 0,
};
