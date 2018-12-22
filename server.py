#~/usr/bin/python

from flask import Flask, request
import Adafruit_PCA9685
import time
from line_following import auto_routes

pwm = Adafruit_PCA9685.PCA9685()
app = Flask(__name__)
app.register_blueprint(auto_routes)

SERVO_PIN = 1
ESC_PIN = 2

servo_center = 320
servo_variation = 100

esc_center = 340
esc_variation = 150

servo_pwm = servo_center
esc_pwm = esc_center



@app.route('/drive', methods=['POST'])
def drive():
    speed = float(request.args.get('speed'))
    diff = esc_variation * speed
    esc_pwm = int(esc_center + diff)
    pwm.set_pwm(ESC_PIN, 0, int(esc_pwm))
    print(esc_pwm)
    return 'Driving'

@app.route('/stop', methods=['POST'])
def stop():
    pwm.set_pwm(ESC_PIN, 0, esc_center)
    return 'Stopping'

@app.route('/turn', methods=['POST'])
def turn():
    radius = float(request.args.get('radius'))
    diff = servo_variation * radius * -1
    servo_pwm = int(servo_center + diff)
    pwm.set_pwm(SERVO_PIN, 0, servo_pwm)
    print(servo_pwm)
    return 'DONE'

@app.route('/calibration/prepare', methods=['POST'])
def start_calibration():
    high_signal = esc_center + esc_variation
    pwm.set_pwm(ESC_PIN, 0, high_signal)
    return 'CALIBRATION STARTED'

@app.route('/calibration/calibrate', methods=['POST'])
def calibrate():
    speed = esc_center + esc_variation
    while speed > esc_center:
        speed -= 10
        pwm.set_pwm(ESC_PIN, 0, speed)
        time.sleep(0.1)
    pwm.set_pwm(ESC_PIN, 0, esc_center)
    time.sleep(1)
    return 'DONE'

if __name__ == "__main__":
    pwm.set_pwm_freq(50)
    pwm.set_pwm(SERVO_PIN, 0, servo_pwm)
    pwm.set_pwm(ESC_PIN, 0, esc_pwm)
    app.run(host='10.0.0.23', port=5000)
    
    