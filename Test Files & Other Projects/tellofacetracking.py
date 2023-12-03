from djitellopy import Tello
import cv2
import numpy as np
import dlib
import time
import threading as th
RESX = 640
RESY = 480
#Boundaries
#270 - 370
#190 - 290

setting = "tello"
extraad = -20
adjustment_velocity = 40
THRESHOLD = 0.6 # Value between 0 and 1 for confidence score

if setting == "tello":
    tello = Tello()
    tello.connect()
    tello.streamon()
    #tello.set_video_fps('30')
    telloFrame = tello.get_frame_read()

else:
    vid = cv2.VideoCapture(0)
    
detector = dlib.get_frontal_face_detector()

def stopMovement():
    tello.send_rc_control(0,0,0,0)

while True:
    count = 0
    locations = []
    locationdata = []
    
    if setting == "tello":
        imgframe = telloFrame.frame
        #tello.send_keepalive()
        
    else:
        imgframe = vid.read()
    
    imgframe = cv2.flip(imgframe,1)
    
    if setting == "tello":
        grayimg = cv2.cvtColor(imgframe, cv2.COLOR_BGR2RGB)
    
    else: 
        grayimg = imgframe
    
    faces = detector(grayimg)
    
    # Loop through list (if empty this will be skipped) and overlay green bboxes
    for face in faces:
        count += 1
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        
        centrex = (x1 + x2)/2
        centrey = (y1 + y2)/2
        
        #locations.append(x1, y1, x2, y2)
        
        cv2.rectangle(grayimg, (x1, y1), (x2, y2), (0, 255, 0), 3)
        #cv2.rectangle(grayimg, (370,290), (270, 190), (255, 255, 255), 3)
        #trimxdistance = RESX - centrex #270 & 370 
        boxarea = (x2 - x1) * (y2 - y1)
        print(boxarea)
        stop = th.Timer(1, stopMovement)
        
        if setting == "tello":
            if centrex > 370-extraad:
                print(f"[TRIM] Right Adjustment | Off By: {centrex - 370}")
                tello.send_rc_control(0, 0, 0, +adjustment_velocity)
                stop.start()
                
            if centrex < 270+extraad:
                print(f"[TRIM] Left Adjustment | Off By: {370 - centrex}")
                tello.send_rc_control(0, 0, 0, -adjustment_velocity)
                stop.start()
            
            if centrey > 290-extraad:
                print(f"[TRIM] Down Adjustment | Off By: {centrey - 290}")
                tello.send_rc_control(0, -adjustment_velocity, 0, 0)
                stop.start()
                
            if centrey < 190+extraad:
                print(f"[TRIM] Up   Adjustment | Off By: {190 - centrey}")
                tello.send_rc_control(0, adjustment_velocity, 0, 0)
                stop.start()

            else: 
                stopMovement()
                

            
        else:
            if centrex > 370-extraad:
                print(f"[TRIM] Right Adjustment | Off By: {centrex - 370}")
                #tello.send_rc_control(0, 0, 0, +adjustment_velocity)
                
            if centrex < 270+extraad:
                print(f"[TRIM] Left Adjustment | Off By: {370 - centrex}")
                #tello.send_rc_control(0, 0, 0, -adjustment_velocity)
                        
            if centrey > 290-extraad:
                print(f"[TRIM] Down Adjustment | Off By: {centrey - 290}")
                #tello.send_rc_control(0, -adjustment_velocity, 0, 0)

            if centrey < 190+extraad:
                print(f"[TRIM] Up   Adjustment | Off By: {190 - centrey}")
                #tello.send_rc_control(0, adjustment_velocity, 0, 0)
                
            else:
                print(f"[TRIM] No Trim")
              
            
    cv2.imshow('frame', grayimg)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frames
    # if the `q` key was pressed, break from the loop
    
    if key == ord("t"):
        tello.takeoff()
        
    if key == ord("l"):
        tello.land()
    
    if key == ord("w"):
        tello.move_up(50)
        
    if key == ord("s"):
        tello.move_down(50)
    
    if key == ord("q"):
        print("Quitting...")
        
        if setting == "tello":
            tello.streamoff()
            
        else:
            vid.release() 
            cv2.destroyAllWindows() 
            
            time.sleep(1)
            break  


