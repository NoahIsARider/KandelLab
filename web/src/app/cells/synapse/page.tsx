'use client';

import { useState, useCallback } from 'react';
import { simulateSynapses, temporalSummation, spatialSummation } from '@/lib/cells/synapse';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function SynapsePage() {
  const [tau, setTau] = useState(5);
  const [weight, setWeight] = useState(2);
  const [nPulses, setNPulses] = useState(5);
  const [isi, setIsi] = useState(10);
  const [temporalResult, setTemporalResult] = useState<{ t: number[]; V: number[] } | null>(null);
  const [spatialResult, setSpatialResult] = useState<{ nInputs: number; peakV: number }[]>([]);

  const run = useCallback(() => {
    const t = temporalSummation({
      nPulses,
      isi: [isi],
      tau,
      weight,
      duration: 200,
    });
    setTemporalResult(t);

    const nInputs = linspace(1, 20, 15).map(Math.round);
    const s = spatialSummation({
      nInputs: nInputs as number[],
      tau,
      weight,
      duration: 200,
    });
    setSpatialResult(s);
  }, [tau, weight, nPulses, isi]);

  return (
    <article>
      <ChapterHeading>§5 Synapse Model — EPSP/IPSP and Spatiotemporal Integration</ChapterHeading>

      <FormulaBlock>
        ΔV(t) = w · (t-t<sub>s</sub>)/τ · exp(1 - (t-t<sub>s</sub>)/τ) · Θ(t-t<sub>s</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Synaptic events are described by an alpha function: a fast rise followed by a slow decay.
        Multiple synaptic inputs can summate in time (high-frequency pulses) or in space
        (many synapses active at once), driving the membrane potential to threshold.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Synaptic τ" value={tau} onChange={setTau} unit="ms" min={1} max={30} step={1} />
        <ParamField label="Weight w" value={weight} onChange={setWeight} unit="mV" min={0.1} max={10} step={0.1} />
        <ParamField label="Number of pulses" value={nPulses} onChange={setNPulses} unit="" min={1} max={20} step={1} />
        <ParamField label="Inter-pulse interval" value={isi} onChange={setIsi} unit="ms" min={1} max={100} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {temporalResult && (
        <ResultCard title="Temporal Summation">
          <Waveform data={temporalResult.V} height={80} label={`V (mV), ${nPulses} pulses, ISI = ${isi} ms`} />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Short ISI → pulses superimpose → larger peak (temporal summation)
          </p>
        </ResultCard>
      )}

      {spatialResult.length > 0 && (
        <ResultCard title="Spatial Summation (Peak Potential vs Number of Inputs)">
          <BarChart
            data={spatialResult.map(d => ({
              label: `${d.nInputs}`,
              value: d.peakV + 70,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            More inputs → larger peak depolarization (spatial summation)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
