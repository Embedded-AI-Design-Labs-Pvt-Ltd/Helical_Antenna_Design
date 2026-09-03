"""Launch the helical antenna HFSS GUI."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gui"))

from app import main  # noqa: E402

if __name__ == "__main__":
    main()
