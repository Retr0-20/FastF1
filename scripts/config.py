from pathlib import Path

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs
# ---------------------------------------------------------------------

YEAR = 2026
EVENT = "Monza"
SESSION_TYPE = "FP3"  # Options: FP1, FP2, FP3, Q, R, SQ, S

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
