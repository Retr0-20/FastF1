from pathlib import Path
import fastf1

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

OUTPUT_PATH = Path("data/processed/practice_session_fastest_laps.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

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



# ---------------------------------------------------------------------

def get_fastest_valid_soft_laps(session, useful_columns, limit=20):

    # take session.laps
    # select useful columns
    # copy the data
    if session is None:
         return "Session was empty..."
    
    fp_display = session.laps[useful_columns].copy()
    fp_display = fp_display.dropna(subset=["LapTime"])
    fp_display = fp_display[
         (fp_display["IsAccurate"] == True) &
         (fp_display["Deleted"] == False) &
         (fp_display["Compound"] == "SOFT") &
         (fp_display["TyreLife"] <= 10)
    ]

    # sort before formatting
    fp_display = fp_display.sort_values("LapTime").head(limit)

    # format LapTime
    # format sector times
    # convert TyreLife to whole number
    fp_display["LapTime"] = fp_display["LapTime"].apply(format_lap_time)
    fp_display["Sector1Time"] = fp_display["Sector1Time"].apply(format_sector_time)
    fp_display["Sector2Time"] = fp_display["Sector2Time"].apply(format_sector_time)
    fp_display["Sector3Time"] = fp_display["Sector3Time"].apply(format_sector_time)
    fp_display["TyreLife"] = fp_display["TyreLife"].astype("Int64")

    # return the display table
    fp_display.to_csv(OUTPUT_PATH, index=False)

    print("Saved driver features:")
    print(OUTPUT_PATH)
    return fp_display

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

fp1_display = get_fastest_valid_soft_laps(fp1, useful_columns)
fp2_display = get_fastest_valid_soft_laps(fp2, useful_columns)
fp3_display = get_fastest_valid_soft_laps(fp3, useful_columns)

print("\nFP1 fastest valid soft laps:")
print(fp1_display.to_string(index=False))

print("\nFP2 fastest valid soft laps:")
print(fp2_display.to_string(index=False))

print("\nFP3 fastest valid soft laps:")
print(fp3_display.to_string(index=False))