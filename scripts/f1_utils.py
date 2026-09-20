import pandas as pd
import fastf1
import f1_utils
import config

# ----------------------------------------------
# Utility function for getting the lap data (laps, results, etc.) for the specified year, event, and session type
# Used for practice sessions (FP1, FP2, FP3) and qualifying sessions (Q, SQ)

def get_laps_data():
    session = fastf1.get_session(config.YEAR, config.EVENT, config.SESSION_TYPE)
    session.load()

    laps = session.laps.copy()

    # If laps are empty, print a message and return
    if laps.empty:
        print(f"\nNo laps found for {config.YEAR} {config.EVENT} {config.SESSION_TYPE}.\n")
        return

    return laps

# ----------------------------------------------
# Utility function for getting the session results for the specified year, event, and session type
# Used for qualifying sessions (Q, SQ) and race sessions (R, S)

def get_session_data():
    session = fastf1.get_session(config.YEAR, config.EVENT, config.SESSION_TYPE)
    session.load()

    results = session.results.copy()

    # If results are empty, print a message and return
    if results.empty:
        print(f"\nNo results found for {config.YEAR} {config.EVENT} {config.SESSION_TYPE}.\n")
        return

    return results

# ----------------------------------------------
# Utility function for getting the folder name for the event and year

def get_event_folder():
    return f"{config.YEAR}_{config.EVENT.lower()}"

# ----------------------------------------------
# Utility functions for time conversions

def time_to_seconds(value):
    if value is None or pd.isna(value):
        return None

    # Convert a timedelta to seconds with millisecond precision 3rd decimal place
    return round(value.total_seconds(), 3)


def seconds_to_lap_time(seconds):
    if seconds is None or pd.isna(seconds):
        return "N/A"

    # extract minutes through floor division and seconds through modulo - returning remaining seconds
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    # '0' - pad with leading zeroes, '6' - total width of 6 characters, '.3f' - 3 decimal places
    return f"{minutes}:{remaining_seconds:06.3f}"


def seconds_to_sector_time(seconds):
    if seconds is None or pd.isna(seconds):
        return "N/A"
    # '0' - pad with leading zeroes, '.3f' - 3 decimal places
    return f"{seconds:.3f}"


# ----------------------------------------------
# Utility function for getting the points

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