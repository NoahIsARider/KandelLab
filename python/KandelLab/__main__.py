"""支持 `python -m KandelLab` 运行 CLI。"""

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())
