'use client';

import { useState, useCallback } from 'react';
import { simulateLateralInhibition, machBandsStimulus, edgeStimulus, gradientStimulus, dogKernel2D } from '@/lib/circuits/lateral-inhibition';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, HeatMap, ResultCard } from '@/components/simulation-ui';

export default function LateralInhibitionPage() {
  const [sigmaCenter, setSigmaCenter] = useState(2);
  const [sigmaSurround, setSigmaSurround] = useState(6);
  const [ampCenter, setAmpCenter] = useState(1);
  const [ampSurround, setAmpSurround] = useState(0.5);
  const [stimType, setStimType] = useState('mach');
  const [result, setResult] = useState<ReturnType<typeof simulateLateralInhibition> | null>(null);
  const [kernel2D, setKernel2D] = useState<number[][]>([]);

  const run = useCallback(() => {
    const n = 100;
    const stimulus = stimType === 'mach' ? machBandsStimulus(n, 5) :
                     stimType === 'edge' ? edgeStimulus(n) :
                     gradientStimulus(n);

    const res = simulateLateralInhibition({
      stimulus,
      dogParams: {
        sigmaCenter,
        sigmaSurround,
        amplitudeCenter: ampCenter,
        amplitudeSurround: ampSurround,
        size: 21,
      },
    });
    setResult(res);

    const k2d = dogKernel2D({
      sigmaCenter,
      sigmaSurround,
      amplitudeCenter: ampCenter,
      amplitudeSurround: ampSurround,
      size: 21,
    });
    setKernel2D(k2d);
  }, [sigmaCenter, sigmaSurround, ampCenter, ampSurround, stimType]);

  return (
    <article>
      <ChapterHeading>§7 Lateral Inhibition — Center–Surround Antagonism and Edge Enhancement</ChapterHeading>

      <FormulaBlock>
        K(x) = A<sub>c</sub> · exp(-x²/2σ<sub>c</sub>²) - A<sub>s</sub> · exp(-x²/2σ<sub>s</sub>²)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Difference-of-Gaussians (DOG) model describes the center–surround antagonism of receptive
        fields. Uniform regions elicit a flat response, while edges are enhanced (Mach band effect) —
        a basic mechanism by which the visual system enhances contrast.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="σ_center" value={sigmaCenter} onChange={setSigmaCenter} min={0.5} max={5} step={0.5} />
        <ParamField label="σ_surround" value={sigmaSurround} onChange={setSigmaSurround} min={2} max={15} step={1} />
        <ParamField label="A_center" value={ampCenter} onChange={setAmpCenter} min={0.1} max={3} step={0.1} />
        <ParamField label="A_surround" value={ampSurround} onChange={setAmpSurround} min={0.1} max={2} step={0.1} />
        <div className="flex items-center gap-3 mt-2">
          <label className="text-sm text-[var(--ink)] font-[var(--font-display)] min-w-[120px]">Stimulus type</label>
          <select
            value={stimType}
            onChange={(e) => setStimType(e.target.value)}
            className="param-input w-auto"
          >
            <option value="mach">Mach Bands</option>
            <option value="edge">Step edge</option>
            <option value="gradient">Linear gradient</option>
          </select>
        </div>
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="Stimulus and Response">
            <Waveform data={result.stimulus} height={60} color="var(--ink-light)" label="Stimulus" />
            <Waveform data={result.response} height={60} color="var(--oxide)" label="Response (edge enhancement)" />
          </ResultCard>

          <ResultCard title="DOG Kernel">
            <Waveform data={result.kernel} height={50} color="var(--verdigris)" label="1D DOG kernel" />
          </ResultCard>
        </>
      )}

      {kernel2D.length > 0 && (
        <ResultCard title="2D DOG Receptive Field Heatmap">
          <div style={{ width: '280px', margin: '0 auto' }}>
            <HeatMap data={kernel2D} colorScheme="diverging" />
          </div>
          <p className="text-xs text-[var(--ink-light)] mt-2 text-center">
            Center excitation (warm) / surround inhibition (cool)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
