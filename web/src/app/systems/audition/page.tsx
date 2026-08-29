'use client';

import { useState, useCallback } from 'react';
import { filterBank, frequencyTuning, tonotopicMap, populationTuning } from '@/lib/systems/audition';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function AuditionPage() {
  const [cf, setCf] = useState(1000);
  const [nNeurons, setNNeurons] = useState(8);
  const [result, setResult] = useState<{
    tuning: { freq: number; response: number }[];
    tonotopy: { position: number; cf: number }[];
    population: ReturnType<typeof populationTuning>;
  } | null>(null);

  const run = useCallback(() => {
    const tuning = frequencyTuning({
      cf,
      frequencies: linspace(100, 8000, 40),
    });

    const tonotopy = tonotopicMap({ nPositions: 20 });

    const frequencies = linspace(100, 8000, 30);
    const population = populationTuning({
      nNeurons,
      frequencies,
      cfMin: 200,
      cfMax: 4000,
    });

    setResult({ tuning, tonotopy, population });
  }, [cf, nNeurons]);

  return (
    <article>
      <ChapterHeading>§10b Auditory System — Frequency Tuning and Cochlear Tonotopy</ChapterHeading>

      <FormulaBlock>
        h(t) = t<sup>n-1</sup> · exp(-2π·bw·t) · cos(2π·cf·t)<br />
        ERB(cf) = 24.7 · (4.37 · cf/1000 + 1)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The cochlear basilar membrane is organized tonotopically: high frequencies at the base,
        low frequencies at the apex. A γ-tone filter bank simulates this frequency analysis.
        Each neuron has a characteristic frequency (CF) at which its response is maximal,
        falling off as frequency deviates from the CF.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Characteristic frequency CF" value={cf} onChange={setCf} unit="Hz" min={100} max={8000} step={100} />
        <ParamField label="Number of neurons" value={nNeurons} onChange={setNNeurons} min={3} max={20} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Frequency Tuning Curve">
            <BarChart
              data={result.tuning.filter((_, i) => i % 2 === 0).map(d => ({
                label: `${d.freq.toFixed(0)}`,
                value: d.response,
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Response maximal at CF = {cf} Hz (frequency in Hz)
            </p>
          </ResultCard>

          <ResultCard title="Cochlear Tonotopy Map">
            <DataTable
              headers={['Position (relative)', 'Characteristic frequency (Hz)']}
              rows={result.tonotopy.map(t => [t.position.toFixed(2), t.cf.toFixed(0)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Position 0 = base (high frequencies) → position 1 = apex (low frequencies)
            </p>
          </ResultCard>

          <ResultCard title="Population Tuning">
            <DataTable
              headers={['Neuron', 'CF (Hz)', 'Best frequency']}
              rows={result.population.neurons.map((n, i) => [
                i + 1,
                n.cf.toFixed(0),
                n.tuning.reduce((a, b) => a.response > b.response ? a : b).freq.toFixed(0),
              ])}
            />
          </ResultCard>
        </>
      )}
    </article>
  );
}
