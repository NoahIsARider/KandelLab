/** Memory: Hopfield network - associative memory, energy function, capacity */
import { seededRandom } from '../math-utils';

export interface HopfieldParams {
  N: number;
  nPatterns: number;
  noiseLevel: number;
  maxIterations: number;
}

/** Generate random binary pattern {-1, +1} */
function generatePattern(N: number, rng: () => number): number[] {
  return Array.from({ length: N }, () => rng() > 0.5 ? 1 : -1);
}

/** Store patterns using Hebbian rule */
export function storePatterns(patterns: number[][]): number[][] {
  const N = patterns[0].length;
  const P = patterns.length;
  const W: number[][] = Array.from({ length: N }, () => new Array(N).fill(0));

  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      let sum = 0;
      for (let p = 0; p < P; p++) {
        sum += patterns[p][i] * patterns[p][j];
      }
      W[i][j] = sum / N;
      W[j][i] = W[i][j];
    }
  }

  return W;
}

/** Calculate energy of a state */
export function hopfieldEnergy(state: number[], W: number[][]): number {
  const N = state.length;
  let E = 0;
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      E -= W[i][j] * state[i] * state[j];
    }
  }
  return E;
}

/** Async update one neuron */
function updateNeuron(state: number[], W: number[][], idx: number): number[] {
  const N = state.length;
  let h = 0;
  for (let j = 0; j < N; j++) {
    if (j !== idx) h += W[idx][j] * state[j];
  }
  const newState = [...state];
  newState[idx] = h >= 0 ? 1 : -1;
  return newState;
}

/** Simulate Hopfield network recall */
export function simulateHopfield(params: {
  N: number;
  nPatterns: number;
  noiseLevel: number;
  maxIterations: number;
  seed?: number;
}): {
  patterns: number[][];
  corruptedPattern: number[];
  recallHistory: number[][];
  energyHistory: number[];
  converged: boolean;
  iterations: number;
} {
  const { N, nPatterns, noiseLevel, maxIterations, seed = 42 } = params;
  const rng = seededRandom(seed);

  // Generate and store patterns
  const patterns = Array.from({ length: nPatterns }, () => generatePattern(N, rng));
  const W = storePatterns(patterns);

  // Corrupt first pattern
  const corrupted = patterns[0].map(s => rng() < noiseLevel ? -s : s);

  // Recall
  let state = [...corrupted];
  const recallHistory: number[][] = [[...state]];
  const energyHistory: number[] = [hopfieldEnergy(state, W)];
  let converged = false;
  let iterations = 0;

  for (let iter = 0; iter < maxIterations; iter++) {
    const prevState = [...state];

    // Random async update
    const idx = Math.floor(rng() * N);
    state = updateNeuron(state, W, idx);

    const energy = hopfieldEnergy(state, W);
    recallHistory.push([...state]);
    energyHistory.push(energy);
    iterations = iter + 1;

    // Check convergence
    if (state.every((s, i) => s === prevState[i])) {
      converged = true;
      break;
    }
  }

  return { patterns, corruptedPattern: corrupted, recallHistory, energyHistory, converged, iterations };
}

/** Test capacity: max patterns vs N */
export function capacityTest(params: {
  N: number;
  nPatternsRange: number[];
  nTrials: number;
  seed?: number;
}): { nPatterns: number; successRate: number }[] {
  const { N, nPatternsRange, nTrials, seed = 42 } = params;

  return nPatternsRange.map(nPatterns => {
    let successes = 0;

    for (let trial = 0; trial < nTrials; trial++) {
      const result = simulateHopfield({
        N,
        nPatterns,
        noiseLevel: 0.3,
        maxIterations: 200,
        seed: seed + trial * 100,
      });

      // Check if recalled pattern matches stored pattern
      const recalled = result.recallHistory[result.recallHistory.length - 1];
      const match = recalled.every((s, i) => s === result.patterns[0][i]) ||
                    recalled.every((s, i) => s === -result.patterns[0][i]);
      if (match) successes++;
    }

    return { nPatterns, successRate: successes / nTrials };
  });
}
