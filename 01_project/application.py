import os
import requests

from flask import Flask, flash, session, render_template, request, redirect, url_for, Markup, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from psycopg2.extensions import AsIs
from functools import wraps

app = Flask(__name__)
 
KEY="t00295auIVdosK82l8e8Q"
os.environ['no_proxy'] = '127.0.0.1,localhost'


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

    # Get title, author, publication year, ISBN number BY USING MY OWN API OH WOW
    apiURL = "http://localhost:5000/api/" + isbn
    
    localBookInfo = requests.get(apiURL).json()

    # Get all reviews and usernames of reviewers
    allReviews = db.execute("SELECT reviews.text, reviews.rating, users.username FROM reviews JOIN users ON reviews.user_id=users.id WHERE isbn_ref = :isbn", {"isbn": isbn}).fetchall()

    # Check if current user has already reviewed
    userHasReviewed = "no"
    for review in allReviews:
        if session['username'] == review[2]:
            userHasReviewed = "yes"

    # Get goodreads review numbers and avgs
    goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn}).json()

    return render_template("book.html", name=session['username'], userHasReviewed=userHasReviewed, allReviews=allReviews, localBookInfo=localBookInfo, goodreads=goodreads['books'][0])

@app.route("/addreview/", methods=["POST"])
@login_required 
def addreview():
    reviewText = request.form['textreview']
    rating = request.form['inlineRadioOptions']
    isbn = request.form['isbn']
    user_id = session['user_id']  

    db.execute("INSERT INTO reviews (isbn_ref, user_id, rating, text) VALUES (:isbn_ref, :user_id, :rating, :reviewText)", {"isbn_ref": isbn, "user_id": user_id, "rating": rating, "reviewText": reviewText})
    db.commit()
    return redirect(url_for('book', isbn=isbn)) 

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    """
    API Access: If users make a GET request to your website’s /api/<isbn> route, where <isbn> is an ISBN number, your website should return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. The resulting JSON should follow the format:
    {
        "title": "Memory",
        "author": "Doug Lloyd",
        "year": 2015,
        "isbn": "1632168146",
        "review_count": 28,
        "average_score": 5.0
    }
    If the requested ISBN number isn’t in your database, your website should return a 404 error.
    """
    # first see if there are local reviews for the book 
    hasReview = db.execute("SELECT isbn_ref FROM reviews WHERE isbn_ref = :isbn", {"isbn": isbn}).fetchone()

    # if there are reviews, do joined get for return
    if hasReview:
        apiReturn = db.execute("SELECT books.title, books.author, books.year, books.isbn, COUNT(reviews.rating) AS review_count, ROUND(AVG(reviews.rating), 1) AS average_score FROM books JOIN reviews ON reviews.isbn_ref=books.isbn WHERE isbn = :isbn GROUP BY books.isbn", {"isbn": isbn}).fetchone()
        # do silly number formatting stuff
        d = dict(apiReturn.items())
        d['average_score'] = float(d['average_score'])
        return jsonify(d)
    
    # else just get book info
    apiReturn = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # if there's something there, return it as json  
    if apiReturn:
        d = dict(apiReturn.items())
        # d['average_score'] = 0.0  Better to just not include this if no reviews
        # d['review_count'] = 0     Better to just not include this if no reviews
        return jsonify(d)

    # else if no book found, return 404
    abort(404)