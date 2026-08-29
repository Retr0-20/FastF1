from pathlib import Path
import config
import pandas as pd

YEAR = config.YEAR
EVENT = config.EVENT
EVENT_FOLDER = config.get_event_folder()

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", "{:.0f}".format)

PROJECT_ROOT = config.PROJECT_ROOT

prediction = pd.read_csv(PROJECT_ROOT / "data" / "predictions" / EVENT_FOLDER / f"quali_prediction_from_practice.csv")
quali_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"Q_results.csv")

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

comparison = comparison[[
    "Driver",
    "Team",
    "predicted_quali_position",
    "actual_quali_position",
    "position_error",
    "prediction_outcome"
]]

pole_position = comparison['actual_quali_position'] == 1
exact_matches = (comparison["position_error"] == 0).sum()
total_drivers = len(comparison)
pole_driver = comparison["Driver"][comparison["actual_quali_position"] == 1]
comparison = comparison.sort_values("actual_quali_position")

print("\nPrediction vs Actual Qualifying:")
print(comparison.to_string(index=False))
print(f"\n{exact_matches} out of {total_drivers} predicted CORRECTLY...")
print(f"\nThe Driver on Pole is: {pole_driver.iloc[0]}\n")