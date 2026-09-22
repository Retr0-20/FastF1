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
# Utility function for printing a weather summary for the specified year, event, and session type
def get_weather_data():
    session = fastf1.get_session(config.YEAR, config.EVENT, config.SESSION_TYPE)
    session.load()
    return session.weather_data


# ----------------------------------------------
# Utility function for printing a weather summary for the specified year, event, and session type
def get_weather_summary(weather):
    first = weather.iloc[0]
    last = weather.iloc[-1]

    return {
        "Starting Air Temp": first['AirTemp'],
        "Ending Air Temp": last['AirTemp'],
        "Starting Track Temp": first['TrackTemp'],
        "Ending Track Temp": last['TrackTemp'],
        "Starting Humidity": first['Humidity'],
        "Ending Humidity": last['Humidity'],
        "Rainfall Recorded": weather['Rainfall'].any()
    }


# ----------------------------------------------
# Utility function for getting the session times for the specified year, event, and session type
# f1_utils.py — replace get_time_of_day_summary():
def get_time_of_day_summary(weather):
    if weather is None or weather.empty:
        return None

    # Time column is Timedelta from session start, not absolute datetime
    start_td = weather["Time"].iloc[0]      # Timedelta
    end_td = weather["Time"].iloc[-1]       # Timedelta

    # Extract hours/minutes from Timedelta
    start_seconds = int(start_td.total_seconds())
    end_seconds = int(end_td.total_seconds())

    # Convert to HH:MM
    start_hour = start_seconds // 3600
    start_minute = (start_seconds % 3600) // 60
    end_hour = end_seconds // 3600
    end_minute = (end_seconds % 3600) // 60

    return {
        "Starting Hour": f"{start_hour:02d}:{start_minute:02d}",
        "Ending Hour": f"{end_hour:02d}:{end_minute:02d}"
    }


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