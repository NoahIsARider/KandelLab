"""KandelLab — 神经科学原理仿真系统。

细胞 → 回路 → 系统 → 认知，四层递进，12 个核心概念的 Python 从零实现。
"""

try:
    from importlib.metadata import version as _dist_version
    __version__ = _dist_version("kandellab")
except Exception:  # source-tree runs (no install)
    __version__ = "0.0.0-dev"
__all__ = ["__version__"]
