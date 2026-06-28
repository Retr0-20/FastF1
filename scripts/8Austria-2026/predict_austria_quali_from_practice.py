from pathlib import Path

import fastf1
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "fastf1_cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PRACTICE_SESSIONS = ["FP1", "FP2", "FP3"]
YEAR = 2026
EVENT = "Austria"
MAX_TYRE_LIFE = 15  # Max tyre life for qualifying-style laps


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
    return PROJECT_ROOT / "data" / "processed" / \
        f"{year}_{event}_{session_type}_fastest_soft_laps.csv"


def practice_driver_features_path(year, event):
    return PROJECT_ROOT / "data" / "processed" / \
        f"{year}_{event}_practice_driver_features.csv"


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

def extract_practice_laps(session, session_type, useful_columns):
    if session is None:
        return None

    fp_laps = session.laps[useful_columns].copy()

    # Filter to useful qualifying-style laps
    fp_laps = fp_laps.dropna(subset=["LapTime"])
    fp_laps = fp_laps[
        (fp_laps["IsAccurate"] == True) &
        (fp_laps["Deleted"] == False) &
        # (fp_laps["Compound"] == "SOFT") &
        (fp_laps["TyreLife"] <= MAX_TYRE_LIFE)
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
    prediction = practice_features.copy(deep=True)

    prediction["prediction_score"] = 0.0
    prediction["weight_total"] = 0.0

    def safe_weight(col, weight):
        if col in prediction.columns:
            valid = prediction[col].notna()
            prediction["prediction_score"] += prediction[col].fillna(0) * weight
            prediction["weight_total"] += valid.astype(int) * weight

    safe_weight("best_FP1_lap_seconds", 0.15)
    safe_weight("best_FP2_lap_seconds", 0.25)
    safe_weight("best_FP3_lap_seconds", 0.60)

    prediction["prediction_score"] = (
        prediction["prediction_score"] /
        prediction["weight_total"].replace(0, pd.NA)
    )

    prediction = prediction.dropna(subset=["prediction_score"])
    prediction = prediction.sort_values("prediction_score").reset_index(drop=True)
    prediction["predicted_quali_position"] = range(1, len(prediction) + 1)

    return prediction

# ---------------------------------------------------------------------
# Driver feature extraction
# ---------------------------------------------------------------------

def get_best_lap_per_driver(csv_path, session_type):
    laps = pd.read_csv(csv_path)

    laps = laps.sort_values("LapTimeSeconds")

    # Best complete lap per driver
    best_laps = laps.groupby(["Driver"]).first().reset_index()

    # Best individual sectors per driver
    best_sectors = (
        laps.groupby(["Driver"])
        .agg(
                best_sector1_seconds=("Sector1Seconds", "min"),
                best_sector2_seconds=("Sector2Seconds", "min"),
                best_sector3_seconds=("Sector3Seconds", "min")
        ).reset_index()
    )
    
    # Merge best complete lap with best individual sectors
    best_laps = best_laps.merge(
        best_sectors,
        on=["Driver"],
        how="left"
    )

    # Rename actual best lap column
    best_laps = best_laps.rename(columns={
        "LapTimeSeconds": f"best_{session_type}_lap_seconds"
    })

    # Create readable actual best lap
    best_laps[f"best_{session_type}_lap"] = best_laps[
        f"best_{session_type}_lap_seconds"
    ].apply(seconds_to_lap_time)

    # Calculate theoretical best lap
    best_laps[f"best_{session_type}_theoretical_seconds"] = (
        best_laps["best_sector1_seconds"]
        + best_laps["best_sector2_seconds"]
        + best_laps["best_sector3_seconds"]
    )

    # Create readable theoretical best lap
    best_laps[f"best_{session_type}_theoretical_lap"] = best_laps[
        f"best_{session_type}_theoretical_seconds"
    ].apply(seconds_to_lap_time)

    # Keep useful driver-level features
    best_laps = best_laps[[
        "Driver",
        "Team",
        f"best_{session_type}_lap",
        f"best_{session_type}_lap_seconds",
        f"best_{session_type}_theoretical_lap",
        f"best_{session_type}_theoretical_seconds"
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

# For loop for each practice session to load, extract, and save the fastest laps and driver features
session_displays = {}
best_laps_by_session = {}

for session_name in PRACTICE_SESSIONS:
    session = load_practice_session(YEAR, EVENT, session_name)

    session_displays[session_name] = extract_practice_laps(
        session,
        session_name,
        useful_columns
    )

    best_laps_by_session[session_name] = get_best_lap_per_driver(
        practice_laps_path(YEAR, EVENT, session_name),
        session_name
    )

# Dictionary of session displays for terminal output
fp1_display = session_displays["FP1"]
fp2_display = session_displays["FP2"]
fp3_display = session_displays["FP3"]

# Dictionary of best laps per session
fp1_best = best_laps_by_session["FP1"]
fp2_best = best_laps_by_session["FP2"]
fp3_best = best_laps_by_session["FP3"]

# Filter to drivers who participated in at least one of FP2 or FP3 as well as FP1
valid_drivers = set(fp2_best["Driver"]) | set(fp3_best["Driver"])
fp1_best = fp1_best[fp1_best["Driver"].isin(valid_drivers)]

# Removes the Team column from FP1 and FP2 to avoid duplicate columns when merging
fp1_best = fp1_best.drop(columns=["Team"])
fp2_best = fp2_best.drop(columns=["Team"])

practice_features = fp1_best.merge(
    fp2_best,
    on=["Driver"],
    how="outer"
)

practice_features = practice_features.merge(
    fp3_best,
    on=["Driver"],
    how="outer"
)

# Move Team right after Driver
cols = practice_features.columns.tolist()
cols.remove("Team")
cols.insert(1, "Team")
practice_features = practice_features[cols]

output_path = practice_driver_features_path(YEAR, EVENT)
practice_features.to_csv(output_path, index=False)

print("\nSaved practice driver features:")
print(output_path)

quali_prediction = predict_quali_from_practice(practice_features)
# Move Team right after Driver in the prediction too
cols = quali_prediction.columns.tolist()
cols.remove("Team")
cols.insert(1, "Team")
quali_prediction = quali_prediction[cols]

prediction_path = (
    PROJECT_ROOT
    / "data"
    / "predictions"
    / f"{YEAR}_{EVENT}_quali_prediction_from_practice.csv"
)
prediction_path.parent.mkdir(parents=True, exist_ok=True)

# After predict_quali_from_practice(), save prediction first
quali_prediction.to_csv(prediction_path, index=False)

# Create CLEAN display version (ONLY seconds, human-readable preview)
display_output = quali_prediction[['predicted_quali_position', 'Driver', 'Team', 'best_FP1_lap', 'best_FP1_theoretical_lap',
                                   'best_FP2_lap', 'best_FP2_theoretical_lap', 'best_FP3_lap', 'best_FP3_theoretical_lap',
                                   'prediction_score']]

print("\nPredicted Qualifying Order (Clean Format):")
print(display_output.to_string(index=False))

print("\nSaved qualifying prediction:")
print(prediction_path)