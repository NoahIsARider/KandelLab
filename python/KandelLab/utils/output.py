"""KandelLab — 控制台输出：表格、键值对、ASCII 标题。"""

from __future__ import annotations

import csv
import os
from pathlib import Path


def ascii_banner(title: str, width: int = 60, char: str = "=") -> str:
    """居中的 ASCII 分隔横幅。"""
    pad = max(0, (width - len(title) - 2) // 2)
    line = char * width
    return f"{line}\n{char} {title:<{pad*2}} {char}\n{line}"


def print_table(rows, headers=None, float_fmt=".3f"):
    """以对齐的等宽列打印表格。

    Parameters
    ----------
    rows : list[list]
        数据行。
    headers : list[str] | None
    float_fmt : str
        浮点数格式；None 表示原样输出。
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
    """打印键值对块。"""
    if title:
        print(f"[ {title} ]")
    for k, v in pairs:
        print(f"  {k:<24}: {v}")


def save_csv(rows, path, headers=None, float_fmt="%.6g"):
    """保存数据到 CSV。

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
    """确保输出目录存在并返回其路径。"""
    out = Path(root)
    out.mkdir(parents=True, exist_ok=True)
    return out


def ensure_subdir(root: str, name: str) -> Path:
    """在输出根目录下创建（若不存在）子目录并返回路径。"""
    d = Path(root) / name
    d.mkdir(parents=True, exist_ok=True)
    return d
