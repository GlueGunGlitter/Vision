import cv2
import numpy as np
import time

import image_processor as imp
from calculations import *
import threshold_gui

def Main():
    cap = cv2.VideoCapture('hub test.avi')
    _,wh = cap.read()
    height, width, _ = wh.shape

    while cap.isOpened():
        #get camera stream
        ret, frame = cap.read()
        #process image
        if ret:
            hreshold_values = threshold_gui.get_values()
            try:
                top = frame[:int(height/2), :]
                thresh_img = imp.threshold(top, [60,50,129],[102,255,255])
                binary_img = imp.erode(thresh_img, np.ones((4, 4), np.uint8))
                binary_img = imp.dilate(binary_img, kernel = np.ones((5, 25), np.uint8))

                contours = imp.detect_shapes(frame,binary_img)

                x,y,_ = imp.find_median(contours,True)
                print(len(contours))

                cv2.drawContours(frame, contours, -1, (255,0,0), 3)

                cv2.line(frame, (x, 0), (x, 240), (255, 0, 255), thickness=1)
                cv2.line(frame, (0, y), (320, y), (255, 0, 255), thickness=1)


                #_, img = imp.find_target(contours,frame)                        
            
                #binary_img, _, img,_ = imp.process(frame, threshold_values, height)
                cv2.imshow("img", frame)
                cv2.imshow("binary_img", binary_img)
                cv2.imshow("thresh_img", thresh_img)


            except Exception as p: print(p)
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

        threshold_gui.update()

        time.sleep(0.03)
Main()