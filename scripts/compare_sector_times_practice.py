from pathlib import Path
import config
import f1_utils
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

PROJECT_ROOT = config.PROJECT_ROOT
EVENT_FOLDER = f1_utils.get_event_folder()

# Pull and read the fastest lap sector times for FP1, FP2, and FP3 from stored CSVs
fp1 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"FP1_fastest_laps_by_driver.csv")
fp2 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"FP2_fastest_laps_by_driver.csv")
fp3 = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"FP3_fastest_laps_by_driver.csv")

# Fill NaN values in the "Team" column with an empty string to avoid issues during merging
fp1["Team"] = fp1["Team"].fillna("")
fp2["Team"] = fp2["Team"].fillna("")
fp3["Team"] = fp3["Team"].fillna("")

# Now merge on Driver only (drop Team from merge keys)
comparison = fp3.merge(fp1.merge(
    fp2,
    on=["Driver"],
    how="right"
), on=["Driver"], how="right")

# Rename columns to indicate which session they belong to
comparison["S1Time_FP1"] = comparison["Sector1Seconds_x"]
comparison["S1Time_FP2"] = comparison["Sector1Seconds_y"]
comparison["S1Time_FP3"] = comparison["Sector1Seconds"]

comparison["S2Time_FP1"] = comparison["Sector2Seconds_x"]
comparison["S2Time_FP2"] = comparison["Sector2Seconds_y"]
comparison["S2Time_FP3"] = comparison["Sector2Seconds"]

comparison["S3Time_FP1"] = comparison["Sector3Seconds_x"]
comparison["S3Time_FP2"] = comparison["Sector3Seconds_y"]
comparison["S3Time_FP3"] = comparison["Sector3Seconds"]

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
