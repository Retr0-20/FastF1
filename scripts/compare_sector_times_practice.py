from pathlib import Path
import config
import pandas as pd

PROJECT_ROOT = config.PROJECT_ROOT
YEAR = config.YEAR
EVENT = config.EVENT

fp1 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / config.get_event_folder() / f"FP1_fastest_laps_by_driver.csv")
fp2 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / config.get_event_folder() / f"FP2_fastest_laps_by_driver.csv")
fp3 = pd.read_csv(config.PROJECT_ROOT / "data" / "processed" / config.get_event_folder() / f"FP3_fastest_laps_by_driver.csv")

# After reading CSVs, before merge
fp1["Team"] = fp1["Team"].fillna("")
fp2["Team"] = fp2["Team"].fillna("")
fp3["Team"] = fp3["Team"].fillna("")

# Now merge on Driver only (drop Team from merge keys)
comparison = fp3.merge(fp1.merge(
    fp2,
    on=["Driver"],
    how="right"
), on=["Driver"], how="right")

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
