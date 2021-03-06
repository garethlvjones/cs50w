import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # create()
    fill()

def create():
    # Create table users
    # db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR UNIQUE NOT NULL,password VARCHAR NOT NULL)")
    # db.commit()

    # create table books
    # db.execute("CREATE TABLE books (isbn VARCHAR NOT NULL UNIQUE PRIMARY KEY, author VARCHAR,title VARCHAR NOT NULL, year INTEGER)")
    # db.commit()

    # create table reviews
    # db.execute("CREATE TABLE reviews (isbn_ref VARCHAR REFERENCES books, user_id INTEGER REFERENCES users, rating INTEGER NOT NULL, text VARCHAR)")
    # db.commit()
    pass

def fill():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added {title} by {author} with {isbn} isbn to db")
    db.commit()

if __name__ == "__main__":
    main()

    