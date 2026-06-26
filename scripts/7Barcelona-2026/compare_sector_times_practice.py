from pathlib import Path

import pandas as pd

fp1 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Barcelona_FP1_fastest_laps_by_driver.csv")

fp2 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Barcelona_FP2_fastest_laps_by_driver.csv")

fp3 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Barcelona_FP3_fastest_laps_by_driver.csv")

comparison = fp2.merge(
    fp1,
    on=["Driver", "Team"],
    how="left"
)

comparison = fp3.merge(
    fp2,
    on=["Driver", "Team"],
    how="left"
)

comparison["time_difference_Sector1"] = (
    comparison["Sector1Time_y"] - comparison["Sector1Time_x"]
).abs()

comparison["time_difference_Sector2"] = (
    comparison["Sector2Time_y"] - comparison["Sector2Time_x"]
).abs()

comparison["time_difference_Sector3"] = (
    comparison["Sector3Time_y"] - comparison["Sector3Time_x"]
).abs()

comparison["time_difference_overall"] = (
    comparison["Sector3Time_y"] - comparison["Sector3Time_x"]
).abs()

comparison = comparison[[
    "Driver",
    "Team",
    "Sector1Time_x",
    "Sector2Time_x",
    "Sector3Time_x",
    "Sector1Time_y",
    "Sector2Time_y",
    "Sector3Time_y",
    "time_difference_Sector1",
    "time_difference_Sector2",
    "time_difference_Sector3",
    "time_difference_overall"
]]

comparison = comparison.rename(columns={
    "Sector1Time_x": "Sector1TimeFP2",
    "Sector2Time_x": "Sector2TimeFP2",
    "Sector3Time_x": "Sector3TimeFP2",
    "Sector1Time_y": "Sector1TimeFP1",
    "Sector2Time_y": "Sector2TimeFP1",
    "Sector3Time_y": "Sector3TimeFP1",
    "time_difference_Sector1": "Sector1Time_Difference",
    "time_difference_Sector2": "Sector2Time_Difference",
    "time_difference_Sector3": "Sector3Time_Difference"
})

comparison = comparison.sort_values("time_difference_overall", ascending=False)

print("\nFP1 vs FP2 Sector Times:")
print(comparison.to_string(index=False))
