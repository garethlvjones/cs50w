import os
import requests

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
## KEY=t00295auIVdosK82l8e8Q

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
    return render_template("index.html")
