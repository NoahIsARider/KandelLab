/** Leaky Integrate-and-Fire (LIF) Model */
import { LIF_PARAMS } from '../constants';
import { seededRandom, seededRandn } from '../math-utils';

export interface LIFParams {
  tau: number;
  E_L: number;
  V_thresh: number;
  V_reset: number;
  R: number;
  t_ref: number;
}

/** Simulate LIF neuron */
export function simulateLIF(params: {
  duration: number;
  dt: number;
  I_ext: (t: number) => number;
  lifParams?: LIFParams;
  seed?: number;
}): {
  t: number[];
  V: number[];
  spikes: number[];
} {
  const { duration, dt, I_ext, seed = 42 } = params;
  const p = params.lifParams || { ...LIF_PARAMS };
  const rng = seed > 0 ? seededRandom(seed) : Math.random;

  const steps = Math.ceil(duration / dt);
  const t: number[] = [];
  const V: number[] = [];
  const spikes: number[] = [];

  let v = p.E_L;
  let inRef = false;
  let refCounter = 0;

  for (let i = 0; i <= steps; i++) {
    const time = i * dt;
    t.push(time);
    V.push(v);

    if (inRef) {
      v = p.V_reset;
      refCounter -= dt;
      if (refCounter <= 0) {
        inRef = false;
      }
      continue;
    }

    const I = I_ext(time);
    const dv = dt * (-(v - p.E_L) + p.R * I) / p.tau;
    v += dv;

    if (v >= p.V_thresh) {
      spikes.push(time);
      v = p.V_reset;
      inRef = true;
      refCounter = p.t_ref;
    }
  }

  return { t, V, spikes };
}

/** Calculate firing rate for constant current (analytical) */
export function analyticalFiringRate(I: number, params: LIFParams = { ...LIF_PARAMS }): number {
  if (I <= 0) return 0;
  const { tau, E_L, V_thresh, V_reset, R, t_ref } = params;
  const V_ss = E_L + R * I;
  if (V_ss <= V_thresh) return 0;

  const arg = (V_thresh - E_L) / (V_ss - E_L);
  if (arg <= 0 || arg >= 1) return 0;
  const T = t_ref + tau * Math.log(1 / (1 - (V_thresh - E_L) / (R * I)));
  return 1000 / T; // Hz
}

/** Numerical firing rate */
export function numericalFiringRate(I: number, duration: number = 2000, params?: LIFParams): number {
  const result = simulateLIF({
    duration,
    dt: 0.1,
    I_ext: () => I,
    lifParams: params,
  });
  // Exclude first 200ms for transient
  const validSpikes = result.spikes.filter(s => s > 200);
  return validSpikes.length / ((duration - 200) / 1000);
}

/** Generate f-I curve */
export function fICurve(params: {
  currents: number[];
  duration?: number;
  lifParams?: LIFParams;
}): { I: number; freq_analytical: number; freq_numerical: number }[] {
  const { currents, duration = 2000, lifParams } = params;
  const p = lifParams || { ...LIF_PARAMS };

  return currents.map(I => ({
    I,
    freq_analytical: analyticalFiringRate(I, p),
    freq_numerical: numericalFiringRate(I, duration, p),
  }));
}

/** Generate raster plot data for multiple neurons */
export function rasterPlot(params: {
  nNeurons: number;
  duration: number;
  dt: number;
  I_ext: (t: number, neuronIdx: number) => number;
  lifParams?: LIFParams;
}): { neuronIdx: number; spikeTime: number }[] {
  const { nNeurons, duration, dt, I_ext, lifParams } = params;
  const allSpikes: { neuronIdx: number; spikeTime: number }[] = [];

  for (let n = 0; n < nNeurons; n++) {
    const result = simulateLIF({
      duration,
      dt,
      I_ext: (t) => I_ext(t, n),
      lifParams,
      seed: 42 + n,
    });
    result.spikes.forEach(t => allSpikes.push({ neuronIdx: n, spikeTime: t }));
  }

  return allSpikes;
}
