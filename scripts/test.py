from matplotlib import pyplot as plt
import fastf1
from fastf1 import plotting
import config
import f1_utils

YEAR = config.YEAR
EVENT = config.EVENT
SESSION_TYPE = config.SESSION_TYPE
EVENT_FOLDER = f1_utils.get_event_folder()

plotting.setup_mpl(color_scheme='fastf1')

session1 = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session2 = fastf1.get_event(YEAR, EVENT).get_session(SESSION_TYPE)
session3 = fastf1.get_events_remaining()
session1.load()
session2.load()
print("SESSION")
print(type(session1))

print("\nRESULTS")
print(session1.results.columns.tolist())

print("\nLAPS")
print(session1.laps.columns.tolist())

print("\nWEATHER")
print(session1.weather_data.columns.tolist())

print("\nRACE CONTROL")
print(session1.race_control_messages.columns.tolist())

print(session1.laps.pick_fastest())
print(session1.laps.pick_box_laps())