/** Synapse Model: EPSP/IPSP, temporal and spatial summation */
import { SYNAPSE_PARAMS } from '../constants';

export interface SynapseParams {
  tau_epsp: number;
  tau_ipsp: number;
  w_epsp: number;
  w_ipsp: number;
}

/** Single synaptic event (alpha function) */
export function synapticEvent(t: number, t_synapse: number, tau: number, weight: number): number {
  const dt = t - t_synapse;
  if (dt < 0) return 0;
  const alpha = (dt / tau) * Math.exp(1 - dt / tau);
  return weight * alpha;
}

/** Simulate membrane potential with synaptic inputs */
export function simulateSynapses(params: {
  duration: number;
  dt: number;
  E_L: number;
  tau_m: number;
  events: { time: number; type: 'EPSP' | 'IPSP'; weight?: number }[];
  synParams?: SynapseParams;
}): { t: number[]; V: number[]; totalSynaptic: number[] } {
  const { duration, dt, E_L, tau_m, events } = params;
  const sp = params.synParams || { ...SYNAPSE_PARAMS };

  const steps = Math.ceil(duration / dt);
  const t: number[] = [];
  const V: number[] = [];
  const totalSynaptic: number[] = [];

  for (let i = 0; i <= steps; i++) {
    const time = i * dt;
    t.push(time);

    // Sum all synaptic events
    let synTotal = 0;
    for (const event of events) {
      const tau = event.type === 'EPSP' ? sp.tau_epsp : sp.tau_ipsp;
      const w = event.weight ?? (event.type === 'EPSP' ? sp.w_epsp : sp.w_ipsp);
      synTotal += synapticEvent(time, event.time, tau, w);
    }
    totalSynaptic.push(synTotal);

    // Membrane response (simplified: exponential decay + synaptic drive)
    const V_syn = E_L + synTotal;
    V.push(V_syn);
  }

  return { t, V, totalSynaptic };
}

/** Temporal summation: multiple pulses at different frequencies */
export function temporalSummation(params: {
  nPulses: number;
  isi: number[];  // inter-stimulus intervals (ms)
  tau: number;
  weight: number;
  duration: number;
}): { t: number[]; V: number[] } {
  const { nPulses, isi, tau, weight, duration } = params;
  const dt = 0.1;

  // Generate spike times
  const events: { time: number; type: 'EPSP' | 'IPSP'; weight?: number }[] = [];
  let time = 10; // start at 10ms
  for (let i = 0; i < nPulses; i++) {
    events.push({ time, type: 'EPSP', weight });
    time += isi[Math.min(i, isi.length - 1)];
  }

  const result = simulateSynapses({
    duration,
    dt,
    E_L: -70,
    tau_m: 20,
    events,
    synParams: { tau_epsp: tau, tau_ipsp: tau, w_epsp: weight, w_ipsp: -weight },
  });

  return { t: result.t, V: result.V };
}

/** Spatial summation: multiple inputs at same time */
export function spatialSummation(params: {
  nInputs: number[];
  tau: number;
  weight: number;
  duration: number;
}): { nInputs: number; peakV: number }[] {
  const { nInputs, tau, weight, duration } = params;

  return nInputs.map(n => {
    const events: { time: number; type: 'EPSP' | 'IPSP'; weight?: number }[] = [];
    for (let i = 0; i < n; i++) {
      events.push({ time: 10 + i * 0.5, type: 'EPSP', weight });
    }

    const result = simulateSynapses({
      duration,
      dt: 0.1,
      E_L: -70,
      tau_m: 20,
      events,
      synParams: { tau_epsp: tau, tau_ipsp: tau, w_epsp: weight, w_ipsp: -weight },
    });

    const peakV = Math.max(...result.V);
    return { nInputs: n, peakV };
  });
}
