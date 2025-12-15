import tkinter as tk
from urllib.request import urlopen
import json
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageTk
import numpy as np
import random
import os
import time

DATA_FOLDER = "./f1-data/"

session_key = -1

def read_file(filePath):
    '''
    Reads the file, returning the content or -1 if it doesn't exist
    
    :param filePath: the file path
    :return: -1 if the file doesn't exist or the file content reading
    '''
    if os.path.exists(filePath):
        file = open(filePath, "r")
        data = file.read()
        file.close()
        return data
    else:
        return -1

def fetch_data(jsonValues):
    '''
    Fetches data from the openf1 api using the specific parameters
    
    :param jsonValues: the parameters, eg "drivers?driverNum=1"
    :return: the fetched data
    '''
    print("Fetching data for "+jsonValues)
    response = urlopen('https://api.openf1.org/v1/'+jsonValues)
    data = json.loads(response.read().decode('utf-8'))

    return data

def fetch_and_write_data(filePath, jsonValues):
    '''
    Fetches the data from the file path, or if the file doesn't exist, fetches the data from the api and writes it into the file
    
    :param filePath: the file path to read or write to
    :param jsonValues: the parameters, eg "drivers?driverNum=1"
    :return: the fetched data
    '''
    data = read_file(filePath)
    if data == -1:
        # doesn't exist, fetch and save
        data = fetch_data(jsonValues)
        
        file = open(filePath, "w")
        file.write(str(data))
        file.close()
    else:
        # exists
        data = eval(data)
    
    return data
    
def get_session_data():
    '''
    Gets race session data from OpenF1, returning the data and current time and writing the data into the preset file
    '''
    print("> Getting Session Data")
    sessionData = fetch_data("sessions?session_type=Race")
    sessionDataLastUpdated = time.time()

    file = open(DATA_FOLDER+"session_info.txt", "w")
    file.write(str(sessionDataLastUpdated)+"\n---\n"+str(sessionData))
    file.close()

    return sessionData, sessionDataLastUpdated

def get_values_by_key(dictArr, key) -> list:
    '''
    Takes in a list dictionaries and returns the values for the given key for each dictionary
    
    :param dictArr: the list of dictionaries
    :param key: the key to get the values for
    :return: the values for the key for each dictionary in the list
    :rtype: list
    '''
    arr = []
    for vals in dictArr:
        arr.append(vals[key])
    return arr

def parse_time(p):
    return datetime.fromisoformat(p["date"])

def get_data_per_second(data, startTime):
    data.sort(key=parse_time)

    t = startTime
    result = []

    for val in data:
        if val['x'] == 0 and val['y'] == 0 and val['z'] == 0:
            # invalid value
            pass
        elif datetime.fromisoformat(val['date']) > t:
            result.append(val)
            t += timedelta(seconds=1)

    return result

# --- get session info ---
# TODO: Read session info and update if more that a week has passed
info = read_file(DATA_FOLDER+"session_info.txt")
# NOTE: info is last updated time + \n---\n + data
if info == -1:
    # doesn't exist
    sessionData, sessionDataLastUpdated = get_session_data()
else:
    # exists, check date
    info = info.split("\n---\n")
    sessionDataLastUpdated = eval(info[0])
    sessionData = eval(info[1])

    if time.time()-sessionDataLastUpdated > 604800:
        # needs to update
        sessionData, sessionDataLastUpdated = get_session_data()

# --- get meeting + session key ---
meeting_keys = get_values_by_key(sessionData, "meeting_key")
session_keys = get_values_by_key(sessionData, "session_key")

# raceIdx = random.randrange(0, len(meeting_keys))
# meeting_key = meeting_keys[raceIdx]
# session_key = session_keys[raceIdx]
meeting_key = 1208
session_key = 9078
raceIdx = meeting_keys.index(meeting_key)
print(meeting_key, ", ", session_key)

# --- get each driver's locations ---
startTime = datetime.fromisoformat(sessionData[raceIdx]['date_start'])
driverLocs = eval(read_file(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d1_locs.txt"))

# result = get_data_per_second(driverLocs, startTime)
for val in driverLocs:
    print(val['date'])

# print("---")
# for val in result:
#     print(val['date'])