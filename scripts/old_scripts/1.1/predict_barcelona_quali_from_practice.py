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
EVENT = "Barcelona"


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

def build_fastest_valid_soft_laps(session, session_type, useful_columns):
    if session is None:
        return None

    fp_laps = session.laps[useful_columns].copy()

    # Filter to useful qualifying-style laps
    fp_laps = fp_laps.dropna(subset=["LapTime"])
    fp_laps = fp_laps[
        (fp_laps["IsAccurate"] == True) &
        (fp_laps["Deleted"] == False) &
        # (fp_laps["Compound"] == "SOFT") &
        (fp_laps["TyreLife"] <= 15)
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

    prediction["prediction_score"] = 0
    prediction["weight_total"] = 0

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

fp1 = load_practice_session(YEAR, EVENT, "FP1")
fp2 = load_practice_session(YEAR, EVENT, "FP2")
fp3 = load_practice_session(YEAR, EVENT, "FP3")

fp1_display = build_fastest_valid_soft_laps(fp1, "FP1", useful_columns)
fp2_display = build_fastest_valid_soft_laps(fp2, "FP2", useful_columns)
fp3_display = build_fastest_valid_soft_laps(fp3, "FP3", useful_columns)

# if fp1_display is not None:
#     print("\nFP1 fastest valid soft laps:")
#     print(fp1_display.to_string(index=False))

# if fp2_display is not None:
#     print("\nFP2 fastest valid soft laps:")
#     print(fp2_display.to_string(index=False))

# if fp3_display is not None:
#     print("\nFP3 fastest valid soft laps:")
#     print(fp3_display.to_string(index=False))

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

fp1_best = fp1_best[fp1_best["Driver"].isin(fp2_best["Driver"])]

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

# print("\nBest practice laps per driver:")
# print(practice_features.to_string(index=False))

output_path = practice_driver_features_path(YEAR, EVENT)
practice_features.to_csv(output_path, index=False)

print("\nSaved practice driver features:")
print(output_path)


quali_prediction = predict_quali_from_practice(practice_features)

print("\nPredicted Qualifying Order from Practice Sessions:")
print(quali_prediction.to_string(index=False))

prediction_path = (
    PROJECT_ROOT
    / "data"
    / "predictions"
    / f"{YEAR}_{EVENT}_quali_prediction_from_practice.csv"
)
prediction_path.parent.mkdir(parents=True, exist_ok=True)

quali_prediction.to_csv(prediction_path, index=False)

print("\nSaved qualifying prediction:")
print(prediction_path)

# print(practice_features.head())
# print(practice_features.columns.tolist())