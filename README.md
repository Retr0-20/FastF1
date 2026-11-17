# FastF1 Analysis Scripts

Python scripts for pulling Formula 1 session data via the
[FastF1](https://docs.fastf1.dev) library, comparing practice pace,
predicting qualifying outcomes, and reviewing results.


# How to use

Install deps:

    pip install termcolor
    pip install fastf1 pandas

FastF1 (3.9+) needs an active F1 TV subscription to pull session data.
Sign in once before your first pull:

    python -m fastf1 auth f1tv --authenticate

The token lasts about four days. Cached sessions load fine without it,
so sign-in only matters for fresh pulls.

Run scripts from the scripts folder (`/home/USERNAME/Documents/Code/FastF1/scripts/`):

    python3 SCRIPT_NAME.py

## Typical weekend workflow

1. Set `YEAR`, `EVENT`, and `SESSION_TYPE` in `config.py`
2. After each practice session: `SESSION_TYPE = "FP1"/"FP2"/"FP3"`,
   run `pull_session_results.py`, then a prediction script
3. After qualifying: `SESSION_TYPE = "Q"`, run `pull_session_results.py`
4. After the race: `SESSION_TYPE = "R"`, run `pull_session_results.py`
5. Run the comparison scripts to score your predictions

Session data is cached in `fastf1_cache/` (gitignored), so repeat runs are
fast and work offline; deleting it forces a re-download. Results go under
`data/processed/<year>_<event>/` and predictions under
`data/predictions/<year>_<event>/` — these are committed.


# config.py

Global variables that re-point every script at a session:

- `YEAR`, `EVENT` — season and race weekend
- `SESSION_TYPE` — one of `FP1`, `FP2`, `FP3`, `Q`, `SQ`, `R`, `S`
- `PROJECT_ROOT` — anchored to the file (`parents[1]`), so scripts run the
  same from any folder. `config.py` must sit exactly one directory below
  the project root for this to hold
- `CACHE_DIR` (`PROJECT_ROOT / "fastf1_cache"`) — FastF1's download cache

Change these and all scripts follow — no per-script editing.


# f1_utils.py

Shared helpers used by the pull and comparison scripts:

- `get_event_folder()`
    Builds the `{YEAR}_{EVENT}` folder name from config.

- `time_to_seconds()`
    Converts a timedelta to seconds, to 3 decimal places.

- `seconds_to_lap_time()`
    Seconds to an `MM:SS.mmm` string via floor division (minutes) and
    modulo (seconds), zero-padded.

- `seconds_to_sector_time()`
    Seconds to a zero-padded sector time string.

Also holds the session/laps/weather loaders and the points maps used by
the pull script.


# pull_session_results.py

One script, driven by `SESSION_TYPE`:

    SESSION_TYPE = "FP1/FP2/FP3"
    Position, Driver, Team, BestLap, LapTimeSeconds, Compound, TyreLife,
    TrackStatus, and the three sector times — fastest valid lap per driver,
    with a sector summary printed at the end.

    SESSION_TYPE = "Q"/"SQ"
    Position, Driver, DriverName, Team, Q1–Q3 times and seconds
    equivalents (renamed SQ1–SQ3 for sprint qualifying), Status,
    and Potential Points.

    SESSION_TYPE = "R"/"S"
    Position, Driver, Driver Name, Team, Status, Points, GridPosition,
    and Change.

Notes on race mode:

- `Position` is the official post-penalty classification, so it can
  contain `"R"` for retirees, not just numbers.
- `Change` is the grid→finish arrow: `↑3` gained, `↓2` lost, `→` held,
  `OUT` retired, `PIT` pit-lane start. `—` if grids aren't published yet.
- The script refuses to write a CSV until official results are out, so
  you can't archive provisional data as final.

Every pull ends with a timing and weather summary (temps, humidity,
rainfall).


# Prediction Scripts

`predict_quali_from_practice.py`
    Predicts the qualifying order from the three practice sessions:
    predicted_quali_position, Driver, Team, best and theoretical-best
    (best sectors stitched together) laps per session, and a
    prediction_score weighted FP1 15% / FP2 25% / FP3 60%.
    Needs the three practice pulls done first.

`predict_quali_from_sprint.py`
    Same idea for sprint weekends, using FP1 and Sprint Qualifying:
    best/theoretical laps for each, weighted FP1 40% / SQ 60%.
    Needs the FP1 and SQ pulls done first.


# Compare Scripts

`compare_quali_prediction_to_actual_quali.py`
    Scores your prediction against the real qualifying result: predicted
    grid vs. actual grid, per-driver error, spot-on/over/under outcomes.
    Needs the prediction CSV and the `Q` pull done first.

`compare_sector_times_practice.py`
    Best sector times across FP1/FP2/FP3, so you can see who was quick
    in which sector all weekend.

`compare_race_to_quali.py`
    The original single-stage quali→race comparison. Currently broken
    against the new official-position format and due for retirement in
    favour of the two-stage quali/grid/race comparison — don't rely on it.
