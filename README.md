# FastF1 Analysis Scripts

Python scripts for pulling Formula 1 session data via the
[FastF1](https://docs.fastf1.dev) library and analyzing it — comparing
practice pace, predicting qualifying outcomes, and reviewing results.


# How to use

In order to run scripts you must navigate to the appropriate place, in my case,
`/home/USERNAME/Documents/Code/FastF1/scripts/`

From here you can run any script by entering `python3 SCRIPT_NAME.py` in the terminal.

## Typical workflow

1. Set `YEAR`, `EVENT`, and `SESSION_TYPE` in `config.py`
2. Pull practice results → run a prediction script
3. After qualifying: `SESSION_TYPE = "Q"` and `pull_quali_results.py`
4. After the race: `SESSION_TYPE = "R"` and `pull_race_results.py`
5. Run the comparison scripts to score your predictions

## Setup

Requires `fastf1` and `pandas` (`pip install fastf1 pandas`). Session
data is cached in `fastf1_cache/`, so repeat runs are fast and work
offline. The `fastf1_cache/` and `data/` directories are
gitignored.


# config.py

This script enables you to edit global variables which indicate which session:
race, sprint, quali, sprint quali and practice.
As well as from what year and which race within that year's season.
Additionally, this is where you can also adjust the `PROJECT_ROOT`;
it's anchored to the file rather than the
current working directory, scripts behave identically no matter
which folder you launch them from.
`CACHE_DIR` (`PROJECT_ROOT / "fastf1_cache"`) — FastF1's download
cache. Session data is fetched once, then loaded from disk on every
later run. Deleting it forces a full re-download.

Changing these values re-points **all** scripts at the selected event.
Results are saved under `data/processed/<year>_<event>/` and predictions
under `data/predictions/<year>_<event>/`.

Note: `config.py` must sit exactly one directory below the project root — the `parents[1]` anchor depends on it.


# f1_utils.py

This script contains 4 functions with appropriate names:

- `get_event_folder()`
    This function pulls two global variables, YEAR and EVENT, to create a folder
    following the convention `{config.YEAR}_{config.EVENT}`.

- `time_to_seconds()`
    This function converts a timedelta to seconds with millisecond precision,
    to the 3rd decimal place.

- `seconds_to_lap_time()`
    This function extracts minutes through floor division and seconds through modulo,
    returning remaining seconds padded with leading zeroes, with a total width
    of 6 characters, to 3 decimal places.

- `seconds_to_sector_time()`
    This function converts a timedelta to seconds for sector times,
    returning remaining seconds padded with leading zeroes, to 3 decimal places.


# Pull Scripts

These scripts are used for 3 main purposes, indicated by their names:

`pull_practice_results.py`
    This script pulls data such as: Position, Driver, Team, BestLap,
    LapTimeSeconds, Compound, TyreLife,
    TrackStatus, Sector1Time, Sector2Time
    and Sector3Time.
    Allows all 3 Free Practice (FP) sessions to be configured in config.py.

`pull_quali_results.py`
    This script pulls data such as: Position, Driver, DriverName, Team, Q1, Q1Seconds,
    Q2, Q2Seconds, Q3, Q3Seconds, Status.
    Allows both race qualifying and sprint qualifying formats to be configured in config.py.

`pull_race_results.py`
    This script pulls data such as: Position, Driver, Team and Points.
    Allows both race and sprint formats to be configured in config.py.


# Prediction Scripts

These scripts are used for 2 main purposes, indicated by their names:

`predict_quali_from_practice.py`
    This script predicts qualifying based on the 3 Free Practice sessions,
    pulled using the pull_practice_results.py script, configuring the config.py
    script for the 3 sessions.
    This script provides the following insights:
        predicted_quali_position
        Driver
        Team
        best_FP1_lap
        best_FP1_theoretical_lap
        best_FP2_lap
        best_FP2_theoretical_lap
        best_FP3_lap
        best_FP3_theoretical_lap
        prediction_score
    Allowing the comparison of their best laps in practice sessions and getting
    from each sector, a theoretical best lap with the best sector for each practice
    session's laps.
    Weighted score: (FP1 15%, FP2 25%, FP3 60%)

`predict_quali_from_sprint.py`
    This script predicts qualifying based on the Sprint Qualifying and the Sprint Race,
    pulled using the pull_quali_results.py and pull_race_results.py scripts,
    configuring the config.py script for the 3 sessions.
    This script provides the following insights:
        predicted_quali_position
        Driver
        best_FP1_lap
        best_FP1_theoretical_lap
        best_SQ_lap
        best_SQ_theoretical_lap
        prediction_score
    Allowing the comparison of their best laps in practice sessions and getting
    from each sector, a theoretical best lap with the best sector for FP1 practice
    session laps and Sprint Qualifying laps.
    Weighted score: (FP1 40%, SQ 60%)


# Compare Scripts

These scripts are used for 3 main purposes, indicated by their names:

`compare_quali_prediction_to_actual_quali.py` — a long name, (need a better one)
    This script compares the prediction .CSV file which needs to be gathered by
    running pull_practice_results.py; configuring which session and event in what
    year you wish to pull results from, in the config.py script.
    Following this you shall wish to do the same for the pull_quali_results.py script.
    Finally, you will now want to run the predict_quali_from_practice.py script.
    You can now run the compare_quali_prediction_to_actual_quali.py script.
    This script will show the predicted grid vs. actual grid for the race format
    with per-driver error and spot-on/over/under outcomes.

`compare_race_to_quali.py`
    This script compares the quali results .CSV file which needs to be gathered by
    running pull_quali_results.py and pull_race_results.py, configuring in the config.py script.
    You can now run the compare_race_to_quali.py script.
    This script will show the starting grid vs. finished grid, showing who gained (↑)
    or lost (↓) positions.

`compare_sector_times_practice.py`
    This script compares the sector times recorded in each practice session results .CSV
    file which needs to be gathered by running pull_practice_results.py and configuring
    in the config.py script.
    You can now run the compare_sector_times_practice.py script.
    This script will show the best sector times across FP1/FP2/FP3.