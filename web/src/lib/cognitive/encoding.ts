/** Population Encoding: tuning curves, Fisher information, Cramér-Rao bound */
import { linspace, normCdf } from '../math-utils';

export interface EncodingParams {
  nNeurons: number;
  stimulusRange: number[];
  tuningWidth: number;
  maxRate: number;
  baseline: number;
  noiseStd: number;
}

/** Single neuron tuning curve (von Mises / circular Gaussian) */
export function tuningCurve(stimulus: number, preferred: number, width: number, maxRate: number, baseline: number): number {
  let diff = Math.abs(stimulus - preferred);
  if (diff > Math.PI) diff = 2 * Math.PI - diff;
  return baseline + maxRate * Math.exp(-(diff ** 2) / (2 * width ** 2));
}

/** Population response */
export function populationResponse(params: {
  stimulus: number;
  nNeurons: number;
  tuningWidth: number;
  maxRate: number;
  baseline: number;
  noiseStd: number;
  seed?: number;
}): {
  preferredAngle: number[];
  response: number[];
  responseNoNoise: number[];
} {
  const { stimulus, nNeurons, tuningWidth, maxRate, baseline, noiseStd } = params;
  const preferredAngle = linspace(0, 2 * Math.PI, nNeurons + 1).slice(0, -1);

  const responseNoNoise = preferredAngle.map(pref =>
    tuningCurve(stimulus, pref, tuningWidth, maxRate, baseline)
  );

  // Add noise
  const response = responseNoNoise.map(r => Math.max(0, r + noiseStd * (Math.random() - 0.5) * 2));

  return { preferredAngle, response, responseNoNoise };
}

/** Fisher information for population code */
export function fisherInformation(params: {
  stimulus: number;
  nNeurons: number;
  tuningWidth: number;
  maxRate: number;
  baseline: number;
  noiseStd: number;
}): number {
  const { stimulus, nNeurons, tuningWidth, maxRate, baseline, noiseStd } = params;
  const preferredAngle = linspace(0, 2 * Math.PI, nNeurons + 1).slice(0, -1);

  let J = 0;
  for (const pref of preferredAngle) {
    const r = tuningCurve(stimulus, pref, tuningWidth, maxRate, baseline);
    // Derivative of tuning curve w.r.t. stimulus
    let diff = stimulus - pref;
    if (diff > Math.PI) diff -= 2 * Math.PI;
    if (diff < -Math.PI) diff += 2 * Math.PI;
    const dr_dtheta = -(r - baseline) * diff / (tuningWidth ** 2);
    J += (dr_dtheta ** 2) / (noiseStd ** 2);
  }

  return J;
}

/** Cramér-Rao bound: minimum decoding variance */
export function cramerRaoBound(J: number): number {
  return 1 / J;
}

/** Effect of noise on decoding accuracy */
export function noiseEffect(params: {
  noiseLevels: number[];
  nNeurons: number;
  stimulus: number;
  tuningWidth: number;
  maxRate: number;
  baseline: number;
}): { noiseStd: number; fisherInfo: number; crb: number; minStd: number }[] {
  const { noiseLevels, nNeurons, stimulus, tuningWidth, maxRate, baseline } = params;

  return noiseLevels.map(noiseStd => {
    const J = fisherInformation({ stimulus, nNeurons, tuningWidth, maxRate, baseline, noiseStd });
    const crb = cramerRaoBound(J);
    return {
      noiseStd,
      fisherInfo: J,
      crb,
      minStd: Math.sqrt(crb),
    };
  });
}

/** Effect of population size on decoding accuracy */
export function populationSizeEffect(params: {
  nNeuronsRange: number[];
  stimulus: number;
  tuningWidth: number;
  maxRate: number;
  baseline: number;
  noiseStd: number;
}): { nNeurons: number; fisherInfo: number; crb: number; minStd: number }[] {
  const { nNeuronsRange, stimulus, tuningWidth, maxRate, baseline, noiseStd } = params;

  return nNeuronsRange.map(nNeurons => {
    const J = fisherInformation({ stimulus, nNeurons, tuningWidth, maxRate, baseline, noiseStd });
    const crb = cramerRaoBound(J);
    return {
      nNeurons,
      fisherInfo: J,
      crb,
      minStd: Math.sqrt(crb),
    };
  });
}

/** ML decoder: find stimulus that maximizes likelihood */
export function mlDecoder(params: {
  responses: number[];
  preferredAngles: number[];
  tuningWidth: number;
  maxRate: number;
  baseline: number;
  nCandidates: number;
}): { estimated: number; candidates: { stimulus: number; likelihood: number }[] } {
  const { responses, preferredAngles, tuningWidth, maxRate, baseline, nCandidates } = params;
  const candidates = linspace(0, 2 * Math.PI, nCandidates);

  const likelihoods = candidates.map(stimulus => {
    let logLik = 0;
    for (let i = 0; i < responses.length; i++) {
      const expected = tuningCurve(stimulus, preferredAngles[i], tuningWidth, maxRate, baseline);
      logLik += -0.5 * (responses[i] - expected) ** 2;
    }
    return { stimulus, likelihood: logLik };
  });

  const best = likelihoods.reduce((a, b) => a.likelihood > b.likelihood ? a : b);

  return { estimated: best.stimulus, candidates: likelihoods };
}
