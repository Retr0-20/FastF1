from pathlib import Path
import fastf1

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def format_time(value):
    if str(value) == "NaT":
        return "N/A"

    text = str(value)

    if "0 days " in text:
        text = text.replace("0 days ", "")

    if text.startswith("00:00:"):
        seconds = text.replace("00:00:", "")
        seconds = seconds[:6]
        return f"+{seconds}s"

    if text.startswith("00:"):
        return text[3:11]

    return text


def print_results_summary(results, limit=10):
    print("\nTop Results")
    print("-" * 80)

    clean_results = results[[
        "Position",
        "FullName",
        "TeamName",
        "Time",
        "Status",
        "Points"
    ]].head(limit)

    for _, row in clean_results.iterrows():
        position = int(row["Position"])
        name = row["FullName"]
        team = row["TeamName"]
        points = int(row["Points"])
        status = row["Status"]
        time = format_time(row["Time"])

        print(f"{position:>2}. {name:<20} {team:<18} {points:>2} pts   {time:<12} {status}")


def print_weather_summary(weather):
    first = weather.iloc[0]
    last = weather.iloc[-1]

    print("\nWeather Summary")
    print("-" * 80)

    print(f"Starting air temp:   {first['AirTemp']}°C")
    print(f"Ending air temp:     {last['AirTemp']}°C")
    print(f"Starting track temp: {first['TrackTemp']}°C")
    print(f"Ending track temp:   {last['TrackTemp']}°C")
    print(f"Starting humidity:   {first['Humidity']}%")
    print(f"Ending humidity:     {last['Humidity']}%")
    print(f"Rainfall recorded:   {weather['Rainfall'].any()}")


def print_fastest_laps(laps, limit=10):
    accurate_laps = laps[laps["IsAccurate"] == True]

    fastest = accurate_laps[[
        "Driver",
        "Team",
        "LapNumber",
        "LapTime",
        "Compound",
        "TyreLife"
    ]].sort_values("LapTime").head(limit)

    print("\nFastest Laps")
    print("-" * 80)

    for _, row in fastest.iterrows():
        driver = row["Driver"]
        team = row["Team"]
        lap_number = int(row["LapNumber"])
        lap_time = format_time(row["LapTime"])
        compound = row["Compound"]
        tyre_life = int(row["TyreLife"])

        print(f"{driver:<4} {team:<18} Lap {lap_number:<3} {lap_time:<12} {compound:<8} Tyre age: {tyre_life}")


def inspect_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load()

    print("\n\n\n")

    print("\n" + "=" * 80)
    print(f"{year} {event} Grand Prix - {session.name}")
    print("=" * 80)

    print_results_summary(session.results)
    print_fastest_laps(session.laps)
    print_weather_summary(session.weather_data)

    print("\n\n\n")

years = [2021, 2022, 2023, 2024, 2025]

for year in years:
    try:
        inspect_session(year, "Monaco", "R")
    except Exception as e:
        print(f"\nFailed to load {year} Monaco Race")
        print(f"Reason: {e}")