import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'KandelLab — 神经科学原理仿真系统',
    template: '%s — KandelLab',
  },
  description: '把神经科学教材的核心模型，逐个从零实现。供本科生/研究生学习、做实验、做课堂作业。',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        <div className="manuscript-page">
          <header className="text-center mb-8">
            <h1 className="font-[var(--font-display)] text-3xl md:text-4xl font-bold text-[var(--oxide)] tracking-[0.15em] uppercase mb-2">
              KandelLab
            </h1>
            <p className="text-[var(--ink-light)] text-sm tracking-widest uppercase font-[var(--font-display)]">
              神经科学原理仿真系统
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
              细胞 → 回路 → 系统 → 认知
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
        <NavLink href="/" label="卷首" />
        <span className="text-[var(--border-old)]">|</span>
        <NavLink href="/cells" label="I. 细胞" />
        <NavLink href="/circuits" label="II. 回路" />
        <NavLink href="/systems" label="III. 系统" />
        <NavLink href="/cognitive" label="IV. 认知" />
        <span className="text-[var(--border-old)]">|</span>
        <NavLink href="/experiments" label="实验" />
      </div>
    </nav>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <a href={href} className="nav-link">
      {label}
    </a>
  );
}
