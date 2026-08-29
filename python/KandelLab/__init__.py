"""KandelLab — a simulation system for principles of neuroscience.

Cells → circuits → systems → cognition: four progressive layers implementing
12 core concepts in Python from scratch.
"""

try:
    from importlib.metadata import version as _dist_version
    __version__ = _dist_version("kandellab")
except Exception:  # source-tree runs (no install)
    __version__ = "0.0.0-dev"
__all__ = ["__version__"]
