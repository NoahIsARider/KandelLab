"""KandelLab — console output: tables, key-value pairs, ASCII banners."""

from __future__ import annotations

import csv
import os
from pathlib import Path


def ascii_banner(title: str, width: int = 60, char: str = "=") -> str:
    """Centered ASCII separator banner."""
    pad = max(0, (width - len(title) - 2) // 2)
    line = char * width
    return f"{line}\n{char} {title:<{pad*2}} {char}\n{line}"


def print_table(rows, headers=None, float_fmt=".3f"):
    """Print a table with aligned fixed-width columns.

    Parameters
    ----------
    rows : list[list]
        Data rows.
    headers : list[str] | None
    float_fmt : str
        Float format; None prints values as-is.
    """
    def fmt(v):
        if float_fmt is not None and isinstance(v, (int, float)):
            return f"{v:{float_fmt}}"
        return str(v)

    if headers is not None:
        body = [[fmt(v) for v in row] for row in rows]
        grid = [headers] + body
    else:
        grid = [[fmt(v) for v in row] for row in rows]

    widths = [max(len(r[i]) for r in grid) for i in range(len(grid[0]))]
    lines = []
    for r in grid:
        lines.append("  ".join(cell.ljust(w) for cell, w in zip(r, widths)))
    if headers is not None:
        lines.insert(1, "  ".join("-" * w for w in widths))
    print("\n".join(lines))


def print_kv(pairs, title=None):
    """Print a key-value block."""
    if title:
        print(f"[ {title} ]")
    for k, v in pairs:
        print(f"  {k:<24}: {v}")


def save_csv(rows, path, headers=None, float_fmt="%.6g"):
    """Save data to CSV.

    Parameters
    ----------
    rows : list[list] | np.ndarray
    path : str | Path
    headers : list[str] | None
    float_fmt : str
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        if headers is not None:
            writer.writerow(headers)
        for row in rows:
            line = []
            for v in row:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    line.append(float_fmt % v)
                else:
                    line.append(v)
            writer.writerow(line)
    return str(path)


def make_output_dir(root: str = "output") -> Path:
    """Ensure the output directory exists and return its path."""
    out = Path(root)
    out.mkdir(parents=True, exist_ok=True)
    return out


def ensure_subdir(root: str, name: str) -> Path:
    """Create (if missing) a subdirectory under the output root and return its path."""
    d = Path(root) / name
    d.mkdir(parents=True, exist_ok=True)
    return d
