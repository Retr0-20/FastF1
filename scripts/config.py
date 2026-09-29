from pathlib import Path

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs
# ---------------------------------------------------------------------

YEAR = 2026
<<<<<<< HEAD
EVENT = "Azerbaijan"
=======
EVENT = "Spain"
>>>>>>> d3418d1 (Changed an example script from the documenation online to work with the config script, need to read through, understand and refactor.)
SESSION_TYPE = "R"  # Options: FP1, FP2, FP3, Q, R, SQ, S

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
