'use client';

import { useState, useCallback } from 'react';
import { populationResponse, fisherInformation, noiseEffect, populationSizeEffect, mlDecoder } from '@/lib/cognitive/encoding';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function EncodingPage() {
  const [stimulus, setStimulus] = useState(1.5);
  const [nNeurons, setNNeurons] = useState(16);
  const [tuningWidth, setTuningWidth] = useState(0.5);
  const [noiseStd, setNoiseStd] = useState(0.5);
  const [result, setResult] = useState<{
    response: ReturnType<typeof populationResponse>;
    fisherInfo: number;
    crb: number;
    noiseData: ReturnType<typeof noiseEffect>;
    sizeData: ReturnType<typeof populationSizeEffect>;
  } | null>(null);

  const run = useCallback(() => {
    const resp = populationResponse({
      stimulus,
      nNeurons,
      tuningWidth,
      maxRate: 50,
      baseline: 5,
      noiseStd,
    });

    const J = fisherInformation({
      stimulus,
      nNeurons,
      tuningWidth,
      maxRate: 50,
      baseline: 5,
      noiseStd,
    });

    const noiseLevels = linspace(0.1, 3, 10);
    const nData = noiseEffect({
      noiseLevels,
      nNeurons,
      stimulus,
      tuningWidth,
      maxRate: 50,
      baseline: 5,
    });

    const nRange = linspace(4, 64, 10).map(Math.round);
    const sData = populationSizeEffect({
      nNeuronsRange: nRange as number[],
      stimulus,
      tuningWidth,
      maxRate: 50,
      baseline: 5,
      noiseStd,
    });

    setResult({
      response: resp,
      fisherInfo: J,
      crb: 1 / J,
      noiseData: nData,
      sizeData: sData,
    });
  }, [stimulus, nNeurons, tuningWidth, noiseStd]);

  return (
    <article>
      <ChapterHeading>§15 Population Coding — Tuning Curves and Fisher Information</ChapterHeading>

      <FormulaBlock>
        f(θ) = f<sub>max</sub> · exp(-(θ - θ<sub>pref</sub>)² / (2σ²)) + f<sub>base</sub><br />
        J(θ) = Σ<sub>i</sub> (∂f<sub>i</sub>/∂θ)² / σ²<sub>noise</sub><br />
        Var(θ̂) ≥ 1/J(θ) (Cramér–Rao lower bound)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Population coding theory describes how the nervous system represents external stimuli precisely
        through the activity of a population of neurons. Each neuron has a tuning curve (preferring a
        particular stimulus value); Fisher information quantifies coding precision, and the Cramér–Rao
        bound gives the minimum variance achievable by any unbiased decoder.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Stimulus value θ" value={stimulus} onChange={setStimulus} unit="rad" min={0} max={6.28} step={0.1} />
        <ParamField label="Number of neurons" value={nNeurons} onChange={setNNeurons} min={4} max={64} step={4} />
        <ParamField label="Tuning width σ" value={tuningWidth} onChange={setTuningWidth} unit="rad" min={0.1} max={2} step={0.1} />
        <ParamField label="Noise σ" value={noiseStd} onChange={setNoiseStd} min={0.1} max={5} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Population Response">
            <BarChart
              data={result.response.preferredAngle.map((a, i) => ({
                label: `${(a * 180 / Math.PI).toFixed(0)}°`,
                value: result.response.responseNoNoise[i],
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Tuning peaks at the preferred angle closest to the stimulus θ = {(stimulus * 180 / Math.PI).toFixed(0)}°
            </p>
          </ResultCard>

          <ResultCard title="Fisher Information and Coding Precision">
            <DataTable
              headers={['Metric', 'Value']}
              rows={[
                ['Fisher information J(θ)', result.fisherInfo.toFixed(4)],
                ['Cramér–Rao lower bound', result.crb.toFixed(6)],
                ['Minimum decoding error σ_min', Math.sqrt(result.crb).toFixed(4) + ' rad'],
              ]}
            />
          </ResultCard>

          <ResultCard title="Effect of Noise on Coding Precision">
            <DataTable
              headers={['Noise σ', 'Fisher J', 'CRB', 'σ_min (rad)']}
              rows={result.noiseData.map(d => [d.noiseStd.toFixed(2), d.fisherInfo.toFixed(4), d.crb.toFixed(6), d.minStd.toFixed(4)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              More noise → lower J → higher CRB → larger decoding error
            </p>
          </ResultCard>

          <ResultCard title="Effect of Population Size on Coding Precision">
            <DataTable
              headers={['N', 'Fisher J', 'CRB', 'σ_min (rad)']}
              rows={result.sizeData.map(d => [d.nNeurons, d.fisherInfo.toFixed(4), d.crb.toFixed(6), d.minStd.toFixed(4)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Larger N → higher J → lower CRB → smaller decoding error (precision improves with population size)
            </p>
          </ResultCard>
        </>
      )}
    </article>
  );
}
