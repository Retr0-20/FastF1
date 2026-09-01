from pathlib import Path
import config
import f1_utils
import fastf1
import pandas as pd

PROJECT_ROOT = config.PROJECT_ROOT
CACHE_DIR = config.CACHE_DIR
# Enable FastF1 cache
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs - config.py
# ---------------------------------------------------------------------
YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = f1_utils.get_event_folder()

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{EVENT_FOLDER}/{SESSION_TYPE}_fastest_laps_by_driver.csv"
# create file if it doesn't exist if it does exist, don't freak out (FileExistsError)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def pull_practice_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    laps = session.laps.copy()

    laps = laps.dropna(subset=["LapTime"])
    # Filter out laps that are not accurate or have been deleted
    laps = laps[
        (laps["IsAccurate"] == True) &
        (laps["Deleted"] == False)
    ]

    # Convert LapTime to seconds for easier comparison and sorting
    laps["LapTimeSeconds"] = laps["LapTime"].apply(time_to_seconds)

    # Fastest valid lap per driver
    results = (
        laps.sort_values("LapTimeSeconds")
        .groupby(["Driver", "Team"])
        .first()
        .reset_index()
    )

    # Convert best lap time to seconds for easier comparison and sorting
    results["BestLap"] = results["LapTimeSeconds"].apply(seconds_to_lap_time)

    # Select relevant columns and sort by lap time
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

    # Sort by lap time and assign position
    results = results.sort_values("LapTimeSeconds").reset_index(drop=True)
    results["Position"] = range(1, len(results) + 1)
    # Convert sector times to seconds for easier comparison and sorting
    results["Sector1Time"] = results["Sector1Time"].apply(time_to_seconds)
    results["Sector2Time"] = results["Sector2Time"].apply(time_to_seconds)
    results["Sector3Time"] = results["Sector3Time"].apply(time_to_seconds)

    # Append position to DataFrame
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

    # Save results to CSV
    results.to_csv(OUTPUT_PATH, index=False)

    # Print results to console for debugging purposes
    print(f"\nSaved Free Practice " f"{SESSION_TYPE}" " results to: " f"{OUTPUT_PATH}\n")
    print(results.to_string(index=False), "\n")

# Call the function to pull practice results when the script is run directly
pull_practice_results()