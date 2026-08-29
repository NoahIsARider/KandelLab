import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function ExperimentsPage() {
  return (
    <article>
      <ChapterHeading>Twelve Classic Experiments</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        Each experiment corresponds to a core neuroscience concept. Adjust parameters → run the
        simulation → observe results → analyze and answer. All experiments run in real time in
        your browser.
      </p>

      <OrnamentDivider symbol="❧ ※ ❧" />

      <div className="space-y-3">
        <ExperimentCard
          num={1}
          title="Ionic Basis of the Resting Potential"
          desc="Sweep [K⁺]₀ and observe its effect on V_rest, testing the Nernst prediction"
          href="/cells/nernst"
          layer="Cells"
        />
        <ExperimentCard
          num={2}
          title="Generation of the Action Potential"
          desc="Stimulus strength → threshold, all-or-none behavior, and refractoriness (HH model)"
          href="/cells/hodgkin-huxley"
          layer="Cells"
        />
        <ExperimentCard
          num={3}
          title="Rate Coding"
          desc="LIF: input current → f-I curve → raster plot"
          href="/cells/lif"
          layer="Cells"
        />
        <ExperimentCard
          num={4}
          title="Spatiotemporal Synaptic Integration"
          desc="Frequency × number of inputs → firing probability"
          href="/cells/synapse"
          layer="Cells"
        />
        <ExperimentCard
          num={5}
          title="Hebbian Learning"
          desc="Training with correlated input → selective strengthening"
          href="/circuits/hebbian"
          layer="Circuits"
        />
        <ExperimentCard
          num={6}
          title="Lateral Inhibition and Edge Enhancement"
          desc="DOG kernel → Mach band effect"
          href="/circuits/lateral-inhibition"
          layer="Circuits"
        />
        <ExperimentCard
          num={7}
          title="Excitation–Inhibition Balance"
          desc="Wilson–Cowan: input strength → monostability/bistability"
          href="/circuits/wilson-cowan"
          layer="Circuits"
        />
        <ExperimentCard
          num={8}
          title="Neural Oscillation and Synchronization"
          desc="Kuramoto: coupling strength → phase transition"
          href="/circuits/kuramoto"
          layer="Circuits"
        />
        <ExperimentCard
          num={9}
          title="Visual Orientation Selectivity"
          desc="Gabor tuning curve"
          href="/systems/vision"
          layer="Systems"
        />
        <ExperimentCard
          num={10}
          title="Associative Memory"
          desc="Hopfield: retrieval of corrupted patterns"
          href="/systems/memory"
          layer="Systems"
        />
        <ExperimentCard
          num={11}
          title="Reward Learning"
          desc="RW/TD: conditioning + blocking effect"
          href="/systems/reward"
          layer="Systems"
        />
        <ExperimentCard
          num={12}
          title="Perceptual Decision-Making"
          desc="DDM: accuracy–RT trade-off + ROC"
          href="/cognitive/ddm"
          layer="Cognition"
        />
      </div>
    </article>
  );
}

function ExperimentCard({ num, title, desc, href, layer }: {
  num: number;
  title: string;
  desc: string;
  href: string;
  layer: string;
}) {
  return (
    <Link href={href} className="block border border-[var(--border-old)] p-4 hover:bg-[rgba(232,213,176,0.2)] transition-colors">
      <div className="flex items-baseline gap-3">
        <span className="font-[var(--font-mono)] text-xs text-[var(--border-old)]">
          Exp.{num}
        </span>
        <h3 className="font-[var(--font-display)] text-base font-semibold text-[var(--oxide)]">
          {title}
        </h3>
        <span className="text-xs text-[var(--ink-light)] ml-auto">[{layer}]</span>
      </div>
      <p className="text-sm text-[var(--ink)] ml-12 mt-1">{desc}</p>
    </Link>
  );
}
