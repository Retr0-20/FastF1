from pathlib import Path

import pandas as pd

prediction = pd.read_csv("data/predictions/2026_Monaco_quali_prediction_from_practice.csv")

quali_results = pd.read_csv("data/processed/2026_Monaco_Q_results.csv")

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

comparison = comparison[[
    "Driver",
    "Team",
    "predicted_quali_position",
    "actual_quali_position",
    "position_error",
    "prediction_score",
]]

exact_matches = (comparison["position_error"] == 0).sum()
total_drivers = len(comparison)
comparison = comparison.sort_values("predicted_quali_position")

print("\nPrediction vs Actual Qualifying:")
print(comparison.to_string(index=False))
print(f"\n{exact_matches} out of {total_drivers} predicted CORRECTLY...")
