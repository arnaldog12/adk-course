"""Evaluation module for the support agent."""

import sys
from pathlib import Path

# Ensure evaluation/ is on sys.path so sibling modules (e.g. tools.py) are
# importable as bare names regardless of who loads this package (ADK server,
# pytest, importlib, etc.). pyproject.toml's pythonpath only covers pytest.
_pkg_dir = str(Path(__file__).parent)
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from .agent import root_agent

__all__ = ["root_agent"]
