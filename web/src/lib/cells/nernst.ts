/** Nernst Equation: Equilibrium potential for a single ion */
import { R, F, celsiusToKelvin, DEFAULT_TEMP_C } from '../constants';

export interface NernstParams {
  tempC: number;
  z: number;        // valence
  concOut: number;  // mM
  concIn: number;   // mM
}

/** Calculate Nernst equilibrium potential (mV) */
export function nernstPotential(params: NernstParams): number {
  const { tempC, z, concOut, concIn } = params;
  const T = celsiusToKelvin(tempC);
  return (R * T) / (z * F) * Math.log(concOut / concIn) * 1000;
}

/** Calculate equilibrium potentials for all major ions */
export function allEquilibriumPotentials(tempC: number = DEFAULT_TEMP_C) {
  const ions = [
    { name: 'K⁺', z: 1, out: 5, in_: 140 },
    { name: 'Na⁺', z: 1, out: 145, in_: 15 },
    { name: 'Ca²⁺', z: 2, out: 2, in_: 0.0001 },
    { name: 'Cl⁻', z: -1, out: 110, in_: 10 },
  ];

  return ions.map(ion => ({
    ion: ion.name,
    z: ion.z,
    concOut: ion.out,
    concIn: ion.in_,
    E_mV: nernstPotential({ tempC, z: ion.z, concOut: ion.out, concIn: ion.in_ }),
  }));
}

/** Scan equilibrium potential vs extracellular concentration */
export function scanConcentration(
  ion: string,
  z: number,
  concIn: number,
  tempC: number,
  outRange: number[]
): { concOut: number; E_mV: number }[] {
  return outRange.map(concOut => ({
    concOut,
    E_mV: nernstPotential({ tempC, z, concOut, concIn }),
  }));
}

/** Scan equilibrium potential vs temperature */
export function scanTemperature(
  z: number,
  concOut: number,
  concIn: number,
  tempRange: number[]
): { tempC: number; E_mV: number }[] {
  return tempRange.map(tempC => ({
    tempC,
    E_mV: nernstPotential({ tempC, z, concOut, concIn }),
  }));
}
