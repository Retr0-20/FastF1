from pathlib import Path
import config
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
EVENT_FOLDER = config.get_event_folder()

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{EVENT_FOLDER}/{SESSION_TYPE}_fastest_laps_by_driver.csv"
# create file if it doesn't exist if it does exist, don't freak out (FileExistsError)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def time_to_seconds(value):
    if str(value) == "NaT":
        return None

    # Convert a timedelta to seconds with millisecond precision 3rd decimal place
    return round(value.total_seconds(), 3)


def seconds_to_lap_time(seconds):
    if seconds is None:
        return "N/A"

    # extract minutes through floor division and seconds through modulo - returning remaining seconds
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    # '0' - pad with leading zeroes, '6' - total width of 6 characters, '.3f' - 3 decimal places
    return f"{minutes}:{remaining_seconds:06.3f}"


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