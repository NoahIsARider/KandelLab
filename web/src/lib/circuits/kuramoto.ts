/** Kuramoto Model: Phase oscillator synchronization */
import { seededRandom, seededRandn, linspace } from '../math-utils';
import { KURAMOTO_PARAMS } from '../constants';

export interface KuramotoParams {
  N: number;
  K: number;
  omega_mean: number;
  omega_std: number;
}

/** Simulate Kuramoto model */
export function simulateKuramoto(params: {
  duration: number;
  dt: number;
  kurParams?: KuramotoParams;
  seed?: number;
}): {
  t: number[];
  phases: number[][];
  R: number[];
  psi: number[];
} {
  const { duration, dt, seed = 42 } = params;
  const p = params.kurParams || { ...KURAMOTO_PARAMS };
  const rng = seededRandom(seed);

  const { N, K, omega_mean, omega_std } = p;

  // Generate natural frequencies
  const omega = Array.from({ length: N }, () => omega_mean + omega_std * seededRandn(rng));

  // Initial phases (uniform random)
  let phases = Array.from({ length: N }, () => rng() * 2 * Math.PI);

  const steps = Math.ceil(duration / dt);
  const t: number[] = [];
  const allPhases: number[][] = [];
  const R: number[] = [];
  const psi: number[] = [];

  for (let i = 0; i <= steps; i++) {
    const time = i * dt;
    t.push(time);
    allPhases.push([...phases]);

    // Calculate order parameter
    const cosSum = phases.reduce((s, p) => s + Math.cos(p), 0) / N;
    const sinSum = phases.reduce((s, p) => s + Math.sin(p), 0) / N;
    const Ri = Math.sqrt(cosSum ** 2 + sinSum ** 2);
    const psi_i = Math.atan2(sinSum, cosSum);
    R.push(Ri);
    psi.push(psi_i);

    // Update phases
    if (i < steps) {
      const newPhases = phases.map((theta_i, idx) => {
        const coupling = (K / N) * phases.reduce((s, theta_j) => s + Math.sin(theta_j - theta_i), 0);
        return theta_i + dt * (omega[idx] + coupling);
      });
      phases = newPhases.map(p => ((p % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI));
    }
  }

  return { t, phases: allPhases, R, psi };
}

/** Calculate R(K) curve - phase transition */
export function phaseTransitionCurve(params: {
  KValues: number[];
  N?: number;
  duration?: number;
  omega_mean?: number;
  omega_std?: number;
  seed?: number;
}): { K: number; R_mean: number; R_final: number }[] {
  const { KValues, N = 50, duration = 100, omega_mean = 1, omega_std = 0.5, seed = 42 } = params;

  return KValues.map(K => {
    const result = simulateKuramoto({
      duration,
      dt: 0.1,
      kurParams: { N, K, omega_mean, omega_std },
      seed,
    });

    // Mean R in second half
    const halfIdx = Math.floor(result.R.length / 2);
    const R_mean = result.R.slice(halfIdx).reduce((s, v) => s + v, 0) / (result.R.length - halfIdx);
    const R_final = result.R[result.R.length - 1];

    return { K, R_mean, R_final };
  });
}

/** Synchronization time for different K values */
export function syncTime(params: {
  KValues: number[];
  threshold?: number;
  N?: number;
  seed?: number;
}): { K: number; syncTime: number }[] {
  const { KValues, threshold = 0.9, N = 50, seed = 42 } = params;

  return KValues.map(K => {
    const result = simulateKuramoto({
      duration: 200,
      dt: 0.1,
      kurParams: { N, K, omega_mean: 1, omega_std: 0.5 },
      seed,
    });

    // Find first time R exceeds threshold
    const idx = result.R.findIndex(r => r > threshold);
    return { K, syncTime: idx >= 0 ? result.t[idx] : Infinity };
  });
}
