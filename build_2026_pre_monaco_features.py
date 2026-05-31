from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/2026_pre_monaco_results.csv")
OUTPUT_PATH = Path("data/processed/2026_pre_monaco_driver_features.csv")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def build_driver_features():
    results = pd.read_csv(INPUT_PATH)

    # Convert numeric columns properly
    numeric_columns = [
        "grid_position",
        "finish_position",
        "points",
        "laps"
    ]

    for column in numeric_columns:
        results[column] = pd.to_numeric(results[column], errors="coerce")

    # Create useful derived columns
    results["positions_gained"] = results["grid_position"] - results["finish_position"]

    results["is_dnf"] = results["status"].str.contains(
        "Retired", case=False, na=False
    )

    results["is_dns"] = results["status"].str.contains(
        "Did not start", case=False, na=False
    )

    results["is_points_finish"] = results["points"] > 0
    results["is_podium"] = results["finish_position"] <= 3

    # Group by driver
    features = results.groupby(["driver_code", "driver_name", "team"]).agg(
        races_entered=("event", "count"),
        points_before_monaco=("points", "sum"),
        average_grid_position=("grid_position", "mean"),
        average_finish_position=("finish_position", "mean"),
        best_finish=("finish_position", "min"),
        worst_finish=("finish_position", "max"),
        average_positions_gained=("positions_gained", "mean"),
        dnf_count=("is_dnf", "sum"),
        dns_count=("is_dns", "sum"),
        points_finishes=("is_points_finish", "sum"),
        podiums=("is_podium", "sum"),
        average_laps_completed=("laps", "mean")
    ).reset_index()

    # Sort strongest-looking drivers first
    features = features.sort_values(
        by=["points_before_monaco", "average_finish_position"],
        ascending=[False, True]
    )

    # Round floats for readability
    features["average_grid_position"] = features["average_grid_position"].round(2)
    features["average_finish_position"] = features["average_finish_position"].round(2)
    features["average_positions_gained"] = features["average_positions_gained"].round(2)
    features["average_laps_completed"] = features["average_laps_completed"].round(2)

    features.to_csv(OUTPUT_PATH, index=False)

    print("Saved driver features:")
    print(OUTPUT_PATH)

    print("\nPreview:")
    print(features.to_string(index=False))


build_driver_features()