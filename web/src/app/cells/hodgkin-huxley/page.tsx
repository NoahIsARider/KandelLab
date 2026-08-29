'use client';

import { useState, useCallback } from 'react';
import { simulateHH, fICurve, findThreshold } from '@/lib/cells/hodgkin-huxley';
import { HH_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function HodgkinHuxleyPage() {
  const [duration, setDuration] = useState(100);
  const [stimCurrent, setStimCurrent] = useState(10);
  const [stimStart, setStimStart] = useState(10);
  const [stimEnd, setStimEnd] = useState(90);
  const [result, setResult] = useState<ReturnType<typeof simulateHH> | null>(null);
  const [fiData, setFiData] = useState<{ I: number; freq: number }[]>([]);
  const [threshold, setThreshold] = useState(0);

  const run = useCallback(() => {
    const s = stimStart;
    const e = stimEnd;
    const I = stimCurrent;
    const res = simulateHH({
      duration,
      dt: 0.01,
      I_ext: (t) => (t >= s && t <= e) ? I : 0,
    });
    setResult(res);

    const currents = linspace(0, 20, 15);
    const fi = fICurve({ currents, duration: 500, dt: 0.01 });
    setFiData(fi);

    const thresh = findThreshold();
    setThreshold(thresh);
  }, [duration, stimCurrent, stimStart, stimEnd]);

  return (
    <article>
      <ChapterHeading>§3 Hodgkin–Huxley Model — Action Potential</ChapterHeading>

      <FormulaBlock>
        C<sub>m</sub> dV/dt = -g<sub>Na</sub>m³h(V-E<sub>Na</sub>) - g<sub>K</sub>n⁴(V-E<sub>K</sub>) - g<sub>L</sub>(V-E<sub>L</sub>) + I<sub>ext</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Hodgkin–Huxley model describes action potential generation with four coupled ODEs.
        The sodium channel activation (m) and inactivation (h) gating variables, together with the
        potassium channel activation (n) gating variable, determine the membrane&apos;s excitability.
        Solved numerically with the RK4 method.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Duration" value={duration} onChange={setDuration} unit="ms" min={20} max={500} step={10} />
        <ParamField label="Stimulus current" value={stimCurrent} onChange={setStimCurrent} unit="µA/cm²" min={0} max={30} step={0.5} />
        <ParamField label="Stimulus start" value={stimStart} onChange={setStimStart} unit="ms" min={0} max={50} step={1} />
        <ParamField label="Stimulus end" value={stimEnd} onChange={setStimEnd} unit="ms" min={10} max={500} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Membrane Potential V(t)">
            <Waveform data={result.V} height={100} label={`V (mV), peak ${Math.max(...result.V).toFixed(1)} mV`} />
          </ResultCard>

          <ResultCard title="Gating Variables m, h, n">
            <Waveform data={result.m} height={50} color="var(--verdigris)" label="m (Na⁺ activation)" />
            <Waveform data={result.h} height={50} color="var(--ochre)" label="h (Na⁺ inactivation)" />
            <Waveform data={result.n} height={50} color="var(--oxide)" label="n (K⁺ activation)" />
          </ResultCard>

          <ResultCard title="Ionic Conductances">
            <Waveform data={result.gNa} height={50} color="var(--verdigris)" label={`g_Na (mS/cm²), peak ${Math.max(...result.gNa).toFixed(1)}`} />
            <Waveform data={result.gK} height={50} color="var(--ochre)" label={`g_K (mS/cm²), peak ${Math.max(...result.gK).toFixed(1)}`} />
          </ResultCard>
        </>
      )}

      <ResultCard title="Key Features">
        <DataTable
          headers={['Parameter', 'Value']}
          rows={[
            ['Resting potential', `${HH_PARAMS.V_rest} mV`],
            ['Firing threshold (numerical)', `${threshold.toFixed(1)} mV`],
            ['Na⁺ reversal potential', `${HH_PARAMS.E_Na} mV`],
            ['K⁺ reversal potential', `${HH_PARAMS.E_K} mV`],
            ['Maximum g_Na', `${HH_PARAMS.g_Na} mS/cm²`],
            ['Maximum g_K', `${HH_PARAMS.g_K} mS/cm²`],
          ]}
        />
      </ResultCard>

      {fiData.length > 0 && (
        <ResultCard title="f-I Curve (Firing Rate vs Input Current)">
          <BarChart
            data={fiData.map(d => ({
              label: `${d.I.toFixed(1)}`,
              value: d.freq,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Firing rate increases monotonically with input current (I in µA/cm², f in Hz)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
