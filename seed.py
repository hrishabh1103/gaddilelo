#!/usr/bin/env python3
"""
Convenience entry point for seeding realistic Indore pilot data.
Usage:
  python3 seed.py
"""
import os
import sys
from pathlib import Path

# If virtual environment exists and is not currently active, re-exec with venv python
root_dir = Path(__file__).resolve().parent
venv_python = root_dir / "backend" / "venv" / "bin" / "python3"
if venv_python.exists() and sys.executable != str(venv_python):
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import asyncio
from backend.app.seed.seed_data import seed_all

if __name__ == "__main__":
    asyncio.run(seed_all())
