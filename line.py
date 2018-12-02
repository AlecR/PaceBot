import io
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import RPi.GPIO as GPIO

#Get the picture (low resolution, so it should be quite fast)
#Here you can also specify other parameters (e.g.:rotate the image)

camera = PiCamera()
HEIGHT = 480
WIDTH = 640

HORIZ_LINE_WIDTH = 480

LEFT_PIN = 20
RIGHT_PIN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_PIN, GPIO.OUT)
GPIO.setup(RIGHT_PIN, GPIO.OUT)

camera.resolution = (WIDTH, HEIGHT)
camera.framerate = 60

rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    GPIO.output(LEFT_PIN, GPIO.LOW)
    GPIO.output(RIGHT_PIN, GPIO.LOW)

    image = frame.array
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred_gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    
    ret,thresh = cv2.threshold(blurred_gray_image,60,255,cv2.THRESH_BINARY_INV) 
    
    x, contours, y = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
     
    # Find the biggest contour (if detected)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        x, y, w, h = cv2.boundingRect(c)
        
        if M['m00'] is 0: continue
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        
        cv2.circle(image, (cx, cy), 10, (255, 255, 0))
        cv2.line(image, (int(WIDTH / 2), 0), (int(WIDTH / 2),720),(255,255,0),2)
        cv2.line(image, (cx, cy), (int(WIDTH / 2), cy), (255, 255, 0), 2)
        cv2.rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 2)
        distance_from_center = str(abs(int(WIDTH/ 2) - cx))
        cv2.putText(image, distance_from_center, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 0), 2, cv2.LINE_AA)
        #cv2.drawContours(image, contours, -1, (0,255,0), 1)
        
        if w > HORIZ_LINE_WIDTH:
            print("Horizontal Line! =====")
            # Do something here to prevent horizontal line confusion
        
        if cx >= (WIDTH / 2 + 50):
            print("Turn Right!")
            GPIO.output(LEFT_PIN, GPIO.LOW)
            GPIO.output(RIGHT_PIN, GPIO.HIGH)
        if cx < (WIDTH / 2 + 50) and cx > (WIDTH / 2 - 50):
            print("On Track!")
            GPIO.output(LEFT_PIN, GPIO.HIGH)
            GPIO.output(RIGHT_PIN, GPIO.HIGH)
        if cx <= (WIDTH / 2 - 50):
            print("Turn Left")
            GPIO.output(LEFT_PIN, GPIO.HIGH)
            GPIO.output(RIGHT_PIN, GPIO.LOW)
    else:
        print("I don't see the line")
        GPIO.output(LEFT_PIN, GPIO.LOW)
        GPIO.output(RIGHT_PIN, GPIO.LOW)

    cv2.imshow("Edges", image)

    key = cv2.waitKey(25)
    if key == 27:
        break

    rawCapture.truncate(0)
