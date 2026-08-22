from pathlib import Path

# Configurable information for Grand Prixs

YEAR = 2026
EVENT = "Netherlands"
SESSION_TYPE = "FP1"  # Options: FP1, FP2, FP3, Q, R
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
