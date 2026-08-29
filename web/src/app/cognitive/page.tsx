import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function CognitivePage() {
  return (
    <article>
      <ChapterHeading>IV. 认知层 · Cognitive</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        认知层探讨决策、感知与编码的计算机制。漂移扩散模型将决策描述为
        证据累积过程，信号检测论量化感知敏感性，群体编码理论则揭示
        神经系统如何以群体活动精确表征外部刺激。
      </p>

      <OrnamentDivider symbol="— ✦ —" />

      <div className="space-y-4">
        <ModuleCard
          number="13"
          title="漂移扩散模型"
          subtitle="DDM — 决策的证据累积"
          href="/cognitive/ddm"
          desc="dx = μ·dt + σ·dW，边界 ±a 吸收。漂移率↑则正确率↑RT↓；边界↑则正确率↑RT↑。"
        />
        <ModuleCard
          number="14"
          title="信号检测论"
          subtitle="SDT — d&apos;、判断标准与 ROC"
          href="/cognitive/sdt"
          desc="d&apos; = z(H) - z(FA)。分离敏感性与反应偏差。ROC 曲线下面积 AUC = Φ(d&apos;/√2)。"
        />
        <ModuleCard
          number="15"
          title="群体编码"
          subtitle="调谐曲线、Fisher 信息与 Cramér-Rao 界"
          href="/cognitive/encoding"
          desc="调谐曲线（高斯/von Mises）描述单个神经元对刺激的偏好。Fisher 信息量化编码精度。"
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
