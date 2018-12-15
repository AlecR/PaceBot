from flask import Flask
app = Flask(__name__)

@app.route('/turn', methods=['POST'])
def turn():
    print(request.args.get('radius'))
    return 'Starting'