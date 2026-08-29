"""KandelLab CLI 入口（对应 `mankiw-econ`）：

    neuro-lab                # 默认：细胞层 + 回路层演示
    neuro-lab --cells        # 细胞层（Nernst → HH → LIF → 突触）
    neuro-lab --circuits     # 回路层（Hebb → 侧抑制 → WC → 同步）
    neuro-lab --systems      # 系统层（视觉 → 听觉 → 记忆 → 奖赏）
    neuro-lab --cognitive    # 认知层（DDM → SDT → 群体编码）
    neuro-lab --demo         # 十二大核心概念演示
    neuro-lab --experiments  # 运行全部 12 个实验
    neuro-lab --version
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, config
from . import experiments
from .utils.output import ascii_banner, print_table, print_kv


def _print_summary(s):
    print(f"\n实验 {s.get('num', '?')} — {s['name']}")
    if s.get("results"):
        print_kv(list(s["results"].items()), title="关键结果")
    if s.get("rows"):
        print_table(s["rows"], s.get("headers"))
    print("  [输出文件]")
    for f in s["figures"]:
        print(f"    {f}")
    for c in s["csvs"]:
        print(f"    {c}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="neuro-lab",
        description="KandelLab — 神经科学原理仿真系统",
        add_help=True)
    parser.add_argument("--cells", action="store_true", help="细胞层实验")
    parser.add_argument("--circuits", action="store_true", help="回路层实验")
    parser.add_argument("--systems", action="store_true", help="系统层实验")
    parser.add_argument("--cognitive", action="store_true", help="认知层实验")
    parser.add_argument("--demo", action="store_true", help="十二大核心概念演示")
    parser.add_argument("--experiments", action="store_true",
                        help="运行全部 12 个实验")
    parser.add_argument("--out", default="output", help="输出目录（默认 output）")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（默认 config 中的全局种子）")
    parser.add_argument("--quiet", action="store_true",
                        help="只输出文件路径")
    parser.add_argument("--version", action="store_true", help="版本信息")
    args = parser.parse_args(argv)

    if args.version:
        print(f"KandelLab {__version__}")
        return 0

    if args.seed is not None:
        config.NUMERICS["seed"] = args.seed

    groups = []
    for g, flag in (("cells", args.cells), ("circuits", args.circuits),
                    ("systems", args.systems), ("cognitive", args.cognitive),
                    ("demo", args.demo), ("experiments", args.experiments)):
        if flag:
            groups.append(g)
    if not groups:
        groups = ["cells", "circuits"]   # 默认行为

    total_files = []
    for g in groups:
        label = experiments._GROUP_LABEL.get(g, g)
        print(ascii_banner(f"KandelLab · {label}", char="─"))
        for s in experiments.run_group(g, args.out):
            if args.quiet:
                for f in s["figures"] + s["csvs"]:
                    print(f)
            else:
                _print_summary(s)
            total_files.extend(s["figures"] + s["csvs"])

    if not args.quiet:
        print("\n" + ascii_banner(f"完成 · 共生成 {len(total_files)} 个文件",
                                  char="─"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
