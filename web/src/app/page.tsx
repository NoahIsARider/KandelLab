import Link from 'next/link';

export default function HomePage() {
  return (
    <article>
      <section className="mb-8">
        <p className="text-base leading-relaxed text-[var(--ink)] mb-4">
          <span className="font-[var(--font-display)] text-2xl text-[var(--oxide)]">K</span>
          andelLab 是一个神经科学原理仿真系统——将 Eric Kandel 经典教材{' '}
          <em>Principles of Neural Science</em>{' '}
          中的核心模型，逐个用代码从零实现。每一个概念都对应一个可运行的仿真实验，
          供学生调整参数、观察现象、验证理论。
        </p>
        <p className="text-sm leading-relaxed text-[var(--ink-light)]">
          本系统覆盖四个层次：从离子通道的分子动力学，到神经回路的群体行为，
          再到感觉系统的信息编码，最终抵达认知层面的决策模型。
          所有仿真均在浏览器内实时运算，无需安装任何软件。
        </p>
      </section>

      <div className="ornament-divider">⁂</div>

      <section className="mb-8">
        <h2 className="chapter-heading">十二大核心概念</h2>
        <p className="text-sm text-[var(--ink-light)] mb-4">
          层次递进：细胞 → 回路 → 系统 → 认知
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ConceptSection
            number="I"
            title="细胞层 · Cells"
            href="/cells"
            concepts={[
              '离子浓度差决定膜电位（Nernst 方程）',
              '通透性决定静息电位（GHK 方程）',
              '动作电位是电压门控离子通道的动力学（HH 模型）',
              '神经元以脉冲序列编码信息（LIF 模型）',
              '突触输入在时空上整合决定发放',
            ]}
          />
          <ConceptSection
            number="II"
            title="回路层 · Circuits"
            href="/circuits"
            concepts={[
              '突触强度随使用改变（Hebbian 可塑性）',
              '侧抑制增强感觉对比（中心-周围拮抗）',
              '皮层兴奋-抑制平衡（Wilson-Cowan）',
              '振荡与同步是神经节律的基础（Kuramoto）',
            ]}
          />
          <ConceptSection
            number="III"
            title="系统层 · Systems"
            href="/systems"
            concepts={[
              '感觉系统按特征调谐（视觉/听觉）',
              '运动学习与 VOR 增益适应',
              '联想记忆（Hopfield 网络）',
              '学习依赖奖赏预测误差（多巴胺）',
            ]}
          />
          <ConceptSection
            number="IV"
            title="认知层 · Cognitive"
            href="/cognitive"
            concepts={[
              '决策是证据累积到阈值（漂移扩散模型）',
              '信号检测论：d&apos; 与判断标准',
              '群体编码与 Fisher 信息',
            ]}
          />
        </div>
      </section>

      <div className="ornament-divider">❧ ☙</div>

      <section className="mb-8">
        <h2 className="chapter-heading">参考教材</h2>
        <div className="border border-[var(--border-old)] p-4 bg-[rgba(239,224,198,0.3)]">
          <table className="data-table">
            <thead>
              <tr>
                <th>层次</th>
                <th>基准教材</th>
                <th>辅助参考</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>本科基准</td>
                <td>Kandel, Principles of Neural Science, 6th</td>
                <td>Bear, Connors &amp; Paradiso</td>
              </tr>
              <tr>
                <td>研究生计算</td>
                <td>Dayan &amp; Abbott, Theoretical Neuroscience</td>
                <td>Gerstner et al., Neuronal Dynamics</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="chapter-heading">使用说明</h2>
        <p className="text-sm text-[var(--ink)] mb-3">
          每个模块页面均包含：
        </p>
        <ul className="text-sm text-[var(--ink)] space-y-1 ml-4 list-disc">
          <li>核心公式与理论背景</li>
          <li>可调参数面板——修改参数后点击「运行仿真」</li>
          <li>仿真结果以纯 CSS 图表呈现（无 SVG/Canvas）</li>
          <li>数值数据表格供进一步分析</li>
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
