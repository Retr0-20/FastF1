from pathlib import Path

import fastf1
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

YEAR = 2026
EVENT = "Austria"
SESSION_TYPE = "FP2"

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{YEAR}_{EVENT}_{SESSION_TYPE}_fastest_laps_by_driver.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def time_to_seconds(value):
    if str(value) == "NaT":
        return None

    return round(value.total_seconds(), 3)


def seconds_to_lap_time(seconds):
    if seconds is None:
        return "N/A"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes}:{remaining_seconds:06.3f}"


def pull_fp2_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    laps = session.laps.copy()

    laps = laps.dropna(subset=["LapTime"])
    laps = laps[
        (laps["IsAccurate"] == True) &
        (laps["Deleted"] == False)
    ]

    laps["LapTimeSeconds"] = laps["LapTime"].apply(time_to_seconds)

    # Fastest valid lap per driver
    results = (
        laps.sort_values("LapTimeSeconds")
        .groupby(["Driver", "Team"])
        .first()
        .reset_index()
    )

    results["BestLap"] = results["LapTimeSeconds"].apply(seconds_to_lap_time)

    results = results[[
        "Driver",
        "Team",
        "BestLap",
        "LapTimeSeconds",
        "Compound",
        "TyreLife",
        "TrackStatus",
        "Sector1Time",
        "Sector2Time",
        "Sector3Time"
    ]]

    results = results.sort_values("LapTimeSeconds").reset_index(drop=True)
    results["Position"] = range(1, len(results) + 1)
    results["Sector1Time"] = results["Sector1Time"].apply(time_to_seconds)
    results["Sector2Time"] = results["Sector2Time"].apply(time_to_seconds)
    results["Sector3Time"] = results["Sector3Time"].apply(time_to_seconds)

    results = results[[
        "Position",
        "Driver",
        "Team",
        "BestLap",
        "LapTimeSeconds",
        "Compound",
        "TyreLife",
        "TrackStatus",
        "Sector1Time",
        "Sector2Time",
        "Sector3Time"
    ]]

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved FP2 results to: {OUTPUT_PATH}")
    print(results.to_string(index=False))


pull_fp2_results()