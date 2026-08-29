/** Motor: VOR gain adaptation, cerebellar Marr-Albus learning */
import { rk4Step, linspace, seededRandom } from '../math-utils';

export interface VORParams {
  targetGain: number;
  initialGain: number;
  learningRate: number;
  nTrials: number;
  noiseStd: number;
}

/** Simulate VOR gain adaptation */
export function simulateVOR(params: {
  nTrials: number;
  targetGain: number;
  initialGain: number;
  learningRate: number;
  noiseStd: number;
  seed?: number;
}): {
  trial: number[];
  gain: number[];
  error: number[];
  targetGain: number[];
} {
  const { nTrials, targetGain, initialGain, learningRate, noiseStd, seed = 42 } = params;
  const rng = seededRandom(seed);

  let gain = initialGain;
  const trial: number[] = [];
  const gainArr: number[] = [];
  const errorArr: number[] = [];
  const targetGainArr: number[] = [];

  for (let t = 0; t < nTrials; t++) {
    // Retinal slip error
    const error = targetGain - gain + noiseStd * (rng() - 0.5) * 2;

    // Cerebellar learning: Δw ∝ error
    gain += learningRate * error;
    gain = Math.max(0, Math.min(3, gain));

    trial.push(t);
    gainArr.push(gain);
    errorArr.push(targetGain - gain);
    targetGainArr.push(targetGain);
  }

  return { trial, gain: gainArr, error: errorArr, targetGain: targetGainArr };
}

/** Marr-Albus model: simple perceptron learning */
export function simulateMarrAlbus(params: {
  nInputs: number;
  nTrials: number;
  learningRate: number;
  targetFunction: (x: number[]) => number;
  seed?: number;
}): {
  trial: number[];
  output: number[];
  target: number[];
  error: number[];
  weights: number[][];
} {
  const { nInputs, nTrials, learningRate, targetFunction, seed = 42 } = params;
  const rng = seededRandom(seed);

  let weights = Array.from({ length: nInputs }, () => rng() - 0.5);
  const trial: number[] = [];
  const output: number[] = [];
  const target: number[] = [];
  const error: number[] = [];
  const weightsHistory: number[][] = [];

  for (let t = 0; t < nTrials; t++) {
    const x = Array.from({ length: nInputs }, () => rng() * 2 - 1);
    const yTarget = targetFunction(x);
    const yOut = weights.reduce((s, w, i) => s + w * x[i], 0);

    // Error-driven learning
    const err = yTarget - yOut;
    weights = weights.map((w, i) => w + learningRate * err * x[i]);

    trial.push(t);
    output.push(yOut);
    target.push(yTarget);
    error.push(err);
    weightsHistory.push([...weights]);
  }

  return { trial, output, target, error, weights: weightsHistory };
}
