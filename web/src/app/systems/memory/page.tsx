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
      <ChapterHeading>§11 联想记忆 — Hopfield 网络</ChapterHeading>

      <FormulaBlock>
        w<sub>ij</sub> = (1/N) · Σ<sub>μ</sub> ξ<sub>i</sub><sup>μ</sup> · ξ<sub>j</sub><sup>μ</sup><br />
        E = -(1/2) · Σ<sub>i,j</sub> w<sub>ij</sub> · s<sub>i</sub> · s<sub>j</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Hopfield 网络是一种递归神经网络，可存储二元模式并通过异步更新恢复损坏的输入。
        每次更新使能量函数单调下降，保证收敛到局部极小。
        存储容量约为 0.138N 个模式。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="神经元数 N" value={N} onChange={setN} min={20} max={200} step={10} />
        <ParamField label="存储模式数" value={nPatterns} onChange={setNPatterns} min={1} max={20} step={1} />
        <ParamField label="噪声水平" value={noiseLevel} onChange={setNoiseLevel} min={0.05} max={0.5} step={0.05} />
        <ParamField label="最大迭代" value={maxIter} onChange={setMaxIter} min={50} max={500} step={50} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="能量函数下降">
            <Waveform data={result.energyHistory} height={80} color="var(--verdigris)" label="E(t)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              能量单调不增 → 收敛于 {result.converged ? `第 ${result.iterations} 步` : '未收敛'}
            </p>
          </ResultCard>

          <ResultCard title="恢复结果">
            <DataTable
              headers={['指标', '值']}
              rows={[
                ['存储模式数', nPatterns],
                ['噪声翻转率', `${(noiseLevel * 100).toFixed(0)}%`],
                ['收敛', result.converged ? '是' : '否'],
                ['迭代次数', result.iterations],
                ['最终能量', result.energyHistory[result.energyHistory.length - 1].toFixed(2)],
              ]}
            />
          </ResultCard>
        </>
      )}

      {capData.length > 0 && (
        <ResultCard title="容量测试（成功率 vs 模式数）">
          <BarChart
            data={capData.map(d => ({
              label: `${d.nPatterns}`,
              value: d.successRate,
              color: d.successRate > 0.5 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            模式数超过 ~0.138N 时成功率急剧下降
          </p>
        </ResultCard>
      )}
    </article>
  );
}
