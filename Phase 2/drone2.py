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
currpadCoords = 0
startingpadCoords = 3
endingpadCoords = 48
previousBranchedNode = 0
backTracked = False
missionPads = {}
medicPads = {}
travelledTo = []
specialLocations = {}

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
MAPFILEPATH = r'C:\Users\delay\OneDrive\Documents\Code & Programs\Visual Studio Code\YDSP\DSTA-YDSP\Phase 2\drone1.txt'

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

map = pickle.load(mapgraphfile)
#mapdata = pickle.load(mapdatafile)
#specialLocations = pickle.load(specialLocationsfile)

mapgraphfile.close()
#mapdatafile.close()
#specialLocationsfile.close()

print(f"[LOAD] Loading data from file...")
print(Fore.RESET + Fore.RED + f"[CHECK] Current Coordinate: {currpadCoords}" + Fore.RESET)
print(f"[LOAD] Map: {nx.nodes(map)}")
#print(f"[LOAD] Map Data: {mapdata}")
#print(f"[LOAD] Locations: {specialLocations}")

print(f"[SETUP] Setup OK. Battery: {battLev}%")

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

def detectMedKid():
	global tooClose
	global sensortime
	global aligningTime
	
	sensorvalue = getTOF()
	time.sleep(sensortime)
 
	if sensorvalue < tooClose:
		print("[ADJ] Too Close, Moving Back...")
		t.move_back(20)
		time.sleep(aligningTime)
		
	if detect() == False:
		print("[DETECT] Med Kit is not detected in front")
		yawRight90() #Front
		sensorvalue = getTOF()
		time.sleep(sensortime)

		if sensorvalue < tooClose:
			print("[ADJ] Too Close, Moving Back...")
			t.move_back(20)
			time.sleep(aligningTime)

		if detect() == False:
			print("[DETECT] Med Kit is not detected in front")
			yawRight90() #east
			detect()
			sensorvalue = getTOF()
			time.sleep(sensortime)
   
			if sensorvalue < tooClose:
				print("[ADJ] Too Close, Moving Back...")
				t.move_back(20)
				time.sleep(aligningTime)

			if detect() == False:
				print("[DETECT] Med Kit is not detected in front")
				yawRight90() #south
				detect()
				sensorvalue = getTOF()
				time.sleep(sensortime)
	
				if sensorvalue < tooClose:
					print("[ADJ] Too Close, Moving Back...")
					t.move_back(20)
					time.sleep(aligningTime)

				if detect() == False:
					print("[DETECT] Med Kit is not detected in front")
					yawRight90() #south
					detect()
					sensorvalue = getTOF()
					time.sleep(sensortime)

				else:
					yawRight90()
					time.sleep(aligningTime)
	
			else:
				yawLeft90()
				time.sleep(aligningTime)
				yawLeft90()
				time.sleep(aligningTime)
	
		else:
			yawLeft90()
			time.sleep(aligningTime)

	else:
		pass
	 
def detect():
	# Grab the webcamera's image.
	telloFrame = t.get_frame_read()
	image = telloFrame.frame
	# Resize the raw image into (224-height,224-width) pixels
	image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

	# Make the image a numpy array and reshape it to the models input shape.
	image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

	# Normalize the image array
	image = (image / 127.5) - 1

	# Predicts the model
	prediction = model.predict(image)
	index = np.argmax(prediction)
	class_name = class_names[index]
	confidence_score = prediction[0][index]

	# Print prediction and confidence score
	print("Class:", class_name[2:], end="")
	print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
 
	if confidence_score>0.8 and class_name == class_names[0]:
		t.send_expansion_command("led bl 3 255 0 0 0 0 0")
		time.sleep(1)
		return True

	else:
		return False

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

def executeNextMovement(next_pad_coordinate):
	global currpadCoords
	
	if (currpadCoords - next_pad_coordinate) == -5:
		print(f"[MOVE] Forward movement from {currpadCoords} to {next_pad_coordinate}")
		t.move_forward(moveDistance)
		travelledTo.append(currpadCoords)
		currpadCoords = next_pad_coordinate
	
	elif (currpadCoords - next_pad_coordinate) == 5:
		print(f"[MOVE] Backward movement from {currpadCoords} to {next_pad_coordinate}")
		t.move_back(moveDistance)
		travelledTo.append(currpadCoords)
		currpadCoords = next_pad_coordinate
		
	elif (currpadCoords - next_pad_coordinate) == -1:
		print(f"[MOVE] Right movement from {currpadCoords} to {next_pad_coordinate}")
		t.move_right(moveDistance)
		travelledTo.append(currpadCoords)
		currpadCoords = next_pad_coordinate
		
	elif (currpadCoords - next_pad_coordinate) == 1:
		print(f"[MOVE] Left movement from {currpadCoords} to {next_pad_coordinate}")
		t.move_left(moveDistance)
		travelledTo.append(currpadCoords)
		currpadCoords = next_pad_coordinate

	else:
		print(Fore.RESET + Fore.RED + f"[MOVE] Error! Pad {next_pad_coordinate} is not connected to {currpadCoords}!")
		
travelledTo.append(currpadCoords)
passNode = True
def main():
	global battLev
	global orientation
	global currentmove
	global inAir
	global previousnode
	#global mapdata
	global currpadCoords
	global backTracked
	#global specialLocations
	global travelledTo
	global passNode	
 
	battLev = t.get_battery()

	#Run
	print(f"\n[MAIN] Move {currentmove} | Height {t.get_height()}cm | Orientation {orientation} | Battery {battLev}%")
	maintainHeight()
	
	padInfo = getPadInfo()
	padCoords = currpadCoords
 
	#First, Get if the current pad is a missionpad!
	if padInfo.get("type") == "missionpad":
		if padInfo.get("id") > 2 and padInfo.get("id") < 6:
			print(f"[PAD] Special Pad detected! Mission Pad: {padInfo.get('id')}")
			specialLocations[currpadCoords] = padInfo.get("id") #Store as dictionary with node as identifier
			print(f"[PAD] Special Locations Found: {specialLocations}")
			t.send_expansion_command("led bl 3 255 0 0 0 0 0")
			time.sleep(1)
			
		else:
			print("[PAD] Mission Pad detected, but it is not a location!")
			
	#Second, Check if you have reached the end of the maze
	if currpadCoords == 48:
		print(Fore.RESET + Fore.GREEN + f"[MAIN] Task Completed!" + Fore.RESET)
		
		while True:
			t.send_keepalive()
 
	nodeNeighboursDict = map[currpadCoords] #dict
	number_of_neighbours = len(nodeNeighboursDict)
	nodeNeighboursList = []
	
	x = 0
	while x < 48:
		try: #try find the node in nodeNeighbours
			nodeNeighboursDict[x]
			nodeNeighboursList.append(x)
			x += 1

		except KeyError:
			x += 1
   
	print(f"[NAVI] Number of Neighbouring nodes: {number_of_neighbours}")
	print(f"[NAVI] Neighbouring Nodes: {nodeNeighboursList}")
 
	if (currpadCoords == 29): #29 is a dead end
		#Backtracking to pad 35
		executeNextMovement(currpadCoords+1)
		executeNextMovement(currpadCoords+5)
 
	if (currpadCoords == 41):
		#Back tracking to pad 49
		executeNextMovement(currpadCoords+5) #46
		executeNextMovement(currpadCoords+1) #47
		executeNextMovement(currpadCoords-5) #42
		executeNextMovement(currpadCoords+1) #43
		executeNextMovement(44)
		executeNextMovement(49)
	
	for node in nodeNeighboursList: #Finding its movement
		if travelledTo.count(node) == 0: #If node has not been travelled to
			print(f"[NAVI] Drone has not travelled to node {node}!")
			executeNextMovement(node)
			break
		
		else:
			print(f"[NAVI] Node {node} has already been travelled to, finding other nodes...")		
   
   
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

