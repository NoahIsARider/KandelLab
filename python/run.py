#!/usr/bin/env python3
"""KandelLab convenience launcher.

Run from the python/ directory:
    python run.py              # default: cells + circuits demo
    python run.py --cells      # cells layer
    python run.py --experiments
    python run.py --version
"""

import os
import sys

# Make the python/ directory importable so KandelLab works without install.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from KandelLab.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
