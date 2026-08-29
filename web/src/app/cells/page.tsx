import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CellsPage() {
  return (
    <article>
      <ChapterHeading>I. Cellular Level · Cells</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The cellular level focuses on the electrophysiological properties of single neurons. From the
        equilibrium potentials set by ion concentration gradients, to action potentials driven by
        voltage-gated channels, to spike-train coding and synaptic integration —
        these are the foundations for understanding how the nervous system works.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="1"
          title="Nernst Equation"
          subtitle="Ion Equilibrium Potential"
          href="/cells/nernst"
          desc="E = (RT/zF)·ln([X]₀/[X]ᵢ). The equilibrium potential of a single ion is determined by the concentration gradient across the membrane and the temperature."
        />
        <ModuleCard
          number="2"
          title="Goldman–Hodgkin–Katz Equation"
          subtitle="Resting Membrane Potential"
          href="/cells/goldman"
          desc="The membrane potential weighted by the permeability of multiple ions. When only one ion is permeable, GHK reduces to the Nernst equation."
        />
        <ModuleCard
          number="3"
          title="Hodgkin–Huxley Model"
          subtitle="Action Potential"
          href="/cells/hodgkin-huxley"
          desc="A four-variable ODE system: V, m, h, n. The gating dynamics of sodium and potassium channels produce all-or-none action potentials."
        />
        <ModuleCard
          number="4"
          title="Leaky Integrate-and-Fire"
          subtitle="Spiking Neuron Model"
          href="/cells/lif"
          desc="τ·dV/dt = -(V-E_L) + R·I. A simplified neuron model whose f-I curve can be solved analytically."
        />
        <ModuleCard
          number="5"
          title="Synapse Model"
          subtitle="EPSP/IPSP and Spatiotemporal Integration"
          href="/cells/synapse"
          desc="Alpha-function synaptic currents. Temporal and spatial summation of multiple synaptic inputs determine whether the neuron fires."
        />
      </div>
    </article>
  );
}

function ModuleCard({ number, title, subtitle, href, desc }: {
  number: string;
  title: string;
  subtitle: string;
  href: string;
  desc: string;
}) {
  return (
    <Link href={href} className="block border border-[var(--border-old)] p-4 hover:bg-[rgba(232,213,176,0.2)] transition-colors">
      <div className="flex items-baseline gap-3 mb-1">
        <span className="font-[var(--font-mono)] text-xs text-[var(--border-old)]">§{number}</span>
        <h3 className="font-[var(--font-display)] text-base font-semibold text-[var(--oxide)]">{title}</h3>
        <span className="text-xs text-[var(--ink-light)]">— {subtitle}</span>
      </div>
      <p className="text-sm text-[var(--ink)] ml-8">{desc}</p>
    </Link>
  );
}
