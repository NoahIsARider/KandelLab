import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CircuitsPage() {
  return (
    <article>
      <ChapterHeading>II. Circuit Level · Circuits</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The circuit level explores interactions among multiple neurons. From the Hebbian rule of
        synaptic plasticity, to lateral inhibition sharpening sensory contrast, to the dynamics of
        excitatory–inhibitory populations and oscillatory synchronization —
        these mechanisms form the circuit-level basis of neural computation.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="6"
          title="Hebbian Learning"
          subtitle="Synaptic Plasticity and the BCM Rule"
          href="/circuits/hebbian"
          desc="Δw = η·x·y. Synaptic strength changes with the correlation between pre- and postsynaptic activity. The BCM rule introduces a sliding threshold separating LTP from LTD."
        />
        <ModuleCard
          number="7"
          title="Lateral Inhibition"
          subtitle="Center–Surround Antagonism and Edge Enhancement"
          href="/circuits/lateral-inhibition"
          desc="Difference-of-Gaussians receptive field. Uniform regions elicit a flat response; edges produce Mach band effects."
        />
        <ModuleCard
          number="8"
          title="Wilson–Cowan Model"
          subtitle="Excitatory–Inhibitory Population Dynamics"
          href="/circuits/wilson-cowan"
          desc="A two-population ODE system. Produces a range of dynamical behaviors, including monostability, bistability, and oscillations."
        />
        <ModuleCard
          number="9"
          title="Kuramoto Model"
          subtitle="Synchronization of Phase Oscillators"
          href="/circuits/kuramoto"
          desc="dθᵢ/dt = ωᵢ + K/N·Σsin(θⱼ-θᵢ). As the coupling strength K increases, the system undergoes a phase transition from desynchronization to synchronization."
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
