'use client';

import { useState, useCallback } from 'react';
import { simulateHebbian, simulateBCM, ltpLtdCurve } from '@/lib/circuits/hebbian';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function HebbianPage() {
  const [eta, setEta] = useState(0.01);
  const [nPre, setNPre] = useState(10);
  const [nSteps, setNSteps] = useState(500);
  const [correlated, setCorrelated] = useState(true);
  const [hebbResult, setHebbResult] = useState<ReturnType<typeof simulateHebbian> | null>(null);
  const [bcmResult, setBcmResult] = useState<ReturnType<typeof simulateBCM> | null>(null);
  const [ltpData, setLtpData] = useState<{ dt: number; dw: number }[]>([]);

  const run = useCallback(() => {
    const h = simulateHebbian({
      nPre,
      nPost: 1,
      nSteps,
      eta,
      correlated,
    });
    setHebbResult(h);

    const b = simulateBCM({
      nSteps,
      eta,
      inputRate: [0.3, 0.5, 0.8, 0.5, 0.3],
    });
    setBcmResult(b);

    const dtRange = linspace(-50, 50, 50);
    const ltp = ltpLtdCurve({
      dtRange,
      tauPlus: 20,
      tauMinus: 20,
      APlus: 1,
      AMinus: 0.5,
    });
    setLtpData(ltp);
  }, [eta, nPre, nSteps, correlated]);

  return (
    <article>
      <ChapterHeading>§6 Hebbian 学习 — 突触可塑性</ChapterHeading>

      <FormulaBlock>
        Hebb: Δw = η · x · y<br />
        BCM: Δw = η · x · y · (y - θ<sub>M</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Hebb 规则：同时激活的神经元之间的连接增强。BCM 规则引入滑动阈值 θ<sub>M</sub>，
        当突触后活动高于阈值时产生 LTP，低于阈值时产生 LTD。
        STDP（脉冲时序依赖可塑性）进一步精确到毫秒级时序。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="学习率 η" value={eta} onChange={setEta} min={0.001} max={0.1} step={0.001} />
        <ParamField label="突触前数量" value={nPre} onChange={setNPre} min={3} max={20} step={1} />
        <ParamField label="步数" value={nSteps} onChange={setNSteps} min={100} max={2000} step={100} />
        <div className="flex items-center gap-3 mt-2">
          <label className="text-sm text-[var(--ink)] font-[var(--font-display)] min-w-[120px]">输入模式</label>
          <select
            value={correlated ? 'correlated' : 'random'}
            onChange={(e) => setCorrelated(e.target.value === 'correlated')}
            className="param-input w-auto"
          >
            <option value="correlated">相关输入</option>
            <option value="random">随机输入</option>
          </select>
        </div>
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {hebbResult && (
        <ResultCard title="Hebbian 权重演化">
          <p className="text-xs text-[var(--ink-light)] mb-2">
            最终权重（{nPre} 个突触前神经元 → 1 个突触后）
          </p>
          <BarChart
            data={hebbResult.weights[hebbResult.weights.length - 1].map((w, i) => ({
              label: `w${i}`,
              value: w,
              color: w > 0 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            {correlated ? '相关输入 → 部分权重定向增强（选择性学习）' : '随机输入 → 权重均匀分布'}
          </p>
        </ResultCard>
      )}

      {bcmResult && (
        <ResultCard title="BCM 滑动阈值">
          <Waveform data={bcmResult.weight} height={60} color="var(--verdigris)" label="突触权重 w(t)" />
          <Waveform data={bcmResult.theta_M} height={60} color="var(--ochre)" label="滑动阈值 θ_M(t)" />
        </ResultCard>
      )}

      {ltpData.length > 0 && (
        <ResultCard title="STDP 学习窗口（LTP-LTD 曲线）">
          <BarChart
            data={ltpData.filter((_, i) => i % 2 === 0).map(d => ({
              label: `${d.dt.toFixed(0)}`,
              value: d.dw,
              color: d.dw > 0 ? 'var(--verdigris)' : 'var(--oxide)',
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            正 Δt（前→后）→ LTP；负 Δt（后→前）→ LTD
          </p>
        </ResultCard>
      )}
    </article>
  );
}
