import networkx as nx
from djitellopy import Tello
import matplotlib.pyplot as plt
import pickle
import time
import pygame
import sys
import threading as th

#Internal Values
inAir = False
battLev = 0
orientation = "N"
currentmove = 1

#Settings
distancefromwall = 500 #mm
aligningDistance = 25 #cm
moveDistance = 60 #cm
sensortime = 0.5 #secs
rottime = 1 #secs
aligningTime = 1 #secs
maxheight = 100 #cm
minheight = 80 #cm
horizontalAligningSpeed = 10 #cm/s
verticalAligningSpeed = 30 #cm/s

#Discontinued
padHeightDiffAllowance = 40 
maintainheightupdatefreq = 5


#Initialisation
print("[SETUP] Setting Up...")
t = Tello()
t.connect()
t.enable_mission_pads()
#t.set_speed(90)
battLev = t.get_battery()
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Tello Command Centre')
pygame.mouse.set_visible(0)
map = nx.Graph()
print(f"[SETUP] Setup OK. Battery: {battLev}%")


#Functions
def getPadCoordinates():
    if t.get_mission_pad_distance_x != -100 or t.get_mission_pad_distance_x != -1:
        data = [t.get_mission_pad_distance_x(), t.get_mission_pad_distance_y(), t.get_mission_pad_distance_z()]
        print(f"[PAD] Pad Detected: {data}")
        return data
        
    else:
        print(f"[PAD] Pad not Detected!")
        return None

def stopMovement():
    t.send_rc_control(0,0,0,0)
    
def maintainHeight():
    print(f"[HEIGHT] 70cm")
    currentheight = t.get_height()
    desiredheight = (maxheight + minheight)/2
    print(currentheight)
    
    if currentheight > maxheight:
        t.send_rc_control(0, 0, -verticalAligningSpeed, 0)
        
    if currentheight < minheight:
        t.send_rc_control(0, 0, verticalAligningSpeed, 0)
        
    stop = th.Timer(2, stopMovement)
    stop.start()
    
    '''
    if currentheight > maxheight:
        t.move_down(20)
        currheight = t.get_height()
        print(f"[HEIGHT] {currentheight} | [CORR] {currentheight - currheight}")

    elif currentheight < minheight:
        t.move_up(20)
        currheight = t.get_height()
        print(f"[HEIGHT] Maintained: {currentheight} | [CORR] {-1 * (currentheight - currheight)}")
        
    else:
        print(f"[HEIGHT] Maintained: {currentheight} | [CORR] +0")
    '''
    #mh = th.Timer(maintainheightupdatefreq, maintainHeight)
    #mh.start()  
    
def aligntoPad():
    padCoords = getPadCoordinates()
    if padCoords != [-100, -100, -100]:
        x = padCoords[0]
        y = padCoords[1]
        z = padCoords[2]
        
        print(f"[PAD] Starting Alignment at: {padCoords}")
        x = 0
        #Aligning to X Axis
        while x < 0 and x <= 10:
            print("[PAD] Left Alignment")
            t.send_rc_control(-horizontalAligningSpeed, 0, 0, 0)
            #stop = th.Timer(1, stopMovement)
            #stop.start()
            x +=1
        x = 0
        while x > 0 and x <= 10:
            t.send_rc_control(horizontalAligningSpeed, 0, 0, 0)
            print("[PAD] Right Alignment")
            #stop = th.Timer(1, stopMovement)
            #stop.start()
            x +=1
        x = 0
        while y < 0 and x <= 10:
            t.send_rc_control(0, -horizontalAligningSpeed, 0, 0)
            print("[PAD] Backward Alignment")
            #stop = th.Timer(1, stopMovement)
            #stop.start()
            x +=1
        x = 0
        while y > 0 and x <= 10:
            t.send_rc_control(0, horizontalAligningSpeed, 0, 0)
            print("[PAD] Forward Alignment")
            #stop = th.Timer(1, stopMovement)
            #stop.start()
            x +=1
        x = 0
        stopMovement()
        print(f"[PAD] Finishing Alignment at: {padCoords}")
        
    else:
        print("[PAD] Pad not Detected!")  

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
        orientation = "W"
        
    else:
        orientation = "S"
    
    t.rotate_counter_clockwise(90)
    print(f"[YAW] Left 90 | Origin: {origin} | Final: {orientation}")

def backTrack():
    global orientation
    global inAir
    t.move_back(moveDistance)
    time.sleep(2)
    padData = getPadInfo()
    cont = True
    
    while cont:
        #insert if pad not detected try again & align code
        #str(padInfo.get("id")), type=padInfo.get("type"), bl=branchleft, br = branchright, mn = currentmove, o = orientation, m = action, lmove = <truefalse>
        padID = padData.get("id")
        dataBL = nx.get_node_attributes(map, "bl")
        dataBR = nx.get_node_attributes(map, "br")
        dataOr = nx.get_node_attributes(map, "o")
        dataAc = nx.get_node_attributes(map, "m")
        dataLm = nx.get_node_attributes(map, "lmove")
        dataRm = nx.get_node_attributes(map, "rmove")
        
        BLbranch = dataBL.get(str(padID))
        BRbranch = dataBR.get(str(padID))
        nodeOrient = dataOr.get(str(padID))
        nodeAction = dataAc.get(str(padID))
        nodeLeftMoved = dataLm.get(str(padID)) #if it has been to left, True, else false
        nodeRightMoved = dataRm.get(str(padID)) #if it has been to right, True, else false
        
        if nodeOrient != orientation: #First change orientation if not in correct orientation
            if nodeAction == "l":
                yawRight90()
                print(f"[BACK] Desired Orientation: {nodeOrient} |  Final: {orientation}")
                
            elif nodeAction == "r":
                yawLeft90()
                print(f"[BACK] Desired Orientation: {nodeOrient} |  Final: {orientation}")
                
            else:
                print(f"[BACK] Error! Orientation not matching original node??\n")
                t.land()
                inAir = False
            
        else:
            print(f"[BACK] Desired Orientation already reached!")
        
        #if there is only one branch 
        if (BLbranch == True and BRbranch == False) or (BLbranch == False and BRbranch == True) : 
           #go pack to previous orientation and move back (it should already be in the desired orientation)
            print("[BACK] Node Branches Available: 1")
            print("[BACK] Moving Back...")
            t.move_back(moveDistance)
        
        elif BLbranch == True and BRbranch == True: #if there are two branches
            #!! remember to code it such that it also remembers if it has done left and right and instead now go straight
            #get orientation and previous action? prolly go back to original orientation and do the opposite of previous action
                
            print("[BACK] Node Branches Available: 2")
            #turn left (left priority)
            
            if nodeLeftMoved == False:
                print(f"[BACK] Moving Left...")
                yawLeft90()
                t.move_forward(moveDistance)
                cont = False
                
            elif nodeLeftMoved == True and nodeRightMoved == False:
                print(f"[BACK] Left already mapped, Moving Right...")
                yawRight90()
                t.move_forward(moveDistance)
                cont = False
                
            #you dont need a nodeLeftMoved = False and nodeRightMoved = True as you already have left priority
            else:
                print(f"[BACK] Left and Right already mapped, Moving Back...")
                t.move_back(moveDistance)             
                
def getTOF():
    global inAir 
    data_return = t.send_command_with_return('EXT tof?')
    if "tof" in data_return:
        data = data_return.split()
        return_value = int(data[1])
        if return_value == 8190:
            return_value = 1000
            
       # print(f"[TOF] Returning Data: {return_value}")
        return return_value
        
    else:
        print("[TOF] Get unavailable!")
        t.land()
        inAir = False
        return None

def getPadInfo():
    padID = t.get_mission_pad_id()
    returndata = {}
    
    if padID != -1:
        if padID == 12:
            returndata["type"] = 'carpet'
            returndata["id"] = [t.get_mission_pad_distance_x(), t.get_mission_pad_distance_y(), t.get_mission_pad_distance_z()]
            returndata["debug"] = t.get_mission_pad_id()
        
        else:
            returndata["type"] = 'missionpad'
            returndata["id"] = padID
        
        return returndata
        
    else:
        print(f"[PAD] Pad not Detected!")
        return None
        #write code for aligning

def getWalls():
    leftwall = False
    rightwall = False
    frontwall = False
    returndata = [frontwall, leftwall, rightwall]
    
    frontvalue = getTOF()
    time.sleep(sensortime)
    
    yawLeft90()
    time.sleep(rottime)
    leftvalue = getTOF()
    time.sleep(sensortime)
    
    yawRight90()
    time.sleep(0.3)
    yawRight90() 
    time.sleep(rottime)
    rightvalue = getTOF()
    
    print(f"{frontvalue}, {leftvalue}, {rightvalue}")
    
    time.sleep(1)
    yawLeft90()
    
    #print(orientation)
    
    if frontvalue < distancefromwall:
        print("[WALL] Front Wall Detected")
        frontwall = True
        returndata[0] = frontwall
    
    if leftvalue < distancefromwall:
        print("[WALL] Left Wall Detected")
        leftwall = True
        returndata[1] = leftwall
        
    if rightvalue < distancefromwall:
        print("[WALL] Right Wall Detected")
        rightwall = True     
        returndata[2] = rightwall
    
    print(f"[WALL] Data: {returndata}")
    return returndata     
   
def alignMiddle():
    global orientation
    
    print("[ALI] Starting Alignment...")
    yawLeft90()
    time.sleep(1)
    distance = getTOF()
    print(f"[ALI] Distance from left wall: {distance}mm")
    time.sleep(1)
    
    if distance > 500:
        yawRight90()
        time.sleep(rottime)
        yawRight90()
        time.sleep(rottime)
        distance = getTOF()
        print(f"[ALI] Distance from right wall: {distance}mm")
        time.sleep(sensortime)
    
    if distance < aligningDistance*10+80:
        print(f"[ALI] Too Close... Aligning")
        t.move_back(20)
        
    if distance > aligningDistance*10+80:
        print(f"[ALI] Too Far... Aligning")
        t.move_forward(20)
        
    else:
        print("[ALI] No need for alignment")
        
    if orientation == "W":
        yawRight90()
        time.sleep(rottime)
        
    if orientation == "E":
        yawLeft90()
        time.sleep(rottime)

def getNextOrientation(action):
    global orientation
    
    if action == "l":
        if orientation == "N":
            orient = "W"
            
        elif orientation == "S":
            orient = "E"
            
        elif orientation == "E":
            orient = "W"
            
        else:
            orient = "S"
    
    elif action == 'r':
        if orientation == "N":
            orient = "E"
            
        elif orientation == "E":
            orient = "S"
            
        elif orientation == "S":
            orient = "W"
            
        else:
            orient = "N"
            
    else:
        orient = orientation
        
    return orient
            
def main():
    #Variables
    global battLev
    global orientation
    global currentmove
    global inAir
    
    action = ""
    actionCompleted = False
    lmove = False
    rmove = False
    currorientation = orientation
    battLev = t.get_battery()
    
    #Run
    print(f"\n[INFO] Move {currentmove} | Height {t.get_height()}cm | Orientation {orientation} | Battery {battLev}%")
    maintainHeight()
    
    #Getting Information
    walls = getWalls()
    padInfo = getPadInfo()
    print(f"[INFO] PAD | {padInfo}")
        
    if walls[1] == False:
        branchleft = False
    else:
        branchleft = True
    if walls[2] == False:
        branchright = False
    else:
        branchright = True
    
    if padInfo == None:
        print("[PAD] Not Detected, Adjusting Height!")
        maintainHeight()
        #align code
        
        padInfo = getPadInfo()
        
        if padInfo == None:
            t.land()
            inAir = False
    
    else: #if pad is found
        if walls[0] == False and walls[1] == False and walls[2] == False: #If there is no available path except backwards
            backTrack()
        
        if walls[0] == False: 
            if getNextOrientation(action) == "N": #If there is no front wall and going forward in N direction 
                print("[NAVI] Moving Forward")
                action = "f"
                t.move_forward(moveDistance)
                actionCompleted = True
            
            else: #Check for alternative actions
                #Check if any other actions are going N
                if (walls[1] == False and getNextOrientation("l") == "N"): #if no left walls and left turn = N
                    print("[NAVI] Moving Left instead of Forward")
                    action = "l"
                    yawLeft90()
                    t.move_forward(moveDistance)
                    actionCompleted = True

                elif (walls[2] == False and getNextOrientation("r") == "N"): #if no right walls and right turn = N
                    print("[NAVI] Moving Right instead of Forward")
                    action = "r"
                    yawRight90()
                    t.move_forward(moveDistance)
                    actionCompleted = True
                
                #Check if any other actions are NOT N
                elif walls[1] == False and getNextOrientation("l") != "S": #if no left walls and left turn != S
                    print("[NAVI] Moving Left instead of Forward")
                    action = "l"
                    yawLeft90()
                    t.move_forward(moveDistance)
                    actionCompleted = True
                    
                elif walls[2] == False and getNextOrientation("r") != "S": #if no right walls and right turn != S
                    print("[NAVI] Moving Right instead of Forward")
                    action = "r"
                    yawRight90()
                    t.move_forward(moveDistance)
                    actionCompleted = True   
                    
                else:
                    print("[NAVI] Moving Forward")
                    action = "f"
                    t.move_forward(moveDistance)
                    actionCompleted = True
                
        else: 
            if walls[1] == False: #If there is a front wall but no left wall
                action = "l"
                if getNextOrientation(action) == "N": #If turning left will result in a N direction, continue
                    print("[NAVI] Moving Left")
                    yawLeft90()
                    t.move_forward(moveDistance)
                    actionCompleted = True
                    
                else: #Find other alternatives
                    if (walls[2] == False and getNextOrientation("r") == "N"): #If turning right will result in a N direction
                        action = 'r'
                        print("[NAVI] Moving Right instead of Left")
                        yawRight90()
                        t.move_forward(moveDistance)
                        actionCompleted = True
                        
                    elif (walls[1] == False and getNextOrientation("l") != "S"): #If turning left will result in a non S direction
                        action = "l"
                        print("[NAVI] Moving Left")
                        yawLeft90()
                        t.move_forward(moveDistance)
                        actionCompleted = True
                        
                    elif (walls[2] == False and getNextOrientation("r") != "S"):#If turning right will result in a non S direction
                        action = 'r'
                        print("[NAVI] Moving Right instead of Left")
                        yawRight90()
                        t.move_forward(moveDistance)
                        actionCompleted = True
                        
                    else: #No choice but to move left
                        action = "l"
                        print("[NAVI] Moving Left")
                        yawLeft90()
                        t.move_forward(moveDistance)
                        actionCompleted = True
                            
            else: #If there is no front wall and left wall...
                if walls[2] == False:
                    print("[NAVI] Moving Right")
                    action = "r"
                    yawRight90()
                    t.move_forward(moveDistance)
              
        if action == "l":
            lmove = True     
            print(f"[DEBUG] Left Move: {lmove}")
            
        if action == "r":
            rmove = True
            print(f"[DEBUG] Right Move: {rmove}")
        
        map.add_node(str(padInfo.get("id")), type=padInfo.get("type"), bl=branchleft, br = branchright, mn = currentmove, o = currorientation, m = action, lmove = lmove, rmove = rmove)
        #Connect to previous node + other connecting code
        #beenleft code (make it such that diff options add nodes with diff atrributes)
        #remember to pickle dump!
        currentmove += 1
        
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
                
            if event.key == pygame.K_a:
                alignMiddle()
                
            if event.key == pygame.K_t and battLev > 20:
                t.takeoff()
                inAir = True
                
            if event.key == pygame.K_l:
                t.land()   
                inAir = False
                
            if event.key == pygame.K_1:
                aligntoPad()             

            if event.key == pygame.K_h:
                maintainHeight()
                
            if event.key == pygame.K_m:
                if mainRun == True:
                    mainRun = False
                    
                if mainRun == False:
                    mainRun = True
                
    if mainRun:
        main()

while True:
    run()