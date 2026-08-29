"""KandelLab CLI entry point (the counterpart of `mankiw-econ`):

    neuro-lab                # default: cell-layer + circuit-layer demo
    neuro-lab --cells        # cell layer (Nernst → HH → LIF → synapse)
    neuro-lab --circuits     # circuit layer (Hebb → lateral inhibition → WC → sync)
    neuro-lab --systems      # system layer (vision → audition → memory → reward)
    neuro-lab --cognitive    # cognition layer (DDM → SDT → population coding)
    neuro-lab --demo         # demo of the twelve core concepts
    neuro-lab --experiments  # run all 12 experiments
    neuro-lab --version
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, config
from . import experiments
from .utils.output import ascii_banner, print_table, print_kv


def _print_summary(s):
    print(f"\nExperiment {s.get('num', '?')} — {s['name']}")
    if s.get("results"):
        print_kv(list(s["results"].items()), title="Key results")
    if s.get("rows"):
        print_table(s["rows"], s.get("headers"))
    print("  [Output files]")
    for f in s["figures"]:
        print(f"    {f}")
    for c in s["csvs"]:
        print(f"    {c}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="neuro-lab",
        description="KandelLab — simulation system for principles of neuroscience",
        add_help=True)
    parser.add_argument("--cells", action="store_true", help="cell-layer experiments")
    parser.add_argument("--circuits", action="store_true", help="circuit-layer experiments")
    parser.add_argument("--systems", action="store_true", help="system-layer experiments")
    parser.add_argument("--cognitive", action="store_true", help="cognition-layer experiments")
    parser.add_argument("--demo", action="store_true", help="demo of the twelve core concepts")
    parser.add_argument("--experiments", action="store_true",
                        help="run all 12 experiments")
    parser.add_argument("--out", default="output", help="output directory (default: output)")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed (default: the global seed in config)")
    parser.add_argument("--quiet", action="store_true",
                        help="print only file paths")
    parser.add_argument("--version", action="store_true", help="version info")
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
        groups = ["cells", "circuits"]   # default behavior

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
        print("\n" + ascii_banner(f"Done · generated {len(total_files)} files",
                                  char="─"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
