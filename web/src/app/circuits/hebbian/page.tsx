'use client';

import { useState, useCallback } from 'react';
import { simulateHebbian, simulateBCM, ltpLtdCurve } from '@/lib/circuits/hebbian';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function HebbianPage() {
  const [eta, setEta] = useState(0.01);
  const [nPre, setNPre] = useState(10);
  const [nSteps, setNSteps] = useState(500);
  const [correlated, setCorrelated] = useState(true);
  const [hebbResult, setHebbResult] = useState<ReturnType<typeof simulateHebbian> | null>(null);
  const [bcmResult, setBcmResult] = useState<ReturnType<typeof simulateBCM> | null>(null);
  const [ltpData, setLtpData] = useState<{ dt: number; dw: number }[]>([]);

  const run = useCallback(() => {
    const h = simulateHebbian({
      nPre,
      nPost: 1,
      nSteps,
      eta,
      correlated,
    });
    setHebbResult(h);

    const b = simulateBCM({
      nSteps,
      eta,
      inputRate: [0.3, 0.5, 0.8, 0.5, 0.3],
    });
    setBcmResult(b);

    const dtRange = linspace(-50, 50, 50);
    const ltp = ltpLtdCurve({
      dtRange,
      tauPlus: 20,
      tauMinus: 20,
      APlus: 1,
      AMinus: 0.5,
    });
    setLtpData(ltp);
  }, [eta, nPre, nSteps, correlated]);

  return (
    <article>
      <ChapterHeading>§6 Hebbian Learning — Synaptic Plasticity</ChapterHeading>

      <FormulaBlock>
        Hebb: Δw = η · x · y<br />
        BCM: Δw = η · x · y · (y - θ<sub>M</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Hebb&apos;s rule: connections between neurons that fire together are strengthened.
        The BCM rule introduces a sliding threshold θ<sub>M</sub>: postsynaptic activity above the
        threshold produces LTP, while activity below it produces LTD.
        STDP (spike-timing-dependent plasticity) refines this to millisecond-scale timing.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Learning rate η" value={eta} onChange={setEta} min={0.001} max={0.1} step={0.001} />
        <ParamField label="Number of presynaptic neurons" value={nPre} onChange={setNPre} min={3} max={20} step={1} />
        <ParamField label="Number of steps" value={nSteps} onChange={setNSteps} min={100} max={2000} step={100} />
        <div className="flex items-center gap-3 mt-2">
          <label className="text-sm text-[var(--ink)] font-[var(--font-display)] min-w-[120px]">Input pattern</label>
          <select
            value={correlated ? 'correlated' : 'random'}
            onChange={(e) => setCorrelated(e.target.value === 'correlated')}
            className="param-input w-auto"
          >
            <option value="correlated">Correlated input</option>
            <option value="random">Random input</option>
          </select>
        </div>
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {hebbResult && (
        <ResultCard title="Hebbian Weight Evolution">
          <p className="text-xs text-[var(--ink-light)] mb-2">
            Final weights ({nPre} presynaptic neurons → 1 postsynaptic)
          </p>
          <BarChart
            data={hebbResult.weights[hebbResult.weights.length - 1].map((w, i) => ({
              label: `w${i}`,
              value: w,
              color: w > 0 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            {correlated ? 'Correlated input → specific weights selectively strengthened (selective learning)' : 'Random input → weights stay uniform'}
          </p>
        </ResultCard>
      )}

      {bcmResult && (
        <ResultCard title="BCM Sliding Threshold">
          <Waveform data={bcmResult.weight} height={60} color="var(--verdigris)" label="Synaptic weight w(t)" />
          <Waveform data={bcmResult.theta_M} height={60} color="var(--ochre)" label="Sliding threshold θ_M(t)" />
        </ResultCard>
      )}

      {ltpData.length > 0 && (
        <ResultCard title="STDP Learning Window (LTP–LTD Curve)">
          <BarChart
            data={ltpData.filter((_, i) => i % 2 === 0).map(d => ({
              label: `${d.dt.toFixed(0)}`,
              value: d.dw,
              color: d.dw > 0 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Positive Δt (pre → post) → LTP; negative Δt (post → pre) → LTD
          </p>
        </ResultCard>
      )}
    </article>
  );
}
