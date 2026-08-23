from pathlib import Path
import config
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", "{:.0f}".format)

PROJECT_ROOT = config.PROJECT_ROOT

quali_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "2026_Netherlands_Q_results.csv")
race_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "2026_Netherlands_R_results.csv")

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

comparison["change_arrow"] = comparison.apply(
    lambda row: f"↑{row['position_diff']}" if row['quali_position'] 
        > row['race_position'] 
    else f"↓{row['position_diff']}" if row['position_diff'] > 0
    else f"→",
    axis=1
)

comparison = comparison[[
    "Driver",
    "Team",
    "race_position",
    "quali_position",
    "position_diff",
    "change_arrow"
]]

comparison["race_position"] = comparison["race_position"].astype(int)
comparison["quali_position"] = comparison["quali_position"].astype(int)
comparison["position_diff"] = comparison["position_diff"].astype(int)

exact_matches = (comparison["position_diff"] == 0).sum()
winning_driver = comparison["Driver"][comparison["race_position"] == 1]
comparison = comparison.sort_values("race_position")

print("\nQualifying vs Race:")
print(comparison.to_string(index=False))
print(f"\nThe Winning Driver is: {winning_driver.iloc[0]}")
print(f"\nDrivers who held position: {exact_matches}\n")