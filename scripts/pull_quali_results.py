from pathlib import Path
import config
from f1_utils import time_to_seconds, seconds_to_lap_time
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


def pull_quali_results():
    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load()

    results = session.results.copy()

    results["Q1Seconds"] = results["Q1"].apply(time_to_seconds)
    results["Q2Seconds"] = results["Q2"].apply(time_to_seconds)
    results["Q3Seconds"] = results["Q3"].apply(time_to_seconds)

    results["Q1"] = results["Q1Seconds"].apply(seconds_to_lap_time)
    results["Q2"] = results["Q2Seconds"].apply(seconds_to_lap_time)
    results["Q3"] = results["Q3Seconds"].apply(seconds_to_lap_time)

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

    results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved Quali results to: {OUTPUT_PATH}")
    print(results.to_string(index=False))

pull_quali_results()