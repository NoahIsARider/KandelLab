/** Audition: Frequency tuning, gamma-tone filter bank, tonotopy */
import { linspace, seededRandom } from '../math-utils';

export interface GammaToneParams {
  cf: number;        // center frequency (Hz)
  bw: number;        // bandwidth (Hz)
  order: number;     // filter order
  duration: number;  // seconds
  fs: number;        // sampling rate (Hz)
}

/** ERB (Equivalent Rectangular Bandwidth) */
export function erb(cf: number): number {
  return 24.7 * (4.37 * cf / 1000 + 1);
}

/** Gamma-tone filter impulse response */
export function gammaToneIR(params: GammaToneParams): { t: number[]; ir: number[] } {
  const { cf, bw, order, duration, fs } = params;
  const nSamples = Math.floor(duration * fs);
  const t: number[] = [];
  const ir: number[] = [];

  for (let i = 0; i < nSamples; i++) {
    const ti = i / fs;
    t.push(ti * 1000); // ms
    const envelope = ti ** (order - 1) * Math.exp(-2 * Math.PI * bw * ti);
    const carrier = Math.cos(2 * Math.PI * cf * ti);
    ir.push(envelope * carrier);
  }

  return { t, ir };
}

/** Filter bank: multiple gamma-tone filters */
export function filterBank(params: {
  cfValues: number[];
  duration: number;
  fs: number;
  order?: number;
}): {
  cf: number[];
  responses: { t: number[]; ir: number[] }[];
} {
  const { cfValues, duration, fs, order = 4 } = params;

  const responses = cfValues.map(cf => {
    const bw = erb(cf);
    return gammaToneIR({ cf, bw, order, duration, fs });
  });

  return { cf: cfValues, responses };
}

/** Frequency tuning curve: response vs frequency for a single filter */
export function frequencyTuning(params: {
  cf: number;
  frequencies: number[];
  bandwidth?: number;
}): { freq: number; response: number }[] {
  const { cf, frequencies } = params;
  const bw = params.bandwidth || erb(cf);

  return frequencies.map(freq => {
    const diff = (freq - cf) / bw;
    const response = Math.exp(-0.5 * diff ** 2);
    return { freq, response };
  });
}

/** Tonotopic map: CF as function of position along basilar membrane */
export function tonotopicMap(params: {
  nPositions: number;
  cfMin?: number;
  cfMax?: number;
}): { position: number; cf: number }[] {
  const { nPositions, cfMin = 100, cfMax = 8000 } = params;
  const positions = linspace(0, 1, nPositions);

  // Greenwood function approximation (log scale)
  return positions.map(pos => {
    const cf = cfMin * Math.pow(cfMax / cfMin, 1 - pos);
    return { position: pos, cf };
  });
}

/** Generate frequency tuning data for multiple neurons */
export function populationTuning(params: {
  nNeurons: number;
  frequencies: number[];
  cfMin?: number;
  cfMax?: number;
}): {
  neurons: { cf: number; tuning: { freq: number; response: number }[] }[];
} {
  const { nNeurons, frequencies, cfMin = 200, cfMax = 4000 } = params;
  const cfValues = linspace(cfMin, cfMax, nNeurons);

  const neurons = cfValues.map(cf => ({
    cf,
    tuning: frequencyTuning({ cf, frequencies }),
  }));

  return { neurons };
}
