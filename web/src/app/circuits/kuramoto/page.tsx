'use client';

import { useState, useCallback } from 'react';
import { simulateKuramoto, phaseTransitionCurve } from '@/lib/circuits/kuramoto';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, TextScatter } from '@/components/simulation-ui';

export default function KuramotoPage() {
  const [N, setN] = useState(50);
  const [K, setK] = useState(2);
  const [duration, setDuration] = useState(100);
  const [result, setResult] = useState<ReturnType<typeof simulateKuramoto> | null>(null);
  const [phaseData, setPhaseData] = useState<{ K: number; R_mean: number; R_final: number }[]>([]);

  const run = useCallback(() => {
    const res = simulateKuramoto({
      duration,
      dt: 0.1,
      kurParams: { N, K, omega_mean: 1, omega_std: 0.5 },
    });
    setResult(res);

    const KValues = linspace(0, 8, 20);
    const phase = phaseTransitionCurve({ KValues, N, duration: 100 });
    setPhaseData(phase);
  }, [N, K, duration]);

  return (
    <article>
      <ChapterHeading>§9 Kuramoto 模型 — 相位振荡器同步</ChapterHeading>

      <FormulaBlock>
        dθ<sub>i</sub>/dt = ω<sub>i</sub> + (K/N) · Σ<sub>j</sub> sin(θ<sub>j</sub> - θ<sub>i</sub>)<br />
        R · e<sup>iψ</sup> = (1/N) · Σ<sub>j</sub> e<sup>iθ<sub>j</sub></sup>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Kuramoto 模型描述 N 个相位振荡器通过全局耦合实现同步的过程。
        序参量 R 度量同步程度：R ≈ 0 为非同步态，R ≈ 1 为完全同步。
        当耦合强度 K 超过临界值时，系统发生从非同步到同步的连续相变。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="振子数 N" value={N} onChange={setN} min={10} max={200} step={10} />
        <ParamField label="耦合强度 K" value={K} onChange={setK} min={0} max={10} step={0.5} />
        <ParamField label="时长" value={duration} onChange={setDuration} min={20} max={500} step={10} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <ResultCard title="序参量 R(t)">
          <Waveform data={result.R} height={80} color="var(--verdigris)" label={`R (同步度), 终值 ${result.R[result.R.length - 1].toFixed(3)}`} />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            R → 1: 完全同步; R → 0: 完全非同步
          </p>
        </ResultCard>
      )}

      {phaseData.length > 0 && (
        <ResultCard title="相变曲线 R(K)">
          <TextScatter
            points={phaseData.map(d => ({ x: d.K, y: d.R_mean }))}
            width={40}
            height={15}
            xLabel="K"
            yLabel="R"
          />
          <BarChart
            data={phaseData.filter((_, i) => i % 2 === 0).map(d => ({
              label: d.K.toFixed(1),
              value: d.R_mean,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            K 增大 → R 单调上升，发生同步相变
          </p>
        </ResultCard>
      )}
    </article>
  );
}
