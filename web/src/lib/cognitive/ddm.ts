/** Drift Diffusion Model: RT distribution, speed-accuracy tradeoff */
import { seededRandom, seededRandn } from '../math-utils';
import { DDM_PARAMS } from '../constants';

export interface DDMParams {
  drift: number;
  boundary: number;
  sigma: number;
  dt: number;
  maxTime: number;
}

/** Simulate single DDM trial */
export function simulateDDMTrial(params: {
  drift: number;
  boundary: number;
  sigma: number;
  dt: number;
  maxTime: number;
  rng: () => number;
}): {
  t: number[];
  x: number[];
  decision: 'upper' | 'lower' | 'none';
  rt: number;
} {
  const { drift, boundary, sigma, dt, maxTime, rng } = params;

  const t: number[] = [0];
  const x: number[] = [0];
  let decision: 'upper' | 'lower' | 'none' = 'none';
  let rt = maxTime;

  const steps = Math.ceil(maxTime / dt);
  for (let i = 0; i < steps; i++) {
    const time = (i + 1) * dt;
    const dW = seededRandn(rng) * Math.sqrt(dt);
    const newX = x[x.length - 1] + drift * dt + sigma * dW;

    t.push(time);
    x.push(newX);

    if (newX >= boundary) {
      decision = 'upper';
      rt = time;
      break;
    } else if (newX <= -boundary) {
      decision = 'lower';
      rt = time;
      break;
    }
  }

  return { t, x, decision, rt };
}

/** Simulate multiple DDM trials */
export function simulateDDMBatch(params: {
  nTrials: number;
  drift: number;
  boundary: number;
  sigma: number;
  dt: number;
  maxTime: number;
  seed?: number;
}): {
  trials: { decision: string; rt: number }[];
  accuracy: number;
  meanRT: number;
  meanRTCorrect: number;
  rtDistribution: { bin: number; countUpper: number; countLower: number }[];
} {
  const { nTrials, drift, boundary, sigma, dt, maxTime, seed = 42 } = params;
  const rng = seededRandom(seed);

  const trials: { decision: string; rt: number }[] = [];
  let correct = 0;
  let totalRT = 0;
  let correctRT = 0;
  let nCorrect = 0;

  for (let i = 0; i < nTrials; i++) {
    const result = simulateDDMTrial({ drift, boundary, sigma, dt, maxTime, rng });
    trials.push({ decision: result.decision, rt: result.rt });

    if (result.decision === 'upper') {
      correct++;
      correctRT += result.rt;
      nCorrect++;
    } else if (result.decision === 'lower') {
      totalRT += result.rt;
    }
    totalRT += result.rt;
  }

  // RT distribution
  const nBins = 20;
  const binWidth = maxTime / nBins;
  const rtDistribution = Array.from({ length: nBins }, (_, b) => {
    const binStart = b * binWidth;
    const binEnd = (b + 1) * binWidth;
    const countUpper = trials.filter(t => t.decision === 'upper' && t.rt >= binStart && t.rt < binEnd).length;
    const countLower = trials.filter(t => t.decision === 'lower' && t.rt >= binStart && t.rt < binEnd).length;
    return { bin: binStart + binWidth / 2, countUpper, countLower };
  });

  return {
    trials,
    accuracy: correct / nTrials,
    meanRT: totalRT / nTrials,
    meanRTCorrect: nCorrect > 0 ? correctRT / nCorrect : 0,
    rtDistribution,
  };
}

/** Speed-accuracy tradeoff: vary boundary */
export function speedAccuracyTradeoff(params: {
  boundaries: number[];
  nTrials: number;
  drift: number;
  sigma: number;
  seed?: number;
}): { boundary: number; accuracy: number; meanRT: number }[] {
  const { boundaries, nTrials, drift, sigma, seed = 42 } = params;

  return boundaries.map(boundary => {
    const result = simulateDDMBatch({
      nTrials,
      drift,
      boundary,
      sigma,
      dt: 0.01,
      maxTime: 5,
      seed,
    });
    return { boundary, accuracy: result.accuracy, meanRT: result.meanRT };
  });
}

/** Drift rate effect: vary drift */
export function driftRateEffect(params: {
  drifts: number[];
  nTrials: number;
  boundary: number;
  sigma: number;
  seed?: number;
}): { drift: number; accuracy: number; meanRT: number }[] {
  const { drifts, nTrials, boundary, sigma, seed = 42 } = params;

  return drifts.map(drift => {
    const result = simulateDDMBatch({
      nTrials,
      drift,
      boundary,
      sigma,
      dt: 0.01,
      maxTime: 5,
      seed,
    });
    return { drift, accuracy: result.accuracy, meanRT: result.meanRT };
  });
}
