import cv2
from cv2 import threshold
import numpy as np

def find_median(contours, sort=False):
    if sort:
        contours = sorted(contours, key=lambda cnt: cv2.boundingRect(cnt)[0])

    if len(contours)%2 == 0:
        #print('even')
        left_moments = cv2.moments(contours[int((len(contours)/2)-1)])
        right_moments = cv2.moments(contours[int((len(contours)/2))])

        x = int((int(left_moments['m10']/left_moments['m00']) + int(right_moments['m10']/right_moments['m00']))/2)
        size = (left_moments['m00'] + right_moments['m00'])/2
    else: 
        #print('odd')

        moments = cv2.moments(contours[int((len(contours)+1)/2-1)])
        x = int(moments['m10']/moments['m00'])
        size = moments['m00']
    return x, size



def threshold(img, p_lower_limit, p_upper_limit):
    lower_limit = np.array(p_lower_limit ,np.uint8)
    upper_limit = np.array(p_upper_limit ,np.uint8)

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    frame_threshed = cv2.inRange(hsv_img, lower_limit, upper_limit)

    return frame_threshed

def erode(img, kernel = np.ones((3, 3), np.uint8)):
    img = cv2.erode(img, kernel, iterations = 1)

    return img
    
def dilate(img, kernel = np.ones((3, 3), np.uint8)):
    img = cv2.dilate(img, kernel, iterations = 1)

    return img


def detect_shapes(img, binary_img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    #find contours
    _,contours,_ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def filter_contours(contours, img):
    center = [0,0]

    if len(contours) != 0:
        
        #get median size
        _,size = find_median(contours,sort=True)

        #print(median_size)
        new_contours = []
        for i, c in enumerate(contours):
            M = cv2.moments(c)

            if M['m00'] < 1.5*size and  M['m00'] > 0.66*size:
                new_contours.append(c)

                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(img,str(i),(x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 2, cv2.LINE_AA)

        x,_ = find_median(new_contours,sort=True)        
        
        cv2.line(img, (x, 0), (x, 240), (255, 0, 255), thickness=1)



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

    return center, img
    

def process(input_img, threshold_parameters):
    thresholded_img = threshold(input_img, threshold_parameters[0], threshold_parameters[1])
    cleared_img = erode(thresholded_img)
    detected_shapes = detect_shapes(input_img, thresholded_img)
    
    center, detected_shapes_img = find_target(detected_shapes, input_img)
    
    return thresholded_img, detected_shapes_img, center, cleared_img

