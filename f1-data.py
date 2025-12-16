import tkinter as tk
from urllib.request import urlopen
import json
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageTk
import numpy as np
import random
import os
import time
import visCanvas as visC


DATA_FOLDER = "./f1-data/"
REPLAY_MAP_INFO = {
    'dot-size':5,
    'map-width':400,
    'map-height':250,
    'map-x-offset':50,
    'map-y-offset':100,
    'dot-pos-size':5,
    'x-pos-offset':600,
    'y-pos-offset':100,
    'x-pos-spacing':200,
    'y-pos-spacing':25,
    'title-width':700,
    'subtitle-width':700,
}

### CODE START -- overall parameters
WIDTH = 930
HEIGHT = 510
FPS = 30
TIMESCALE = 60
### CODE END

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

def get_data_per_interval(data, startTime, location=True):
    data.sort(key=parse_time)

    t = startTime
    result = []

    for val in data:
        dateTimeVal = datetime.fromisoformat(val['date'])
        if location:
            if val['x'] == 0 and val['y'] == 0 and val['z'] == 0:
                # invalid value
                pass
        if dateTimeVal >= t:
            result.append(val)
            while dateTimeVal >= t:
                t += timedelta(milliseconds=100)

    return result

def transform_locations(coords, maxCoords, minCoords, newScale):
    newLoc = []

    xScale = newScale[0]/(maxCoords[0] - minCoords[0])
    yScale = newScale[1]/(maxCoords[1] - minCoords[1])

    # scale:
    # (a - minA) * newScale/(maxA - minA)
    newLoc.append((coords[0] - minCoords[0]) * xScale)
    newLoc.append((coords[1] - minCoords[1]) * yScale)

    return newLoc


# --- get session info ---
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

# --- get the drivers for that meeting ---
driverData = fetch_and_write_data(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_drivers.txt", 
                                  "drivers?meeting_key="+str(meeting_key)+"&session_key="+str(session_key))
driverNums = get_values_by_key(driverData, "driver_number")

# --- get each driver's locations ---
startTime = datetime.fromisoformat(sessionData[raceIdx]['date_start'])
endTime = datetime.fromisoformat(sessionData[raceIdx]['date_end'])
driverLocData = {}
for dNum in driverNums:
    # driverLocData[dNum] = fetch_and_write_data(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d"+str(dNum)+"_locs.txt",
    #                                            "location?meeting_key="+str(meeting_key)+"&session_key="+str(session_key)+"&driver_number="+str(dNum))

    driverLocs = read_file(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d"+str(dNum)+"_locs.txt")
    if driverLocs == -1:
        print("Fetching data for driver "+str(dNum))
        # doesn't exist, get data
        driverLocs = []
        t = startTime
        while t < endTime:
            t2 = t + timedelta(minutes=3) # Go by 3 minute intervals

            driverLocs += fetch_data("location?meeting_key="+str(meeting_key)+"&session_key="+str(session_key)+"&driver_number="+str(dNum)+"&date>="+t.replace(tzinfo=None).isoformat()+"&date<="+t2.replace(tzinfo=None).isoformat())

            t = t2
            time.sleep(0.5)
    
        filteredData = get_data_per_interval(driverLocs, startTime, location=True)
        driverLocData[dNum] = filteredData
        file = open(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d"+str(dNum)+"_locs.txt", "w")
        file.write(str(filteredData))
        file.close()
        time.sleep(5)
        print("Finished fectching data for driver "+str(dNum)+"\n")
    else:
        # print("Getting data for driver "+str(dNum))
        driverLocData[dNum] = eval(driverLocs)
        # print("Finished getting data for driver "+str(dNum)+"\n")

# --- get the track dimensions ---
# TODO add track image?
# pick random 5 drivers, get the max and min coords of all locations
tempDNums = random.choices(driverNums, k=5)
tempDLocs = []
for t in tempDNums:
    tempDLocs += driverLocData[t]

tempXVals = [p["x"] for p in tempDLocs]
tempYVals = [p["y"] for p in tempDLocs]
tempZVals = [p["z"] for p in tempDLocs]

MAXCOORDS = [max(tempXVals), max(tempYVals), max(tempZVals)]
MINCOORDS = [min(tempXVals), min(tempYVals), min(tempZVals)]

del tempDNums
del tempDLocs
del tempXVals
del tempYVals
del tempZVals

# --- get each driver's positions ---
driverPosData = {}
for dNum in driverNums:
    driverPos = read_file(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d"+str(dNum)+"_positions.txt")
    if driverPos == -1:
        print("Fetching data for driver "+str(dNum))
        # doesn't exist, get data
        driverPos = []
        t = startTime
        while t < endTime:
            t2 = t + timedelta(minutes=3) # Go by 3 minute intervals

            driverPos += fetch_data("position?meeting_key="+str(meeting_key)+"&session_key="+str(session_key)+"&driver_number="+str(dNum)+"&date>="+t.replace(tzinfo=None).isoformat()+"&date<="+t2.replace(tzinfo=None).isoformat())

            t = t2
            time.sleep(0.5)
    
        filteredData = get_data_per_interval(driverPos, startTime, location=False)
        driverPosData[dNum] = filteredData
        file = open(DATA_FOLDER+"m"+str(meeting_key)+"_s"+str(session_key)+"_d"+str(dNum)+"_positions.txt", "w")
        file.write(str(filteredData))
        file.close()
        time.sleep(5)
        print("Finished fectching data for driver "+str(dNum)+"\n")
    else:
        # print("Getting data for driver "+str(dNum))
        driverPosData[dNum] = eval(driverPos)
        # print("Finished getting data for driver "+str(dNum)+"\n")



# --- VISUALS ---
root = tk.Tk(screenName="")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#000")
canvas.pack()

cv = visC.VisCanvas(canvas, WIDTH, HEIGHT)

### CODE START -- initial setup

# --- ADD TITLE AND SUBTITLE ---
# Hungaroring - Budapest, Hungary
title = ""
title += sessionData[raceIdx]["circuit_short_name"] # Hungaroring
title += " - "
title += sessionData[raceIdx]["location"] # Budapest
title += ", "
title += sessionData[raceIdx]["country_name"] # Hungary
f1RaceTitle = visC.Text("", REPLAY_MAP_INFO["title-width"], 25, 25, color="#FFF", maxSize=45)
cv.add_sprite(f1RaceTitle, "race-info")
f1RaceTitle.change_text(title, 30)

# Race on 10/10/2025 or whatever
subtitle = ""
subtitle += sessionData[raceIdx]["session_type"] # Race or 'session_name' idk which to use
subtitle += " on "
subtitle += ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][startTime.month-1]
subtitle += " "
subtitle += str(startTime.day)
subtitle += ", "
subtitle += str(startTime.year)
f1RaceSubtitle = visC.Text("", REPLAY_MAP_INFO["subtitle-width"], 25, 75, color="#FFF", maxSize=25)
cv.add_sprite(f1RaceSubtitle, "race-info")
f1RaceSubtitle.delay(30)
f1RaceSubtitle.change_text(subtitle, 30)

timeText = visC.Text("", REPLAY_MAP_INFO["subtitle-width"], 25, HEIGHT-50, color="#FFF", maxSize=25)
cv.add_sprite(timeText, "race-info")
# --- make driver location + position dots
driverLocDots = {}
driverLocTime = {}
driverLocIdx = {}

driverPosDots = {}
driverPosText = {}
driverPosTime = {}
driverPosIdx = {}
for dNum in driverNums:
    dIdx = driverNums.index(dNum)

    # add location dot
    dLoc = transform_locations([driverLocData[dNum][0]['x'], driverLocData[dNum][0]['y']], MAXCOORDS, MINCOORDS, [REPLAY_MAP_INFO["map-width"], REPLAY_MAP_INFO['map-height']])
    dLocDot = visC.Dot("#"+driverData[dIdx]['team_colour'], "#FFF", REPLAY_MAP_INFO['dot-size'], dLoc[0]+REPLAY_MAP_INFO['map-x-offset'], dLoc[1]+REPLAY_MAP_INFO['map-y-offset'])
    
    cv.add_sprite(dLocDot, ["map-dot"])
    driverLocDots[dNum] = dLocDot
    driverLocTime[dNum] = startTime
    driverLocIdx[dNum] = 0
    
    # add position dot
    dPos = driverPosData[dNum][0]['position']
    dPosDot = visC.Dot("#"+driverData[dIdx]['team_colour'], "#FFF", REPLAY_MAP_INFO["dot-pos-size"], (int((dPos-1)/10)*REPLAY_MAP_INFO["x-pos-spacing"])+REPLAY_MAP_INFO["x-pos-offset"], (((dPos-1)%10)*REPLAY_MAP_INFO["y-pos-spacing"])+REPLAY_MAP_INFO["y-pos-offset"]+REPLAY_MAP_INFO["dot-pos-size"]*2)
    dPosText = visC.Text(driverData[dIdx]['name_acronym'], 100, (int((dPos-1)/10)*REPLAY_MAP_INFO["x-pos-spacing"])+REPLAY_MAP_INFO["x-pos-offset"]+(REPLAY_MAP_INFO["dot-pos-size"]*3), (((dPos-1)%10)*REPLAY_MAP_INFO["y-pos-spacing"])+REPLAY_MAP_INFO["y-pos-offset"], color="#FFF", autoSize=False, fontSize=15)
    
    cv.add_sprite(dPosDot, ["pos-dot"])
    cv.add_sprite(dPosText, ["pos-name-text"])
    driverPosDots[dNum] = dPosDot
    driverPosText[dNum] = dPosText
    driverPosTime[dNum] = startTime
    driverPosIdx[dNum] = 0

for p in range(20):
    posText = visC.Text(str(p)+".", 100, (int((p-1)/10)*REPLAY_MAP_INFO["x-pos-spacing"])+REPLAY_MAP_INFO["x-pos-offset"]-(REPLAY_MAP_INFO["dot-pos-size"]*6), (((p-1)%10)*REPLAY_MAP_INFO["y-pos-spacing"])+REPLAY_MAP_INFO["y-pos-offset"], color="#FFF", autoSize=False, fontSize=15)
    cv.add_sprite(posText)


currTime = startTime
### CODE END


def onKeyPress(event):
    cv.update_keyboard_input(event.keysym)
    
    ### CODE START - handle key presses
    # keyCodeText.change_text('You pressed %s\n' % event.keysym)
    # keyCodeText2.change_text(cv.get_text_input())
    ### CODE END

def get_mouse_coords(event):
    clickX = event.x
    clickY = event.y

    cv.update_mouse_click(clickX, clickY)
    ### CODE START - handle mouse click
    
    ### CODE END


def update():
    global currTime
    global timeText
    global driverNums

    global driverLocDots
    global driverLocTime
    global driverLocIdx

    global driverPosDots
    global driverPosText
    global driverPosTime
    global driverPosIdx
    ### CODE START - general update stuff
    if currTime < endTime:
        currTime += timedelta(milliseconds=int(1000/FPS))*TIMESCALE # update time

        # -- TODO check if locations or positions need to be updated
        for dNum in driverNums:
            if driverLocTime[dNum] != endTime and driverLocTime[dNum] < currTime:
                # Update!
                while driverLocTime[dNum] < currTime:
                    driverLocIdx[dNum] += 1
                    if driverLocIdx[dNum] >= len(driverLocData[dNum]):
                        driverLocIdx[dNum] = len(driverLocData[dNum])-1
                        driverLocTime[dNum] = endTime
                        break
                    driverLocTime[dNum] = datetime.fromisoformat(driverLocData[dNum][driverLocIdx[dNum]]['date'])
                dLoc = transform_locations([driverLocData[dNum][driverLocIdx[dNum]]['x'], driverLocData[dNum][driverLocIdx[dNum]]['y']], MAXCOORDS, MINCOORDS, [REPLAY_MAP_INFO["map-width"], REPLAY_MAP_INFO['map-height']])
                driverLocDots[dNum].change_pos(dLoc[0]+REPLAY_MAP_INFO["map-x-offset"], dLoc[1]+REPLAY_MAP_INFO["map-y-offset"])#, duration=FPS)
                
            if driverPosTime[dNum] != endTime and driverPosTime[dNum] < currTime:
                # Update!
                while driverPosTime[dNum] < currTime:
                    driverPosIdx[dNum] += 1
                    if driverPosIdx[dNum] >= len(driverPosData[dNum]):
                        driverPosIdx[dNum] = len(driverPosData[dNum])-1
                        driverPosTime[dNum] = endTime
                        print("AAA")
                        print(dNum)
                        break
                    driverPosTime[dNum] = datetime.fromisoformat(driverPosData[dNum][driverPosIdx[dNum]]['date'])
                dPos = driverPosData[dNum][0]['position']
                driverPosDots[dNum].change_pos((int((dPos-1)/10)*REPLAY_MAP_INFO["x-pos-spacing"])+REPLAY_MAP_INFO["x-pos-offset"], (((dPos-1)%10)*REPLAY_MAP_INFO["y-pos-spacing"])+REPLAY_MAP_INFO["y-pos-offset"]+REPLAY_MAP_INFO["dot-pos-size"]*2)#, duration=FPS)
                driverPosText[dNum].change_pos((int((dPos-1)/10)*REPLAY_MAP_INFO["x-pos-spacing"])+REPLAY_MAP_INFO["x-pos-offset"]+(REPLAY_MAP_INFO["dot-pos-size"]*3), (((dPos-1)%10)*REPLAY_MAP_INFO["y-pos-spacing"])+REPLAY_MAP_INFO["y-pos-offset"])#, duration=FPS)

        timeText.change_text(currTime.isoformat())

    ### CODE END

    cv.update()

    # Schedule the next frame
    canvas.after(int(1000/FPS), update)  # ~30 FPS

root.bind('<KeyPress>', onKeyPress)

update()
root.mainloop()