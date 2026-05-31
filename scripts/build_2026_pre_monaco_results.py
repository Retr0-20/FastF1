from pathlib import Path
import pandas as pd
import fastf1

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_race_results(results, year, event_name, round_number):
    clean = results[[
        "Abbreviation",
        "FullName",
        "TeamName",
        "GridPosition",
        "Position",
        "Status",
        "Points",
        "Laps"
    ]].copy()

    clean = clean.rename(columns={
        "Abbreviation": "driver_code",
        "FullName": "driver_name",
        "TeamName": "team",
        "GridPosition": "grid_position",
        "Position": "finish_position",
        "Status": "status",
        "Points": "points",
        "Laps": "laps"
    })

    clean["year"] = year
    clean["event"] = event_name
    clean["round"] = round_number

    clean = clean[[
        "year",
        "round",
        "event",
        "driver_code",
        "driver_name",
        "team",
        "grid_position",
        "finish_position",
        "status",
        "points",
        "laps"
    ]]

    return clean


def build_pre_monaco_results(year=2026):
    schedule = fastf1.get_event_schedule(year)

    monaco_row = schedule[schedule["EventName"].str.contains("Monaco", case=False, na=False)]

    if monaco_row.empty:
        raise ValueError("Could not find Monaco in the schedule.")

    monaco_round = int(monaco_row.iloc[0]["RoundNumber"])

    races_before_monaco = schedule[
        (schedule["RoundNumber"] < monaco_round) &
        (schedule["EventFormat"] != "testing")
    ]

    all_results = []

    for _, race in races_before_monaco.iterrows():
        round_number = int(race["RoundNumber"])
        event_name = race["EventName"]

        print(f"Loading round {round_number}: {event_name}")

        try:
            session = fastf1.get_session(year, event_name, "R")
            session.load()

            clean_results = clean_race_results(
                session.results,
                year,
                event_name,
                round_number
            )

            all_results.append(clean_results)

        except Exception as e:
            print(f"Could not load {event_name}: {e}")

    if not all_results:
        raise ValueError("No race results were loaded.")

    final_dataset = pd.concat(all_results, ignore_index=True)

    output_path = OUTPUT_DIR / "2026_pre_monaco_results.csv"
    final_dataset.to_csv(output_path, index=False)

    print("\nSaved dataset:")
    print(output_path)
    print("\nPreview:")
    print(final_dataset.head(20).to_string())


build_pre_monaco_results()