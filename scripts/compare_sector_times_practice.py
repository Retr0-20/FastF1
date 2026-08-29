from pathlib import Path
import config
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
YEAR = config.YEAR
EVENT = config.EVENT

fp1 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / f"{config.YEAR}_{config.EVENT}_FP1_fastest_laps_by_driver.csv")
fp2 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / f"{config.YEAR}_{config.EVENT}_FP2_fastest_laps_by_driver.csv")
fp3 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / f"{config.YEAR}_{config.EVENT}_FP3_fastest_laps_by_driver.csv")

comparison = fp3.merge(fp1.merge(
    fp2,
    on=["Driver", "Team"],
    how="right"
), on=["Driver", "Team"], how="right")

comparison["S1Time_FP1"] = comparison["Sector1Time_x"]

comparison["S1Time_FP2"] = comparison["Sector1Time_y"]

comparison["S1Time_FP3"] = comparison["Sector1Time"]

comparison["S2Time_FP1"] = comparison["Sector2Time_x"]

comparison["S2Time_FP2"] = comparison["Sector2Time_y"]

comparison["S2Time_FP3"] = comparison["Sector2Time"]

comparison["S3Time_FP1"] = comparison["Sector3Time_x"]

comparison["S3Time_FP2"] = comparison["Sector3Time_y"]

comparison["S3Time_FP3"] = comparison["Sector3Time"]

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

print("\nFP1 vs FP2 vs FP3 Sector Times:")
print(comparison.to_string(index=False))
