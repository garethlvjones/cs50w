import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# KEY="t00295auIVdosK82l8e8Q"


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['TEMPLATES_AUTO_RELOAD'] = True
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Test get from goodreads
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "t00295auIVdosK82l8e8Q", "isbns": "9781632168146"})
# print(res.json())

# Routes

@app.route("/")
def index():
    if 'user_id' not in session:
        return render_template("index.html")
    return render_template("search.html")

@app.route("/login", methods=["POST"])
def login():
    loginName = request.form.get("name")
    passy = request.form.get("password")

    outputLogin = db.execute("SELECT * from users WHERE username = :loginName", {"loginName": loginName}).fetchone()
    session['username'] = loginName
    session['user_id'] = outputLogin['id']

    if outputLogin is None:
        return render_template("index.html", message="No such username")
    elif outputLogin['password'] == passy:
        return render_template("search.html", message="It worked")
    else:
        return redirect(url_for('index'), message="Incorrect password")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/create", methods=["POST"])
def create():
    createName = request.form.get("createName")
    createPassword = request.form.get("createPassword")

    outputCreate = db.execute("SELECT * from users WHERE username = :createName", {"createName": createName}).fetchone()

    if outputCreate is not None:
        return render_template("index.html", message="user already exists, log in instead")
    else:
        try: 
            db.execute("INSERT INTO users (username, password) VALUES (:createName, :createPassword)", {"createName": createName, "createPassword": createPassword})
            db.commit()
            return render_template("index.html", message="user account created") 
        except ValueError:
            return render_template("index.html", message="couldn't create user")


@app.route("/search")
def search():
    if session is None:
        return render_template("index.html")



    return render_template("search.html")
        