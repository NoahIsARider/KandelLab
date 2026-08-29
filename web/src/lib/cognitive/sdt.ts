/** Signal Detection Theory: d', criterion, ROC curves */
import { normCdf, normInv, linspace } from '../math-utils';
import { SDT_PARAMS } from '../constants';

export interface SDTParams {
  d_prime: number;
  criterion: number;
}

/** Calculate hit rate and false alarm rate */
export function sdtRates(dPrime: number, criterion: number): {
  hitRate: number;
  falseAlarmRate: number;
  missRate: number;
  correctRejectionRate: number;
} {
  const hitRate = normCdf(dPrime - criterion);
  const falseAlarmRate = normCdf(-criterion);
  return {
    hitRate,
    falseAlarmRate,
    missRate: 1 - hitRate,
    correctRejectionRate: 1 - falseAlarmRate,
  };
}

/** Calculate d' from hit rate and false alarm rate */
export function dPrimeFromRates(hitRate: number, faRate: number): number {
  return normInv(hitRate) - normInv(faRate);
}

/** Calculate criterion from hit rate and false alarm rate */
export function criterionFromRates(hitRate: number, faRate: number): number {
  return -0.5 * (normInv(hitRate) + normInv(faRate));
}

/** Generate ROC curve */
export function rocCurve(params: {
  dPrime: number;
  nPoints?: number;
}): { faRate: number; hitRate: number; criterion: number }[] {
  const { dPrime, nPoints = 50 } = params;
  const criteria = linspace(-3, 3, nPoints);

  return criteria.map(c => {
    const rates = sdtRates(dPrime, c);
    return {
      faRate: rates.falseAlarmRate,
      hitRate: rates.hitRate,
      criterion: c,
    };
  });
}

/** Calculate AUC (Area Under ROC Curve) */
export function rocAUC(dPrime: number): number {
  return normCdf(dPrime / Math.sqrt(2));
}

/** Compare conditions: vary d' */
export function varyDSensitivity(params: {
  dPrimes: number[];
  criterion: number;
}): { dPrime: number; hitRate: number; faRate: number; dPrimeCalc: number; auc: number }[] {
  const { dPrimes, criterion } = params;

  return dPrimes.map(dPrime => {
    const rates = sdtRates(dPrime, criterion);
    return {
      dPrime,
      hitRate: rates.hitRate,
      faRate: rates.falseAlarmRate,
      dPrimeCalc: dPrimeFromRates(rates.hitRate, rates.falseAlarmRate),
      auc: rocAUC(dPrime),
    };
  });
}

/** Compare conditions: vary criterion */
export function varyCriterion(params: {
  dPrime: number;
  criteria: number[];
}): { criterion: number; hitRate: number; faRate: number; dPrimeCalc: number; bias: string }[] {
  const { dPrime, criteria } = params;

  return criteria.map(c => {
    const rates = sdtRates(dPrime, c);
    const bias = c > 0 ? 'conservative' : c < 0 ? 'liberal' : 'neutral';
    return {
      criterion: c,
      hitRate: rates.hitRate,
      faRate: rates.falseAlarmRate,
      dPrimeCalc: dPrimeFromRates(rates.hitRate, rates.falseAlarmRate),
      bias,
    };
  });
}
