from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

quali_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "2026_Austria_Q_results.csv")
race_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "2026_Austria_R_results.csv")

comparison = race_results.merge(
    quali_results,
    on=["Driver"],
    how="left"
)

comparison = comparison.rename(columns={
    "Team_x": "Team",
    "Team_y": "ActualTeam",
    "Position_y": "quali_position",
    "Position_x": "race_position"
})

comparison["position_diff"] = (
    comparison["race_position"] - comparison["quali_position"]
).abs()

comparison = comparison[[
    "Driver",
    "Team",
    "race_position",
    "quali_position",
    "position_diff",
]]

# pole_position = comparison['actual_quali_position'] == 1
# exact_matches = (comparison["position_diff"] == 0).sum()
# total_drivers = len(comparison)
# pole_driver = comparison["Driver"][comparison["actual_quali_position"] == 1]
comparison = comparison.sort_values("race_position")

print("\nPrediction vs Actual Qualifying:")
print(comparison.to_string(index=False))
# print(f"\n{exact_matches} out of {total_drivers} predicted CORRECTLY...")
# print(f"\n{comparison.head(3)}")
# print(f"\nThe Driver on Pole is: {pole_driver.iloc[0]}")