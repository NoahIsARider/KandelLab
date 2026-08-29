'use client';

import { useState, useCallback } from 'react';
import { simulateLIF, fICurve, rasterPlot } from '@/lib/cells/lif';
import { LIF_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function LIFPage() {
  const [duration, setDuration] = useState(500);
  const [current, setCurrent] = useState(2);
  const [result, setResult] = useState<ReturnType<typeof simulateLIF> | null>(null);
  const [fiData, setFiData] = useState<{ I: number; freq_analytical: number; freq_numerical: number }[]>([]);
  const [raster, setRaster] = useState<{ neuronIdx: number; spikeTime: number }[]>([]);

  const run = useCallback(() => {
    const res = simulateLIF({
      duration,
      dt: 0.1,
      I_ext: () => current,
    });
    setResult(res);

    const currents = linspace(0, 5, 20);
    const fi = fICurve({ currents, duration: 2000 });
    setFiData(fi);

    const r = rasterPlot({
      nNeurons: 10,
      duration: 1000,
      dt: 0.1,
      I_ext: () => current,
    });
    setRaster(r);
  }, [duration, current]);

  return (
    <article>
      <ChapterHeading>§4 Leaky Integrate-and-Fire — Spiking Neuron Model</ChapterHeading>

      <FormulaBlock>
        τ · dV/dt = -(V - E<sub>L</sub>) + R · I<br />
        When V ≥ V<sub>thresh</sub>, a spike is emitted, V → V<sub>reset</sub>, with refractory period t<sub>ref</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The LIF model is the simplest model of neuronal spike generation. The membrane potential decays
        exponentially toward the resting potential while external current drives depolarization.
        When the threshold is reached, a spike is emitted and the potential resets.
        The f-I curve can be solved analytically, and numerical simulations agree closely with the
        analytical result.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Duration" value={duration} onChange={setDuration} unit="ms" min={100} max={2000} step={50} />
        <ParamField label="Input current" value={current} onChange={setCurrent} unit="nA" min={0} max={10} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Membrane Potential V(t)">
            <Waveform data={result.V} height={100} label={`V (mV), ${result.spikes.length} spikes`} />
          </ResultCard>

          <ResultCard title="Spike Times">
            <DataTable
              headers={['Spike #', 'Time (ms)']}
              rows={result.spikes.slice(0, 20).map((t, i) => [i + 1, t])}
            />
            {result.spikes.length > 20 && (
              <p className="text-xs text-[var(--ink-light)] mt-1">... {result.spikes.length} spikes in total</p>
            )}
          </ResultCard>
        </>
      )}

      {fiData.length > 0 && (
        <ResultCard title="f-I Curve (Analytical vs Numerical)">
          <DataTable
            headers={['I (nA)', 'f_analytical (Hz)', 'f_numerical (Hz)']}
            rows={fiData.filter((_, i) => i % 2 === 0).map(d => [d.I, d.freq_analytical, d.freq_numerical])}
          />
          <TextScatter
            points={fiData.map(d => ({ x: d.I, y: d.freq_numerical }))}
            xLabel="I (nA)"
            yLabel="f (Hz)"
          />
        </ResultCard>
      )}

      {raster.length > 0 && (
        <ResultCard title="Raster Plot (10 Neurons)">
          <TextScatter
            points={raster.map(s => ({ x: s.spikeTime, y: s.neuronIdx }))}
            width={50}
            height={10}
            xLabel="time (ms)"
            yLabel="neuron"
          />
        </ResultCard>
      )}
    </article>
  );
}
