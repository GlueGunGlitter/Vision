import platform
#from tkinter.messagebox import NO
import cv2
from cv2 import threshold
import numpy as np
import logging
import math
import json
import time as tm

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
        thresholded_img, detected_shapes_img, center, cleared_img = image_processor(frame, [thresh[0:3],thresh[3:6]])
        


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
        threshold_img, processed_img, center, cleared_img = image_processor(frame, [[0,100,227],[40,255,255]])
        #show processed camera stream
        cv2.imshow('processed',processed_img)
        if cv2.waitKey(1) == ord('q'):
            break

        Xang, Yang = PixelsToAngles(center[0], center[1], {"resx": 640, "resy": 480, "hfov": 57.15, "vfov": 36})
        #print(Xang, Yang)

        distance = Dist(17,Yang,173,62.5)
        #print(distance)

#a1 = camera angle, a2 = Y angle to the target, th = target height, ch = camera height,
def Dist(camera_pitch,pitch,th,ch):
    if pitch == 0:
        return 0
    else:
        distance = ((th-ch)/math.tan(math.radians(camera_pitch) + pitch))
        #print(distance)
    return distance

#px, py specify the point to convert to angles. camera is a list dictionary which contains {"resx":, "resy":, "hfov":, "vfov":}
def PixelsToAngles(px,py, camera):
    '''
    print("px:"+str(px)+"\n")
    print("py:"+str(py)+"\n")
    '''

    hfov = math.radians(camera["hfov"])
    vfov = math.radians(camera["vfov"])

    #convert between regular to normalized pixels
    nx = ((px-(camera["resx"]/2))/(camera["resx"]/2))
    ny = (((camera["resy"]/2-py))/(camera["resy"]/2))
    #print("nx: "+str(nx)+"\nny: "+str(ny)+"\n\n")

    Xangle = math.atan(math.tan(hfov/2)*nx)
    Yangle = math.atan(math.tan(vfov/2)*ny)
    #print("Xangle: "+str(math.degrees(Xangle))+"\nYangle: "+str(math.degrees(Yangle))+"\n\n")

    return Xangle, Yangle

#main image processing function
def image_processor(input_img, threshold_parameters):
    #declar inerfunctions
    def threshold(img, p_lower_limit, p_upper_limit):
        lower_limit = np.array(p_lower_limit ,np.uint8)
        upper_limit = np.array(p_upper_limit ,np.uint8)

        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        frame_threshed = cv2.inRange(hsv_img, lower_limit, upper_limit)

        return frame_threshed

    def clear_noise(img):
        kernel = np.ones((3, 3), np.uint8)
        img = cv2.erode(img, kernel, iterations = 2)

        return img

    def detect_shapes(img, binary_img):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        #find contours
        _,contours,_ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        center = [0,0]
        if len(contours) != 0:
            for c in contours:
                M = cv2.moments(c)
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            '''
            #draw largest contour
            c = max(contours, key = cv2.contourArea)
            M = cv2.moments(c)
            if M['m00'] !=0 :
                cv2.drawContours(img, [c], -1, color = (0, 0, 255), thickness = 2)
                #draw rectangle over largest contour
                x,y,w,h = cv2.boundingRect(c)
                print(w*h)
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

                #contour center of mass
                center = [int(M['m10']/M['m00']),int(M['m01']/M['m00'])]
                cv2.circle(img,(center[0],center[1]),2,(255,0,0),2)
            '''
    

        return img, center

    #function code
    thresholded_img = threshold(input_img, threshold_parameters[0], threshold_parameters[1])
    cleared_img = clear_noise(thresholded_img)
    detected_shapes_img, center= detect_shapes(input_img, thresholded_img)

    return thresholded_img, detected_shapes_img, center, cleared_img

#run correct main(pc or pi)
os = platform.system()
if os == 'Windows':
    WindowsMain()
else:
    RpiMain()
#initialize camera server
