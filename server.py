#~/usr/bin/python
import socket
import os
from flask import Flask
from flask_socketio import SocketIO
import Adafruit_PCA9685
from car_routes import car_routes
from autonomous_routes import autonomous_routes

def current_ip():
    gw = os.popen("ip -4 route show default").read().split()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((gw[2], 0))
    ipaddr = s.getsockname()[0]
    return ipaddr

app = Flask(__name__)
#socketio = SocketIO(app)
pwm = Adafruit_PCA9685.PCA9685()
app.register_blueprint(autonomous_routes)
app.register_blueprint(car_routes)

if __name__ == "__main__":
    pwm.set_pwm_freq(50)
    app.run(host=current_ip(), port=5000)
    #socketio.run(app)
    
    