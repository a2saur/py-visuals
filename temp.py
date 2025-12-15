import tkinter as tk
from urllib.request import urlopen
import json
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageTk
import numpy as np
import random
import os
import time

WIDTH = 800
HEIGHT = 480

DOT_MAP_RADIUS = 5
DOT_POS_RADIUS = 5

dot_map_sizing = {
    "scale":300,
    "x":50,
    "y":125,
    "rotation":135
}

TIME_SCALE = 1
STOP = False

DRIVER_POS_DOT_INFO = {
    "x-start":500,
    "y-start":75,
    "x-spacing":125,
    "y-spacing":40,
    "rows":10,
}

mapInfo = {
    "Monaco":{"scale":0.37, "x":15, "y":75, "dot-rotation":-135, "dot-x":-130, "dot-y":-55, "dot-scale":360}
}

root = tk.Tk(screenName="F1 Display")
# root.configure(bg='#47484a') 
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#47484a")
canvas.pack()

def key_pressed(event, scale=1):
    global dot_map_sizing

    print("Key Pressed: "+event.keysym)
    if event.keysym == "Up":
        dot_map_sizing["y"] -= scale
    elif event.keysym == "Down":
        dot_map_sizing["y"] += scale
    elif event.keysym == "Left":
        dot_map_sizing["x"] -= scale
    elif event.keysym == "Right":
        dot_map_sizing["x"] += scale
    elif event.keysym == "equal":
        dot_map_sizing["scale"] += scale
    elif event.keysym == "minus":
        dot_map_sizing["scale"] -= scale
    
    print(dot_map_sizing)


class Dot():
    def __init__(self, color="white", outline="white", r=5, x=0, y=0):
        self.dot = canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=outline)
        self.r = r
        self.x = x
        self.y = y

        self.dX = 0
        self.dY = 0
        self.endChange = 0
        self.framesPassed = 0

        self.targetR = 0
        self.dR = 0

        self.wait = 0
    
    def delay(self, delayAmount):
        self.wait = delayAmount
    
    def change_pos(self, newX, newY, duration=0):
        if duration == 0:
            self.x = newX
            self.y = newY
            canvas.coords(self.dot, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
        else:
            self.endChange = duration
            self.framesPassed = 0
            self.dX = (newX-self.x)/duration
            self.dY = (newY-self.y)/duration
    
    def change_size(self, newR, duration=0):
        if duration == 0:
            self.r = newR
            canvas.coords(self.dot, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
        else:
            self.targetR = newR
            self.dR = (self.targetR-self.r)/duration

    def change_color(self, newColor):
        canvas.itemconfig(self.dot, fill=newColor)
    
    def update(self):
        if self.wait > 0:
            self.wait -= 1
        else:
            if self.dX != 0 or self.dY != 0:
                self.framesPassed += 1

                self.change_pos(self.x+self.dX, self.y+self.dY)

                if self.framesPassed >= self.endChange:
                    self.dX = 0
                    self.dY = 0
            
            if self.dR != 0:
                if abs(self.targetR-self.r) <= abs(self.dR*2):
                    self.dR = 0
                    self.change_size(self.targetR)
                else:
                    self.change_size(self.r+self.dR)

class Text():
    def __init__(self, text, x=0, y=0, font=("Calibri", 50), color="#000000", justify="left", autoSize=True, width=WIDTH, maxHeight=100):
        # TODO work in auto sizing
        # self.label = tk.Label(root, font=("Calibri", 50), background="#1192a6", foreground="black") #CHANGE
        # self.label.pack(anchor="center") #CHANGE
        self.label = canvas.create_text(x, y, fill=color, font=font, text=text, justify=justify, width=width, anchor="nw")

        self.text = text
        self.x = x
        self.y = y

        self.dX = 0
        self.dY = 0
        self.endChange = 0
        self.framesPassed = 0

        self.dChars = 0
        self.targetText = ""
        self.deletingChars = True
        self.charIdx = 0

        self.wait = 0

        self.autoSize = autoSize
    
    def delay(self, delayAmount):
        self.wait = delayAmount
    
    def change_pos(self, newX, newY, duration=0):
        if duration == 0:
            self.x = newX
            self.y = newY
            canvas.coords(self.label, self.x, self.y)
        else:
            self.endChange = duration
            self.framesPassed = 0
            self.dX = (newX-self.x)/duration
            self.dY = (newY-self.y)/duration
    
    def change_text(self, newText, duration=0):
        if duration == 0:
            self.text = newText
            canvas.itemconfig(self.label, text=newText)
        else:
            self.dChars = (len(newText)+len(self.text))/duration
            self.targetText = newText
            self.deletingChars = True
            self.charIdx = len(self.text)

    def change_color(self, newColor):
        canvas.itemconfig(self.label, fill=newColor)
        
    def change_font(self, newFont):
        canvas.itemconfig(self.label, font=newFont)
    
    def update(self):
        if self.wait > 0:
            self.wait -= 1
        else:
            if self.dX != 0 or self.dY != 0:
                self.framesPassed += 1

                self.change_pos(self.x+self.dX, self.y+self.dY)

                if self.framesPassed >= self.endChange:
                    self.dX = 0
                    self.dY = 0

            if self.dChars != 0:
                if self.deletingChars:
                    if len(self.text) <= self.dChars:
                        self.deletingChars = False
                        self.change_text("")
                    else:
                        self.charIdx -= self.dChars
                        self.change_text(self.text[:int(self.charIdx)])
                else:
                    self.charIdx += self.dChars
                    if self.charIdx >= len(self.targetText):
                        self.dChars = 0
                        self.change_text(self.targetText)
                    else:
                        self.change_text(self.targetText[:int(self.charIdx)])

def read_file(filePath):
    if os.path.exists(filePath):
        file = open(filePath, "r")
        data = file.read()
        file.close()
        return data
    else:
        return -1

def write_file(filePath, content):
    file = open(filePath, "w")
    file.write(content)
    file.close()

def scale_coord(coord, idx):
    global MAXCOORDS
    global MINCOORDS

    global dot_map_sizing

    newVal = (coord-MINCOORDS[idx])/(MAXCOORDS[idx]-MINCOORDS[idx])
    if idx == 0:
        aspect_ratio = (MAXCOORDS[0]-MINCOORDS[0])/(MAXCOORDS[1]-MINCOORDS[1]) # w/h
        newVal *= dot_map_sizing["scale"] * aspect_ratio * -1
        # newVal += dot_map_sizing["x"]
    elif idx == 1:
        newVal *= dot_map_sizing["scale"]
        # newVal += dot_map_sizing["y"]

    return newVal

# point needs to be [x, y]
def rotate_point(point, center=(150, 150)):
    center = dot_map_sizing["x"]+(dot_map_sizing["scale"]/2)
    center = dot_map_sizing["y"]+(dot_map_sizing["scale"]/2)
    angle = np.radians(dot_map_sizing["rotation"])
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])
    
    # Step 1: translate so center is origin
    translated = np.array(point) - np.array(center)
    
    # Step 2: rotate
    rotated = rotation_matrix @ translated
    
    # Step 3: translate back
    return rotated + np.array(center)

def DEBUG(toPrint, on=True):
    if on:
        print(toPrint)

def f1_setup_race(session_key=-1):
    global f1Data
    global f1DriverData
    global f1DriverPositionData
    global f1DriverLocationData

    global f1DriverLocationIdx
    global f1DriverPositionIdx

    global f1Sprites
    global f1PositionSprites
    global f1LocationSprites
    
    global f1RaceTitle
    global f1RaceSubtitle
    global f1RaceTimeSubtitle

    global MAXCOORDS
    global MINCOORDS

    global mapImg
    global mapImgObj
    global dot_map_sizing

    f1DriverData = {}
    f1DriverPositionData = {}
    f1DriverLocationData = {}
    f1PositionSprites = {}
    f1LocationSprites = {}

    # --- get session key ---
    if session_key == -1:
        # f1Data["session-key"] = random.randrange(1, 9928)
        f1Data["session-key"] = 9971
    else:
        f1Data["session-key"] = session_key
    DEBUG("Session: "+str(f1Data["session-key"]))

    # --- get the session data ---
    data = read_file("saved_sessions/"+str(f1Data["session-key"])+"-session_info.txt")
    if data == -1:
        DEBUG("Fetching session-info")
        response = urlopen('https://api.openf1.org/v1/sessions?session_key='+str(f1Data["session-key"]))
        print('https://api.openf1.org/v1/sessions?session_key='+str(f1Data["session-key"]))
        session_info = json.loads(response.read().decode('utf-8'))
        session_info = session_info[0]
        write_file("saved_sessions/"+str(f1Data["session-key"])+"-session_info.txt", str(session_info))
        f1Data["session-info"] = session_info
    else:
        f1Data["session-info"] = eval(data)
    
    # --- ADD TITLE AND SUBTITLE ---
    # Hungaroring - Budapest, Hungary
    title = ""
    title += f1Data["session-info"]["circuit_short_name"] # Hungaroring
    title += " - "
    title += f1Data["session-info"]["location"] # Budapest
    title += ", "
    title += f1Data["session-info"]["country_name"] # Hungary
    f1RaceTitle.change_text(title, 25)

    # Race on 10/10/2025 or whatever
    subtitle = ""
    subtitle += f1Data["session-info"]["session_type"] # Race or 'session_name' idk which to use
    subtitle += " on "
    eventDate = datetime.fromisoformat(f1Data["session-info"]["date_start"]) # 2025-08-03T13:00:00+00:00
    subtitle += ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][eventDate.month-1]
    subtitle += " "
    subtitle += str(eventDate.day)
    subtitle += ", "
    subtitle += str(eventDate.year)
    f1RaceSubtitle.delay(25)
    f1RaceSubtitle.change_text(subtitle, 25)

    # --- get the drivers data ---
    data = read_file("saved_sessions/"+str(f1Data["session-key"])+"-drivers.txt")
    if data == -1:
        DEBUG("Fetching driver info")
        response = urlopen('https://api.openf1.org/v1/drivers?session_key='+str(f1Data["session-key"]))
        data = json.loads(response.read().decode('utf-8'))
        write_file("saved_sessions/"+str(f1Data["session-key"])+"-drivers.txt", str(data))
        f1DriverData = data
    else:
        f1DriverData = eval(data)

    # --- get the race driver location and position data ---
    all_locations = []
    for driverInfo in f1DriverData:
        driverNum = driverInfo["driver_number"]
        data = read_file("saved_sessions/"+str(f1Data["session-key"])+"-driver_position-"+str(driverNum)+".txt")
        if data == -1:
            DEBUG("Fetching driver position for "+str(driverNum))
            response = urlopen("https://api.openf1.org/v1/position?session_key="+str(f1Data["session-key"])+"&driver_number="+str(driverNum))
            data = json.loads(response.read().decode('utf-8'))
            write_file("saved_sessions/"+str(f1Data["session-key"])+"-driver_position-"+str(driverNum)+".txt", str(data))
            f1DriverPositionData[str(driverNum)] = data
            time.sleep(30)
        else:
            f1DriverPositionData[str(driverNum)] = eval(data)

        
        data = read_file("saved_sessions/"+str(f1Data["session-key"])+"-driver_location-"+str(driverNum)+".txt")
        if data == -1:
            DEBUG("Fetching driver location for "+str(driverNum))
            response = urlopen("https://api.openf1.org/v1/location?session_key="+str(f1Data["session-key"])+"&driver_number="+str(driverNum))
            data = json.loads(response.read().decode('utf-8'))
            write_file("saved_sessions/"+str(f1Data["session-key"])+"-driver_location-"+str(driverNum)+".txt", str(data))
            f1DriverLocationData[str(driverNum)] = data
            time.sleep(30)
        else:
            f1DriverLocationData[str(driverNum)] = eval(data)
        all_locations += f1DriverLocationData[str(driverNum)]
    
    x_vals = [p["x"] for p in all_locations]
    y_vals = [p["y"] for p in all_locations]
    z_vals = [p["z"] for p in all_locations]

    MAXCOORDS = [max(x_vals), max(y_vals), max(z_vals)]
    MINCOORDS = [min(x_vals), min(y_vals), min(z_vals)]

    # --- add background image ---
    tempInfo = mapInfo[f1Data["session-info"]["location"]]
    image_path = f1Data["session-info"]["location"]+"-map.png"  # Replace with your image path
    original_image = Image.open(image_path)
    w, h = original_image.size
    original_image = original_image.resize((int(w*tempInfo["scale"]), int(h*tempInfo["scale"])), Image.Resampling.LANCZOS)
    mapImg = ImageTk.PhotoImage(original_image)
    mapImgObj = canvas.create_image(tempInfo["x"], tempInfo["y"], image=mapImg, anchor="nw")
    dot_map_sizing["rotation"] = tempInfo["dot-rotation"]
    dot_map_sizing["x"] = tempInfo["dot-x"]
    dot_map_sizing["y"] = tempInfo["dot-y"]
    dot_map_sizing["scale"] = tempInfo["dot-scale"]

    # --- make dots and visuals ---
    f1DriverLocationIdx = {}
    f1DriverPositionIdx = {}
    posDotX = DRIVER_POS_DOT_INFO["x-start"]
    posDotY = DRIVER_POS_DOT_INFO["y-start"]
    posDotCount = 0
    for driverInfo in f1DriverData:
        driverNum = driverInfo["driver_number"]
        f1DriverLocationIdx[str(driverNum)] = 0
        f1DriverPositionIdx[str(driverNum)] = 0

        posDotCount += 1

        xSpot = int((f1DriverPositionData[str(driverNum)][0]["position"]-1)/DRIVER_POS_DOT_INFO["rows"]) # for y positon
        ySpot = (f1DriverPositionData[str(driverNum)][0]["position"]-1)%DRIVER_POS_DOT_INFO["rows"] # for y positon
        xPos = DRIVER_POS_DOT_INFO["x-start"]+(xSpot*DRIVER_POS_DOT_INFO["x-spacing"])
        yPos = DRIVER_POS_DOT_INFO["y-start"]+(ySpot*DRIVER_POS_DOT_INFO["y-spacing"])
        
        if posDotCount < 10:
            place = Text(" "+str(posDotCount)+". ", posDotX, posDotY, ("Rockwell", 15), "#FFFFFF", autoSize=False)
        else:
            place = Text(str(posDotCount)+". ", posDotX, posDotY, ("Rockwell", 15), "#FFFFFF", autoSize=False)
        posDot = Dot("#"+driverInfo["team_colour"], "#"+driverInfo["team_colour"], DOT_POS_RADIUS, xPos+40, yPos+10)
        name = Text(driverInfo["name_acronym"], xPos+70, yPos, ("Times", 15), "#FFFFFF", autoSize=False)
        # posDot = Dot("#"+driverInfo["team_colour"], "#"+driverInfo["team_colour"], 10, posDotX+40, posDotY+10)
        # name = Text(driverInfo["name_acronym"], posDotX+70, posDotY, ("Times", 15), "#FFFFFF", autoSize=False)
        
        posDotY += DRIVER_POS_DOT_INFO["y-spacing"]
        if posDotCount % DRIVER_POS_DOT_INFO["rows"] == 0:
            posDotY = DRIVER_POS_DOT_INFO["y-start"]
            posDotX += DRIVER_POS_DOT_INFO["x-spacing"]
        
        f1PositionSprites[str(driverNum)] = [posDot, name]
        f1Sprites.append(place)
        f1Sprites.append(posDot)
        f1Sprites.append(name)

        point = rotate_point([scale_coord(f1DriverLocationData[str(driverNum)][0]["x"], 0), scale_coord(f1DriverLocationData[str(driverNum)][0]["y"], 1)])
        point[0] += dot_map_sizing["x"]
        point[1] += dot_map_sizing["y"]
        locDot = Dot("#"+driverInfo["team_colour"], "#"+driverInfo["team_colour"], DOT_MAP_RADIUS, point[0], point[1])
        f1Sprites.append(locDot)
        f1LocationSprites[str(driverNum)] = locDot


def f1_update():
    global f1Data
    global f1DriverData
    global f1DriverPositionData
    global f1DriverLocationData

    global f1DriverLocationIdx
    global f1DriverPositionIdx

    global f1Sprites
    global f1PositionSprites
    global f1LocationSprites
    
    global f1RaceTitle
    global f1RaceSubtitle

    global f1Timestamp
    global STOP

    if f1Data["raceSetup"]:
        f1_setup_race()
        f1Timestamp = datetime.fromisoformat(f1Data["session-info"]["date_start"])
        f1Data["raceSetup"] = False
    
    # f1Timestamp += timedelta(microseconds=32*TIME_SCALE)
    f1Timestamp += timedelta(seconds=0.5)
    f1RaceTimeSubtitle.change_text(f1Timestamp.strftime("%H:%M:%S, %m/%d/%Y"))
    
    for sprite in f1Sprites:
        sprite.update()
        
    for driverInfo in f1DriverData:
        driverNum = driverInfo["driver_number"]
        if f1DriverLocationIdx[str(driverNum)] != -1:
            currentLocationData = f1DriverLocationData[str(driverNum)][f1DriverLocationIdx[str(driverNum)]]
            # --- check location change ---
            changed = False
            while datetime.fromisoformat(currentLocationData["date"]) < f1Timestamp:
                f1DriverLocationIdx[str(driverNum)] += 1
                try:
                    currentLocationData = f1DriverLocationData[str(driverNum)][f1DriverLocationIdx[str(driverNum)]]
                    changed = True
                except IndexError:
                    DEBUG("Out of range for driver "+str(driverNum)+": "+str(f1DriverLocationData[str(driverNum)][-1]))
                    f1DriverLocationIdx[str(driverNum)] = -1
                    f1LocationSprites[str(driverNum)].change_pos(0, HEIGHT, 10)
                    break
            if changed:
                point = rotate_point([scale_coord(currentLocationData["x"], 0), scale_coord(currentLocationData["y"], 1)])
                point[0] += dot_map_sizing["x"]
                point[1] += dot_map_sizing["y"]
                f1LocationSprites[str(driverNum)].change_pos(point[0], point[1])
        if f1DriverPositionIdx[str(driverNum)] != -1:
            # --- check position change ---
            try:
                if datetime.fromisoformat(f1DriverPositionData[str(driverNum)][f1DriverPositionIdx[str(driverNum)]+1]["date"]) < f1Timestamp:
                    f1DriverPositionIdx[str(driverNum)] += 1
                    newPositionData = f1DriverPositionData[str(driverNum)][f1DriverPositionIdx[str(driverNum)]]

                    xSpot = int((newPositionData["position"]-1)/DRIVER_POS_DOT_INFO["rows"]) # for y positon
                    ySpot = (newPositionData["position"]-1)%DRIVER_POS_DOT_INFO["rows"] # for y positon
                    xPos = DRIVER_POS_DOT_INFO["x-start"]+(xSpot*DRIVER_POS_DOT_INFO["x-spacing"])
                    yPos = DRIVER_POS_DOT_INFO["y-start"]+(ySpot*DRIVER_POS_DOT_INFO["y-spacing"])
                    f1PositionSprites[str(driverNum)][0].change_pos(xPos+40, yPos+10, 10)
                    f1PositionSprites[str(driverNum)][1].change_pos(xPos+70, yPos, 10)
            except IndexError:
                DEBUG("Out of range (position) for driver "+str(driverNum)+": "+str(f1DriverPositionData[str(driverNum)][-1]))
                f1DriverPositionIdx[str(driverNum)] = -1
                f1PositionSprites[str(driverNum)][0].change_pos(0, HEIGHT, 5)
                f1PositionSprites[str(driverNum)][0].change_color("#FFFFFF")
                f1PositionSprites[str(driverNum)][1].change_pos(0, HEIGHT, 5)

def update():
    f1_update()

    # Schedule the next frame
    # canvas.after(16, update)  # ~60 FPS
    canvas.after(32, update)  # ~30 FPS

f1Data = {
    "raceSetup":True,
    "session-key":-1,
    "session-info":{},
}

f1Sprites = []

# TODO resize text based on the length and font
f1RaceTitle = Text("", 25, 25, font=("Rockwell", 25), color="#FFFFFF", width=WIDTH, autoSize=True, maxHeight=25)
f1RaceSubtitle = Text("", 25, 60, font=("Rockwell", 15), color="#FFFFFF", width=int(WIDTH*0.75), autoSize=True)
f1RaceTimeSubtitle = Text("", 25, HEIGHT-50, font=("Times", 15), color="#FFFFFF", width=int(WIDTH*0.75), autoSize=True)
f1Sprites.append(f1RaceTitle)
f1Sprites.append(f1RaceSubtitle)
f1Sprites.append(f1RaceTimeSubtitle)

# Bind key presses to the root window
root.bind("<Key>", key_pressed)

# Make sure the root window has focus
root.focus_force()  # forces the window to take focus

update()


root.mainloop()