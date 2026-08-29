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
      <ChapterHeading>§10a 视觉系统 — Gabor 滤波器与方位调谐</ChapterHeading>

      <FormulaBlock>
        G(x,y) = exp(-(x&apos;² + γ²y&apos;²)/(2σ²)) · cos(2πx&apos;/λ + ψ)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        V1 简单细胞的感受野可用 2D Gabor 函数描述：高斯包络调制正弦波。
        不同细胞偏好不同朝向，形成方位调谐曲线。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="最优朝向 θ" value={preferredAngle} onChange={setPreferredAngle} unit="rad" min={0} max={3.14} step={0.1} />
        <ParamField label="σ (包络)" value={sigma} onChange={setSigma} min={1} max={10} step={0.5} />
        <ParamField label="λ (波长)" value={lambda} onChange={setLambda} min={4} max={20} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rfData && (
        <ResultCard title="感受野热图 (Gabor 核)">
          <div style={{ width: '280px', margin: '0 auto' }}>
            <HeatMap data={rfData.data} colorScheme="diverging" />
          </div>
          <p className="text-xs text-[var(--ink-light)] mt-2 text-center">
            θ = {preferredAngle.toFixed(2)} rad ({(preferredAngle * 180 / Math.PI).toFixed(0)}°)
          </p>
        </ResultCard>
      )}

      {result && (
        <ResultCard title="方位调谐曲线">
          <BarChart
            data={result.tuningCurve.map(d => ({
              label: `${(d.angle * 180 / Math.PI).toFixed(0)}°`,
              value: d.response,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            最优朝向处响应最大，偏离时响应下降（调谐半宽 ≈ σ_angular）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
