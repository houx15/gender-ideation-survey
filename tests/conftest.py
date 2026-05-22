"""Pytest config: make the analysis scripts importable as modules."""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "outputs" / "survey_exploration" / "scripts"
sys.path.insert(0, str(SCRIPTS))
