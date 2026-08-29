'use client';

import { useState, useCallback } from 'react';
import { simulateWC, findFixedPoints, nullclines, bifurcationSweep } from '@/lib/circuits/wilson-cowan';
import { WC_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function WilsonCowanPage() {
  const [P_ext, setP_ext] = useState(0);
  const [E0, setE0] = useState(0.1);
  const [I0, setI0] = useState(0.1);
  const [duration, setDuration] = useState(100);
  const [result, setResult] = useState<ReturnType<typeof simulateWC> | null>(null);
  const [fixedPts, setFixedPts] = useState<{ E: number; I: number; stable: boolean }[]>([]);
  const [bifurData, setBifurData] = useState<{ P: number; E_ss: number; I_ss: number; nFixed: number }[]>([]);

  const run = useCallback(() => {
    const wcParams = { ...WC_PARAMS, P_ext };
    const res = simulateWC({
      duration,
      dt: 0.1,
      E0,
      I0,
      wcParams,
    });
    setResult(res);

    const fps = findFixedPoints(wcParams);
    setFixedPts(fps);

    const PValues = linspace(-2, 5, 20);
    const bifur = bifurcationSweep({ PValues });
    setBifurData(bifur);
  }, [P_ext, E0, I0, duration]);

  return (
    <article>
      <ChapterHeading>§8 Wilson-Cowan 模型 — 兴奋-抑制群体动力学</ChapterHeading>

      <FormulaBlock>
        τ<sub>E</sub> · dE/dt = -E + S(w<sub>EE</sub>E - w<sub>EI</sub>I + P - θ<sub>E</sub>)<br />
        τ<sub>I</sub> · dI/dt = -I + S(w<sub>IE</sub>E - w<sub>II</sub>I + Q - θ<sub>I</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Wilson-Cowan 模型描述兴奋性（E）与抑制性（I）神经元群体的平均活动。
        系统可呈现单稳态、双稳态（切换）、振荡等多种动力学行为，
        取决于连接强度和外部输入。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="P_ext" value={P_ext} onChange={setP_ext} unit="" min={-2} max={5} step={0.1} />
        <ParamField label="E₀" value={E0} onChange={setE0} min={0} max={1} step={0.05} />
        <ParamField label="I₀" value={I0} onChange={setI0} min={0} max={1} step={0.05} />
        <ParamField label="时长" value={duration} onChange={setDuration} unit="" min={20} max={500} step={10} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <ResultCard title="群体活动 E(t), I(t)">
          <Waveform data={result.E} height={60} color="var(--verdigris)" label="E (兴奋)" />
          <Waveform data={result.I} height={60} color="var(--ochre)" label="I (抑制)" />
          <TextScatter
            points={result.E.map((e, i) => ({ x: e, y: result.I[i] }))}
            width={30}
            height={15}
            xLabel="E"
            yLabel="I"
          />
          <p className="text-xs text-[var(--ink-light)] mt-1">相空间轨迹 (E, I)</p>
        </ResultCard>
      )}

      {fixedPts.length > 0 && (
        <ResultCard title="不动点">
          <DataTable
            headers={['E*', 'I*', '稳定性']}
            rows={fixedPts.map(fp => [fp.E, fp.I, fp.stable ? '稳定' : '不稳定'])}
          />
        </ResultCard>
      )}

      {bifurData.length > 0 && (
        <ResultCard title="分岔：E_ss vs P_ext">
          <BarChart
            data={bifurData.map(d => ({
              label: d.P.toFixed(1),
              value: d.E_ss,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            P_ext 增大 → 兴奋活动增大，可能出现双稳态切换
          </p>
        </ResultCard>
      )}
    </article>
  );
}
