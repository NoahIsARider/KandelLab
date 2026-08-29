/** Lateral Inhibition: DOG receptive field, edge enhancement, Mach bands */
import { linspace } from '../math-utils';

export interface DOGParams {
  sigmaCenter: number;
  sigmaSurround: number;
  amplitudeCenter: number;
  amplitudeSurround: number;
  size: number;
}

/** 1D Difference-of-Gaussians kernel */
export function dogKernel1D(x: number[], params: DOGParams): number[] {
  const { sigmaCenter, sigmaSurround, amplitudeCenter, amplitudeSurround } = params;
  return x.map(xi => {
    const center = amplitudeCenter * Math.exp(-(xi ** 2) / (2 * sigmaCenter ** 2));
    const surround = amplitudeSurround * Math.exp(-(xi ** 2) / (2 * sigmaSurround ** 2));
    return center - surround;
  });
}

/** 2D DOG kernel */
export function dogKernel2D(params: DOGParams): number[][] {
  const { size, sigmaCenter, sigmaSurround, amplitudeCenter, amplitudeSurround } = params;
  const half = Math.floor(size / 2);
  const kernel: number[][] = [];

  for (let i = 0; i < size; i++) {
    kernel[i] = [];
    for (let j = 0; j < size; j++) {
      const x = i - half;
      const y = j - half;
      const r2 = x * x + y * y;
      const center = amplitudeCenter * Math.exp(-r2 / (2 * sigmaCenter ** 2));
      const surround = amplitudeSurround * Math.exp(-r2 / (2 * sigmaSurround ** 2));
      kernel[i][j] = center - surround;
    }
  }

  return kernel;
}

/** 1D convolution */
export function convolve1D(signal: number[], kernel: number[]): number[] {
  const n = signal.length;
  const k = kernel.length;
  const half = Math.floor(k / 2);
  const result: number[] = [];

  for (let i = 0; i < n; i++) {
    let sum = 0;
    for (let j = 0; j < k; j++) {
      const idx = i + j - half;
      if (idx >= 0 && idx < n) {
        sum += signal[idx] * kernel[j];
      }
    }
    result.push(sum);
  }

  return result;
}

/** Simulate lateral inhibition on a 1D stimulus */
export function simulateLateralInhibition(params: {
  stimulus: number[];
  dogParams: DOGParams;
}): {
  x: number[];
  stimulus: number[];
  response: number[];
  kernel: number[];
} {
  const { stimulus, dogParams } = params;
  const x = linspace(0, stimulus.length - 1, stimulus.length);
  const kx = linspace(-dogParams.size / 2, dogParams.size / 2, dogParams.size);
  const kernel = dogKernel1D(kx, dogParams);
  const response = convolve1D(stimulus, kernel);

  return { x: x as number[], stimulus, response, kernel };
}

/** Generate Mach bands stimulus */
export function machBandsStimulus(n: number, nBands: number = 5): number[] {
  const stimulus: number[] = [];
  const bandWidth = Math.floor(n / nBands);

  for (let b = 0; b < nBands; b++) {
    const intensity = (b + 1) / nBands;
    for (let i = 0; i < bandWidth && stimulus.length < n; i++) {
      stimulus.push(intensity);
    }
  }

  return stimulus;
}

/** Generate edge stimulus */
export function edgeStimulus(n: number, edgePos: number = 0.5): number[] {
  return Array.from({ length: n }, (_, i) => i / n < edgePos ? 0.2 : 0.8);
}

/** Generate gradient stimulus */
export function gradientStimulus(n: number): number[] {
  return Array.from({ length: n }, (_, i) => i / n);
}
