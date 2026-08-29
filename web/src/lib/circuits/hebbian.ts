/** Hebbian Learning: Hebb rule, BCM sliding threshold, LTP-LTD */
import { seededRandom } from '../math-utils';

export interface HebbianParams {
  eta: number;
  theta_M: number;
  nPre: number;
  nPost: number;
}

/** Basic Hebbian learning: Δw = η·x·y */
export function hebbianUpdate(w: number[], x: number[], y: number, eta: number): number[] {
  return w.map((wi, i) => wi + eta * x[i] * y);
}

/** BCM rule: Δw = η·x·y·(y - θ_M) */
export function bcmUpdate(w: number[], x: number[], y: number, theta: number, eta: number): number[] {
  return w.map((wi, i) => wi + eta * x[i] * y * (y - theta));
}

/** Simulate Hebbian learning over time */
export function simulateHebbian(params: {
  nPre: number;
  nPost: number;
  nSteps: number;
  eta: number;
  correlated: boolean;
  seed?: number;
}): {
  step: number[];
  weights: number[][];
  correlations: number[];
} {
  const { nPre, nPost, nSteps, eta, correlated, seed = 42 } = params;
  const rng = seededRandom(seed);

  let w = Array.from({ length: nPre }, () => rng() * 0.2 - 0.1);
  const step: number[] = [];
  const weights: number[][] = [];
  const correlations: number[] = [];

  for (let t = 0; t < nSteps; t++) {
    // Generate pre-synaptic input
    const x = Array.from({ length: nPre }, () => rng());

    // Post-synaptic activity
    let y: number;
    if (correlated) {
      // Post correlates with specific pre-synaptic pattern
      const targetPattern = Array.from({ length: nPre }, (_, i) => i < nPre / 2 ? 1 : 0);
      y = x.reduce((s, xi, i) => s + xi * targetPattern[i], 0) / nPre;
    } else {
      y = rng();
    }

    // Hebbian update
    w = hebbianUpdate(w, x, y, eta);

    // Normalize weights
    const wMax = Math.max(...w.map(Math.abs));
    if (wMax > 1) {
      w = w.map(wi => wi / wMax);
    }

    step.push(t);
    weights.push([...w]);
    correlations.push(y);
  }

  return { step, weights, correlations };
}

/** BCM sliding threshold simulation */
export function simulateBCM(params: {
  nSteps: number;
  eta: number;
  inputRate: number[];
  seed?: number;
}): {
  step: number[];
  weight: number[];
  theta_M: number[];
  postRate: number[];
} {
  const { nSteps, eta, inputRate, seed = 42 } = params;
  const rng = seededRandom(seed);

  let w = 0.5;
  let theta_M = 0.5;
  const alpha = 0.001; // threshold learning rate

  const step: number[] = [];
  const weight: number[] = [];
  const thetaArr: number[] = [];
  const postRate: number[] = [];

  for (let t = 0; t < nSteps; t++) {
    const x = inputRate[t % inputRate.length] + (rng() - 0.5) * 0.1;
    const y = Math.max(0, w * x);

    // BCM update
    const dw = eta * x * y * (y - theta_M);
    w += dw;
    w = Math.max(0, Math.min(2, w));

    // Sliding threshold: θ_M = <y²>
    theta_M += alpha * (y * y - theta_M);

    step.push(t);
    weight.push(w);
    thetaArr.push(theta_M);
    postRate.push(y);
  }

  return { step, weight, theta_M: thetaArr, postRate };
}

/** LTP-LTD curve: Δw as function of post-pre timing */
export function ltpLtdCurve(params: {
  dtRange: number[];
  tauPlus: number;
  tauMinus: number;
  APlus: number;
  AMinus: number;
}): { dt: number; dw: number }[] {
  const { dtRange, tauPlus, tauMinus, APlus, AMinus } = params;

  return dtRange.map(dt => {
    let dw: number;
    if (dt > 0) {
      // Pre before post → LTP
      dw = APlus * Math.exp(-dt / tauPlus);
    } else {
      // Post before pre → LTD
      dw = -AMinus * Math.exp(dt / tauMinus);
    }
    return { dt, dw };
  });
}
