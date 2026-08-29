/**
 * KandelLab — Neuroscience Principles Code Lab (TypeScript core)
 *
 * Pure, dependency-free implementations of the classic neuroscience models:
 * cells → circuits → systems → cognition. All functions are deterministic
 * and browser-safe (no Node APIs).
 */

// Physical constants & math utilities
export * from './constants';
export * from './math-utils';

// cells — single-neuron models
export * from './cells/nernst';
export * from './cells/goldman';
// fICurve is exported by both HH and LIF; disambiguate with namespaced aliases
export {
  steadyState,
  simulateHH,
  findThreshold,
  type HHParams,
  type HHState,
} from './cells/hodgkin-huxley';
export { fICurve as hhFICurve } from './cells/hodgkin-huxley';
export * from './cells/lif';
export { fICurve as lifFICurve } from './cells/lif';
export * from './cells/synapse';

// circuits — multi-neuron interactions
export * from './circuits/hebbian';
export * from './circuits/kuramoto';
export * from './circuits/lateral-inhibition';
export * from './circuits/wilson-cowan';

// systems — sensory, motor, memory, reward
export * from './systems/vision';
export * from './systems/audition';
export * from './systems/motor';
export * from './systems/memory';
export * from './systems/reward';

// cognitive — decision-making and coding
export * from './cognitive/ddm';
export * from './cognitive/sdt';
export * from './cognitive/encoding';
