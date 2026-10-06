import fastf1
import config
import f1_utils
from termcolor import colored

YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = f1_utils.get_event_folder()

session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session.load()
laps = session.laps

# Get drivers and convert to abbreviations
drivers = [session.get_driver(d)["Abbreviation"] for d in session.drivers]

# Group laps by driver, stint, and compound
stints = laps[["Driver", "Compound", "LapNumber", "TyreLife"]]
stints = stints.groupby(["Driver", "Compound"]).count().reset_index()
stints = stints.rename(columns={"LapNumber": "Lap Number", "TyreLife": "Tyre Life"})

print(f"\n{YEAR} {EVENT} — {SESSION_TYPE} TYRE STRATEGY SUMMARY")
print("=" * 60)
print("-" * 60, "\n")

# HOISTED ABOVE LOOP
compound_names = {
    "INTERMEDIATE": "Intermediate",
    "SOFT": "Soft",
    "MEDIUM": "Medium",
    "HARD": "Hard",
    "WET": "Wet",
}
compound_colours = {
    "INTERMEDIATE": "green",
    "SOFT": "red",
    "MEDIUM": "yellow",
    "HARD": "white",
    "WET": "blue",
}

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    
    print(f"\n{driver} Stints:")
    if driver_stints.empty:
        print("  No stints found.")
        print("─" * 30)
        continue
    
    # Header (pad first, then colour)
    header_compound = "Compound".rjust(12)
    print(f"  {colored(header_compound, 'cyan')}  {colored('Laps', 'cyan'):>5}")
    print(f"  {'─' * 12}  {'─' * 5}")
    
    for _, row in driver_stints.iterrows():
        plain = compound_names.get(row["Compound"], row["Compound"])
        padded = plain.rjust(12)
        colour = compound_colours.get(row["Compound"], "white")
        print(f"  {colored(padded, colour)}  {row['Tyre Life']:>5}")
    
    print("─" * 30)

print("=" * 60, "\n")