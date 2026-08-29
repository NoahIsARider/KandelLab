/** Reward Learning: Rescorla-Wagner + TD(λ) */
import { REWARD_PARAMS } from '../constants';
import { linspace } from '../math-utils';

export interface RWParams {
  alpha: number;
  nTrials: number;
}

/** Rescorla-Wagner model: classical conditioning */
export function simulateRW(params: {
  nTrials: number;
  alpha: number;
  reward: number;
  contingency: (trial: number) => boolean;
}): {
  trial: number[];
  V: number[];
  delta: number[];
  reward: number[];
} {
  const { nTrials, alpha, reward, contingency } = params;

  let V = 0;
  const trial: number[] = [];
  const VArr: number[] = [];
  const deltaArr: number[] = [];
  const rewardArr: number[] = [];

  for (let t = 0; t < nTrials; t++) {
    const lambda = contingency(t) ? reward : 0;
    const delta = alpha * (lambda - V);
    V += delta;

    trial.push(t);
    VArr.push(V);
    deltaArr.push(delta);
    rewardArr.push(lambda);
  }

  return { trial, V: VArr, delta: deltaArr, reward: rewardArr };
}

/** Blocking effect simulation */
export function simulateBlocking(params: {
  alpha: number;
  phase1Trials: number;
  phase2Trials: number;
  reward: number;
}): {
  phase: string[];
  trial: number[];
  VA: number[];
  VB: number[];
  delta: number[];
} {
  const { alpha, phase1Trials, phase2Trials, reward } = params;

  let VA = 0, VB = 0;
  const phase: string[] = [];
  const trial: number[] = [];
  const VAArr: number[] = [];
  const VBArr: number[] = [];
  const deltaArr: number[] = [];

  let t = 0;

  // Phase 1: A+ trials
  for (let i = 0; i < phase1Trials; i++) {
    const delta = alpha * (reward - VA);
    VA += delta;
    phase.push('Phase 1 (A+)');
    trial.push(t++);
    VAArr.push(VA);
    VBArr.push(VB);
    deltaArr.push(delta);
  }

  // Phase 2: AB+ trials
  for (let i = 0; i < phase2Trials; i++) {
    const totalV = VA + VB;
    const delta = alpha * (reward - totalV);
    VA += delta * 0.5;
    VB += delta * 0.5;
    phase.push('Phase 2 (AB+)');
    trial.push(t++);
    VAArr.push(VA);
    VBArr.push(VB);
    deltaArr.push(delta);
  }

  return { phase, trial, VA: VAArr, VB: VBArr, delta: deltaArr };
}

/** TD(λ) model: temporal difference learning */
export function simulateTD(params: {
  nSteps: number;
  alpha: number;
  gamma: number;
  lambda: number;
  rewardSchedule: (t: number) => number;
}): {
  t: number[];
  V: number[];
  delta: number[];
  reward: number[];
} {
  const { nSteps, alpha, gamma, lambda, rewardSchedule } = params;

  const V = new Array(nSteps + 1).fill(0);
  const eligibility = new Array(nSteps + 1).fill(0);
  const delta: number[] = [];
  const reward: number[] = [];
  const t: number[] = [];

  for (let step = 0; step < nSteps; step++) {
    const r = rewardSchedule(step);
    const delta_t = r + gamma * V[step + 1] - V[step];

    // Update eligibility trace
    eligibility[step] += 1;

    // Update all values
    for (let s = 0; s <= step; s++) {
      V[s] += alpha * delta_t * eligibility[s];
      eligibility[s] *= gamma * lambda;
    }

    t.push(step);
    delta.push(delta_t);
    reward.push(r);
  }

  return { t, V: V.slice(0, nSteps), delta, reward };
}

/** Dopamine-like prediction error signal */
export function dopamineSignal(params: {
  nSteps: number;
  rewardTime: number;
  alpha: number;
  gamma: number;
}): {
  t: number[];
  predictionError: number[];
  value: number[];
} {
  const { nSteps, rewardTime, alpha, gamma } = params;

  const result = simulateTD({
    nSteps,
    alpha,
    gamma,
    lambda: 0,
    rewardSchedule: (t) => t === rewardTime ? 1 : 0,
  });

  return {
    t: result.t,
    predictionError: result.delta,
    value: result.V,
  };
}
