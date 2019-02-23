#~/usr/bin/python
from flask import Flask, Blueprint, request, jsonify
import Adafruit_PCA9685
import time

car_routes = Blueprint('car_routes', __name__)
pwm = Adafruit_PCA9685.PCA9685()

esc_pwm = 330
esc_center = 330
esc_variation = 100

servo_pwm = 300
servo_center = 300
servo_variation = 100

servo_pin = 0
esc_pin = 1

@car_routes.route('/drive', methods=['POST'])
def drive():
    speed = float(request.args.get('speed'))
    diff = esc_variation * speed * -1
    updated_esc_pwm = int(esc_center + diff)
    print(updated_esc_pwm)
    update_pwms(updated_esc_pwm, servo_pwm)
    return jsonify(success=True, pwm=esc_pwm)

@car_routes.route('/stop', methods=['POST'])
def stop():
    update_pwms(esc_center, servo_pwm)
    return jsonify(success=True, pwm=esc_center)

@car_routes.route('/turn', methods=['POST'])
def turn():
    radius = float(request.args.get('radius'))
    diff = servo_variation * radius * -1
    updated_servo_pwm = int(servo_center + diff)
    update_pwms(esc_pwm, updated_servo_pwm)
    print(servo_pwm)
    return jsonify(success=True, pwm=servo_pwm)

@car_routes.route('/calibration/prepare', methods=['POST'])
def start_calibration():
    high_signal = esc_center + esc_variation
    update_pwms(high_signal, servo_pwm)
    return jsonify(success=True, pwm=high_signal)

@car_routes.route('/calibration/calibrate', methods=['POST'])
def calibrate():
    print(servo_pwm)
    pwm = esc_center + esc_variation
    update_pwms(pwm, servo_pwm)
    while pwm >= esc_center:
        pwm -= 10
        print(pwm)
        update_pwms(pwm, servo_pwm)
        time.sleep(0.1)
    update_pwms(esc_center, servo_pwm)
    time.sleep(1)
    return jsonify(success=True, pwm=pwm)

@car_routes.route('/test/esc_pwm', methods=['POST'])
def test_esc_pwm():
    updated_esc_pwm = int(request.args.get('pwm'))
    update_pwms(updated_esc_pwm, servo_pwm)
    return jsonify(success=True, pwm=updated_esc_pwm)

def update_pwms(updated_esc_pwm, updated_servo_pwm):
    global esc_pwm, servo_pwm
    esc_pwm = updated_esc_pwm
    servo_pwm = updated_servo_pwm
    pwm.set_pwm(esc_pin, 0, esc_pwm)
    pwm.set_pwm(servo_pin, 0, servo_pwm)

update_pwms(esc_pwm, servo_pwm)
    
    