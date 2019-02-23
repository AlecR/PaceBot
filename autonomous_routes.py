import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import Adafruit_PCA9685
from threading import Thread
from flask import Blueprint, jsonify, Response

#Get the picture (low resolution, so it should be quite fast)
#Here you can also specify other parameters (e.g.:rotate the image)

pwm = Adafruit_PCA9685.PCA9685()
camera = PiCamera()

## CONSTANTS ##

HEIGHT = 480
WIDTH = 640

HORIZ_LINE_WIDTH = (WIDTH * .75)
HEIGHT_OFFSET = 360

ESC_PIN = 1
SERVO_PIN = 0

SERVO_LEFT = 350
SERVO_RIGHT = 250

ESC_DRIVE = 350
ESC_STOPPED = 320

current_turn_value = 300

auto_mode = False

camera.resolution = (WIDTH, HEIGHT)
camera.framerate = 32

rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))
time.sleep(0.1)

autonomous_routes = Blueprint('autonomous_routes', __name__)

def follow_line():
  global current_turn_value
  while(True):
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
      rawCapture.truncate(0)
      # if auto_mode is False: return

      image = frame.array
      # cropped_image = image[HEIGHT_OFFSET:image.shape[1]]
      # gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
      # #blurred_gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
      # ret, thresh = cv2.threshold(gray_image,180,255,0) 
      # #thresh = cv2.adaptiveThreshold(blurred_gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
      # #thresh = cv2.bitwise_not(thresh)
      # x, contours, y = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
      # countrs = []
      # # Find the biggest contour (if detected)
      # if len(contours) > 0:
      #     c = max(contours, key=cv2.contourArea)
      #     M = cv2.moments(c)

      #     x, y, w, h = cv2.boundingRect(c)
      #     if M['m00'] != 0:
      #       cx = int(M['m10']/M['m00'])
      #       cy = int(M['m01']/M['m00'])

      #       distance_from_center = (int(WIDTH/ 2) - cx) * -1
            
      #       # Circle indicating the center of the detected area
      #       cv2.circle(image, (cx, cy + HEIGHT_OFFSET), 10, (255, 255, 0))
          
      #       # Line down the center of the image
      #       cv2.line(image, (int(WIDTH / 2), 0), (int(WIDTH / 2),720),(255,255,0),2)

      #       # Horizontal line from displaying the distance offset from the center
      #       cv2.line(image, (cx, cy + HEIGHT_OFFSET), (int(WIDTH / 2), cy + HEIGHT_OFFSET), (255, 255, 0), 2)

      #       # Box indicating detected area
      #       cv2.rectangle(image, (x,y + HEIGHT_OFFSET), (x+w, y+h + HEIGHT_OFFSET), (0, 255, 0), 2)
      #       distance_from_center_str = str(distance_from_center)
            
      #       # Text to display the value of the distance from the center
      #       cv2.putText(image, distance_from_center_str, (cx, cy + HEIGHT_OFFSET), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 0), 2, cv2.LINE_AA)
      #       #cv2.drawContours(image, contours, -1, (0,255,0), 1)
      #       pwm.set_pwm(ESC_PIN, 0, ESC_DRIVE)
      #       calculate_turn_value(distance_from_center)
      #       print(current_turn_value)
      #       pwm.set_pwm(SERVO_PIN, 0, current_turn_value)

      #       if w > HORIZ_LINE_WIDTH:
      #         print("Horizontal Line! =====")
      #         # Do something here to prevent horizontal line confusion
      # else:
          # print("Can't find the line!")
          # pwm.set_pwm(ESC_PIN, 0, ESC_STOPPED)
    
      cv2.imshow("PaceBot Camera", image)
     

      key = cv2.waitKey(25)
      if key == 27:
          break 

def calculate_turn_value(error):
  global current_turn_value, SERVO_LEFT, SERVO_RIGHT
  KP = 0.01
  TARGET = 0

  turn_value = (error * KP) * -1
  current_turn_value += int(turn_value)
  if (current_turn_value < SERVO_RIGHT):
    current_turn_value = SERVO_RIGHT
  elif (current_turn_value > SERVO_LEFT):
    current_turn_value = SERVO_LEFT
  print(current_turn_value)
    
@autonomous_routes.route('/video', methods=['GET'])
def stream_video():
    print("test")
    

@autonomous_routes.route('/toggle-auto', methods=['POST'])
def toggle_auto_drive():
  global auto_mode
  auto_mode = not auto_mode
  if auto_mode:
    auto_thread = Thread(target=follow_line)
    auto_thread.start()
  return jsonify(auto_mode=auto_mode)


