/** Goldman-Hodgkin-Katz (GHK) Equation: Resting membrane potential */
import { R, F, celsiusToKelvin, DEFAULT_TEMP_C } from '../constants';
import { nernstPotential } from './nernst';

export interface GHKParams {
  tempC: number;
  P_K: number;
  P_Na: number;
  P_Cl: number;
  K_out: number;
  K_in: number;
  Na_out: number;
  Na_in: number;
  Cl_out: number;
  Cl_in: number;
}

/** Calculate GHK resting membrane potential (mV) */
export function ghkPotential(params: GHKParams): number {
  const { tempC, P_K, P_Na, P_Cl, K_out, K_in, Na_out, Na_in, Cl_out, Cl_in } = params;
  const T = celsiusToKelvin(tempC);
  const RT_F = (R * T) / F * 1000;

  const numerator = P_K * K_out + P_Na * Na_out + P_Cl * Cl_in;
  const denominator = P_K * K_in + P_Na * Na_in + P_Cl * Cl_out;

  return RT_F * Math.log(numerator / denominator);
}

/** Default GHK parameters for a typical neuron */
export function defaultGHKParams(): GHKParams {
  return {
    tempC: DEFAULT_TEMP_C,
    P_K: 1.0,
    P_Na: 0.04,
    P_Cl: 0.45,
    K_out: 5,
    K_in: 140,
    Na_out: 145,
    Na_in: 15,
    Cl_out: 110,
    Cl_in: 10,
  };
}

/** Verify GHK reduces to Nernst for single permeable ion */
export function verifySingleIonLimit(): {
  ion: string;
  ghk_mV: number;
  nernst_mV: number;
  match: boolean;
}[] {
  const base = defaultGHKParams();

  // K+ only
  const ghk_K = ghkPotential({ ...base, P_Na: 0, P_Cl: 0 });
  const nernst_K = nernstPotential({ tempC: base.tempC, z: 1, concOut: base.K_out, concIn: base.K_in });

  // Na+ only
  const ghk_Na = ghkPotential({ ...base, P_K: 0, P_Cl: 0 });
  const nernst_Na = nernstPotential({ tempC: base.tempC, z: 1, concOut: base.Na_out, concIn: base.Na_in });

  // Cl- only
  const ghk_Cl = ghkPotential({ ...base, P_K: 0, P_Na: 0 });
  const nernst_Cl = nernstPotential({ tempC: base.tempC, z: -1, concOut: base.Cl_out, concIn: base.Cl_in });

  return [
    { ion: 'K⁺', ghk_mV: ghk_K, nernst_mV: nernst_K, match: Math.abs(ghk_K - nernst_K) < 0.01 },
    { ion: 'Na⁺', ghk_mV: ghk_Na, nernst_mV: nernst_Na, match: Math.abs(ghk_Na - nernst_Na) < 0.01 },
    { ion: 'Cl⁻', ghk_mV: ghk_Cl, nernst_mV: nernst_Cl, match: Math.abs(ghk_Cl - nernst_Cl) < 0.01 },
  ];
}

/** Scan V_rest vs P_Na/P_K ratio */
export function scanPermeabilityRatio(
  base: GHKParams,
  ratios: number[]
): { ratio: number; V_rest: number }[] {
  return ratios.map(ratio => {
    const P_Na = base.P_K * ratio;
    return {
      ratio,
      V_rest: ghkPotential({ ...base, P_Na }),
    };
  });
}
