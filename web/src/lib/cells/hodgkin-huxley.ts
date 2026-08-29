/** Hodgkin-Huxley Model: Action potential simulation */
import { rk4Step, linspace, randn, seededRandom, seededRandn } from '../math-utils';
import { HH_PARAMS } from '../constants';

export interface HHParams {
  V_rest: number;
  E_Na: number;
  E_K: number;
  E_L: number;
  g_Na: number;
  g_K: number;
  g_L: number;
  C_m: number;
}

export interface HHState {
  V: number;
  m: number;
  h: number;
  n: number;
}

/** HH gating variable alpha functions */
function alpha_m(V: number): number {
  const dv = V + 40;
  if (Math.abs(dv) < 0.001) return 1.0;
  return 0.1 * dv / (1 - Math.exp(-dv / 10));
}

function beta_m(V: number): number {
  return 4.0 * Math.exp(-(V + 65) / 18);
}

function alpha_h(V: number): number {
  return 0.07 * Math.exp(-(V + 65) / 20);
}

function beta_h(V: number): number {
  return 1.0 / (1 + Math.exp(-(V + 35) / 10));
}

function alpha_n(V: number): number {
  const dv = V + 55;
  if (Math.abs(dv) < 0.001) return 0.1;
  return 0.01 * dv / (1 - Math.exp(-dv / 10));
}

function beta_n(V: number): number {
  return 0.125 * Math.exp(-(V + 65) / 80);
}

/** HH ODE derivatives */
function hhDerivatives(
  state: number[],
  params: HHParams,
  I_ext: number
): number[] {
  const [V, m, h, n] = state;
  const { E_Na, E_K, E_L, g_Na, g_K, g_L, C_m } = params;

  const I_Na = g_Na * m * m * m * h * (V - E_Na);
  const I_K = g_K * n * n * n * n * (V - E_K);
  const I_L = g_L * (V - E_L);

  const dV = (-I_Na - I_K - I_L + I_ext) / C_m;
  const dm = alpha_m(V) * (1 - m) - beta_m(V) * m;
  const dh = alpha_h(V) * (1 - h) - beta_h(V) * h;
  const dn = alpha_n(V) * (1 - n) - beta_n(V) * n;

  return [dV, dm, dh, dn];
}

/** Get steady-state values at given voltage */
export function steadyState(V: number): HHState {
  const am = alpha_m(V), bm = beta_m(V);
  const ah = alpha_h(V), bh = beta_h(V);
  const an = alpha_n(V), bn = beta_n(V);
  return {
    V,
    m: am / (am + bm),
    h: ah / (ah + bh),
    n: an / (an + bn),
  };
}

/** Run HH simulation */
export function simulateHH(params: {
  duration: number;
  dt: number;
  I_ext: (t: number) => number;
  hhParams?: HHParams;
  V0?: number;
  seed?: number;
}): {
  t: number[];
  V: number[];
  m: number[];
  h: number[];
  n: number[];
  gNa: number[];
  gK: number[];
} {
  const { duration, dt, I_ext, V0 = -65 } = params;
  const hp = params.hhParams || { ...HH_PARAMS };
  const ss = steadyState(V0);
  let state = [ss.V, ss.m, ss.h, ss.n];

  const steps = Math.ceil(duration / dt);
  const t: number[] = [];
  const V: number[] = [];
  const mArr: number[] = [];
  const hArr: number[] = [];
  const nArr: number[] = [];
  const gNa: number[] = [];
  const gK: number[] = [];

  for (let i = 0; i <= steps; i++) {
    const time = i * dt;
    t.push(time);
    V.push(state[0]);
    mArr.push(state[1]);
    hArr.push(state[2]);
    nArr.push(state[3]);
    gNa.push(hp.g_Na * state[1] ** 3 * state[2]);
    gK.push(hp.g_K * state[3] ** 4);

    if (i < steps) {
      const I = I_ext(time);
      state = rk4Step(state, (t_, s) => hhDerivatives(s, hp, I), time, dt);
    }
  }

  return { t, V, m: mArr, h: hArr, n: nArr, gNa, gK };
}

/** Generate f-I curve */
export function fICurve(params: {
  currents: number[];
  duration: number;
  dt: number;
  hhParams?: HHParams;
}): { I: number; freq: number }[] {
  const { currents, duration, dt, hhParams } = params;

  return currents.map(I => {
    const result = simulateHH({
      duration,
      dt,
      I_ext: () => I,
      hhParams,
    });

    // Count spikes (threshold crossings at -40 mV)
    let spikes = 0;
    let wasAbove = false;
    for (let i = 0; i < result.V.length; i++) {
      if (result.V[i] > -40 && !wasAbove) {
        spikes++;
        wasAbove = true;
      } else if (result.V[i] < -40) {
        wasAbove = false;
      }
    }

    const freq = spikes / (duration / 1000);
    return { I, freq };
  });
}

/** Find threshold by bisection */
export function findThreshold(hhParams?: HHParams): number {
  const hp = hhParams || { ...HH_PARAMS };
  let low = -70, high = -40;
  for (let iter = 0; iter < 50; iter++) {
    const mid = (low + high) / 2;
    const result = simulateHH({
      duration: 50,
      dt: 0.01,
      I_ext: (t) => t < 5 ? 0 : mid,
      hhParams: hp,
    });
    const maxV = Math.max(...result.V);
    if (maxV > 0) {
      high = mid;
    } else {
      low = mid;
    }
  }
  return (low + high) / 2;
}
