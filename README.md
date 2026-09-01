# FastF1

Insights into races held through the FastF1 API


# How to use

In order to run scripts you must navigate to the appropriate place, in my case, 
/home/USERNAME/Documents/Code/FastF1/scripts/

From here you can run any script by entering python3 SCRIPT_NAME.py in the terminal.


# config.py 

This script enables you to edit global variables which indictate which session;
    race, sprint, quali, sprint quali and practice.
    As well as from what year and which race within that year's season.


# f1_utils.py

This script contains 4 functions with appropriate names:

def get_event_folder()
    This function

def time_to_seconds()
    This function

def seconds_to_lap_time()
    This function

def seconds_to_sector_time()
    This function


# Pull Scripts

These scripts are used for 3 main purposes, indictated by their names:

pull_practice_results.py
    This script pulls data such as: Position, Driver, Team, BestLap, 
                                    LapTimeSeconds, Compound, TyreLife, 
                                    TrackStatus, Sector1Time, Sector2Time 
                                    and Sector3Time.
    Allows all 3 Free Practice (FP) sessions to be configured in config.py.

pull_quali_results.py
    This script pulls data such as: Position, Driver, Team, BestLap, 
                                    LapTimeSeconds, Compound, TyreLife, 
                                    TrackStatus, Sector1Time, Sector2Time 
                                    and Sector3Time.
    Allows both race qualifying and sprint qualifying formats to be configured in config.py.

pull_race_results.py
    This script pulls data such as: Position, Driver, Team and Points.
    Allows both race and sprint formats to be configured in config.py.


# Prediction Scripts

These scripts are used for 2 main purposes, indictated by their names:

predict_quali_from_practice.py

predict_quali_from_sprint.py


# Compare Scripts

These scripts are used for 3 main purposes, indictated by their names:

compare_quali_prediction_to_actual_quali.py -- a long name, (need a better one)
    This script compares the prediction .CSV file which needs to be gathered by 
    running pull_pratice_results.py; configuring which session and event in what 
    year you wish to pull results from, in the config.py script.
    Following this you shall wish to do the same for pull_quali_results.py script.
    Finally, you will now want to run predict_quali_from_practice.py script.
    You can now run the compare_quali_prediction_to_actual_quali.py script.

compare_race_to_quali.py
    This script compares the quali results .CSV file which needs to be gathered by 
    running pull_quali_results.py and pull_race_results configuring in the config.py script.
    You can now run the compare_race_to_quali.py script.

compare_sector_times_practice.py
    This script compares the sector times recorded in each practice session results .CSV 
    file which needs to be gathered by running pull_practice_results.py and configuring 
    in the config.py script.
    You can now run the compare_sector_times_practice.py script.