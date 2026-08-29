'use client';

import { useState, useCallback } from 'react';
import { ghkPotential, defaultGHKParams, verifySingleIonLimit, scanPermeabilityRatio } from '@/lib/cells/goldman';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, DataTable, BarChart, ResultCard } from '@/components/simulation-ui';

export default function GoldmanPage() {
  const [params, setParams] = useState(defaultGHKParams());
  const [vRest, setVRest] = useState(0);
  const [verification, setVerification] = useState<{ ion: string; ghk_mV: number; nernst_mV: number; match: boolean }[]>([]);
  const [ratioData, setRatioData] = useState<{ ratio: number; V_rest: number }[]>([]);

  const run = useCallback(() => {
    const v = ghkPotential(params);
    setVRest(v);
    setVerification(verifySingleIonLimit());
    const ratios = linspace(0.001, 1, 20);
    setRatioData(scanPermeabilityRatio(params, ratios));
  }, [params]);

  return (
    <article>
      <ChapterHeading>§2 Goldman-Hodgkin-Katz 方程 — 静息膜电位</ChapterHeading>

      <FormulaBlock>
        V = (RT/F) · ln((P<sub>K</sub>[K]<sub>o</sub> + P<sub>Na</sub>[Na]<sub>o</sub> + P<sub>Cl</sub>[Cl]<sub>i</sub>) / (P<sub>K</sub>[K]<sub>i</sub> + P<sub>Na</sub>[Na]<sub>i</sub> + P<sub>Cl</sub>[Cl]<sub>o</sub>))
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        GHK 方程将膜电位表示为各离子通透性加权的浓度函数。当仅一种离子可通透时，
        GHK 退化为对应的 Nernst 方程——这是验证模型正确性的关键测试。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="参数">
        <ParamField label="P_K" value={params.P_K} onChange={v => setParams(p => ({ ...p, P_K: v }))} min={0} max={5} step={0.1} />
        <ParamField label="P_Na" value={params.P_Na} onChange={v => setParams(p => ({ ...p, P_Na: v }))} min={0} max={1} step={0.01} />
        <ParamField label="P_Cl" value={params.P_Cl} onChange={v => setParams(p => ({ ...p, P_Cl: v }))} min={0} max={2} step={0.05} />
        <ParamField label="温度" value={params.tempC} onChange={v => setParams(p => ({ ...p, tempC: v }))} unit="°C" min={10} max={42} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      <ResultCard title="计算结果">
        <div className="text-center py-2">
          <span className="font-[var(--font-display)] text-2xl text-[var(--oxide)]">
            V<sub>rest</sub> = {vRest.toFixed(2)} mV
          </span>
        </div>
        <p className="text-xs text-[var(--ink-light)] text-center mt-1">
          典型神经元静息电位约 -70 mV
        </p>
      </ResultCard>

      {verification.length > 0 && (
        <ResultCard title="验证：GHK 单离子极限 → Nernst">
          <DataTable
            headers={['离子', 'GHK (mV)', 'Nernst (mV)', '一致']}
            rows={verification.map(v => [v.ion, v.ghk_mV, v.nernst_mV, v.match ? '✓' : '✗'])}
          />
        </ResultCard>
      )}

      {ratioData.length > 0 && (
        <ResultCard title="V_rest vs P_Na/P_K 比值">
          <BarChart
            data={ratioData.filter((_, i) => i % 2 === 0).map(d => ({
              label: d.ratio.toFixed(3),
              value: d.V_rest,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            P_Na/P_K 增大 → 膜电位去极化（趋向 E_Na）
          </p>
        </ResultCard>
      )}
    </article>
  );
}
