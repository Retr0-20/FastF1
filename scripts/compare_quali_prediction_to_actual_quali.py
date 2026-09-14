from pathlib import Path
import config
import f1_utils
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", "{:.0f}".format)

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs - config.py
# ---------------------------------------------------------------------
YEAR = config.YEAR
EVENT = config.EVENT
EVENT_FOLDER = f1_utils.get_event_folder()
PROJECT_ROOT = config.PROJECT_ROOT

# Pull and read the predicted qualifying positions and actual qualifying results CSVs
prediction = pd.read_csv(PROJECT_ROOT / "data" / "predictions" / EVENT_FOLDER / f"quali_prediction_from_practice.csv")
quali_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"Q_results.csv")

# Merge the prediction DataFrame with the actual qualifying results DataFrame on the "Driver" column
comparison = prediction.merge(
    quali_results,
    on=["Driver"],
    how="left"
)

comparison = comparison.rename(columns={
    "Team_x": "Team",
    "Team_y": "ActualTeam",
    "Position": "actual_quali_position"
})

# After merge/rename, before astype(int):
missing = comparison[comparison["actual_quali_position"].isna()]
if len(missing) > 0:
    print("Drivers with no qualifying result (excluded from comparison):")
    print(missing["Driver"].tolist())
    comparison = comparison.dropna(subset=["actual_quali_position"])

# Add a new column to calculate the absolute difference between predicted and actual qualifying positions
comparison["position_error"] = (
    comparison["predicted_quali_position"] - comparison["actual_quali_position"]
).abs()

comparison["predicted_quali_position"] = comparison["predicted_quali_position"].astype(int)
comparison["actual_quali_position"] = comparison["actual_quali_position"].astype(int)
comparison["position_error"] = comparison["position_error"].astype(int)

# Add a new column to indicate whether the predicted position is higher, lower, or the same as the actual position
comparison["prediction_outcome"] = comparison.apply(
    lambda row: "Spot On" if row['position_error'] == 0
    else ("Overestimated" if row['predicted_quali_position'] < row['actual_quali_position']
    else "Underestimated"),
    axis=1
)

# Create a new column to indicate whether the predicted position is higher, lower, or the same as the actual position
comparison["change_arrow"] = comparison.apply(
    lambda row: f"↑{row['position_error']}" if row['predicted_quali_position'] 
        > row['actual_quali_position'] 
    else f"↓{row['position_error']}" if row['position_error'] > 0
    else f"→",
    axis=1
)

# Add the new column
comparison = comparison.rename(columns={
    "Driver": "Driver",
    "Team": "Team",
    "predicted_quali_position": "Predicted Position",
    "actual_quali_position": "Actual Position",
    "change_arrow": "Change Arrow",
    "prediction_outcome": "Prediction Outcome"
})

# Add the new column
comparison = comparison[[
    "Driver",
    "Team",
    "Predicted Position",
    "Actual Position",
    "Change Arrow",
    "Prediction Outcome"
]]

# Pole position is the driver with actual_quali_position == 1
pole_position = comparison['Actual Position'] == 1
# Exact matches are those where predicted position equals actual position
exact_matches = (comparison["Prediction Outcome"] == "Spot On").sum()
total_drivers = len(comparison)
# Pole driver is the driver with actual_quali_position == 1 but also derives their name
pole_driver = comparison["Driver"][comparison["Actual Position"] == 1]
comparison = comparison.sort_values("Actual Position")

# Print the comparison DataFrame to the console for debugging
print("\nPrediction vs Actual Qualifying:")
print(comparison.to_string(index=False))
print(f"\n{exact_matches} out of {total_drivers} predicted CORRECTLY...")
print(f"\nThe Driver on Pole is: {pole_driver.iloc[0]}\n")