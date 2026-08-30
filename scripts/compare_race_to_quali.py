from pathlib import Path
import config
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", "{:.0f}".format)

# ---------------------------------------------------------------------
# Configurable information for Grand Prixs - config.py
# ---------------------------------------------------------------------
YEAR = config.YEAR
EVENT = config.EVENT
EVENT_FOLDER = config.get_event_folder()
PROJECT_ROOT = config.PROJECT_ROOT

# Pull and read the predicted qualifying positions and actual qualifying results CSVs
quali_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"Q_results.csv")
race_results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / EVENT_FOLDER / f"R_results.csv")

# Merge the race results DataFrame with the actual qualifying results DataFrame on the "Driver" column
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

# Add a new column to calculate the absolute difference between race and qualifying positions
comparison["position_diff"] = (
    comparison["race_position"] - comparison["quali_position"]
).abs()

# Create a new column to indicate whether the predicted position is higher, lower, or the same as the actual position
comparison["change_arrow"] = comparison.apply(
    lambda row: f"↑{row['position_diff']}" if row['quali_position'] 
        > row['race_position'] 
    else f"↓{row['position_diff']}" if row['position_diff'] > 0
    else f"→",
    axis=1
)

# Add the new column
comparison = comparison[[
    "Driver",
    "Team",
    "race_position",
    "quali_position",
    "position_diff",
    "change_arrow"
]]

# Convert the relevant columns to integers for better readability
comparison["race_position"] = comparison["race_position"].astype(int)
comparison["quali_position"] = comparison["quali_position"].astype(int)
comparison["position_diff"] = comparison["position_diff"].astype(int)

# Exact matches are those where position_diff == 0
# Winning driver is the driver with race_position == 1
exact_matches = (comparison["position_diff"] == 0).sum()
winning_driver = comparison["Driver"][comparison["race_position"] == 1]
comparison = comparison.sort_values("race_position")

print("\nQualifying vs Race:")
print(comparison.to_string(index=False))
print(f"\nThe Winning Driver is: {winning_driver.iloc[0]}")
print(f"\nDrivers who held position: {exact_matches}\n")