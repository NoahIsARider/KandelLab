'use client';

import { useState, useCallback } from 'react';
import { simulateVOR } from '@/lib/systems/motor';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, ResultCard } from '@/components/simulation-ui';

export default function MotorPage() {
  const [targetGain, setTargetGain] = useState(1.0);
  const [initialGain, setInitialGain] = useState(0.3);
  const [learningRate, setLearningRate] = useState(0.05);
  const [nTrials, setNTrials] = useState(200);
  const [noiseStd, setNoiseStd] = useState(0.1);
  const [result, setResult] = useState<ReturnType<typeof simulateVOR> | null>(null);

  const run = useCallback(() => {
    const res = simulateVOR({
      nTrials,
      targetGain,
      initialGain,
      learningRate,
      noiseStd,
    });
    setResult(res);
  }, [targetGain, initialGain, learningRate, nTrials, noiseStd]);

  return (
    <article>
      <ChapterHeading>Motor System — VOR Gain Adaptation and Cerebellar Learning</ChapterHeading>

      <FormulaBlock>
        Δg = η · (g<sub>target</sub> - g<sub>current</sub>)<br />
        Cerebellar Marr–Albus rule: Δw ∝ retinal slip error
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The vestibulo-ocular reflex (VOR) compensates for head rotation with eye movements to keep
        vision stable. When visual feedback and motor output mismatch (retinal slip), the cerebellum
        drives gain adaptation — a classic error-driven learning process.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Target gain" value={targetGain} onChange={setTargetGain} min={0.2} max={2} step={0.1} />
        <ParamField label="Initial gain" value={initialGain} onChange={setInitialGain} min={0} max={2} step={0.1} />
        <ParamField label="Learning rate η" value={learningRate} onChange={setLearningRate} min={0.01} max={0.2} step={0.01} />
        <ParamField label="Number of trials" value={nTrials} onChange={setNTrials} min={50} max={500} step={50} />
        <ParamField label="Noise σ" value={noiseStd} onChange={setNoiseStd} min={0} max={0.5} step={0.05} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Gain Adaptation Curve">
            <Waveform data={result.gain} height={80} color="var(--verdigris)" label="Gain g(t)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Gain converges from {initialGain.toFixed(1)} to the target value {targetGain.toFixed(1)}
            </p>
          </ResultCard>

          <ResultCard title="Error Signal">
            <Waveform data={result.error} height={60} color="var(--oxide)" label="Error (target - current)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Error decreases as learning proceeds (exponential decay)
            </p>
          </ResultCard>
        </>
      )}
    </article>
  );
}
