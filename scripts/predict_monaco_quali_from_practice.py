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
    except Exception as e:
            print(f"\nFailed to load {year} Monaco Session Results")
    return session

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

fp1_display = fp1.laps[useful_columns].head(20).copy()

fp1_display["LapTime"] = fp1_display["LapTime"].apply(format_lap_time)
fp1_display["Sector1Time"] = fp1_display["Sector1Time"].apply(format_sector_time)
fp1_display["Sector2Time"] = fp1_display["Sector2Time"].apply(format_sector_time)
fp1_display["Sector3Time"] = fp1_display["Sector3Time"].apply(format_sector_time)
fp1_display["TyreLife"] = fp1_display["TyreLife"].astype("Int64")

print("\nFP1 preview:")
print(fp1_display.to_string(index=False))
