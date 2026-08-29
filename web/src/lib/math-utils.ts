/** Numerical methods and math utilities */

/** Euler method for ODE integration */
export function eulerStep(
  y: number[],
  dydt: (t: number, y: number[]) => number[],
  t: number,
  dt: number
): number[] {
  const dy = dydt(t, y);
  return y.map((val, i) => val + dy[i] * dt);
}

/** RK4 method for ODE integration */
export function rk4Step(
  y: number[],
  dydt: (t: number, y: number[]) => number[],
  t: number,
  dt: number
): number[] {
  const n = y.length;
  const k1 = dydt(t, y);
  const y2 = y.map((val, i) => val + 0.5 * dt * k1[i]);
  const k2 = dydt(t + 0.5 * dt, y2);
  const y3 = y.map((val, i) => val + 0.5 * dt * k2[i]);
  const k3 = dydt(t + 0.5 * dt, y3);
  const y4 = y.map((val, i) => val + dt * k3[i]);
  const k4 = dydt(t + dt, y4);

  return y.map((val, i) =>
    val + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
  );
}

/** Integrate ODE using RK4 over a time range */
export function integrateRK4(
  y0: number[],
  dydt: (t: number, y: number[]) => number[],
  tStart: number,
  tEnd: number,
  dt: number
): { t: number[]; y: number[][] } {
  const steps = Math.ceil((tEnd - tStart) / dt);
  const tArr: number[] = [];
  const yArr: number[][] = [];

  let y = [...y0];
  let t = tStart;

  for (let i = 0; i <= steps; i++) {
    tArr.push(t);
    yArr.push([...y]);
    if (i < steps) {
      y = rk4Step(y, dydt, t, dt);
      t = tStart + (i + 1) * dt;
    }
  }

  return { t: tArr, y: yArr };
}

/** Standard normal random (Box-Muller) */
export function randn(): number {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/** Seeded random number generator (mulberry32) */
export function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s |= 0;
    s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Seeded normal random */
export function seededRandn(rng: () => number): number {
  let u = 0, v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/** Inverse normal CDF (probit function) - rational approximation */
export function normInv(p: number): number {
  if (p <= 0) return -Infinity;
  if (p >= 1) return Infinity;
  if (p === 0.5) return 0;

  const a = [
    -3.969683028665376e1, 2.209460984245205e2,
    -2.759285104469687e2, 1.383577518672690e2,
    -3.066479806614716e1, 2.506628277459239e0,
  ];
  const b = [
    -5.447609879822406e1, 1.615858368580409e2,
    -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1,
  ];
  const c = [
    -7.784894002430293e-3, -3.223964580411365e-1,
    -2.400758277161838e0, -2.549732539343734e0,
    4.374664141464968e0, 2.938163982698783e0,
  ];
  const d = [
    7.784695709041462e-3, 3.224671290700398e-1,
    2.445134137142996e0, 3.754408661907416e0,
  ];

  const pLow = 0.02425;
  const pHigh = 1 - pLow;

  let q: number, r: number;

  if (p < pLow) {
    q = Math.sqrt(-2 * Math.log(p));
    return (
      (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
      ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    );
  } else if (p <= pHigh) {
    q = p - 0.5;
    r = q * q;
    return (
      ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q) /
      (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    );
  } else {
    q = Math.sqrt(-2 * Math.log(1 - p));
    return -(
      (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
      ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    );
  }
}

/** Standard normal CDF */
export function normCdf(x: number): number {
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;

  const sign = x < 0 ? -1 : 1;
  const absX = Math.abs(x);
  const t = 1.0 / (1.0 + p * absX);
  const y = 1.0 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-absX * absX / 2);

  return 0.5 * (1.0 + sign * y);
}

/** Sigmoid function */
export function sigmoid(x: number, beta: number = 1, theta: number = 0): number {
  return 1 / (1 + Math.exp(-beta * (x - theta)));
}

/** Mean of array */
export function mean(arr: number[]): number {
  return arr.reduce((s, v) => s + v, 0) / arr.length;
}

/** Standard deviation */
export function std(arr: number[]): number {
  const m = mean(arr);
  return Math.sqrt(arr.reduce((s, v) => s + (v - m) ** 2, 0) / arr.length);
}

/** Linearly spaced array */
export function linspace(start: number, stop: number, n: number): number[] {
  const step = (stop - start) / (n - 1);
  return Array.from({ length: n }, (_, i) => start + step * i);
}

/** Dot product */
export function dot(a: number[], b: number[]): number {
  return a.reduce((s, v, i) => s + v * b[i], 0);
}

/** Matrix-vector multiply */
export function matVecMul(mat: number[][], vec: number[]): number[] {
  return mat.map(row => dot(row, vec));
}

/** Clamp value */
export function clamp(val: number, min: number, max: number): number {
  return Math.min(Math.max(val, min), max);
}
