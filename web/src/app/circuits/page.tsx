import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CircuitsPage() {
  return (
    <article>
      <ChapterHeading>II. 回路层 · Circuits</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        回路层探索多神经元之间的相互作用。从突触可塑性的 Hebb 规则，
        到侧抑制增强感觉对比，再到兴奋-抑制群体的动力学与振荡同步——
        这些机制构成了神经计算的回路基础。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="6"
          title="Hebbian 学习"
          subtitle="突触可塑性与 BCM 规则"
          href="/circuits/hebbian"
          desc="Δw = η·x·y。突触强度随前后神经元活动的相关性改变。BCM 规则引入滑动阈值区分 LTP 与 LTD。"
        />
        <ModuleCard
          number="7"
          title="侧抑制"
          subtitle="中心-周围拮抗与边缘增强"
          href="/circuits/lateral-inhibition"
          desc="Difference-of-Gaussians 感受野。均匀区域响应平坦，边缘处出现 Mach band 效应。"
        />
        <ModuleCard
          number="8"
          title="Wilson-Cowan 模型"
          subtitle="兴奋-抑制群体动力学"
          href="/circuits/wilson-cowan"
          desc="双群体 ODE 系统。可产生单稳态、双稳态、振荡等多种动力学行为。"
        />
        <ModuleCard
          number="9"
          title="Kuramoto 模型"
          subtitle="相位振荡器同步"
          href="/circuits/kuramoto"
          desc="dθᵢ/dt = ωᵢ + K/N·Σsin(θⱼ-θᵢ)。耦合强度 K 增大时发生从非同步到同步的相变。"
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
