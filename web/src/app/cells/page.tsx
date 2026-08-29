import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CellsPage() {
  return (
    <article>
      <ChapterHeading>I. 细胞层 · Cells</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        细胞层关注单个神经元的电生理特性。从离子浓度差产生的平衡电位，
        到电压门控通道驱动的动作电位，再到脉冲序列编码与突触整合——
        这些是理解神经系统功能的基石。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="1"
          title="Nernst 方程"
          subtitle="离子平衡电位"
          href="/cells/nernst"
          desc="E = (RT/zF)·ln([X]₀/[X]ᵢ)。单一离子的平衡电位由膜内外浓度差与温度决定。"
        />
        <ModuleCard
          number="2"
          title="Goldman-Hodgkin-Katz 方程"
          subtitle="静息膜电位"
          href="/cells/goldman"
          desc="多离子通透性加权的膜电位。当仅一种离子可通透时，GHK 退化为 Nernst 方程。"
        />
        <ModuleCard
          number="3"
          title="Hodgkin-Huxley 模型"
          subtitle="动作电位"
          href="/cells/hodgkin-huxley"
          desc="四变量 ODE 系统：V, m, h, n。钠钾通道的门控动力学产生全或无的动作电位。"
        />
        <ModuleCard
          number="4"
          title="Leaky Integrate-and-Fire"
          subtitle="脉冲发放模型"
          href="/cells/lif"
          desc="τ·dV/dt = -(V-E_L) + R·I。简化的神经元模型，可解析求解 f-I 曲线。"
        />
        <ModuleCard
          number="5"
          title="突触模型"
          subtitle="EPSP/IPSP 与时空整合"
          href="/cells/synapse"
          desc="α 函数突触电流。多个突触输入的时间总和与空间总和决定神经元是否发放。"
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
