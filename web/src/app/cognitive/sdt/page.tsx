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
      <ChapterHeading>§14 Signal Detection Theory — d&apos;, Criterion, and ROC</ChapterHeading>

      <FormulaBlock>
        d&apos; = z(H) - z(FA)<br />
        c = -½(z(H) + z(FA))<br />
        AUC = Φ(d&apos; / √2)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Signal detection theory separates perceptual sensitivity (d&apos;) from response bias
        (criterion c). d&apos; reflects the intrinsic signal-to-noise ratio; c reflects how high or
        low the decision criterion is set. The ROC curve plots hit rate vs FA rate across criteria,
        and the AUC quantifies overall sensitivity.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="d&apos;" value={dPrime} onChange={setDPrime} min={0} max={4} step={0.1} />
        <ParamField label="criterion c" value={criterion} onChange={setCriterion} min={-2} max={2} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rates && (
        <ResultCard title="Detection Rates">
          <DataTable
            headers={['Metric', 'Value']}
            rows={[
              ['Hit rate', rates.hitRate.toFixed(4)],
              ['False alarm rate', rates.falseAlarmRate.toFixed(4)],
              ['Miss rate', rates.missRate.toFixed(4)],
              ['Correct rejection rate', rates.correctRejectionRate.toFixed(4)],
              ['AUC', rocAUC(dPrime).toFixed(4)],
            ]}
          />
        </ResultCard>
      )}

      {rocData.length > 0 && (
        <ResultCard title={`ROC Curve (d' = ${dPrime})`}>
          <TextScatter
            points={rocData.map(d => ({ x: d.faRate, y: d.hitRate }))}
            width={35}
            height={15}
            xLabel="FA Rate"
            yLabel="Hit Rate"
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            d&apos; = 0 → diagonal (chance performance); d&apos; → ∞ → upper-left corner (perfect detection)
          </p>
        </ResultCard>
      )}

      {dSweep.length > 0 && (
        <ResultCard title="Sensitivity Effect (varying d&apos;)">
          <DataTable
            headers={["d'", 'Hit Rate', 'FA Rate', 'AUC']}
            rows={dSweep.map(d => [d.dPrime.toFixed(2), d.hitRate.toFixed(4), d.faRate.toFixed(4), d.auc.toFixed(4)])}
          />
        </ResultCard>
      )}

      {cSweep.length > 0 && (
        <ResultCard title="Criterion Effect (varying c)">
          <DataTable
            headers={['c', 'Hit Rate', 'FA Rate', 'Bias']}
            rows={cSweep.map(d => [d.criterion.toFixed(2), d.hitRate.toFixed(4), d.faRate.toFixed(4), d.bias])}
          />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            c &gt; 0: conservative (fewer hits claimed); c &lt; 0: liberal (more hits claimed)
          </p>
        </ResultCard>
      )}
    </article>
  );
}
