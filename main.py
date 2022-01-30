import platform
#from tkinter.messagebox import NO
import cv2
from cv2 import threshold
import numpy as np
import logging
import math
import json
import time as tm

import image_processor
from calculations import *

def RpiMain():
    #import rpi specific libraries
    from networktables import NetworkTables
    from cscore import CameraServer
    import threading

    with open('/boot/frc.json') as f:
        config = json.load(f)

    camera = config['cameras'][0]

    width = camera['width']
    height = camera['height']

    cs = CameraServer.getInstance()
    cs.enableLogging()

    camera = cs.startAutomaticCapture()
    camera.setResolution(width, height)

    input_stream = cs.getVideo()
    output_stream = cs.putVideo("processed footage", width, height)

    img = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    #initialize NetworkTables
    logging.basicConfig(level=logging.DEBUG)

    ip = "10.16.90.64"

    #print(f"ip = {sys.argv[1]}")

    #add connectoin listener
    NetworkTables.initialize(server=ip)

    sd = NetworkTables.getTable("SmartDashboard")
    

    print('connected')
    while True:


        time, frame = input_stream.grabFrame(img)

        if time == 0: # There is an error
            output_stream.notifyError(input_stream.getError())
            continue

        #process and output image
        thresh = sd.getValue("threshold_pi", (60,50,129,102,255,255))
        #print(thresh)
        thresholded_img, detected_shapes_img, center, cleared_img = image_processor.process(frame, [thresh[0:3],thresh[3:6]])
        

        output_stream.putFrame((frame, thresholded_img, detected_shapes_img)[int(sd.getNumber("stream_type_pi", 0))])

        #publish data to NetworkTables
        Xang, Yang = PixelsToAngles(center[0],center[1],{"resx": width, "resy": height, "hfov": 51.6, "vfov": 29})
        #print(math.degrees(Yang))
        distance = Dist(25,Yang,261,62)
        #print(distance)

        sd.putNumber("cx", center[0])
        sd.putNumber("cy", center[1]) 
        sd.putNumber('distance', distance)
        sd.putNumber('Xang', Xang)
        sd.putNumber('Yang', Yang)
    
def WindowsMain():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        #get camera stream
        _, frame = cap.read()
        #process image
        threshold_img, processed_img, center, cleared_img = ip.process(frame, [[0,100,227],[40,255,255]])
        #show processed camera stream
        cv2.imshow('processed',processed_img)
        if cv2.waitKey(1) == ord('q'):
            break

        Xang, Yang = PixelsToAngles(center[0], center[1], {"resx": 640, "resy": 480, "hfov": 57.15, "vfov": 36})
        #print(Xang, Yang)

        distance = Dist(17,Yang,173,62.5)
        #print(distance)


#run correct main(pc or pi)
os = platform.system()
if os == 'Windows':
    WindowsMain()
else:
    RpiMain()
#initialize camera server
