'use client';

import { useState, useCallback } from 'react';
import { simulateDDMBatch, speedAccuracyTradeoff, driftRateEffect } from '@/lib/cognitive/ddm';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function DDMPage() {
  const [drift, setDrift] = useState(0.5);
  const [boundary, setBoundary] = useState(1.0);
  const [nTrials, setNTrials] = useState(200);
  const [batchResult, setBatchResult] = useState<ReturnType<typeof simulateDDMBatch> | null>(null);
  const [saData, setSaData] = useState<{ boundary: number; accuracy: number; meanRT: number }[]>([]);
  const [driftData, setDriftData] = useState<{ drift: number; accuracy: number; meanRT: number }[]>([]);

  const run = useCallback(() => {
    const batch = simulateDDMBatch({
      nTrials,
      drift,
      boundary,
      sigma: 1,
      dt: 0.01,
      maxTime: 5,
    });
    setBatchResult(batch);

    const boundaries = linspace(0.3, 2.5, 12);
    const sa = speedAccuracyTradeoff({ boundaries, nTrials: 100, drift, sigma: 1 });
    setSaData(sa);

    const drifts = linspace(0.1, 1.5, 10);
    const dr = driftRateEffect({ drifts, nTrials: 100, boundary, sigma: 1 });
    setDriftData(dr);
  }, [drift, boundary, nTrials]);

  return (
    <article>
      <ChapterHeading>§13 Drift-Diffusion Model — Evidence Accumulation in Decision-Making</ChapterHeading>

      <FormulaBlock>
        dx = μ · dt + σ · dW, absorbing boundaries ±a<br />
        accuracy ≈ Φ(μ√(2a)/σ), RT ≈ a/μ (large-a limit)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The DDM models two-alternative decisions as a noisy evidence accumulation process.
        The drift rate μ reflects information quality; the boundary a reflects caution.
        A wider boundary increases accuracy but also RT (speed–accuracy trade-off).
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Drift rate μ" value={drift} onChange={setDrift} min={0} max={2} step={0.1} />
        <ParamField label="Boundary a" value={boundary} onChange={setBoundary} min={0.2} max={3} step={0.1} />
        <ParamField label="Number of trials" value={nTrials} onChange={setNTrials} min={50} max={500} step={50} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {batchResult && (
        <ResultCard title="Batch Simulation Results">
          <DataTable
            headers={['Metric', 'Value']}
            rows={[
              ['Accuracy', `${(batchResult.accuracy * 100).toFixed(1)}%`],
              ['Mean RT', `${(batchResult.meanRT * 1000).toFixed(0)} ms`],
              ['Trials', nTrials],
            ]}
          />
        </ResultCard>
      )}

      {saData.length > 0 && (
        <ResultCard title="Speed–Accuracy Trade-off (Boundary vs Accuracy/RT)">
          <DataTable
            headers={['Boundary a', 'Accuracy', 'Mean RT (s)']}
            rows={saData.map(d => [d.boundary.toFixed(2), `${(d.accuracy * 100).toFixed(1)}%`, d.meanRT.toFixed(3)])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Wider boundary → higher accuracy and longer RT (more cautious but slower)
          </p>
        </ResultCard>
      )}

      {driftData.length > 0 && (
        <ResultCard title="Drift Rate Effect">
          <DataTable
            headers={['Drift rate μ', 'Accuracy', 'Mean RT (s)']}
            rows={driftData.map(d => [d.drift.toFixed(2), `${(d.accuracy * 100).toFixed(1)}%`, d.meanRT.toFixed(3)])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Higher drift rate → higher accuracy and shorter RT (better information quality)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
