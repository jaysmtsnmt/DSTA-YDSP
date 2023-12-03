from djitellopy import Tello
import networkx as nx
import pickle
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import pygame
import sys
from colorama import Fore
import threading as th
from keras.models import load_model

# TensorFlow is required for Keras to work
#Internal Values
inAir = False
battLev = 0
orientation = "N"
currentmove = 1
previousnode = 0
mapdata = {}
currpadCoords = 0
startingpadCoords = 3
previousBranchedNode = 0
backTracked = False
missionPads = {}
medicPads = {}

#Settings
distancefromwall = 700 #mm (at which point is it counted as a wall ) might need to change it to 650 for competition
tooClose = 170 #mm (at which point is the wall too close? for wall adjustment)
moveDistance = 55 #ctm
sensortime = 0.5 #secs
rottime = 1 #secs
aligningTime = 1 #secs
maxheight = 85 #cm
minheight = 75 #cm
pauseTime = 3
horizontalAligningSpeed = 10 #cm/s
verticalAligningSpeed = 30 #cm/s
MAPFILEPATH = r'C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapgraph.txt'
MAPDATAPATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapdata.txt"
LOCATIONPATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\speciallocations.txt"

#Initialisation
print("[SETUP] Setting Up...")
t = Tello()
t.connect()
t.streamon()
t.enable_mission_pads()
#t.set_speed(90)
battLev = t.get_battery()
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Tello Command Centre')
pygame.mouse.set_visible(0)
map = nx.Graph()
currpadCoords = startingpadCoords
previousnode = startingpadCoords

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)
model = load_model("keras_Model.h5", compile=False) #load the trained model
class_names = open("labels.txt", "r").readlines()
print(f"[SETUP] Setup OK. Battery: {battLev}%")

mapgraphfile = open(MAPFILEPATH, "rb")
mapdatafile = open(MAPDATAPATH, "rb")
specialLocationsfile = open(LOCATIONPATH, "rb")

map = pickle.load(mapgraphfile)
mapdata = pickle.load(mapdatafile)
specialLocations = pickle.load(specialLocationsfile)

mapgraphfile.close()
mapdatafile.close()
specialLocationsfile.close()

print(f"[LOAD] Loading data from file...")
print(Fore.RESET + Fore.RED + f"[CHECK] Current Coordinate: {currpadCoords}" + Fore.RESET)
print(f"[LOAD] Map: {nx.nodes(map)}")
print(f"[LOAD] Map Data: {mapdata}")
print(f"[LOAD] Locations: {specialLocations}")

print(f"[SETUP] Setup OK. Battery: {battLev}%")


def getPadInfo():
    global currpadCoords
    padID = t.get_mission_pad_id()
    returndata = {}
    
    if padID != -1:
        if padID == 12:
            returndata["type"] = 'carpet'
            returndata["id"] = currpadCoords
            returndata["debug"] = t.get_mission_pad_id()
        
        else:
            returndata["type"] = 'missionpad'
            returndata["id"] = int(padID)
        
        return returndata
        
    else:
        print(f"[PAD] Pad not Detected!")
        return None
        #write code for aligning

def stopMovement():
    t.send_rc_control(0,0,0,0)

def maintainHeight():
    currentheight = t.get_height()
    print(f"[HEIGHT] Maintaining Height Range: {minheight}cm - {maxheight}cm")

    if currentheight > maxheight:
        print(f"[HEIGHT] Too High | Diff: {currentheight - maxheight}")
        t.send_rc_control(0, 0, -verticalAligningSpeed, 0)
        
    if currentheight < minheight:
        print(f"[HEIGHT] Too Low | Diff: {minheight - currentheight}")
        t.send_rc_control(0, 0, verticalAligningSpeed, 0)
        
    stop = th.Timer(2, stopMovement)
    stop.start()
    
def yawRight90():
    global orientation
    origin = orientation
        
    if orientation == "N":
        orientation = "E"
        
    elif orientation == "E":
        orientation = "S"
        
    elif orientation == "S":
        orientation = "W"
        
    else:
        orientation = "N"
        
    t.rotate_clockwise(90)
    print(f"[YAW] Right 90 | Origin: {origin} | Final: {orientation}")
    
def yawLeft90():
    global orientation
    origin = orientation
    
    if orientation == "N":
        orientation = "W"
        
    elif orientation == "S":
        orientation = "E"
        
    elif orientation == "E":
        orientation = "N"
        
    else:
        orientation = "S"
    
    t.rotate_counter_clockwise(90)
    print(f"[YAW] Left 90 | Origin: {origin} | Final: {orientation}")

def updatePadID(backwards=False): #updating padID will also update the previous node
    global currpadCoords
    global orientation
    global previousnode
    
    previousnode = currpadCoords
    
    if backwards == True:
        #print(f"[PAD] Backwards is True!")
        if orientation == "N":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords - 5}")
            currpadCoords -= 5
            
        elif orientation == "E":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords - 1}")
            currpadCoords -= 1
            
        elif orientation == "S":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords + 5}")
            currpadCoords += 5
            
        elif orientation == "W":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords + 1}")
            currpadCoords += 1
    
    else: 
        if orientation == "N":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords + 5}")
            currpadCoords += 5
            
        elif orientation == "E":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords + 1}")
            currpadCoords += 1
            
        elif orientation == "S":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords - 5}")
            currpadCoords -= 5
            
        elif orientation == "W":
            print(f"[PAD] Old PadID: {currpadCoords} | New PadID: {currpadCoords - 1}")
            currpadCoords -= 1

    print(f"[DEBUG] Check: Previous Node should be DIFFERENT from new node!")
    print(f"[PAD] Updated PadCoord | Previous Node: {previousnode} | New Node: {currpadCoords}")

def main():
    global battLev
    global orientation
    global currentmove
    global inAir
    global previousnode
    global mapdata
    global currpadCoords
    global backTracked
    global specialLocations
    
    battLev = t.get_battery()
    
    #Run
    print(f"\n[MAIN] Move {currentmove} | Height {t.get_height()}cm | Orientation {orientation} | Battery {battLev}%")
    maintainHeight()
    
    padInfo = getPadInfo()
    
    #First, Get if the current pad is a missionpad!
    if padInfo.get("type") == "missionpad":
        if padInfo.get("id") > 2 and padInfo.get("id") < 6:
            print(f"[PAD] Special Pad detected! Mission Pad: {padInfo.get('id')}")
            specialLocations[currpadCoords] = padInfo.get("id") #Store as dictionary with node as identifier
            print(f"[PAD] Special Locations Found: {specialLocations}")
            
        else:
            print("[PAD] Mission Pad detected, but it is not a location!")
            
    
    
    map.nodes()

mainRun = False 
def run():
    global battLev
    global mainRun
    global inAir
    
    battLev = t.get_battery()
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            if event.key == pygame.K_t and battLev > 10:
                t.takeoff()
                inAir = True
                
            if event.key == pygame.K_l:
                t.land()   
                inAir = False
                
            if event.key == pygame.K_m:
                if mainRun == True:
                    mainRun = False
                    
                if mainRun == False:
                    mainRun = True
                
    if mainRun:
        main()

while True:
    run()

