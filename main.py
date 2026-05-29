from pathlib import Path
from fastapi import FastAPI, HTTPException
import fastf1

app = FastAPI()

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

#http://127.0.0.1:8000/
@app.get("/")
def home():
    return {"message": "FastAPI + FastF1 working"}

# http://127.0.0.1:8000/laps/2024/Monaco/R
# http://127.0.0.1:8000/laps/2024/Monaco/R?limit=100
@app.get("/laps/{year}/{event}/{session_type}")
def get_laps(year: int, event: str, session_type: str):
    try:
        session = fastf1.get_session(year, event, session_type)
        session.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

    return laps.astype(str).to_dict(orient="records")

# http://127.0.0.1:8000/schedule/2024
@app.get("/schedule/{year}")
def get_schedule(year: int):
    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return schedule.astype(str).to_dict(orient="records")