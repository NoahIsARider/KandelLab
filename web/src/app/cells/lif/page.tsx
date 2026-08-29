'use client';

import { useState, useCallback } from 'react';
import { simulateLIF, fICurve, rasterPlot } from '@/lib/cells/lif';
import { LIF_PARAMS } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function LIFPage() {
  const [duration, setDuration] = useState(500);
  const [current, setCurrent] = useState(2);
  const [result, setResult] = useState<ReturnType<typeof simulateLIF> | null>(null);
  const [fiData, setFiData] = useState<{ I: number; freq_analytical: number; freq_numerical: number }[]>([]);
  const [raster, setRaster] = useState<{ neuronIdx: number; spikeTime: number }[]>([]);

  const run = useCallback(() => {
    const res = simulateLIF({
      duration,
      dt: 0.1,
      I_ext: () => current,
    });
    setResult(res);

    const currents = linspace(0, 5, 20);
    const fi = fICurve({ currents, duration: 2000 });
    setFiData(fi);

    const r = rasterPlot({
      nNeurons: 10,
      duration: 1000,
      dt: 0.1,
      I_ext: () => current,
    });
    setRaster(r);
  }, [duration, current]);

  return (
    <article>
      <ChapterHeading>§4 Leaky Integrate-and-Fire — 脉冲发放模型</ChapterHeading>

      <FormulaBlock>
        τ · dV/dt = -(V - E<sub>L</sub>) + R · I<br />
        当 V ≥ V<sub>thresh</sub> 时发放脉冲，V → V<sub>reset</sub>，不应期 t<sub>ref</sub>
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        LIF 模型是描述神经元脉冲发放的最简模型。膜电位指数衰减至静息电位，
        外部电流驱动去极化。达到阈值时发放脉冲并重置。
        f-I 曲线可解析求解，数值模拟与解析结果高度吻合。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="时长" value={duration} onChange={setDuration} unit="ms" min={100} max={2000} step={50} />
        <ParamField label="输入电流" value={current} onChange={setCurrent} unit="nA" min={0} max={10} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {result && (
        <>
          <ResultCard title="膜电位 V(t)">
            <Waveform data={result.V} height={100} label={`V (mV), 发放 ${result.spikes.length} 次`} />
          </ResultCard>

          <ResultCard title="发放时间">
            <DataTable
              headers={['脉冲 #', '时间 (ms)']}
              rows={result.spikes.slice(0, 20).map((t, i) => [i + 1, t])}
            />
            {result.spikes.length > 20 && (
              <p className="text-xs text-[var(--ink-light)] mt-1">... 共 {result.spikes.length} 个脉冲</p>
            )}
          </ResultCard>
        </>
      )}

      {fiData.length > 0 && (
        <ResultCard title="f-I 曲线（解析 vs 数值）">
          <DataTable
            headers={['I (nA)', 'f_解析 (Hz)', 'f_数值 (Hz)']}
            rows={fiData.filter((_, i) => i % 2 === 0).map(d => [d.I, d.freq_analytical, d.freq_numerical])}
          />
          <TextScatter
            points={fiData.map(d => ({ x: d.I, y: d.freq_numerical }))}
            xLabel="I (nA)"
            yLabel="f (Hz)"
          />
        </ResultCard>
      )}

      {raster.length > 0 && (
        <ResultCard title="栅栏图（10 个神经元）">
          <TextScatter
            points={raster.map(s => ({ x: s.spikeTime, y: s.neuronIdx }))}
            width={50}
            height={10}
            xLabel="time (ms)"
            yLabel="neuron"
          />
        </ResultCard>
      )}
    </article>
  );
}
