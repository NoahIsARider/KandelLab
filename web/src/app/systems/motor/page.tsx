'use client';

import { useState, useCallback } from 'react';
import { simulateVOR } from '@/lib/systems/motor';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, ResultCard } from '@/components/simulation-ui';

export default function MotorPage() {
  const [targetGain, setTargetGain] = useState(1.0);
  const [initialGain, setInitialGain] = useState(0.3);
  const [learningRate, setLearningRate] = useState(0.05);
  const [nTrials, setNTrials] = useState(200);
  const [noiseStd, setNoiseStd] = useState(0.1);
  const [result, setResult] = useState<ReturnType<typeof simulateVOR> | null>(null);

  const run = useCallback(() => {
    const res = simulateVOR({
      nTrials,
      targetGain,
      initialGain,
      learningRate,
      noiseStd,
    });
    setResult(res);
  }, [targetGain, initialGain, learningRate, nTrials, noiseStd]);

  return (
    <article>
      <ChapterHeading>运动系统 — VOR 增益适应与小脑学习</ChapterHeading>

      <FormulaBlock>
        Δg = η · (g<sub>target</sub> - g<sub>current</sub>)<br />
        小脑 Marr-Albus 规则: Δw ∝ 视网膜滑移误差
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        前庭-眼反射（VOR）通过眼球运动补偿头部转动，维持视觉稳定。
        当视觉反馈与运动输出不匹配时（视网膜滑移），小脑驱动增益适应。
        这是一个经典的误差驱动学习过程。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="目标增益" value={targetGain} onChange={setTargetGain} min={0.2} max={2} step={0.1} />
        <ParamField label="初始增益" value={initialGain} onChange={setInitialGain} min={0} max={2} step={0.1} />
        <ParamField label="学习率 η" value={learningRate} onChange={setLearningRate} min={0.01} max={0.2} step={0.01} />
        <ParamField label="试验次数" value={nTrials} onChange={setNTrials} min={50} max={500} step={50} />
        <ParamField label="噪声 σ" value={noiseStd} onChange={setNoiseStd} min={0} max={0.5} step={0.05} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="增益适应曲线">
            <Waveform data={result.gain} height={80} color="var(--verdigris)" label="增益 g(t)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              增益从 {initialGain.toFixed(1)} 逐渐收敛至目标值 {targetGain.toFixed(1)}
            </p>
          </ResultCard>

          <ResultCard title="误差信号">
            <Waveform data={result.error} height={60} color="var(--oxide)" label="误差 (target - current)" />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              误差随学习逐渐减小（指数衰减）
            </p>
          </ResultCard>
        </>
      )}
    </article>
  );
}
