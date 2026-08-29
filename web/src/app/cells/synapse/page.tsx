'use client';

import { useState, useCallback } from 'react';
import { simulateSynapses, temporalSummation, spatialSummation } from '@/lib/cells/synapse';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function SynapsePage() {
  const [tau, setTau] = useState(5);
  const [weight, setWeight] = useState(2);
  const [nPulses, setNPulses] = useState(5);
  const [isi, setIsi] = useState(10);
  const [temporalResult, setTemporalResult] = useState<{ t: number[]; V: number[] } | null>(null);
  const [spatialResult, setSpatialResult] = useState<{ nInputs: number; peakV: number }[]>([]);

  const run = useCallback(() => {
    const t = temporalSummation({
      nPulses,
      isi: [isi],
      tau,
      weight,
      duration: 200,
    });
    setTemporalResult(t);

    const nInputs = linspace(1, 20, 15).map(Math.round);
    const s = spatialSummation({
      nInputs: nInputs as number[],
      tau,
      weight,
      duration: 200,
    });
    setSpatialResult(s);
  }, [tau, weight, nPulses, isi]);

  return (
    <article>
      <ChapterHeading>§5 突触模型 — EPSP/IPSP 与时空整合</ChapterHeading>

      <FormulaBlock>
        ΔV(t) = w · (t-t<sub>s</sub>)/τ · exp(1 - (t-t<sub>s</sub>)/τ) · Θ(t-t<sub>s</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        突触事件以 α 函数描述：先快速上升，后缓慢衰减。多个突触输入可在时间上
        （高频脉冲）或空间上（多突触同时激活）整合，使膜电位达到发放阈值。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="突触 τ" value={tau} onChange={setTau} unit="ms" min={1} max={30} step={1} />
        <ParamField label="权重 w" value={weight} onChange={setWeight} unit="mV" min={0.1} max={10} step={0.1} />
        <ParamField label="脉冲数" value={nPulses} onChange={setNPulses} unit="" min={1} max={20} step={1} />
        <ParamField label="脉冲间隔" value={isi} onChange={setIsi} unit="ms" min={1} max={100} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {temporalResult && (
        <ResultCard title="时间总和">
          <Waveform data={temporalResult.V} height={80} label={`V (mV), ${nPulses} 脉冲, ISI = ${isi} ms`} />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            短 ISI → 脉冲叠加 → 峰值增大（时间总和）
          </p>
        </ResultCard>
      )}

      {spatialResult.length > 0 && (
        <ResultCard title="空间总和（峰值电位 vs 输入数量）">
          <BarChart
            data={spatialResult.map(d => ({
              label: `${d.nInputs}`,
              value: d.peakV + 70,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            输入数量增多 → 峰值去极化增大（空间总和）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
