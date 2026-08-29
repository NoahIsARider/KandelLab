import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function SystemsPage() {
  return (
    <article>
      <ChapterHeading>III. 系统层 · Systems</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        系统层研究神经系统如何实现感觉、运动、记忆与奖赏学习等功能。
        从视觉皮层的方位选择性到小脑的运动学习，从 Hopfield 网络的联想记忆
        到多巴胺系统的奖赏预测误差——每个系统都有独特的计算策略。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="10a"
          title="视觉系统"
          subtitle="Gabor 滤波器与方位调谐"
          href="/systems/vision"
          desc="V1 简单细胞以 Gabor 函数描述感受野。调谐曲线表征细胞对不同朝向的偏好。"
        />
        <ModuleCard
          number="10b"
          title="听觉系统"
          subtitle="频率调谐与耳蜗拓扑"
          href="/systems/audition"
          desc="γ-tone 滤波组模拟基底膜频率分析。特征频率沿基底膜呈对数排列（tonotopy）。"
        />
        <ModuleCard
          number="—"
          title="运动系统"
          subtitle="VOR 增益适应与小脑学习"
          href="/systems/motor"
          desc="前庭-眼反射的增益通过小脑 Marr-Albus 规则进行误差驱动学习。"
        />
        <ModuleCard
          number="11"
          title="联想记忆"
          subtitle="Hopfield 网络"
          href="/systems/memory"
          desc="w_ij = 1/N·Σξᵢξⱼ。异步更新使能量单调下降，损坏模式可恢复至存储模式。"
        />
        <ModuleCard
          number="12"
          title="奖赏学习"
          subtitle="Rescorla-Wagner 与 TD(λ)"
          href="/systems/reward"
          desc="ΔV = α·(λ-V)。奖赏预测误差驱动学习。TD 模型复现阻塞效应与多巴胺样信号。"
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
