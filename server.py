from flask import Flask
app = Flask(__name__)

@app.route('/start', methods=['PUT'])
def start():
    return 'Starting'

@app.route('/stop', methods=['PUT'])
def stop():
    return 'Stopping'