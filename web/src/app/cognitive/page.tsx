import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CognitivePage() {
  return (
    <article>
      <ChapterHeading>IV. Cognitive Level · Cognition</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        The cognitive level explores the computational mechanisms of decision-making, perception, and
        coding. The drift-diffusion model describes decisions as evidence accumulation; signal detection
        theory quantifies perceptual sensitivity; population coding theory reveals how the nervous
        system represents external stimuli precisely through population activity.
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="13"
          title="Drift-Diffusion Model"
          subtitle="DDM — Evidence Accumulation in Decision-Making"
          href="/cognitive/ddm"
          desc="dx = μ·dt + σ·dW with absorbing boundaries ±a. Higher drift → higher accuracy and faster RT; wider boundary → higher accuracy but slower RT."
        />
        <ModuleCard
          number="14"
          title="Signal Detection Theory"
          subtitle="SDT — d&apos;, Criterion, and ROC"
          href="/cognitive/sdt"
          desc="d&apos; = z(H) - z(FA) separates sensitivity from response bias. The area under the ROC curve is AUC = Φ(d&apos;/√2)."
        />
        <ModuleCard
          number="15"
          title="Population Coding"
          subtitle="Tuning Curves, Fisher Information, and the Cramér–Rao Bound"
          href="/cognitive/encoding"
          desc="Tuning curves (Gaussian/von Mises) describe each neuron's preference for a stimulus. Fisher information quantifies coding precision."
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
