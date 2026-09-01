import pandas as pd
import fastf1
import f1_utils
import config

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