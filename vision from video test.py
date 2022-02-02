import cv2
import numpy as np

import image_processor as imp
from calculations import *

def Main():
    cap = cv2.VideoCapture('hub test.avi')
    _,wh = cap.read()
    height, width, _ = wh.shape

    while cap.isOpened():
        #get camera stream
        ret, frame = cap.read()
        #process image
        if ret:
            '''
            top = frame[:int(height/2), :]
            binary_img = imp.threshold(top, [60,50,129],[102,255,255])
            binary_img = imp.erode(binary_img)
            binary_img = imp.dilate(binary_img, kernel = np.ones((3, 3), np.uint8))

            contours = imp.detect_shapes(frame,binary_img)


            _, img = imp.filter_contours(contours,frame)
            '''
            _, _, img,_ = imp.process(frame, [[60,50,129],[102,255,255]], height)
            cv2.imshow("wwt", img)
        else:
            print('no video')
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if cv2.waitKey(1) == ord('q'):
            break
        
        '''
        Xang, Yang = PixelsToAngles(center[0], center[1], {"resx": 640, "resy": 480, "hfov": 57.15, "vfov": 36})
        #print(Xang, Yang)

        distance = Dist(17,Yang,173,62.5)
        #print(distance)
        '''
Main()