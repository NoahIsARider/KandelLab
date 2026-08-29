'use client';

import { useState, useCallback } from 'react';
import { sdtRates, rocCurve, rocAUC, varyDSensitivity, varyCriterion } from '@/lib/cognitive/sdt';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, BarChart, ResultCard, DataTable, TextScatter } from '@/components/simulation-ui';

export default function SDTPage() {
  const [dPrime, setDPrime] = useState(1.5);
  const [criterion, setCriterion] = useState(0);
  const [rates, setRates] = useState<ReturnType<typeof sdtRates> | null>(null);
  const [rocData, setRocData] = useState<{ faRate: number; hitRate: number; criterion: number }[]>([]);
  const [dSweep, setDSweep] = useState<{ dPrime: number; hitRate: number; faRate: number; auc: number }[]>([]);
  const [cSweep, setCSweep] = useState<{ criterion: number; hitRate: number; faRate: number; bias: string }[]>([]);

  const run = useCallback(() => {
    const r = sdtRates(dPrime, criterion);
    setRates(r);

    const roc = rocCurve({ dPrime });
    setRocData(roc);

    const dPrimes = linspace(0, 3, 12);
    const ds = varyDSensitivity({ dPrimes, criterion });
    setDSweep(ds);

    const criteria = linspace(-2, 2, 12);
    const cs = varyCriterion({ dPrime, criteria });
    setCSweep(cs);
  }, [dPrime, criterion]);

  return (
    <article>
      <ChapterHeading>§14 信号检测论 — d&apos;, 判断标准与 ROC</ChapterHeading>

      <FormulaBlock>
        d&apos; = z(H) - z(FA)<br />
        c = -½(z(H) + z(FA))<br />
        AUC = Φ(d&apos; / √2)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        信号检测论将感知敏感性（d&apos;）与反应偏差（criterion c）分离。
        d&apos; 反映内在的信噪比，c 反映决策标准的高低。
        ROC 曲线描绘不同标准下的 hit rate vs FA rate，AUC 量化总体敏感性。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="d&apos;" value={dPrime} onChange={setDPrime} min={0} max={4} step={0.1} />
        <ParamField label="criterion c" value={criterion} onChange={setCriterion} min={-2} max={2} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rates && (
        <ResultCard title="检测率">
          <DataTable
            headers={['指标', '值']}
            rows={[
              ['Hit Rate (命中率)', rates.hitRate.toFixed(4)],
              ['FA Rate (虚报率)', rates.falseAlarmRate.toFixed(4)],
              ['Miss Rate (漏报率)', rates.missRate.toFixed(4)],
              ['CR Rate (正确拒绝率)', rates.correctRejectionRate.toFixed(4)],
              ['AUC', rocAUC(dPrime).toFixed(4)],
            ]}
          />
        </ResultCard>
      )}

      {rocData.length > 0 && (
        <ResultCard title={`ROC 曲线 (d' = ${dPrime})`}>
          <TextScatter
            points={rocData.map(d => ({ x: d.faRate, y: d.hitRate }))}
            width={35}
            height={15}
            xLabel="FA Rate"
            yLabel="Hit Rate"
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            d&apos; = 0 → 对角线（随机猜测）；d&apos; → ∞ → 左上角（完美检测）
          </p>
        </ResultCard>
      )}

      {dSweep.length > 0 && (
        <ResultCard title="敏感性效应 (vary d&apos;)">
          <DataTable
            headers={["d'", 'Hit Rate', 'FA Rate', 'AUC']}
            rows={dSweep.map(d => [d.dPrime.toFixed(2), d.hitRate.toFixed(4), d.faRate.toFixed(4), d.auc.toFixed(4)])}
          />
        </ResultCard>
      )}

      {cSweep.length > 0 && (
        <ResultCard title="判断标准效应 (vary c)">
          <DataTable
            headers={['c', 'Hit Rate', 'FA Rate', '偏差']}
            rows={cSweep.map(d => [d.criterion.toFixed(2), d.hitRate.toFixed(4), d.faRate.toFixed(4), d.bias])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            c &gt; 0: 保守（少报）; c &lt; 0:  liberal（多报）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
