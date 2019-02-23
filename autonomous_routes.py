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

SCALE_FACTOR = 0.25

SCALED_WIDTH = int(WIDTH * SCALE_FACTOR)
SCALED_HEIGHT = int(HEIGHT * SCALE_FACTOR)

SCALED_X_CENTER = int(SCALED_WIDTH / 2)
SCALED_Y_CENTER = int(SCALED_HEIGHT / 2)

HORIZ_LINE_WIDTH = (WIDTH * .75)

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
      if auto_mode is False: return

      # Resize image
      image = frame.array
      image = cv2.resize(image, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)

      # Convert to gray and threshold
      gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      _, image_thresh = cv2.threshold(gray_image, 180, 255, 0) 

      lines = cv2.HoughLines(image_thresh, 10, np.pi/180, 100)

      # draw lines on image and computer error
      if lines is not None and len(lines) > 0:
        for rho, theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            mid_x = (x1 + x2) / 2

            cv2.line(image, (mid_x, y1), (mid_x, y2),(0,0,255),2)
            cv2.line(image, (SCALED_X_CENTER, 0),(SCALED_X_CENTER, SCALED_HEIGHT),(0,255,255),2)

            error = SCALED_X_CENTER - mid_x
            
            pwm.set_pwm(ESC_PIN, 0, ESC_DRIVE)
            calculate_turn_value(error)
            pwm.set_pwm(SERVO_PIN, 0, current_turn_value)
      else:
        pwm.set_pwm(ESC_PIN, 0, ESC_STOPPED)
    
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


