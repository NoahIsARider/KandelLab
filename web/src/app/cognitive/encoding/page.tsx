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
      <ChapterHeading>§15 群体编码 — 调谐曲线与 Fisher 信息</ChapterHeading>

      <FormulaBlock>
        f(θ) = f<sub>max</sub> · exp(-(θ - θ<sub>pref</sub>)² / (2σ²)) + f<sub>base</sub><br />
        J(θ) = Σ<sub>i</sub> (∂f<sub>i</sub>/∂θ)² / σ²<sub>noise</sub><br />
        Var(θ̂) ≥ 1/J(θ) (Cramér-Rao 下界)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        群体编码理论描述神经系统如何以一群神经元的活动精确表征外部刺激。
        每个神经元有调谐曲线（偏好特定刺激值），Fisher 信息量化编码精度，
        Cramér-Rao 界给出任何无偏解码器的最小方差。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="刺激值 θ" value={stimulus} onChange={setStimulus} unit="rad" min={0} max={6.28} step={0.1} />
        <ParamField label="神经元数" value={nNeurons} onChange={setNNeurons} min={4} max={64} step={4} />
        <ParamField label="调谐宽度 σ" value={tuningWidth} onChange={setTuningWidth} unit="rad" min={0.1} max={2} step={0.1} />
        <ParamField label="噪声 σ" value={noiseStd} onChange={setNoiseStd} min={0.1} max={5} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="群体响应">
            <BarChart
              data={result.response.preferredAngle.map((a, i) => ({
                label: `${(a * 180 / Math.PI).toFixed(0)}°`,
                value: result.response.responseNoNoise[i],
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              调谐曲线峰值出现在最接近刺激值 θ = {(stimulus * 180 / Math.PI).toFixed(0)}° 的偏好角处
            </p>
          </ResultCard>

          <ResultCard title="Fisher 信息与编码精度">
            <DataTable
              headers={['指标', '值']}
              rows={[
                ['Fisher 信息 J(θ)', result.fisherInfo.toFixed(4)],
                ['Cramér-Rao 下界', result.crb.toFixed(6)],
                ['最小解码误差 σ_min', Math.sqrt(result.crb).toFixed(4) + ' rad'],
              ]}
            />
          </ResultCard>

          <ResultCard title="噪声对编码精度的影响">
            <DataTable
              headers={['噪声 σ', 'Fisher J', 'CRB', 'σ_min (rad)']}
              rows={result.noiseData.map(d => [d.noiseStd.toFixed(2), d.fisherInfo.toFixed(4), d.crb.toFixed(6), d.minStd.toFixed(4)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              噪声↑ → J↓ → CRB↑ → 解码误差↑
            </p>
          </ResultCard>

          <ResultCard title="群体大小对编码精度的影响">
            <DataTable
              headers={['N', 'Fisher J', 'CRB', 'σ_min (rad)']}
              rows={result.sizeData.map(d => [d.nNeurons, d.fisherInfo.toFixed(4), d.crb.toFixed(6), d.minStd.toFixed(4)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              N↑ → J↑ → CRB↓ → 解码误差↓（精度随群体增大而提高）
            </p>
          </ResultCard>
        </>
      )}
    </article>
  );
}
