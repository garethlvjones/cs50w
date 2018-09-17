import os
import requests

from flask import Flask, flash, session, render_template, request, redirect, url_for, Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from psycopg2.extensions import AsIs
from functools import wraps

app = Flask(__name__)
 
KEY="t00295auIVdosK82l8e8Q"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session is None:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

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

# Routes

@app.route("/")
def index():
    if 'user_id' not in session:
        return render_template("index.html")
    return redirect(url_for('search'))

@app.route("/login", methods=["POST"])
def login():
    loginName = request.form.get("name")
    passy = request.form.get("password")

    outputLogin = db.execute("SELECT * from users WHERE username = :loginName", {"loginName": loginName}).fetchone()

    if outputLogin is None:
        flash('No such username')
        return redirect(url_for('index'))
    elif outputLogin['password'] == passy:
        session['username'] = loginName
        session['user_id'] = outputLogin['id']
        flash('Login successful')
        return redirect(url_for('search'))
    else:
        flash('Bad password')
        return redirect(url_for('index'))

@app.route("/logout")
@login_required
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

@app.route("/search/", methods=["POST", "GET"])
@login_required 
def search():
    if request.form.get("isbn"):
        field = "isbn"
        query='%' + request.form.get("isbn") + '%'
    elif request.form.get("author"):
        field = "author" 
        query='%' + request.form.get("author") + '%'
    elif request.form.get("title"):
        field = "title"
        query='%' + request.form.get("title") + '%'
    else:
        return render_template("search.html", name=session['username'])

    resultBooks = db.execute("SELECT * from books WHERE :field ILIKE :query LIMIT 50", {"field": AsIs(field), "query": query}).fetchall()
    return render_template("search.html", books=resultBooks, name=session['username'])

@app.route("/book/<string:isbn>")
@login_required
def book(isbn): 

    # to do:
    #   - check if user has reviewed already
    #   - Get average score
    #   - Get number of ratings
    #   - List all text reviews
    #   - store new score. Allow no text
    #   - store new text review, optionally

    # Get title, author, publication year, ISBN number
    bookDetails = db.execute("SELECT * FROM books WHERE isbn =  :isbn", {"isbn": isbn}).fetchone()
    if (bookDetails is None):
        flash('Invalid isbn')
        return redirect(url_for('search')) 
    
    # Get reviews that users have left for the book on your website.
    getReviews = db.execute("SELECT * FROM reviews WHERE isbn_ref = :isbn", {"isbn": isbn}).fetchall()

    # see if userid is in getReviews, i.e. if user has added a review

    # Get review widget as json (reviews_widget) from goodreads
    reviews = requests.get("https://www.goodreads.com/book/isbn/", params={"key": KEY, "format": "json", "isbn": {isbn}})


    return render_template("book.html", isbn=bookDetails[0], author=bookDetails[1], title=bookDetails[2], year=bookDetails[3], res=Markup(reviews.json()["reviews_widget"]), name=session['username'], getReviews=getReviews)

@app.route("/book/addreview", methods=["POST"])
@login_required
def addreview():
    pass
