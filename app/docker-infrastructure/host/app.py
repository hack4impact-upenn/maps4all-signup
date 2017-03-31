from flask import Flask
import subprocess
from flask import render_template
from flask import request
app = Flask(__name__)

port = 3000


def next_port():
    global port
    port += 1
    return port


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create():
    ORG_NAME = request.form['org']
    PORT = str(next_port())
    APP_NAME = ORG_NAME.replace(" ", "-") + "_p" + PORT
    SECRET = "supersecretkeyshhhh"

    subprocess.Popen(["sh", "host/scripts/new_instance.sh", APP_NAME, ORG_NAME,
                      PORT, SECRET], cwd="../")

    return render_template('success.html', port=PORT, org=ORG_NAME)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
