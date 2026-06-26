from pathlib import Path
import fastf1
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

YEAR = 2026
EVENT = "Austria"
SESSION_TYPE = "R"

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{YEAR}_{EVENT}_{SESSION_TYPE}_results.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def time_to_seconds(value):
    if str(value) == "NaT":
        return None

    return round(value.total_seconds(), 3)


def seconds_to_lap_time(seconds):
    if pd.isna(seconds):
        return "N/A"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes}:{remaining_seconds:06.3f}"


def seconds_to_sector_time(seconds):
    if seconds is None:
        return "N/A"

    return f"{seconds:.3f}"


def pull_quali_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    results = session.results.copy()

    results = results[[
        "Position",
        "Abbreviation",
        "TeamName"
    ]]

    results = results.rename(columns={
        "Abbreviation": "Driver",
        "TeamName": "Team"
    })

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved Quali results to: {OUTPUT_PATH}")
    print(results.to_string(index=False))

pull_quali_results()