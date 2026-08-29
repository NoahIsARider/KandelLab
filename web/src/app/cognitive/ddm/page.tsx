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
      <ChapterHeading>§13 漂移扩散模型 — 决策的证据累积</ChapterHeading>

      <FormulaBlock>
        dx = μ · dt + σ · dW, 边界 ±a 吸收<br />
        正确率 ≈ Φ(μ√(2a)/σ), RT ≈ a/μ (大 a 极限)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        DDM 将二选一决策建模为含噪声的证据累积过程。漂移率 μ 表征信息质量，
        边界 a 表征谨慎程度。增大边界 → 正确率↑但 RT↑（速度-准确性权衡）。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="漂移率 μ" value={drift} onChange={setDrift} min={0} max={2} step={0.1} />
        <ParamField label="边界 a" value={boundary} onChange={setBoundary} min={0.2} max={3} step={0.1} />
        <ParamField label="试验次数" value={nTrials} onChange={setNTrials} min={50} max={500} step={50} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {batchResult && (
        <ResultCard title="批量仿真结果">
          <DataTable
            headers={['指标', '值']}
            rows={[
              ['正确率', `${(batchResult.accuracy * 100).toFixed(1)}%`],
              ['平均 RT', `${(batchResult.meanRT * 1000).toFixed(0)} ms`],
              ['试验数', nTrials],
            ]}
          />
        </ResultCard>
      )}

      {saData.length > 0 && (
        <ResultCard title="速度-准确性权衡（边界 vs 正确率/RT）">
          <DataTable
            headers={['边界 a', '正确率', '平均 RT (s)']}
            rows={saData.map(d => [d.boundary.toFixed(2), `${(d.accuracy * 100).toFixed(1)}%`, d.meanRT.toFixed(3)])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            边界增大 → 正确率↑ RT↑（更谨慎但更慢）
          </p>
        </ResultCard>
      )}

      {driftData.length > 0 && (
        <ResultCard title="漂移率效应">
          <DataTable
            headers={['漂移率 μ', '正确率', '平均 RT (s)']}
            rows={driftData.map(d => [d.drift.toFixed(2), `${(d.accuracy * 100).toFixed(1)}%`, d.meanRT.toFixed(3)])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            漂移率增大 → 正确率↑ RT↓（信息质量更高）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
