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
      <ChapterHeading>§2 Goldman–Hodgkin–Katz Equation — Resting Membrane Potential</ChapterHeading>

      <FormulaBlock>
        V = (RT/F) · ln((P<sub>K</sub>[K]<sub>o</sub> + P<sub>Na</sub>[Na]<sub>o</sub> + P<sub>Cl</sub>[Cl]<sub>i</sub>) / (P<sub>K</sub>[K]<sub>i</sub> + P<sub>Na</sub>[Na]<sub>i</sub> + P<sub>Cl</sub>[Cl]<sub>o</sub>))
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The GHK equation expresses the membrane potential as a concentration function weighted by ion
        permeabilities. When only one ion is permeable, GHK reduces to the corresponding Nernst equation —
        a key test for validating the model.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="P_K" value={params.P_K} onChange={v => setParams(p => ({ ...p, P_K: v }))} min={0} max={5} step={0.1} />
        <ParamField label="P_Na" value={params.P_Na} onChange={v => setParams(p => ({ ...p, P_Na: v }))} min={0} max={1} step={0.01} />
        <ParamField label="P_Cl" value={params.P_Cl} onChange={v => setParams(p => ({ ...p, P_Cl: v }))} min={0} max={2} step={0.05} />
        <ParamField label="Temperature" value={params.tempC} onChange={v => setParams(p => ({ ...p, tempC: v }))} unit="°C" min={10} max={42} step={1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      <ResultCard title="Computed Result">
        <div className="text-center py-2">
          <span className="font-[var(--font-display)] text-2xl text-[var(--oxide)]">
            V<sub>rest</sub> = {vRest.toFixed(2)} mV
          </span>
        </div>
        <p className="text-xs text-[var(--ink-light)] text-center mt-1">
          A typical neuron&apos;s resting potential is about -70 mV
        </p>
      </ResultCard>

      {verification.length > 0 && (
        <ResultCard title="Verification: GHK Single-Ion Limit → Nernst">
          <DataTable
            headers={['Ion', 'GHK (mV)', 'Nernst (mV)', 'Match']}
            rows={verification.map(v => [v.ion, v.ghk_mV, v.nernst_mV, v.match ? '✓' : '✗'])}
          />
        </ResultCard>
      )}

      {ratioData.length > 0 && (
        <ResultCard title="V_rest vs P_Na/P_K Ratio">
          <BarChart
            data={ratioData.filter((_, i) => i % 2 === 0).map(d => ({
              label: d.ratio.toFixed(3),
              value: d.V_rest,
            }))}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Increasing P_Na/P_K depolarizes the membrane potential (toward E_Na)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
