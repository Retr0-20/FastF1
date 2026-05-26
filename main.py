# http://127.0.0.1:8000/laps/2024/Monaco/R

from pathlib import Path
from fastapi import FastAPI
import fastf1

app = FastAPI()

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

@app.get("/")
def home():
    return {"message": "FastAPI + FastF1 working"}

@app.get("/laps/{year}/{event}/{session_type}")
def get_laps(year: int, event: str, session_type: str):
    session = fastf1.get_session(year, event, session_type)
    session.load()

    laps = session.laps[[
        "Driver",
        "LapNumber",
        "LapTime",
        "Sector1Time",
        "Sector2Time",
        "Sector3Time",
        "Compound",
        "TyreLife"
    ]]

    return laps.head().astype(str).to_dict(orient="records")

@app.get("/schedule/{year}")
def get_schedule(year: int):
    schedule = fastf1.get_event_schedule(year)

    return schedule.astype(str).to_dict(orient="records")