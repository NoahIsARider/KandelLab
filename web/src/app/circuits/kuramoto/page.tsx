'use client';

import { useState, useCallback } from 'react';
import { simulateKuramoto, phaseTransitionCurve } from '@/lib/circuits/kuramoto';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, TextScatter } from '@/components/simulation-ui';

export default function KuramotoPage() {
  const [N, setN] = useState(50);
  const [K, setK] = useState(2);
  const [duration, setDuration] = useState(100);
  const [result, setResult] = useState<ReturnType<typeof simulateKuramoto> | null>(null);
  const [phaseData, setPhaseData] = useState<{ K: number; R_mean: number; R_final: number }[]>([]);

  const run = useCallback(() => {
    const res = simulateKuramoto({
      duration,
      dt: 0.1,
      kurParams: { N, K, omega_mean: 1, omega_std: 0.5 },
    });
    setResult(res);

    const KValues = linspace(0, 8, 20);
    const phase = phaseTransitionCurve({ KValues, N, duration: 100 });
    setPhaseData(phase);
  }, [N, K, duration]);

  return (
    <article>
      <ChapterHeading>§9 Kuramoto Model — Synchronization of Phase Oscillators</ChapterHeading>

      <FormulaBlock>
        dθ<sub>i</sub>/dt = ω<sub>i</sub> + (K/N) · Σ<sub>j</sub> sin(θ<sub>j</sub> - θ<sub>i</sub>)<br />
        R · e<sup>iψ</sup> = (1/N) · Σ<sub>j</sub> e<sup>iθ<sub>j</sub></sup>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Kuramoto model describes how N phase oscillators synchronize through global coupling.
        The order parameter R measures the degree of synchronization: R ≈ 0 is a desynchronized state,
        R ≈ 1 is full synchronization. When the coupling strength K exceeds a critical value, the system
        undergoes a continuous phase transition from desynchronization to synchronization.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Number of oscillators N" value={N} onChange={setN} min={10} max={200} step={10} />
        <ParamField label="Coupling strength K" value={K} onChange={setK} min={0} max={10} step={0.5} />
        <ParamField label="Duration" value={duration} onChange={setDuration} min={20} max={500} step={10} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <ResultCard title="Order Parameter R(t)">
          <Waveform data={result.R} height={80} color="var(--verdigris)" label={`R (synchronization), final ${result.R[result.R.length - 1].toFixed(3)}`} />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            R → 1: fully synchronized; R → 0: fully desynchronized
          </p>
        </ResultCard>
      )}

      {phaseData.length > 0 && (
        <ResultCard title="Phase Transition Curve R(K)">
          <TextScatter
            points={phaseData.map(d => ({ x: d.K, y: d.R_mean }))}
            width={40}
            height={15}
            xLabel="K"
            yLabel="R"
          />
          <BarChart
            data={phaseData.filter((_, i) => i % 2 === 0).map(d => ({
              label: d.K.toFixed(1),
              value: d.R_mean,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Increasing K → R rises monotonically; a synchronization phase transition occurs
          </p>
        </ResultCard>
      )}
    </article>
  );
}
