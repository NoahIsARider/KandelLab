'use client';

import { useState, useCallback } from 'react';
import { nernstPotential, allEquilibriumPotentials, scanConcentration, scanTemperature } from '@/lib/cells/nernst';
import { ION_CONCENTRATIONS, ION_VALENCES, DEFAULT_TEMP_C } from '@/lib/constants';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, DataTable, BarChart, ResultCard } from '@/components/simulation-ui';

export default function NernstPage() {
  const [tempC, setTempC] = useState(DEFAULT_TEMP_C);
  const [selectedIon, setSelectedIon] = useState('K');
  const [results, setResults] = useState(() => allEquilibriumPotentials(DEFAULT_TEMP_C));
  const [scanData, setScanData] = useState<{ concOut: number; E_mV: number }[]>([]);
  const [tempScanData, setTempScanData] = useState<{ tempC: number; E_mV: number }[]>([]);

  const run = useCallback(() => {
    const eq = allEquilibriumPotentials(tempC);
    setResults(eq);

    const ion = selectedIon;
    const z = ION_VALENCES[ion];
    const concIn = ion === 'K' ? ION_CONCENTRATIONS.K_in :
                   ion === 'Na' ? ION_CONCENTRATIONS.Na_in :
                   ion === 'Ca' ? ION_CONCENTRATIONS.Ca_in :
                   ION_CONCENTRATIONS.Cl_in;
    const concOuts = linspace(0.1, 200, 30);
    const scan = scanConcentration(ion, z, concIn, tempC, concOuts);
    setScanData(scan);

    const temps = linspace(10, 42, 20);
    const concOut = ion === 'K' ? ION_CONCENTRATIONS.K_out :
                    ion === 'Na' ? ION_CONCENTRATIONS.Na_out :
                    ion === 'Ca' ? ION_CONCENTRATIONS.Ca_out :
                    ION_CONCENTRATIONS.Cl_out;
    const tempScan = scanTemperature(z, concOut, concIn, temps);
    setTempScanData(tempScan);
  }, [tempC, selectedIon]);

  return (
    <article>
      <ChapterHeading>§1 Nernst Equation — Ion Equilibrium Potential</ChapterHeading>

      <FormulaBlock>
        E = (RT / zF) · ln([X]<sub>out</sub> / [X]<sub>in</sub>)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Nernst equation describes the equilibrium potential of a single ion across the membrane.
        When the membrane is permeable only to that ion, the membrane potential equals its equilibrium
        potential. Raising the temperature or increasing the concentration gradient increases the
        absolute value of the equilibrium potential.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Temperature" value={tempC} onChange={setTempC} unit="°C" min={10} max={42} step={1} />
        <div className="flex items-center gap-3 mt-2">
          <label className="text-sm text-[var(--ink)] font-[var(--font-display)] min-w-[120px]">Select ion</label>
          <select
            value={selectedIon}
            onChange={(e) => setSelectedIon(e.target.value)}
            className="param-input w-auto"
          >
            <option value="K">K⁺</option>
            <option value="Na">Na⁺</option>
            <option value="Ca">Ca²⁺</option>
            <option value="Cl">Cl⁻</option>
          </select>
        </div>
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      <ResultCard title="Equilibrium Potentials by Ion">
        <DataTable
          headers={['Ion', 'Valence z', '[X]₀ (mM)', '[X]ᵢ (mM)', 'E (mV)']}
          rows={results.map(r => [r.ion, r.z, r.concOut, r.concIn, r.E_mV])}
        />
      </ResultCard>

      {scanData.length > 0 && (
        <>
          <ResultCard title={`${selectedIon}⁺ Equilibrium Potential vs Extracellular Concentration`}>
            <BarChart
              data={scanData.filter((_, i) => i % 3 === 0).map(d => ({
                label: d.concOut.toFixed(1),
                value: d.E_mV,
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Higher extracellular concentration shifts the equilibrium potential toward depolarization
            </p>
          </ResultCard>

          <ResultCard title={`${selectedIon}⁺ Equilibrium Potential vs Temperature`}>
            <BarChart
              data={tempScanData.filter((_, i) => i % 2 === 0).map(d => ({
                label: `${d.tempC.toFixed(0)}°C`,
                value: d.E_mV,
              }))}
            />
            <p className="text-xs text-[var(--ink-light)] mt-2">
              Raising the temperature increases the absolute value of the equilibrium potential linearly (RT/zF depends linearly on temperature)
            </p>
          </ResultCard>
        </>
      )}
    </article>
  );
}
