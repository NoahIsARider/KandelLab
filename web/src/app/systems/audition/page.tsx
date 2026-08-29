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
      <ChapterHeading>§10b 听觉系统 — 频率调谐与耳蜗拓扑</ChapterHeading>

      <FormulaBlock>
        h(t) = t<sup>n-1</sup> · exp(-2π·bw·t) · cos(2π·cf·t)<br />
        ERB(cf) = 24.7 · (4.37 · cf/1000 + 1)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        耳蜗基底膜按频率拓扑排列（tonotopy）：高频在基底，低频在顶端。
        γ-tone 滤波器组模拟这一频率分析过程。每个神经元有其特征频率（CF），
        在 CF 处响应最大，偏离时响应下降。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="特征频率 CF" value={cf} onChange={setCf} unit="Hz" min={100} max={8000} step={100} />
        <ParamField label="神经元数" value={nNeurons} onChange={setNNeurons} min={3} max={20} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="频率调谐曲线">
            <BarChart
              data={result.tuning.filter((_, i) => i % 2 === 0).map(d => ({
                label: `${d.freq.toFixed(0)}`,
                value: d.response,
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              CF = {cf} Hz 处响应最大（频率单位: Hz）
            </p>
          </ResultCard>

          <ResultCard title="耳蜗拓扑图 (Tonotopy)">
            <DataTable
              headers={['位置 (相对)', '特征频率 (Hz)']}
              rows={result.tonotopy.map(t => [t.position.toFixed(2), t.cf.toFixed(0)])}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              位置 0 = 基底（高频）→ 位置 1 = 顶端（低频）
            </p>
          </ResultCard>

          <ResultCard title="群体调谐">
            <DataTable
              headers={['神经元', 'CF (Hz)', '最优响应频率']}
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
