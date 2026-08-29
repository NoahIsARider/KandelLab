import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'KandelLab — Principles of Neural Science, in Simulation',
    template: '%s — KandelLab',
  },
  description: 'Core models from the neuroscience textbook, implemented one by one from scratch. For undergraduate and graduate students to study, run experiments, and complete coursework.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="page-watermark" aria-hidden="true" />
        <div className="manuscript-page">
          <header className="text-center mb-8">
            <h1 className="font-[var(--font-display)] text-3xl md:text-4xl font-bold text-[var(--oxide)] tracking-[0.15em] uppercase mb-2">
              KandelLab
            </h1>
            <p className="text-[var(--ink-light)] text-sm tracking-widest uppercase font-[var(--font-display)]">
              Principles of Neural Science, in Simulation
            </p>
            <div className="ornament-divider">❧ ※ ❧</div>
          </header>
          <Navigation />
          <main className="fade-in">
            {children}
          </main>
          <footer className="mt-12 pt-6 border-t-2 border-double border-[var(--border-old)]">
            <p className="text-center text-xs text-[var(--ink-light)] tracking-wider">
              KandelLab · Inspired by Kandel&apos;s Principles of Neural Science
            </p>
            <p className="text-center text-xs text-[var(--ink-light)] mt-1">
              Cells → Circuits → Systems → Cognition
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}

function Navigation() {
  return (
    <nav className="mb-8">
      <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm">
        <NavLink href="/" label="Prologue" />
        <span className="text-[var(--border-old)]">|</span>
        <NavLink href="/cells" label="I. Cells" />
        <NavLink href="/circuits" label="II. Circuits" />
        <NavLink href="/systems" label="III. Systems" />
        <NavLink href="/cognitive" label="IV. Cognition" />
        <span className="text-[var(--border-old)]">|</span>
        <NavLink href="/experiments" label="Experiments" />
      </div>
    </nav>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link href={href} className="nav-link">
      {label}
    </Link>
  );
}
