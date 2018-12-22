import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import Adafruit_PCA9685
from threading import Thread
from flask import Blueprint

#Get the picture (low resolution, so it should be quite fast)
#Here you can also specify other parameters (e.g.:rotate the image)

pwm = Adafruit_PCA9685.PCA9685()
camera = PiCamera()
HEIGHT = 480
WIDTH = 640

HORIZ_LINE_WIDTH = (WIDTH * .75)

ESC_PIN = 2
SERVO_PIN = 1

SERVO_LEFT = 370
SERVO_RIGHT = 310

ESC_DRIVE = 370
ESC_STOPPED = 340

camera.resolution = (WIDTH, HEIGHT)
camera.framerate = 60

auto_mode = False

rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))
time.sleep(0.1)

auto_routes = Blueprint('auto_routes', __name__)

def follow_line():
  global auto_mode
  while(auto_mode):
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
      
        image = frame.array
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
        ret,thresh = cv2.threshold(blurred_gray_image,130,255,0) 
        x, contours, y = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        # Find the biggest contour (if detected)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)

            x, y, w, h = cv2.boundingRect(c)
            
            if M['m00'] != 0:
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
                pwm.set_pwm(ESC_PIN, 0, ESC_DRIVE)
                pwm.set_pwm(SERVO_PIN, 0, SERVO_RIGHT)
                print("Turn Right!")
              if cx < (WIDTH / 2 + 50) and cx > (WIDTH / 2 - 50):
                pwm.set_pwm(ESC_PIN, 0, ESC_DRIVE)
                print("On Track!")
              if cx <= (WIDTH / 2 - 50):
                pwm.set_pwm(ESC_PIN, 0, ESC_DRIVE)
                pwm.set_pwm(SERVO_PIN, 0, SERVO_LEFT)
                print("Turn Left")
        else:
            pwm.set_pwm(ESC_PIN, 0, ESC_STOPPED)
            print("I don't see the line")

        cv2.imshow("Edges", image)

        key = cv2.waitKey(25)
        if key == 27:
            break

        rawCapture.truncate(0)

@auto_routes.route('/toggle-auto', methods=['POST'])
def toggle_auto_drive():
  global auto_mode
  auto_mode = not auto_mode
  if auto_mode:
    auto_thread = Thread(target=follow_line)
    auto_thread.start()
  return "TOGGLED AUTO MODE"

