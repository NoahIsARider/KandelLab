'use client';

import { useState, useCallback } from 'react';
import { simulateSimpleCell, receptiveFieldData, orientationTuning } from '@/lib/systems/vision';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, HeatMap, BarChart, ResultCard } from '@/components/simulation-ui';

export default function VisionPage() {
  const [preferredAngle, setPreferredAngle] = useState(0);
  const [sigma, setSigma] = useState(4);
  const [lambda, setLambda] = useState(10);
  const [result, setResult] = useState<ReturnType<typeof simulateSimpleCell> | null>(null);
  const [rfData, setRfData] = useState<{ data: number[][]; size: number; minVal: number; maxVal: number } | null>(null);

  const run = useCallback(() => {
    const res = simulateSimpleCell({
      nAngles: 18,
      preferredAngle,
      gaborParams: { sigma, lambda, size: 21 },
    });
    setResult(res);

    const rf = receptiveFieldData({
      theta: preferredAngle,
      lambda,
      sigma,
      gamma: 0.5,
      psi: 0,
      size: 21,
    });
    setRfData(rf);
  }, [preferredAngle, sigma, lambda]);

  return (
    <article>
      <ChapterHeading>§10a Visual System — Gabor Filters and Orientation Tuning</ChapterHeading>

      <FormulaBlock>
        G(x,y) = exp(-(x&apos;² + γ²y&apos;²)/(2σ²)) · cos(2πx&apos;/λ + ψ)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The receptive fields of V1 simple cells can be described by a 2D Gabor function: a sinusoidal
        wave modulated by a Gaussian envelope. Different cells prefer different orientations,
        giving rise to orientation tuning curves.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Preferred orientation θ" value={preferredAngle} onChange={setPreferredAngle} unit="rad" min={0} max={3.14} step={0.1} />
        <ParamField label="σ (envelope)" value={sigma} onChange={setSigma} min={1} max={10} step={0.5} />
        <ParamField label="λ (wavelength)" value={lambda} onChange={setLambda} min={4} max={20} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rfData && (
        <ResultCard title="Receptive Field Heatmap (Gabor Kernel)">
          <div style={{ width: '280px', margin: '0 auto' }}>
            <HeatMap data={rfData.data} colorScheme="diverging" />
          </div>
          <p className="text-xs text-[var(--ink-light)] mt-2 text-center">
            θ = {preferredAngle.toFixed(2)} rad ({(preferredAngle * 180 / Math.PI).toFixed(0)}°)
          </p>
        </ResultCard>
      )}

      {result && (
        <ResultCard title="Orientation Tuning Curve">
          <BarChart
            data={result.tuningCurve.map(d => ({
              label: `${(d.angle * 180 / Math.PI).toFixed(0)}°`,
              value: d.response,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Response is maximal at the preferred orientation and falls off with deviation (tuning half-width ≈ σ_angular)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
