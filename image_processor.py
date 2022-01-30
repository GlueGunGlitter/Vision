import cv2
from cv2 import threshold
import numpy as np

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

    return contours

def find_target(detected_shapes):
    center = [0,0]
    if len(detected_shapes) != 0:
        for c in detected_shapes:
            M = cv2.moments(c)
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        '''
        #draw largest contour
        c = max(detected_shapes, key = cv2.contourArea)
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
    

def process(input_img, threshold_parameters):
    thresholded_img = threshold(input_img, threshold_parameters[0], threshold_parameters[1])
    cleared_img = clear_noise(thresholded_img)
    detected_shapes = detect_shapes(cleared_img, thresholded_img)
    
    return find_target(detected_shapes)

