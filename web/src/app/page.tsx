import Link from 'next/link';

export default function HomePage() {
  return (
    <article>
      <section className="mb-8">
        <p className="text-base leading-relaxed text-[var(--ink)] mb-4">
          <span className="font-[var(--font-display)] text-2xl text-[var(--oxide)]">K</span>
          andelLab is a simulation system for the principles of neuroscience — implementing the core models of Eric Kandel's classic textbook{' '}
          <em>Principles of Neural Science</em>{' '}
          from scratch in code, one by one. Every concept corresponds to a runnable simulation experiment,
          where students adjust parameters, observe phenomena, and verify the theory.
        </p>
        <p className="text-sm leading-relaxed text-[var(--ink-light)]">
          The system spans four levels: from the molecular dynamics of ion channels, to the population
          behavior of neural circuits, to information coding in sensory systems, and finally to decision
          models at the cognitive level. All simulations run in real time in your browser — no software
          installation required.
        </p>
      </section>

      <div className="ornament-divider">⁂</div>

      <section className="mb-8">
        <h2 className="chapter-heading">Twelve Core Concepts</h2>
        <p className="text-sm text-[var(--ink-light)] mb-4">
          Progression: Cells → Circuits → Systems → Cognitive
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ConceptSection
            number="I"
            title="Cellular Level · Cells"
            href="/cells"
            concepts={[
              'Ion concentration gradients determine the membrane potential (Nernst equation)',
              'Permeability determines the resting potential (GHK equation)',
              'Action potentials are the dynamics of voltage-gated ion channels (HH model)',
              'Neurons encode information in spike trains (LIF model)',
              'Synaptic inputs integrate over space and time to trigger firing',
            ]}
          />
          <ConceptSection
            number="II"
            title="Circuit Level · Circuits"
            href="/circuits"
            concepts={[
              'Synaptic strength changes with use (Hebbian plasticity)',
              'Lateral inhibition sharpens sensory contrast (center–surround antagonism)',
              'Cortical excitation–inhibition balance (Wilson–Cowan)',
              'Oscillation and synchronization underlie neural rhythms (Kuramoto)',
            ]}
          />
          <ConceptSection
            number="III"
            title="System Level · Systems"
            href="/systems"
            concepts={[
              'Sensory systems are tuned to stimulus features (vision/audition)',
              'Motor learning and VOR gain adaptation',
              'Associative memory (Hopfield network)',
              'Learning depends on reward prediction error (dopamine)',
            ]}
          />
          <ConceptSection
            number="IV"
            title="Cognitive Level · Cognition"
            href="/cognitive"
            concepts={[
              'Decision-making is evidence accumulation to a threshold (drift-diffusion model)',
              'Signal detection theory: d&apos; and decision criterion',
              'Population coding and Fisher information',
            ]}
          />
        </div>
      </section>

      <div className="ornament-divider">❧ ☙</div>

      <section className="mb-8">
        <h2 className="chapter-heading">Reference Textbooks</h2>
        <div className="border border-[var(--border-old)] p-4 bg-[rgba(239,224,198,0.3)]">
          <table className="data-table">
            <thead>
              <tr>
                <th>Level</th>
                <th>Primary Textbook</th>
                <th>Additional References</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Undergraduate foundation</td>
                <td>Kandel, Principles of Neural Science, 6th</td>
                <td>Bear, Connors &amp; Paradiso</td>
              </tr>
              <tr>
                <td>Graduate / computational</td>
                <td>Dayan &amp; Abbott, Theoretical Neuroscience</td>
                <td>Gerstner et al., Neuronal Dynamics</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="chapter-heading">How to Use</h2>
        <p className="text-sm text-[var(--ink)] mb-3">
          Each module page includes:
        </p>
        <ul className="text-sm text-[var(--ink)] space-y-1 ml-4 list-disc">
          <li>Core equations and theoretical background</li>
          <li>An adjustable parameter panel — change parameters, then click &ldquo;Run Simulation&rdquo;</li>
          <li>Simulation results rendered as pure-CSS charts (no SVG/Canvas)</li>
          <li>Numerical data tables for further analysis</li>
        </ul>
      </section>
    </article>
  );
}

function ConceptSection({
  number,
  title,
  href,
  concepts,
}: {
  number: string;
  title: string;
  href: string;
  concepts: string[];
}) {
  return (
    <div className="border border-[var(--border-old)] p-4">
      <Link href={href} className="nav-link">
        <h3 className="font-[var(--font-display)] text-lg font-semibold text-[var(--oxide)] mb-2">
          {number}. {title}
        </h3>
      </Link>
      <ul className="text-sm text-[var(--ink)] space-y-1">
        {concepts.map((c, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-[var(--border-old)] mt-0.5">◆</span>
            <span>{c}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
