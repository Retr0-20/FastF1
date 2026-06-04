from pathlib import Path

import fastf1
import pandas as pd

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PRACTICE_SESSIONS = ["FP1", "FP2", "FP3"]
YEAR = 2025
EVENT = "Monaco"


# ---------------------------------------------------------------------
# Session loading
# ---------------------------------------------------------------------

def load_practice_session(year, event, session_type):
    try:
        session = fastf1.get_session(year, event, session_type)
        session.load()
        return session
    except Exception as e:
        print(f"\nFailed to load {year} {event} {session_type}")
        print(f"Reason: {e}")
        return None


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

def practice_laps_path(year, event, session_type):
    return Path(f"data/processed/{year}_{event}_{session_type}_fastest_soft_laps.csv")


def practice_driver_features_path(year, event):
    return Path(f"data/processed/{year}_{event}_practice_driver_features.csv")


# ---------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------

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
# Practice lap extraction
# ---------------------------------------------------------------------

def build_fastest_valid_soft_laps(session, session_type, useful_columns):
    if session is None:
        return None

    fp_laps = session.laps[useful_columns].copy()

    # Filter to useful qualifying-style laps
    fp_laps = fp_laps.dropna(subset=["LapTime"])
    fp_laps = fp_laps[
        (fp_laps["IsAccurate"] == True) &
        (fp_laps["Deleted"] == False) &
        (fp_laps["Compound"] == "SOFT") &
        (fp_laps["TyreLife"] <= 10)
    ]

    # Sort before formatting/converting
    fp_laps = fp_laps.sort_values("LapTime")

    # Numeric columns for modelling
    fp_laps["LapTimeSeconds"] = fp_laps["LapTime"].apply(time_to_seconds)
    fp_laps["Sector1Seconds"] = fp_laps["Sector1Time"].apply(time_to_seconds)
    fp_laps["Sector2Seconds"] = fp_laps["Sector2Time"].apply(time_to_seconds)
    fp_laps["Sector3Seconds"] = fp_laps["Sector3Time"].apply(time_to_seconds)

    # Readable columns for display
    fp_laps["LapTimeFormatted"] = fp_laps["LapTimeSeconds"].apply(seconds_to_lap_time)
    fp_laps["Sector1Formatted"] = fp_laps["Sector1Seconds"].apply(seconds_to_sector_time)
    fp_laps["Sector2Formatted"] = fp_laps["Sector2Seconds"].apply(seconds_to_sector_time)
    fp_laps["Sector3Formatted"] = fp_laps["Sector3Seconds"].apply(seconds_to_sector_time)

    # Save model-ready CSV
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

    output_path = practice_laps_path(YEAR, EVENT, session_type)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    csv_output.to_csv(output_path, index=False)

    print("Saved fastest soft laps:")
    print(output_path)

    # Return readable terminal version
    display_output = fp_laps[[
        "Driver",
        "Team",
        "LapTimeFormatted",
        "Sector1Formatted",
        "Sector2Formatted",
        "Sector3Formatted",
        "Compound",
        "TyreLife",
        "IsAccurate",
        "Deleted",
        "TrackStatus"
    ]].copy()

    display_output = display_output.rename(columns={
        "LapTimeFormatted": "LapTime",
        "Sector1Formatted": "Sector1Time",
        "Sector2Formatted": "Sector2Time",
        "Sector3Formatted": "Sector3Time"
    })

    display_output["TyreLife"] = display_output["TyreLife"].astype("Int64")

    return display_output

# ---------------------------------------------------------------------
# Driver feature extraction
# ---------------------------------------------------------------------

def predict_quali_from_practice(practice_features):
    copy practice_features

    calculate prediction_score using:
        15% FP1
        25% FP2
        60% FP3

    sort by prediction_score

    add predicted_quali_position

    save to CSV

    return prediction table

# ---------------------------------------------------------------------
# Driver feature extraction
# ---------------------------------------------------------------------

def get_best_lap_per_driver(csv_path, session_type):
    laps = pd.read_csv(csv_path)

    laps = laps.sort_values("LapTimeSeconds")
    best_laps = laps.groupby(["Driver", "Team"]).first().reset_index()

    best_laps = best_laps[[
        "Driver",
        "Team",
        "LapTimeSeconds"
    ]]

    best_laps = best_laps.rename(columns={
        "LapTimeSeconds": f"best_{session_type}_lap_seconds"
    })

    best_laps[f"best_{session_type}_lap"] = best_laps[
        f"best_{session_type}_lap_seconds"
    ].apply(seconds_to_lap_time)

    best_laps = best_laps[[
        "Driver",
        "Team",
        f"best_{session_type}_lap",
        f"best_{session_type}_lap_seconds"
    ]]

    return best_laps


# ---------------------------------------------------------------------
# Run pipeline
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

fp1 = load_practice_session(YEAR, EVENT, "FP1")
fp2 = load_practice_session(YEAR, EVENT, "FP2")
fp3 = load_practice_session(YEAR, EVENT, "FP3")

fp1_display = build_fastest_valid_soft_laps(fp1, "FP1", useful_columns)
fp2_display = build_fastest_valid_soft_laps(fp2, "FP2", useful_columns)
fp3_display = build_fastest_valid_soft_laps(fp3, "FP3", useful_columns)

if fp1_display is not None:
    print("\nFP1 fastest valid soft laps:")
    print(fp1_display.to_string(index=False))

if fp2_display is not None:
    print("\nFP2 fastest valid soft laps:")
    print(fp2_display.to_string(index=False))

if fp3_display is not None:
    print("\nFP3 fastest valid soft laps:")
    print(fp3_display.to_string(index=False))

fp1_best = get_best_lap_per_driver(
    practice_laps_path(YEAR, EVENT, "FP1"),
    "FP1"
)

fp2_best = get_best_lap_per_driver(
    practice_laps_path(YEAR, EVENT, "FP2"),
    "FP2"
)

fp3_best = get_best_lap_per_driver(
    practice_laps_path(YEAR, EVENT, "FP3"),
    "FP3"
)

practice_features = fp1_best.merge(
    fp2_best,
    on=["Driver", "Team"],
    how="outer"
)

practice_features = practice_features.merge(
    fp3_best,
    on=["Driver", "Team"],
    how="outer"
)

print("\nBest practice laps per driver:")
print(practice_features.to_string(index=False))

output_path = practice_driver_features_path(YEAR, EVENT)
practice_features.to_csv(output_path, index=False)

print("\nSaved practice driver features:")
print(output_path)