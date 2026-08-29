'use client';

import { useState, useCallback } from 'react';
import { simulateHopfield, capacityTest } from '@/lib/systems/memory';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function MemoryPage() {
  const [N, setN] = useState(100);
  const [nPatterns, setNPatterns] = useState(5);
  const [noiseLevel, setNoiseLevel] = useState(0.3);
  const [maxIter, setMaxIter] = useState(200);
  const [result, setResult] = useState<ReturnType<typeof simulateHopfield> | null>(null);
  const [capData, setCapData] = useState<{ nPatterns: number; successRate: number }[]>([]);

  const run = useCallback(() => {
    const res = simulateHopfield({
      N,
      nPatterns,
      noiseLevel,
      maxIterations: maxIter,
    });
    setResult(res);

    const nPatternsRange = linspace(1, Math.floor(N / 3), 10).map(Math.round);
    const cap = capacityTest({ N, nPatternsRange: nPatternsRange as number[], nTrials: 5 });
    setCapData(cap);
  }, [N, nPatterns, noiseLevel, maxIter]);

  return (
    <article>
      <ChapterHeading>§11 Associative Memory — Hopfield Network</ChapterHeading>

      <FormulaBlock>
        w<sub>ij</sub> = (1/N) · Σ<sub>μ</sub> ξ<sub>i</sub><sup>μ</sup> · ξ<sub>j</sub><sup>μ</sup><br />
        E = -(1/2) · Σ<sub>i,j</sub> w<sub>ij</sub> · s<sub>i</sub> · s<sub>j</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Hopfield network is a recurrent neural network that stores binary patterns and retrieves
        corrupted inputs through asynchronous updates. Each update monotonically decreases the energy
        function, guaranteeing convergence to a local minimum. Its storage capacity is roughly 0.138N
        patterns.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Number of neurons N" value={N} onChange={setN} min={20} max={200} step={10} />
        <ParamField label="Number of stored patterns" value={nPatterns} onChange={setNPatterns} min={1} max={20} step={1} />
        <ParamField label="Noise level" value={noiseLevel} onChange={setNoiseLevel} min={0.05} max={0.5} step={0.05} />
        <ParamField label="Maximum iterations" value={maxIter} onChange={setMaxIter} min={50} max={500} step={50} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Energy Function Decay">
            <Waveform data={result.energyHistory} height={80} color="var(--verdigris)" label="E(t)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Energy never increases → {result.converged ? `converged at step ${result.iterations}` : 'did not converge'}
            </p>
          </ResultCard>

          <ResultCard title="Retrieval Results">
            <DataTable
              headers={['Metric', 'Value']}
              rows={[
                ['Stored patterns', nPatterns],
                ['Noise flip rate', `${(noiseLevel * 100).toFixed(0)}%`],
                ['Converged', result.converged ? 'Yes' : 'No'],
                ['Iterations', result.iterations],
                ['Final energy', result.energyHistory[result.energyHistory.length - 1].toFixed(2)],
              ]}
            />
          </ResultCard>
        </>
      )}

      {capData.length > 0 && (
        <ResultCard title="Capacity Test (Success Rate vs Number of Patterns)">
          <BarChart
            data={capData.map(d => ({
              label: `${d.nPatterns}`,
              value: d.successRate,
              color: d.successRate > 0.5 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Success rate drops sharply once the number of patterns exceeds ~0.138N
          </p>
        </ResultCard>
      )}
    </article>
  );
}
