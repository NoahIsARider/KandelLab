/** Wilson-Cowan Model: Excitatory-Inhibitory population dynamics */
import { rk4Step, linspace, sigmoid } from '../math-utils';
import { WC_PARAMS } from '../constants';

export interface WCParams {
  tau_E: number;
  tau_I: number;
  w_EE: number;
  w_EI: number;
  w_IE: number;
  w_II: number;
  theta_E: number;
  theta_I: number;
  P_ext: number;
  Q_ext: number;
}

/** Wilson-Cowan sigmoid */
function S(x: number, beta: number = 1): number {
  return 1 / (1 + Math.exp(-beta * x));
}

/** WC ODE derivatives */
function wcDerivatives(state: number[], p: WCParams): number[] {
  const [E, I] = state;
  const { tau_E, tau_I, w_EE, w_EI, w_IE, w_II, theta_E, theta_I, P_ext, Q_ext } = p;

  const inputE = w_EE * E - w_EI * I + P_ext - theta_E;
  const inputI = w_IE * E - w_II * I + Q_ext - theta_I;

  const dE = (-E + S(inputE)) / tau_E;
  const dI = (-I + S(inputI)) / tau_I;

  return [dE, dI];
}

/** Simulate Wilson-Cowan dynamics */
export function simulateWC(params: {
  duration: number;
  dt: number;
  E0: number;
  I0: number;
  wcParams?: WCParams;
}): { t: number[]; E: number[]; I: number[] } {
  const { duration, dt, E0, I0 } = params;
  const p = params.wcParams || { ...WC_PARAMS };

  const steps = Math.ceil(duration / dt);
  const t: number[] = [];
  const E: number[] = [];
  const I: number[] = [];

  let state = [E0, I0];

  for (let i = 0; i <= steps; i++) {
    const time = i * dt;
    t.push(time);
    E.push(state[0]);
    I.push(state[1]);

    if (i < steps) {
      state = rk4Step(state, (_, s) => wcDerivatives(s, p), time, dt);
      state = state.map(v => Math.max(0, Math.min(1, v)));
    }
  }

  return { t, E, I };
}

/** Find fixed points */
export function findFixedPoints(p: WCParams): { E: number; I: number; stable: boolean }[] {
  // Grid search for fixed points
  const fixedPoints: { E: number; I: number; stable: boolean }[] = [];
  const n = 50;

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const E = i / n;
      const I = j / n;

      const inputE = p.w_EE * E - p.w_EI * I + p.P_ext - p.theta_E;
      const inputI = p.w_IE * E - p.w_II * I + p.Q_ext - p.theta_I;

      const E_null = S(inputE);
      const I_null = S(inputI);

      if (Math.abs(E - E_null) < 0.02 && Math.abs(I - I_null) < 0.02) {
        // Check stability via Jacobian
        const dSE = E_null * (1 - E_null);
        const dSI = I_null * (1 - I_null);
        const J11 = (-1 + p.w_EE * dSE) / p.tau_E;
        const J12 = (-p.w_EI * dSE) / p.tau_E;
        const J21 = (p.w_IE * dSI) / p.tau_I;
        const J22 = (-1 - p.w_II * dSI) / p.tau_I;

        const trace = J11 + J22;
        const det = J11 * J22 - J12 * J21;
        const stable = trace < 0 && det > 0;

        // Avoid duplicates
        const isDuplicate = fixedPoints.some(fp => Math.abs(fp.E - E) < 0.05 && Math.abs(fp.I - I) < 0.05);
        if (!isDuplicate) {
          fixedPoints.push({ E, I, stable });
        }
      }
    }
  }

  return fixedPoints;
}

/** Generate nullclines */
export function nullclines(p: WCParams, nPoints: number = 100): {
  E_nullcline: { E: number; I: number }[];
  I_nullcline: { E: number; I: number }[];
} {
  const EValues = linspace(0, 1, nPoints);

  // E-nullcline: E = S(w_EE*E - w_EI*I + P - θ_E)
  // Solve for I given E
  const E_null = EValues.map(E => {
    const inputE = p.w_EE * E + p.P_ext - p.theta_E;
    // E = S(inputE - w_EI*I) → S⁻¹(E) = inputE - w_EI*I
    const Sinv = Math.log(E / (1 - E + 1e-10));
    const I = (inputE - Sinv) / p.w_EI;
    return { E, I: Math.max(0, Math.min(1, I)) };
  });

  // I-nullcline: I = S(w_IE*E - w_II*I + Q - θ_I)
  const I_null = EValues.map(E => {
    const inputI = p.w_IE * E + p.Q_ext - p.theta_I;
    const Sinv = Math.log(E / (1 - E + 1e-10));
    const I_val = (inputI - Sinv) / p.w_II;
    return { E, I: Math.max(0, Math.min(1, I_val)) };
  });

  return { E_nullcline: E_null, I_nullcline: I_null };
}

/** Bifurcation: sweep P_ext */
export function bifurcationSweep(params: {
  PValues: number[];
  wcParams?: Partial<WCParams>;
}): { P: number; E_ss: number; I_ss: number; nFixed: number }[] {
  const { PValues } = params;

  return PValues.map(P => {
    const p: WCParams = { ...WC_PARAMS, ...params.wcParams, P_ext: P };
    const fps = findFixedPoints(p);
    // Return the stable fixed point with highest E
    const stable = fps.filter(f => f.stable);
    const best = stable.length > 0 ? stable.reduce((a, b) => a.E > b.E ? a : b) : { E: 0, I: 0 };
    return { P, E_ss: best.E, I_ss: best.I, nFixed: fps.length };
  });
}
