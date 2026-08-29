'use client';

import { useState, useCallback } from 'react';
import { simulateRW, simulateBlocking, dopamineSignal } from '@/lib/systems/reward';
import { linspace } from '@/lib/math-utils';
import { ChapterHeading, OrnamentDivider, FormulaBlock, ParamField, RunButton, Waveform, BarChart, ResultCard } from '@/components/simulation-ui';

export default function RewardPage() {
  const [alpha, setAlpha] = useState(0.1);
  const [nTrials, setNTrials] = useState(50);
  const [reward, setReward] = useState(1);
  const [rwResult, setRwResult] = useState<ReturnType<typeof simulateRW> | null>(null);
  const [blockResult, setBlockResult] = useState<ReturnType<typeof simulateBlocking> | null>(null);
  const [dopaResult, setDopaResult] = useState<ReturnType<typeof dopamineSignal> | null>(null);

  const run = useCallback(() => {
    // Rescorla-Wagner: acquisition then extinction
    const rw = simulateRW({
      nTrials,
      alpha,
      reward,
      contingency: (t) => t < nTrials * 0.7,
    });
    setRwResult(rw);

    // Blocking effect
    const block = simulateBlocking({
      alpha,
      phase1Trials: 20,
      phase2Trials: 20,
      reward,
    });
    setBlockResult(block);

    // Dopamine prediction error
    const dopa = dopamineSignal({
      nSteps: 100,
      rewardTime: 50,
      alpha,
      gamma: 0.95,
    });
    setDopaResult(dopa);
  }, [alpha, nTrials, reward]);

  return (
    <article>
      <ChapterHeading>§12 Reward Learning — Rescorla–Wagner and TD(λ)</ChapterHeading>

      <FormulaBlock>
        RW: ΔV = α · (λ - V)<br />
        TD: δ = r + γ · V(s&apos;) - V(s)
      </FormulaBlock>

      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The Rescorla–Wagner model describes classical conditioning: the value V of a stimulus converges
        asymptotically to the reward λ. The TD(λ) model generalizes this to sequential decisions,
        producing a reward prediction error signal δ that closely matches the firing patterns of
        dopamine neurons. The blocking effect is a key prediction of the RW model.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <ResultCard title="Parameters">
        <ParamField label="Learning rate α" value={alpha} onChange={setAlpha} min={0.01} max={0.5} step={0.01} />
        <ParamField label="Number of trials" value={nTrials} onChange={setNTrials} min={20} max={100} step={10} />
        <ParamField label="Reward magnitude λ" value={reward} onChange={setReward} min={0.1} max={2} step={0.1} />
        <div className="mt-4">
          <RunButton onRun={run} />
        </div>
      </ResultCard>

      {rwResult && (
        <ResultCard title="Rescorla–Wagner Learning Curve">
          <Waveform data={rwResult.V} height={60} color="var(--verdigris)" label="V (predicted value)" />
          <Waveform data={rwResult.delta} height={40} color="var(--oxide)" label="δ (prediction error)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Conditioning converges asymptotically → δ turns negative during extinction
          </p>
        </ResultCard>
      )}

      {blockResult && (
        <ResultCard title="Blocking Effect">
          <Waveform data={blockResult.VA} height={50} color="var(--verdigris)" label="V_A (pre-trained stimulus)" />
          <Waveform data={blockResult.VB} height={50} color="var(--ochre)" label="V_B (new stimulus in the compound)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            A already predicts the reward → B learns almost nothing (prediction error has been consumed by A)
          </p>
        </ResultCard>
      )}

      {dopaResult && (
        <ResultCard title="Dopamine-Like Prediction Error Signal">
          <Waveform data={dopaResult.predictionError} height={60} color="var(--oxide)" label="δ(t) (prediction error)" />
          <Waveform data={dopaResult.value} height={50} color="var(--verdigris)" label="V(t) (predicted value)" />
          <p className="text-xs text-[var(--ink-light)] mt-2">
            Before learning: positive δ at reward; after learning: positive δ at the predictive cue, δ = 0 at reward
          </p>
        </ResultCard>
      )}
    </article>
  );
}
