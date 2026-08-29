import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function SystemsPage() {
  return (
    <article>
      <ChapterHeading>III. System Level · Systems</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The system level studies how the nervous system implements sensation, movement, memory, and
        reward-based learning. From orientation selectivity in visual cortex to cerebellar motor
        learning, from associative memory in Hopfield networks to reward prediction error in the
        dopamine system — each system has its own computational strategy.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="10a"
          title="Visual System"
          subtitle="Gabor Filters and Orientation Tuning"
          href="/systems/vision"
          desc="V1 simple cells have receptive fields described by Gabor functions. Tuning curves characterize each cell's preference for different orientations."
        />
        <ModuleCard
          number="10b"
          title="Auditory System"
          subtitle="Frequency Tuning and Cochlear Tonotopy"
          href="/systems/audition"
          desc="A γ-tone filter bank mimics the basilar membrane's frequency analysis. Characteristic frequencies are arranged logarithmically along the membrane (tonotopy)."
        />
        <ModuleCard
          number="—"
          title="Motor System"
          subtitle="VOR Gain Adaptation and Cerebellar Learning"
          href="/systems/motor"
          desc="The vestibulo-ocular reflex gain is learned through error-driven cerebellar learning (Marr–Albus rule)."
        />
        <ModuleCard
          number="11"
          title="Associative Memory"
          subtitle="Hopfield Network"
          href="/systems/memory"
          desc="w_ij = 1/N·Σξᵢξⱼ. Asynchronous updates monotonically decrease the energy, restoring corrupted patterns to stored memories."
        />
        <ModuleCard
          number="12"
          title="Reward Learning"
          subtitle="Rescorla–Wagner and TD(λ)"
          href="/systems/reward"
          desc="ΔV = α·(λ-V). Reward prediction error drives learning. The TD model reproduces the blocking effect and dopamine-like signals."
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
