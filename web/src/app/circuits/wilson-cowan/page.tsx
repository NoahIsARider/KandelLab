'use client';

import { useState, useCallback } from 'react';
import { simulateWC, findFixedPoints, nullclines, bifurcationSweep } from '@/lib/circuits/wilson-cowan';
import { WC_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function WilsonCowanPage() {
  const [P_ext, setP_ext] = useState(0);
  const [E0, setE0] = useState(0.1);
  const [I0, setI0] = useState(0.1);
  const [duration, setDuration] = useState(100);
  const [result, setResult] = useState<ReturnType<typeof simulateWC> | null>(null);
  const [fixedPts, setFixedPts] = useState<{ E: number; I: number; stable: boolean }[]>([]);
  const [bifurData, setBifurData] = useState<{ P: number; E_ss: number; I_ss: number; nFixed: number }[]>([]);

  const run = useCallback(() => {
    const wcParams = { ...WC_PARAMS, P_ext };
    const res = simulateWC({
      duration,
      dt: 0.1,
      E0,
      I0,
      wcParams,
    });
    setResult(res);

    const fps = findFixedPoints(wcParams);
    setFixedPts(fps);

    const PValues = linspace(-2, 5, 20);
    const bifur = bifurcationSweep({ PValues });
    setBifurData(bifur);
  }, [P_ext, E0, I0, duration]);

  return (
    <article>
      <ChapterHeading>§8 Wilson–Cowan Model — Excitatory–Inhibitory Population Dynamics</ChapterHeading>

      <FormulaBlock>
        τ<sub>E</sub> · dE/dt = -E + S(w<sub>EE</sub>E - w<sub>EI</sub>I + P - θ<sub>E</sub>)<br />
        τ<sub>I</sub> · dI/dt = -I + S(w<sub>IE</sub>E - w<sub>II</sub>I + Q - θ<sub>I</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Wilson–Cowan model describes the mean activity of excitatory (E) and inhibitory (I)
        neuronal populations. Depending on connection strengths and external inputs, the system can
        exhibit monostability, bistability (switching), oscillations, and other dynamical behaviors.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="P_ext" value={P_ext} onChange={setP_ext} unit="" min={-2} max={5} step={0.1} />
        <ParamField label="E₀" value={E0} onChange={setE0} min={0} max={1} step={0.05} />
        <ParamField label="I₀" value={I0} onChange={setI0} min={0} max={1} step={0.05} />
        <ParamField label="Duration" value={duration} onChange={setDuration} unit="" min={20} max={500} step={10} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <ResultCard title="Population Activity E(t), I(t)">
          <Waveform data={result.E} height={60} color="var(--verdigris)" label="E (excitatory)" />
          <Waveform data={result.I} height={60} color="var(--ochre)" label="I (inhibitory)" />
          <TextScatter
            points={result.E.map((e, i) => ({ x: e, y: result.I[i] }))}
            width={30}
            height={15}
            xLabel="E"
            yLabel="I"
          />
          <p className="text-xs text-[var(--ink-light)] mt-1">Phase-space trajectory (E, I)</p>
        </ResultCard>
      )}

      {fixedPts.length > 0 && (
        <ResultCard title="Fixed Points">
          <DataTable
            headers={['E*', 'I*', 'Stability']}
            rows={fixedPts.map(fp => [fp.E, fp.I, fp.stable ? 'stable' : 'unstable'])}
          />
        </ResultCard>
      )}

      {bifurData.length > 0 && (
        <ResultCard title="Bifurcation: E_ss vs P_ext">
          <BarChart
            data={bifurData.map(d => ({
              label: d.P.toFixed(1),
              value: d.E_ss,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Increasing P_ext → stronger excitatory activity; bistable switching may appear
          </p>
        </ResultCard>
      )}
    </article>
  );
}
