import cv2
from cv2 import threshold
import numpy as np

def find_median(contours, sort=False):
    if len(contours) != 0:

        try:
            if sort:
                    contours = sorted(contours, key=lambda cnt: cv2.boundingRect(cnt)[0])

            if len(contours)%2 == 0:
                #print('even')
                left_moments = cv2.moments(contours[int((len(contours)/2)-1)])
                right_moments = cv2.moments(contours[int((len(contours)/2))])

                x = int((int(left_moments['m10']/left_moments['m00']) + int(right_moments['m10']/right_moments['m00']))/2)
                y = int((int(left_moments['m01']/left_moments['m00']) + int(right_moments['m01']/right_moments['m00']))/2)
                size = (left_moments['m00'] + right_moments['m00'])/2
            else: 
                #print('odd')
                moments = cv2.moments(contours[int((len(contours)+1)/2-1)])
                x = int(moments['m10']/moments['m00'])
                y = int(moments['m01']/moments['m00'])
                size = moments['m00']
            return x,y, size
        except ZeroDivisionError:
            print('fuck')
            return 0,0,0
    else:
        return 0,0,0

def threshold(img, p_lower_limit, p_upper_limit):
    lower_limit = np.array(p_lower_limit ,np.uint8)
    upper_limit = np.array(p_upper_limit ,np.uint8)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    frame_threshed = cv2.inRange(hsv_img, lower_limit, upper_limit)

    return frame_threshed

def erode(img, kernel = np.ones((3, 3), np.uint8)):
    img = cv2.erode(img, kernel, iterations = 1)

    return img
    
def dilate(img, kernel = np.ones((3, 3), np.uint8), iterations = 1):
    img = cv2.dilate(img, kernel, iterations = iterations)

    return img

def detect_shapes(img, binary_img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    #find contours
    _,contours,_ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def find_target(contours, img):
    center = [0,0]
    
    if len(contours) != 0:
        new_contours = []
        #get median size
        _,n,size = find_median(contours,sort=True)

        #print(median_size)
        for i, c in enumerate(contours):
            M = cv2.moments(c)

            curr_size = int(M['m01']/M['m00'])
    
            if curr_size < 4*n and curr_size > 0.25*n:
                new_contours.append(c)

                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(img,str(i),(x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 2, cv2.LINE_AA)
    
        x,y,_ = find_median(new_contours,sort=True)        
        
        cv2.line(img, (x, 0), (x, 240), (255, 0, 255), thickness=1)
        cv2.line(img, (0, y), (320, y), (255, 0, 255), thickness=1)

        center = [x,y]
    return center
    
def process(img, threshold_parameters, img_height):
    #only process the top part of the image
    top = img[:int(img_height/2), :]
    #threshold and clear noise
    thresh_img = threshold(top, threshold_parameters[0], threshold_parameters[1])
    #cv2.imshow("t_img", binary_img)

    binary_img = erode(thresh_img, np.ones((3, 3), np.uint8))
    binary_img = dilate(binary_img, kernel = np.ones((3, 3), np.uint8))

    #detect and filter contours
    contours = detect_shapes(img, binary_img)
    center = find_target(contours, img)

    return thresh_img, binary_img, img, center

def single_contour(img, threshold_parameters, img_height):
    top = img[:int(img_height/2), :]
    thresh_img = threshold(top, threshold_parameters[0], threshold_parameters[1])
    binary_img = erode(thresh_img, np.ones((4, 4), np.uint8))
    binary_img = dilate(binary_img, kernel = np.ones((5, 25), np.uint8))

    contours = detect_shapes(img,binary_img)

    x,y,_ = find_median(contours,True)
    #print(len(contours))

    cv2.drawContours(img, contours, -1, (255,0,0), 3)

    cv2.line(img, (x, 0), (x, 240), (255, 0, 255), thickness=1)
    cv2.line(img, (0, y), (320, y), (255, 0, 255), thickness=1)

    return thresh_img, binary_img,  img, [x,y]

