from pathlib import Path

import pandas as pd

prediction = pd.read_csv("data/predictions/2026_Austria_quali_prediction_from_practice.csv")

quali_results = pd.read_csv("data/processed/2026_Austria_Q_results.csv")

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

comparison = comparison.sort_values("predicted_quali_position")

print("\nPrediction vs Actual Qualifying:")
print(comparison.to_string(index=False))
