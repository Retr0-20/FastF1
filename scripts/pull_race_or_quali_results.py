from pathlib import Path
import config
import f1_utils
import fastf1
import pandas as pd

PROJECT_ROOT = config.PROJECT_ROOT
CACHE_DIR = config.CACHE_DIR
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = f1_utils.get_event_folder()

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{EVENT_FOLDER}/{SESSION_TYPE}_results.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def pull_race_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    results = session.results.copy()

    if results.empty:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
        return

    results = results.rename(columns={
        "Abbreviation": "Driver",
        "FullName": "Driver Name",
        "TeamName": "Team",
    })

    if config.SESSION_TYPE == "S":
        results = results[[
            "Position",
            "Driver",
            "Driver Name",
            "Team"
        ]]

        results['Points'] = results['Position'].map(f1_utils.points_map_sprint).fillna(0).astype(int)
        
    elif config.SESSION_TYPE == "R":
        results = results[[
            "Position",
            "Driver",
            "Driver Name",
            "Team"
        ]]

        results['Points'] = results['Position'].map(f1_utils.points_map).fillna(0).astype(int)

    elif config.SESSION_TYPE == "Q" or config.SESSION_TYPE == "SQ":
        results = results[[
            "Position",
            "Driver",
            "Driver Name",
            "Team",
            "Q1",
            "Q2",
            "Q3",
        ]]

        results["Q1Seconds"] = results["Q1"].apply(f1_utils.time_to_seconds)
        results["Q2Seconds"] = results["Q2"].apply(f1_utils.time_to_seconds)
        results["Q3Seconds"] = results["Q3"].apply(f1_utils.time_to_seconds)
        
        results["Q1"] = results["Q1Seconds"].apply(f1_utils.seconds_to_lap_time)
        results["Q2"] = results["Q2Seconds"].apply(f1_utils.seconds_to_lap_time)
        results["Q3"] = results["Q3Seconds"].apply(f1_utils.seconds_to_lap_time)

        if config.SESSION_TYPE == "SQ":
            results = results.rename(columns={
                "Q1": "SQ1",
                "Q2": "SQ2",
                "Q3": "SQ3",
                "Q1Seconds": "SQ1Seconds",
                "Q2Seconds": "SQ2Seconds",
                "Q3Seconds": "SQ3Seconds",
            })

        if config.SESSION_TYPE == "Q":
            results['Potential Points'] = results['Position'].map(f1_utils.points_map).fillna(0).astype(int)
        elif config.SESSION_TYPE == "SQ":
            results['Potential Points'] = results['Position'].map(f1_utils.points_map_sprint).fillna(0).astype(int)

    else:
        print(f"\nInvalid session type: {config.SESSION_TYPE}. Please use 'R' for Race, 'S' for Sprint, or 'Q' for Qualifying.\n")
        return

    results.to_csv(OUTPUT_PATH, index=False)

    if config.SESSION_TYPE == "S" and not results.empty:
        print(f"\nSaved Sprint results to: {OUTPUT_PATH}")
    elif config.SESSION_TYPE == "R" and not results.empty:
        print(f"\nSaved Race results to: {OUTPUT_PATH}")
    elif config.SESSION_TYPE == "Q" and not results.empty:
        print(f"\nSaved Qualifying results to: {OUTPUT_PATH}")
    elif config.SESSION_TYPE == "SQ" and not results.empty:
        print(f"\nSaved Sprint Qualifying results to: {OUTPUT_PATH}")
    else:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
    
    print(results.to_string(index=False))

pull_race_results()