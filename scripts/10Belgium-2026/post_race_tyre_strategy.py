from matplotlib import pyplot as plt
import fastf1
from fastf1 import plotting

plotting.setup_mpl(color_scheme='fastf1')

session = fastf1.get_session(2026, "Silverstone", 'R')
session.load()
laps = session.laps

# Get drivers and convert to abbreviations
drivers = [session.get_driver(d)["Abbreviation"] for d in session.drivers]

# Group laps by driver, stint, and compound
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
stints = stints.rename(columns={"LapNumber": "StintLength"})

# Plot strategies
fig, ax = plt.subplots(figsize=(5, 10))

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    
    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        compound_color = plotting.get_compound_color(
            row["Compound"],
            session=session
        )
        plt.barh(
            y=driver,
            width=row["StintLength"],
            left=previous_stint_end,
            color=compound_color,
            edgecolor="black",
            fill=True
        )
        previous_stint_end += row["StintLength"]

plt.title("2026 Silverstone GP - Tire Strategies")
plt.xlabel("Lap Number")
plt.grid(False)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.tight_layout()
plt.show()