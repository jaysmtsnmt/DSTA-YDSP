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
previousnode = 0
mapdata = {}
currpadCoords = 0
startingpadCoords = 3

#Settings
distancefromwall = 700 #mm
aligningDistance = 25 #cm
tooClose = 150
moveDistance = 55 #ctm
sensortime = 0.5 #secs
rottime = 1 #secs
aligningTime = 1 #secs
maxheight = 85 #cm
minheight = 75 #cm
horizontalAligningSpeed = 10 #cm/s
verticalAligningSpeed = 30 #cm/s
MAPFILEPATH = r'C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapgraph.txt'
MAPDATAPATH = r"C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\mapdata.txt"

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
currpadCoords = startingpadCoords
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
    #print(currentheight)
    
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
        orientation = "N"
        
    else:
        orientation = "S"
    
    t.rotate_counter_clockwise(90)
    print(f"[YAW] Left 90 | Origin: {origin} | Final: {orientation}")

def updatePadID(backwards=False):
    global currpadCoords
    global orientation
    
    if backwards == True:
        print(f"[PAD] Backwards is True!")
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
        
    
def backTrack():
    global orientation
    global inAir
    global previousnode
    global mapdata
    global currpadCoords
    global mapdata
    
    t.move_back(moveDistance)
    updatePadID(backwards=True)
    
    padData = getPadInfo()
    cont = True
    minicont = True
    
    while cont:
        print("\n")
        while minicont:
            padData = getPadInfo()
            minicont = False
            #insert if pad not detected try again & align code
            #str(padInfo.get("id")), type=padInfo.get("type"), bl=branchleft, br = branchright, mn = currentmove, o = orientation, m = action, lmove = <truefalse>
            padID = padData.get("id")
            print(f"[DEBUG] BACK PadID: {padID}")

            try:
                nodedata = mapdata.get(padID)
                BLbranch = nodedata.get("bl")
                BRbranch = nodedata.get("br")
                BFbranch = nodedata.get("bf")
                nodeOrient = nodedata.get("o")
                nodeAction = nodedata.get("m")
                nodeLeftMoved = nodedata.get('lmove') #if it has been to left, True, else false
                nodeRightMoved = nodedata.get("rmove") #if it has been to right, True, else false
                nodeForwardMoved = nodedata.get("fmove")
                
            except AttributeError:
                print("[BACK] Not Mapped, Exiting.")
                cont = False
                minicont = False
                break
            
            if nodeOrient != orientation: #First change orientation if not in correct orientation
                print(f"[DEBUG] Original Orientation: {nodeOrient} | Current: {orientation} | Action: {nodeAction}")
                
                if nodeAction == "l":
                    print(f"[DEBUG] Original Node Action: {nodeAction}")
                    yawRight90()
                    print(f"[BACK] Desired Orientation: {nodeOrient} |  Final: {orientation}")
                    
                elif nodeAction == "r":
                    print(f"[DEBUG] Original Node Action: {nodeAction}")
                    yawLeft90()
                    print(f"[BACK] Desired Orientation: {nodeOrient} |  Final: {orientation}")
                
                '''
                else:
                    print(f"[BACK] Error! Orientation not matching original node??\n")
                    t.land()
                    inAir = False
                '''    
                
            else:
                print(f"[BACK] Desired Orientation already reached!")
            
            #If there are no branches
            if (BLbranch == False and BRbranch == False and BFbranch == False):
                print("[BACK] No Node Branches Available")
                print("[BACK] Moving Back")
                previousnode = padID
                t.move_back(moveDistance)
                updatePadID(backwards=True)
                time.sleep(4)
                minicont = True
            
            #if there is only one branch 
            elif (BLbranch == True and BRbranch == False and BFbranch == True) or (BLbranch == False and BRbranch == True and BFbranch == True):
            #go pack to previous orientation and move back (it should already be in the desired orientation)
                print("[BACK] Node Branches Available: 1")
                
                if (BRbranch == True):
                    yawRight90()
                    t.move_forward(moveDistance)
                    updatePadID(backwards=False)
                    time.sleep(4)
                    minicont = True
                    cont = True
                    
                elif (BFbranch == True):
                    yawLeft90()
                    t.move_forward(moveDistance)
                    updatePadID(backwards=False)
                    time.sleep(4)
                    minicont = True
            
            #if there are two branches
            elif BLbranch == True and BRbranch == True and BFbranch == True:
                #[DONE] remember to code it such that it also remembers if it has done left and right and instead now go straight
                #get orientation and previous action? prolly go back to original orientation and do the opposite of previous action
                print("[BACK] Node Branches Available: 2")
                #turn left (left priority)
                previousnode = padID
                
                if nodeLeftMoved == False:
                    print(f"[BACK] Moving Left...")
                    yawLeft90()
                    t.move_forward(moveDistance)
                    updatePadID()
                    cont = False
                    time.sleep(4)
                    minicont = True
                    
                elif nodeLeftMoved == True and nodeRightMoved == False:
                    print(f"[BACK] Left already mapped, Moving Right...")
                    yawRight90()
                    t.move_forward(moveDistance)
                    updatePadID()
                    cont = False
                    time.sleep(4)
                    minicont = False
                    
                #you dont need a nodeLeftMoved = False and nodeRightMoved = True as you already have left priority
                else:
                    print(f"[BACK] Left and Right already mapped, Moving Back...")
                    t.move_back(moveDistance)  
                    updatePadID(backwards=True)      
                    
            else:
                print("[ERROR] you did not account for one of the options ")
                    
        #checking if mapped
        check = mapdata.get(currpadCoords)
        
        if check == None:
            print(f"[BACK] Current Pad is Unmapped, stopping backtracking!")
            cont = False
            minicont = False
            break
            
        else:
            pass
                
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
            returndata["id"] = padID
        
        return returndata
        
    else:
        print(f"[PAD] Pad not Detected!")
        return None
        #write code for aligning

def align():
    print("[ALIGN] Aligning")
    walls = getWalls()
    
    if walls[0] == True:
        print("[ALIGN] Aligning with Front wall")
        t.send_rc_control(0, horizontalAligningSpeed, 0, 0)
        time.sleep(3)
        t.move_back(30)
        
    elif walls[1] == True:
        print("[ALIGN] Aligning with Left wall")
        t.send_rc_control(-horizontalAligningSpeed, 0, 0, 0)
        time.sleep(3)
        t.move_back(30)
        
    elif walls[2] == True:
        print("[ALIGN] Aliging with Right wall")
        t.send_rc_control(horizontalAligningSpeed, 0, 0, 0, 0)
        time.sleep(3)
        t.move_back(30)
        
    else:
        print("[ALIGN] No wall to align with.")

def getWalls():
    leftwall = False
    rightwall = False
    frontwall = False
    returndata = [frontwall, leftwall, rightwall]
    
    frontvalue = getTOF()
    time.sleep(sensortime)
    if frontvalue < tooClose:
        print("[ADJ] Too Close, Moving Back...")
        t.move_back(20)
        time.sleep(aligningTime)
    
    yawLeft90()
    time.sleep(rottime)
    leftvalue = getTOF()
    time.sleep(sensortime)
    if leftvalue < tooClose:
        print("[ADJ] Too Close, Moving Back...")
        t.move_back(20)
        time.sleep(aligningTime)
        
    
    yawRight90()
    time.sleep(0.3)
    yawRight90() 
    time.sleep(rottime)
    rightvalue = getTOF()
    if rightvalue < tooClose:
        print("[ADJ] Too Close, Moving Back...")
        t.move_back(20)
        time.sleep(aligningTime)
        
    #print(f"{frontvalue}, {leftvalue}, {rightvalue}")
    
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
    global previousnode
    global mapdata
    global currpadCoords
    
    action = ""
    actionCompleted = False
    lmove = False
    rmove = False
    fmove = False
    currorientation = orientation
    battLev = t.get_battery()
    nodedata = {}
    previousnode = currpadCoords
    
    #Run
    print(f"\n[INFO] Move {currentmove} | Height {t.get_height()}cm | Orientation {orientation} | Battery {battLev}%")
    maintainHeight()
    
    #Getting Information
    walls = getWalls()
    padInfo = getPadInfo()
    print(f"[INFO] PAD | {padInfo}")
        
    if walls[0] == False:
        branchforward = True
    else:
        branchforward = False
        
    if walls[1] == False:
        branchleft = True
    else:
        branchleft = False
        
    if walls[2] == False:
        branchright = True
    else:
        branchright = False
    
    if padInfo == None:
        print("[PAD] Not Detected, Adjusting Height!")
        maintainHeight()
        #align code
        
        time.sleep(5)
        padInfo = getPadInfo()
        
        if padInfo == None:
            t.land()
            inAir = False
    
    else: #if pad is found
        if walls[0] == True and walls[1] == True and walls[2] == True: #If there is no available path except backwards
            nodedata["id"] = currpadCoords
            nodedata["type"] = padInfo.get("type")
            nodedata["bl"] = branchleft
            nodedata["br"] = branchright
            nodedata["mn"] = currentmove
            nodedata["o"] = currorientation
            nodedata["m"] = action
            nodedata["lmove"] = lmove
            nodedata["rmove"] = rmove
            nodedata["bf"] = branchforward
            
            mapdata[nodedata["id"]] = nodedata
            map.add_node(nodedata["id"], type=nodedata["type"], bl=nodedata["bl"], br = nodedata["mn"], mn = nodedata["mn"], o = nodedata["o"], m = nodedata["m"], lmove = nodedata["lmove"], rmove = nodedata["rmove"], bf=branchforward)
            backTrack()
            
        elif walls[0] == False: 
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
                elif walls[0] == False and getNextOrientation("f") != "S":
                    print("[NAVI] Moving Forward")
                    action = "f"
                    t.move_forward(moveDistance)
                    actionCompleted = True
                
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
            
        elif action == "r":
            rmove = True
            print(f"[DEBUG] Right Move: {rmove}")
            
        elif action == "f":
            fmove = True
        
        nodedata["id"] = currpadCoords
        nodedata["type"] = padInfo.get("type")
        nodedata["bl"] = branchleft
        nodedata["br"] = branchright
        nodedata["mn"] = currentmove
        nodedata["o"] = currorientation
        nodedata["m"] = action
        nodedata["lmove"] = lmove
        nodedata["rmove"] = rmove
        nodedata["bf"] = branchforward
        
        mapdata[nodedata["id"]] = nodedata
        map.add_node(nodedata["id"], type=nodedata["type"], bl=nodedata["bl"], br = nodedata["mn"], mn = nodedata["mn"], o = nodedata["o"], m = nodedata["m"], lmove = nodedata["lmove"], rmove = nodedata["rmove"], bf=branchforward)
        
        #getting new padID
        updatePadID()
        
        
        
        print(f"[DEBUG] Previous NodeID: {previousnode}")
        map.add_edge(previousnode, currpadCoords)
          
        subax1 = plt.subplot(221)  
        nx.draw(map, with_labels = True, font_weight='bold')
        plt.show()
        
        #Connect to previous node + other connecting code
        #beenleft code (make it such that diff options add nodes with diff atrributes)
        #remember to pickle dump!
        mapfile = open(MAPFILEPATH, 'wb')
        pickle.dump(map, mapfile)
        mapfile.close()
        
        mapdatafile = open(MAPDATAPATH, "w")
        mapdatafile.write(str(mapdata))
        mapdatafile.close()
        
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
                
            if event.key == pygame.K_t and battLev > 10:
                t.takeoff()
                inAir = True
                
            if event.key == pygame.K_l:
                t.land()   
                inAir = False
                
            if event.key == pygame.K_1:
                align()           

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