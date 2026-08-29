'use client';

import { useState, useCallback } from 'react';
import { simulateRW, simulateBlocking, dopamineSignal } from '@/lib/systems/reward';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard } from '@/components/simulation-ui';

export default function RewardPage() {
  const [alpha, setAlpha] = useState(0.1);
  const [nTrials, setNTrials] = useState(50);
  const [reward, setReward] = useState(1);
  const [rwResult, setRwResult] = useState<ReturnType<typeof simulateRW> | null>(null);
  const [blockResult, setBlockResult] = useState<ReturnType<typeof simulateBlocking> | null>(null);
  const [dopaResult, setDopaResult] = useState<ReturnType<typeof dopamineSignal> | null>(null);

  const run = useCallback(() => {
    // Rescorla-Wagner: acquisition then extinction
    const rw = simulateRW({
      nTrials,
      alpha,
      reward,
      contingency: (t) => t < nTrials * 0.7,
    });
    setRwResult(rw);

    // Blocking effect
    const block = simulateBlocking({
      alpha,
      phase1Trials: 20,
      phase2Trials: 20,
      reward,
    });
    setBlockResult(block);

    // Dopamine prediction error
    const dopa = dopamineSignal({
      nSteps: 100,
      rewardTime: 50,
      alpha,
      gamma: 0.95,
    });
    setDopaResult(dopa);
  }, [alpha, nTrials, reward]);

  return (
    <article>
      <ChapterHeading>§12 奖赏学习 — Rescorla-Wagner 与 TD(λ)</ChapterHeading>

      <FormulaBlock>
        RW: ΔV = α · (λ - V)<br />
        TD: δ = r + γ · V(s&apos;) - V(s)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Rescorla-Wagner 模型描述经典条件反射：刺激的价值 V 渐近收敛至奖赏 λ。
        TD(λ) 模型将此推广到序贯决策，产生奖赏预测误差信号 δ，
        与多巴胺神经元的放电模式高度吻合。阻塞效应（blocking）是 RW 模型的关键预测。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="学习率 α" value={alpha} onChange={setAlpha} min={0.01} max={0.5} step={0.01} />
        <ParamField label="试验次数" value={nTrials} onChange={setNTrials} min={20} max={100} step={10} />
        <ParamField label="奖赏量 λ" value={reward} onChange={setReward} min={0.1} max={2} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rwResult && (
        <ResultCard title="Rescorla-Wagner 学习曲线">
          <Waveform data={rwResult.V} height={60} color="var(--verdigris)" label="V (预测值)" />
          <Waveform data={rwResult.delta} height={40} color="var(--oxide)" label="δ (预测误差)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            条件反射渐近收敛 → 消退时 δ 变负
          </p>
        </ResultCard>
      )}

      {blockResult && (
        <ResultCard title="阻塞效应">
          <Waveform data={blockResult.VA} height={50} color="var(--verdigris)" label="V_A (预训练刺激)" />
          <Waveform data={blockResult.VB} height={50} color="var(--ochre)" label="V_B (复合刺激中新刺激)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            A 已学会预测奖赏 → B 几乎学不到（预测误差已被 A 消耗）
          </p>
        </ResultCard>
      )}

      {dopaResult && (
        <ResultCard title="多巴胺样预测误差信号">
          <Waveform data={dopaResult.predictionError} height={60} color="var(--oxide)" label="δ(t) (预测误差)" />
          <Waveform data={dopaResult.value} height={50} color="var(--verdigris)" label="V(t) (预测值)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            学习前：奖赏时 δ 正脉冲；学习后：预测线索时 δ 正脉冲，奖赏时 δ = 0
          </p>
        </ResultCard>
      )}
    </article>
  );
}
