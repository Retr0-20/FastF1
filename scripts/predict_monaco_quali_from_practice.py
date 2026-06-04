from pathlib import Path
import fastf1

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------

YEAR = 2025
EVENT = "Monaco"

def load_practice_session(year, event, session_type):
    try:
        session = fastf1.get_session(year, event, session_type)
        session.load()
        return session
    except Exception as e:
            print(f"\nFailed to load {year} {event} {session_type}")
            print(f"Reason: {e}")
    return None

fp1 = load_practice_session(YEAR, EVENT, "FP1")
fp2 = load_practice_session(YEAR, EVENT, "FP2")
fp3 = load_practice_session(YEAR, EVENT, "FP3")

print("FP1 Loaded...")
print("FP2 Loaded...")
print("FP3 Loaded...")

# ---------------------------------------------------------------------

def format_lap_time(value):
    if str(value) == "NaT":
        return "N/A"

    total_seconds = value.total_seconds()

    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    return f"{minutes}:{seconds:06.3f}"

def format_sector_time(value):
    if str(value) == "NaT":
        return "N/A"

    return f"{value.total_seconds():.3f}"


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


def seconds_to_sector_time(seconds):
    if seconds is None:
        return "N/A"

    return f"{seconds:.3f}"


# ---------------------------------------------------------------------

def get_fastest_valid_soft_laps(session, session_type, useful_columns, limit=20):

    # take session.laps
    # select useful columns
    # copy the data
    if session is None:
         return None
    
    fp_laps = session.laps[useful_columns].copy()

    # filter
    fp_laps = fp_laps.dropna(subset=["LapTime"])
    fp_laps = fp_laps[
         (fp_laps["IsAccurate"] == True) &
         (fp_laps["Deleted"] == False) &
         (fp_laps["Compound"] == "SOFT") &
         (fp_laps["TyreLife"] <= 10)
    ]

    # sort before formatting
    fp_laps = fp_laps.sort_values("LapTime").head(limit)

    # create numeric seconds columns first
    fp_laps["LapTimeSeconds"] = fp_laps["LapTime"].apply(time_to_seconds)
    fp_laps["Sector1Seconds"] = fp_laps["Sector1Time"].apply(time_to_seconds)
    fp_laps["Sector2Seconds"] = fp_laps["Sector2Time"].apply(time_to_seconds)
    fp_laps["Sector3Seconds"] = fp_laps["Sector3Time"].apply(time_to_seconds)

    # then create readable formatted columns
    fp_laps["LapTimeFormatted"] = fp_laps["LapTimeSeconds"].apply(seconds_to_lap_time)
    fp_laps["Sector1Formatted"] = fp_laps["Sector1Seconds"].apply(seconds_to_sector_time)
    fp_laps["Sector2Formatted"] = fp_laps["Sector2Seconds"].apply(seconds_to_sector_time)
    fp_laps["Sector3Formatted"] = fp_laps["Sector3Seconds"].apply(seconds_to_sector_time)

    # save numeric CSV
    csv_output = fp_laps[[
        "Driver",
        "Team",
        "LapTimeSeconds",
        "Sector1Seconds",
        "Sector2Seconds",
        "Sector3Seconds",
        "Compound",
        "TyreLife",
        "IsAccurate",
        "Deleted",
        "TrackStatus"
    ]].copy()
    
    csv_output["TyreLife"] = csv_output["TyreLife"].astype("Int64")

    # return the display table
    output_path = Path(f"data/processed/{YEAR}_{EVENT}_{session_type}_fastest_soft_laps.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    csv_output.to_csv(output_path, index=False)

    print("Saved fastest soft laps:")
    print(output_path)


    # create readable version for terminal only
    display_output = fp_laps[[
        "Driver",
        "Team",
        "LapTime",
        "Sector1Time",
        "Sector2Time",
        "Sector3Time",
        "Compound",
        "TyreLife",
        "IsAccurate",
        "Deleted",
        "TrackStatus"
    ]].copy()

    display_output["LapTime"] = display_output["LapTime"].apply(format_lap_time)
    display_output["Sector1Time"] = display_output["Sector1Time"].apply(format_sector_time)
    display_output["Sector2Time"] = display_output["Sector2Time"].apply(format_sector_time)
    display_output["Sector3Time"] = display_output["Sector3Time"].apply(format_sector_time)
    display_output["TyreLife"] = display_output["TyreLife"].astype("Int64")

    return display_output

# ---------------------------------------------------------------------

useful_columns = [
     "Driver",
     "Team",
     "LapTime",
     "Sector1Time",
     "Sector2Time",
     "Sector3Time",
     "Compound",
     "TyreLife",
     "IsAccurate",
     "Deleted",
     "TrackStatus"
]

# ---------------------------------------------------------------------

fp1_display = get_fastest_valid_soft_laps(fp1, "FP1", useful_columns)
fp2_display = get_fastest_valid_soft_laps(fp2, "FP2", useful_columns)
fp3_display = get_fastest_valid_soft_laps(fp3, "FP3", useful_columns)

    
if fp1_display is not None:
    print("\nFP1 fastest valid soft laps:")
    print(fp1_display.to_string(index=False))

if fp2_display is not None:
    print("\nFP2 fastest valid soft laps:")
    print(fp2_display.to_string(index=False))

if fp3_display is not None:
    print("\nFP3 fastest valid soft laps:")
    print(fp3_display.to_string(index=False))