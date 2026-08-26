from pathlib import Path
import config
import fastf1
import pandas as pd

PROJECT_ROOT = config.PROJECT_ROOT
CACHE_DIR = config.CACHE_DIR
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = config.get_event_folder()

OUTPUT_PATH = PROJECT_ROOT / f"data/processed/{EVENT_FOLDER}/{SESSION_TYPE}_results.csv"
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


def pull_race_results():
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

    points_map = {
        1: 25,
        2: 18,
        3: 15,
        4: 12,
        5: 10,
        6: 8,
        7: 6,
        8: 4,
        9: 2,
        10: 1
    }

    points_map_sprint = {
        1: 8,
        2: 7,
        3: 6,
        4: 5,
        5: 4,
        6: 3,
        7: 2,
        8: 1
    }

    if config.SESSION_TYPE == "S":
        results['Points'] = results['Position'].map(points_map_sprint).fillna(0).astype(int)
    else:
        results['Points'] = results['Position'].map(points_map).fillna(0).astype(int)

    results.to_csv(OUTPUT_PATH, index=False)

    if config.SESSION_TYPE == "S" and not results.empty:
        print(f"\nSaved Sprint results to: {OUTPUT_PATH}")
    elif config.SESSION_TYPE == "R" and not results.empty:
        print(f"\nSaved Race results to: {OUTPUT_PATH}")
    else:
        print(f"\nNo results found for {YEAR} {EVENT} {SESSION_TYPE}.\n")
    
    print(results.to_string(index=False))

pull_race_results()