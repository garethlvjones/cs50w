import os, random, string

from flask import Flask, flash, jsonify, render_template, request
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

# Session(app)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")
