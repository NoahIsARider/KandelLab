import Link from 'next/link';
import { ChapterHeading, OrnamentDivider } from '@/components/simulation-ui';

export default function ExperimentsPage() {
  return (
    <article>
      <ChapterHeading>十二大经典实验</ChapterHeading>
      <p className="text-sm text-[var(--ink)] mb-4 leading-relaxed">
        每个实验对应一个核心神经科学概念。修改参数 → 运行仿真 → 观察结果 → 分析回答。
        所有实验均可在浏览器中实时运算。
      </p>

      <OrnamentDivider symbol="❧ ※ ❧" />

      <div className="space-y-3">
        <ExperimentCard
          num={1}
          title="静息电位的离子基础"
          desc="扫描 [K⁺]₀ 对 V_rest 的影响，验证 Nernst 预测"
          href="/cells/nernst"
          layer="细胞"
        />
        <ExperimentCard
          num={2}
          title="动作电位的产生"
          desc="刺激强度 → 阈值/全或无/不应期（HH 模型）"
          href="/cells/hodgkin-huxley"
          layer="细胞"
        />
        <ExperimentCard
          num={3}
          title="频率编码"
          desc="LIF：输入电流 → f-I 曲线 → 栅栏图"
          href="/cells/lif"
          layer="细胞"
        />
        <ExperimentCard
          num={4}
          title="突触时空整合"
          desc="频率 × 数量 → 发放概率"
          href="/cells/synapse"
          layer="细胞"
        />
        <ExperimentCard
          num={5}
          title="Hebbian 学习"
          desc="相关输入训练 → 选择性强化"
          href="/circuits/hebbian"
          layer="回路"
        />
        <ExperimentCard
          num={6}
          title="侧抑制与边缘增强"
          desc="DOG 核 → Mach band 效应"
          href="/circuits/lateral-inhibition"
          layer="回路"
        />
        <ExperimentCard
          num={7}
          title="兴奋-抑制平衡"
          desc="Wilson-Cowan：输入强度 → 单稳态/双稳态"
          href="/circuits/wilson-cowan"
          layer="回路"
        />
        <ExperimentCard
          num={8}
          title="神经振荡同步"
          desc="Kuramoto：耦合强度 → 相变"
          href="/circuits/kuramoto"
          layer="回路"
        />
        <ExperimentCard
          num={9}
          title="视觉方位选择性"
          desc="Gabor 调谐曲线"
          href="/systems/vision"
          layer="系统"
        />
        <ExperimentCard
          num={10}
          title="联想记忆"
          desc="Hopfield：损坏模式恢复过程"
          href="/systems/memory"
          layer="系统"
        />
        <ExperimentCard
          num={11}
          title="奖赏学习"
          desc="RW/TD：条件反射 + 阻塞效应"
          href="/systems/reward"
          layer="系统"
        />
        <ExperimentCard
          num={12}
          title="知觉决策"
          desc="DDM：正确率-RT 权衡 + ROC"
          href="/cognitive/ddm"
          layer="认知"
        />
      </div>
    </article>
  );
}

function ExperimentCard({ num, title, desc, href, layer }: {
  num: number;
  title: string;
  desc: string;
  href: string;
  layer: string;
}) {
  return (
    <Link href={href} className="block border border-[var(--border-old)] p-4 hover:bg-[rgba(232,213,176,0.2)] transition-colors">
      <div className="flex items-baseline gap-3">
        <span className="font-[var(--font-mono)] text-xs text-[var(--border-old)]">
          Exp.{num}
        </span>
        <h3 className="font-[var(--font-display)] text-base font-semibold text-[var(--oxide)]">
          {title}
        </h3>
        <span className="text-xs text-[var(--ink-light)] ml-auto">[{layer}]</span>
      </div>
      <p className="text-sm text-[var(--ink)] ml-12 mt-1">{desc}</p>
    </Link>
  );
}
