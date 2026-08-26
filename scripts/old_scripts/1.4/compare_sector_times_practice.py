from pathlib import Path

import pandas as pd

fp1 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Belgium_FP1_fastest_laps_by_driver.csv")

fp2 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Belgium_FP2_fastest_laps_by_driver.csv")

fp3 = pd.read_csv("/Users/dylancourt/Coding/FastF1/data/processed/2026_Belgium_FP3_fastest_laps_by_driver.csv")

comparison = fp3.merge(fp1.merge(
    fp2,
    on=["Driver", "Team"],
    how="right"
), on=["Driver", "Team"], how="right")

comparison["S1Time_FP1"] = (
    comparison["Sector1Time_x"]
).abs()

comparison["S1Time_FP2"] = (
    comparison["Sector1Time_y"]
).abs()

comparison["S1Time_FP3"] = (
    comparison["Sector1Time"]
).abs()

comparison["S2Time_FP1"] = (
    comparison["Sector2Time_x"]
).abs()

comparison["S2Time_FP2"] = (
    comparison["Sector2Time_y"]
).abs()

comparison["S2Time_FP3"] = (
    comparison["Sector2Time"]
).abs()

comparison["S3Time_FP1"] = (
    comparison["Sector3Time_x"]
).abs()

comparison["S3Time_FP2"] = (
    comparison["Sector3Time_y"]
).abs()

comparison["S3Time_FP3"] = (
    comparison["Sector3Time"]
).abs()

comparison = comparison[[
    "Driver",
    "Team",
    "S1Time_FP1",
    "S1Time_FP2",
    "S1Time_FP3",
    "S2Time_FP1",
    "S2Time_FP2",
    "S2Time_FP3",
    "S3Time_FP1",
    "S3Time_FP2",
    "S3Time_FP3"
]]

comparison = comparison.rename(columns={
    "S1Time_FP1": "S1Time_FP1",
    "S1Time_FP2": "S1Time_FP2",
    "S1Time_FP3": "S1Time_FP3",
    "S2Time_FP1": "S2Time_FP1",
    "S2Time_FP2": "S2Time_FP2",
    "S2Time_FP3": "S2Time_FP3",
    "S3Time_FP1": "S3Time_FP1",
    "S3Time_FP2": "S3Time_FP2",
    "S3Time_FP3": "S3Time_FP3"
})

# comparison = comparison.sort_values("S3Time_FP3", ascending=True)

print("\nFP1 vs FP2 vs FP3 Sector Times:")
print(comparison.to_string(index=False))
