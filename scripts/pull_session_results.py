from pathlib import Path
import config
import f1_utils
import fastf1
import pandas as pd

PROJECT_ROOT = config.PROJECT_ROOT
CACHE_DIR = config.CACHE_DIR
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs
# ---------------------------------------------------------------------
YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = f1_utils.get_event_folder()

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{EVENT_FOLDER}/{SESSION_TYPE}_results.csv"
# create file if it doesn't exist if it does exist, don't freak out (FileExistsError)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def pull_practice_results():

    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    laps = session.laps.copy()

    if laps.empty:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
        return

    laps = laps.dropna(subset=["LapTime"])
    # Filter out laps that are not accurate or have been deleted
    laps = laps[
        (laps["IsAccurate"] == True) &
        (laps["Deleted"] == False)
    ]

    # Convert LapTime to seconds for easier comparison and sorting
    laps["LapTimeSeconds"] = laps["LapTime"].apply(f1_utils.time_to_seconds)

    # Fastest valid lap per driver
    results = (
        laps.sort_values("LapTimeSeconds")
        .groupby(["Driver", "Team"])
        .first()
        .reset_index()
    )

    # Convert best lap time to seconds for easier comparison and sorting
    results["BestLap"] = results["LapTimeSeconds"].apply(f1_utils.seconds_to_lap_time)

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
    results["Sector1Time"] = results["Sector1Time"].apply(f1_utils.time_to_seconds)
    results["Sector2Time"] = results["Sector2Time"].apply(f1_utils.time_to_seconds)
    results["Sector3Time"] = results["Sector3Time"].apply(f1_utils.time_to_seconds)

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
    # create file if it doesn't exist if it does exist, don't freak out (FileExistsError)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Print results to console for debugging purposes
    if not results.empty:
        print(f"\nSaved Free Practice " f"{SESSION_TYPE}" " results to: " f"{OUTPUT_PATH}\n")
    else:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")

    print(results.to_string(index=False), "\n")

def pull_quali_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    results = session.results.copy()

    if results.empty:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
        return

    results["Q1Seconds"] = results["Q1"].apply(f1_utils.time_to_seconds)
    results["Q2Seconds"] = results["Q2"].apply(f1_utils.time_to_seconds)
    results["Q3Seconds"] = results["Q3"].apply(f1_utils.time_to_seconds)

    results["Q1"] = results["Q1Seconds"].apply(f1_utils.seconds_to_lap_time)
    results["Q2"] = results["Q2Seconds"].apply(f1_utils.seconds_to_lap_time)
    results["Q3"] = results["Q3Seconds"].apply(f1_utils.seconds_to_lap_time)

    results = results[[
        "Position",
        "Abbreviation",
        "FullName",
        "TeamName",
        "Q1",
        "Q1Seconds",
        "Q2",
        "Q2Seconds",
        "Q3",
        "Q3Seconds",
        "Status"
    ]]

    results = results.rename(columns={
    "Abbreviation": "Driver",
    "FullName": "DriverName",
    "TeamName": "Team"
    })

    if config.SESSION_TYPE == "SQ":
                results = results.rename(columns={
                    "Q1": "SQ1",
                    "Q2": "SQ2",
                    "Q3": "SQ3",
                    "Q1Seconds": "SQ1Seconds",
                    "Q2Seconds": "SQ2Seconds",
                    "Q3Seconds": "SQ3Seconds",
                })

    # If Session Type is Qualifying or Sprint Qualifying, assign points based on the respective points map
    if config.SESSION_TYPE == "Q":
        results['Potential Points'] = results['Position'].map(f1_utils.points_map).fillna(0).astype(int)
    elif config.SESSION_TYPE == "SQ":
        results['Potential Points'] = results['Position'].map(f1_utils.points_map_sprint).fillna(0).astype(int)
    else:
        print(f"\nInvalid session type: {config.SESSION_TYPE}. Please use 'Q' for Qualifying or 'SQ' for Sprint Qualifying.\n")
        return

    results.to_csv(OUTPUT_PATH, index=False)

    # Print results to console and indicate where the results have been saved
    if config.SESSION_TYPE == "SQ" and not results.empty:
        print(f"\nSaved Sprint Qualifying results to: {OUTPUT_PATH}")
    elif config.SESSION_TYPE == "Q" and not results.empty:
        print(f"\nSaved Qualifying results to: {OUTPUT_PATH}\n")
    else:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")

    print(results.to_string(index=False))

def pull_race_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    results = session.results.copy()

    # If results are empty, print a message and return
    if results.empty:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
        return

    # Amend DataFrame column names across all session types for consistency
    results = results.rename(columns={
        "Abbreviation": "Driver",
        "FullName": "Driver Name",
        "TeamName": "Team",
    })

    results = results[[
                "Position",
                "Driver",
                "Driver Name",
                "Team"
            ]]

    # If Session Type is Sprint, assign points based on Sprint points map
    if config.SESSION_TYPE == "S":
        results['Points'] = results['Position'].map(f1_utils.points_map_sprint).fillna(0).astype(int)
    # If Session Type is Race, assign points based on Race points map
    elif config.SESSION_TYPE == "R":
        results['Points'] = results['Position'].map(f1_utils.points_map).fillna(0).astype(int)
    # If Session Type is not recognized, print an error message and return
    else:
        print(f"\nInvalid session type: {config.SESSION_TYPE}. Please use 'R' for Race, 'S' for Sprint.\n")
        return

    results.to_csv(OUTPUT_PATH, index=False)

    # Print results to console and indicate where the results have been saved
    if config.SESSION_TYPE == "S" and not results.empty:
        print(f"\nSaved Sprint results to: {OUTPUT_PATH}\n")
    elif config.SESSION_TYPE == "R" and not results.empty:
        print(f"\nSaved Race results to: {OUTPUT_PATH}\n")
    else:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")

    print(results.to_string(index=False))

if __name__ == "__main__":
    
    if config.SESSION_TYPE in ["R", "S"]:
        pull_race_results()
    elif config.SESSION_TYPE in ["Q", "SQ"]:
        pull_quali_results()
    elif config.SESSION_TYPE in ["FP1", "FP2", "FP3"]:
        pull_practice_results()
    else:
        print(f"\nInvalid session type: {config.SESSION_TYPE}. Please use 'FP1', 'FP2', 'FP3', 'Q', 'SQ', 'R', or 'S'.\n")