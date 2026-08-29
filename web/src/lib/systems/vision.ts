/** Vision: Gabor filters, orientation tuning, receptive fields */
import { linspace } from '../math-utils';

export interface GaborParams {
  theta: number;      // orientation (radians)
  lambda: number;     // wavelength
  sigma: number;      // Gaussian envelope width
  gamma: number;      // aspect ratio
  psi: number;        // phase offset
  size: number;       // kernel size
}

/** 2D Gabor filter kernel */
export function gaborKernel(params: GaborParams): number[][] {
  const { theta, lambda, sigma, gamma, psi, size } = params;
  const half = Math.floor(size / 2);
  const kernel: number[][] = [];

  const cosT = Math.cos(theta);
  const sinT = Math.sin(theta);

  for (let i = 0; i < size; i++) {
    kernel[i] = [];
    for (let j = 0; j < size; j++) {
      const x = i - half;
      const y = j - half;
      const xRot = x * cosT + y * sinT;
      const yRot = -x * sinT + y * cosT;

      const gaussian = Math.exp(-(xRot ** 2 + gamma ** 2 * yRot ** 2) / (2 * sigma ** 2));
      const sinusoidal = Math.cos(2 * Math.PI * xRot / lambda + psi);
      kernel[i][j] = gaussian * sinusoidal;
    }
  }

  return kernel;
}

/** Orientation tuning curve */
export function orientationTuning(params: {
  preferredAngle: number;
  angles: number[];
  bandwidth: number;
  maxResponse: number;
  baseline: number;
}): { angle: number; response: number }[] {
  const { preferredAngle, angles, bandwidth, maxResponse, baseline } = params;

  return angles.map(angle => {
    let diff = Math.abs(angle - preferredAngle);
    if (diff > Math.PI) diff = 2 * Math.PI - diff;
    const response = baseline + maxResponse * Math.exp(-(diff ** 2) / (2 * bandwidth ** 2));
    return { angle, response };
  });
}

/** Simulate V1 simple cell responses to different orientations */
export function simulateSimpleCell(params: {
  nAngles: number;
  preferredAngle: number;
  gaborParams: Partial<GaborParams>;
}): {
  angle: number;
  response: number;
  tuningCurve: { angle: number; response: number }[];
} {
  const { nAngles, preferredAngle, gaborParams } = params;
  const angles = linspace(0, Math.PI, nAngles);

  const tuningCurve = angles.map(angle => {
    const kernel = gaborKernel({
      theta: angle,
      lambda: gaborParams.lambda || 10,
      sigma: gaborParams.sigma || 4,
      gamma: gaborParams.gamma || 0.5,
      psi: gaborParams.psi || 0,
      size: gaborParams.size || 21,
    });

    // Response = sum of squared kernel values (energy)
    let response = 0;
    for (const row of kernel) {
      for (const val of row) {
        response += val * val;
      }
    }

    return { angle, response };
  });

  // Normalize
  const maxResp = Math.max(...tuningCurve.map(t => t.response));
  const normalized = tuningCurve.map(t => ({
    angle: t.angle,
    response: t.response / maxResp,
  }));

  return {
    angle: preferredAngle,
    response: 1,
    tuningCurve: normalized,
  };
}

/** Generate receptive field heatmap data */
export function receptiveFieldData(params: GaborParams): {
  data: number[][];
  size: number;
  minVal: number;
  maxVal: number;
} {
  const kernel = gaborKernel(params);
  let minVal = Infinity, maxVal = -Infinity;

  for (const row of kernel) {
    for (const val of row) {
      minVal = Math.min(minVal, val);
      maxVal = Math.max(maxVal, val);
    }
  }

  return { data: kernel, size: params.size, minVal, maxVal };
}
