'use client';

import { useState, useCallback } from 'react';
import { simulateHH, fICurve, findThreshold } from '@/lib/cells/hodgkin-huxley';
import { HH_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable } from '@/components/simulation-ui';

export default function HodgkinHuxleyPage() {
  const [duration, setDuration] = useState(100);
  const [stimCurrent, setStimCurrent] = useState(10);
  const [stimStart, setStimStart] = useState(10);
  const [stimEnd, setStimEnd] = useState(90);
  const [result, setResult] = useState<ReturnType<typeof simulateHH> | null>(null);
  const [fiData, setFiData] = useState<{ I: number; freq: number }[]>([]);
  const [threshold, setThreshold] = useState(0);

  const run = useCallback(() => {
    const s = stimStart;
    const e = stimEnd;
    const I = stimCurrent;
    const res = simulateHH({
      duration,
      dt: 0.01,
      I_ext: (t) => (t >= s && t <= e) ? I : 0,
    });
    setResult(res);

    const currents = linspace(0, 20, 15);
    const fi = fICurve({ currents, duration: 500, dt: 0.01 });
    setFiData(fi);

    const thresh = findThreshold();
    setThreshold(thresh);
  }, [duration, stimCurrent, stimStart, stimEnd]);

  return (
    <article>
      <ChapterHeading>§3 Hodgkin-Huxley 模型 — 动作电位</ChapterHeading>

      <FormulaBlock>
        C<sub>m</sub> dV/dt = -g<sub>Na</sub>m³h(V-E<sub>Na</sub>) - g<sub>K</sub>n⁴(V-E<sub>K</sub>) - g<sub>L</sub>(V-E<sub>L</sub>) + I<sub>ext</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Hodgkin-Huxley 模型用四个耦合 ODE 描述动作电位的产生机制。
        钠通道的激活（m）与失活（h）门控变量，以及钾通道的激活（n）门控变量，
        共同决定了膜的兴奋性。使用 RK4 方法数值求解。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="时长" value={duration} onChange={setDuration} unit="ms" min={20} max={500} step={10} />
        <ParamField label="刺激电流" value={stimCurrent} onChange={setStimCurrent} unit="µA/cm²" min={0} max={30} step={0.5} />
        <ParamField label="刺激起始" value={stimStart} onChange={setStimStart} unit="ms" min={0} max={50} step={1} />
        <ParamField label="刺激结束" value={stimEnd} onChange={setStimEnd} unit="ms" min={10} max={500} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="膜电位 V(t)">
            <Waveform data={result.V} height={100} label={`V (mV), 峰值 ${Math.max(...result.V).toFixed(1)} mV`} />
          </ResultCard>

          <ResultCard title="门控变量 m, h, n">
            <Waveform data={result.m} height={50} color="var(--verdigris)" label="m (Na⁺ 激活)" />
            <Waveform data={result.h} height={50} color="var(--ochre)" label="h (Na⁺ 失活)" />
            <Waveform data={result.n} height={50} color="var(--oxide)" label="n (K⁺ 激活)" />
          </ResultCard>

          <ResultCard title="离子电导">
            <Waveform data={result.gNa} height={50} color="var(--verdigris)" label={`g_Na (mS/cm²), 峰值 ${Math.max(...result.gNa).toFixed(1)}`} />
            <Waveform data={result.gK} height={50} color="var(--ochre)" label={`g_K (mS/cm²), 峰值 ${Math.max(...result.gK).toFixed(1)}`} />
          </ResultCard>
        </>
      )}

      <ResultCard title="关键特征">
        <DataTable
          headers={['参数', '值']}
          rows={[
            ['静息电位', `${HH_PARAMS.V_rest} mV`],
            ['发放阈值 (数值)', `${threshold.toFixed(1)} mV`],
            ['Na⁺ 反转电位', `${HH_PARAMS.E_Na} mV`],
            ['K⁺ 反转电位', `${HH_PARAMS.E_K} mV`],
            ['最大 g_Na', `${HH_PARAMS.g_Na} mS/cm²`],
            ['最大 g_K', `${HH_PARAMS.g_K} mS/cm²`],
          ]}
        />
      </ResultCard>

      {fiData.length > 0 && (
        <ResultCard title="f-I 曲线（发放频率 vs 输入电流）">
          <BarChart
            data={fiData.map(d => ({
              label: `${d.I.toFixed(1)}`,
              value: d.freq,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            发放频率随输入电流单调递增（I 单位: µA/cm², f 单位: Hz）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
