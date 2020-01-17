import os, random, string
import time
from room import Room

from flask import Flask, flash, jsonify, render_template, request
from flask_socketio import SocketIO, emit, send, join_room, leave_room
# from flask_login import LoginManager - TODO: Decide on using login
# from flask_sqlalchemy import SQLAlchemy - TODO: Store login data in simple db


# DB for logins
# db = SQLAlchemy()

app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

# Session(app)
socketio = SocketIO(app)  

######
# TODO:
#     - stay within one url, single page app. hash roomname and #
#     - owner can kill room
#     - format current room using bootstrap
#     - format date nicely
#     - format page nicely
#         - show current time
#     - remove 'blah entered the room' after a while
#     - Login using flask login (adding to localstorage just for show)
#     - clean up forms. Stop blank enters, click twice, etc
#     - maybe private chat option

######################
## GLOBAL VARIABLES ##
######################

# list of current Room objects
# contains roomname as as {string roomName : Object room}
roomsDict = {} 

# dict to hold usernames & id (TODO: id may not be needed)
usernames = {}
userId = 0

###################
##    ROUTES     ##
###################

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/username')
def username():
    return render_template("username.html")

@app.route('/rooms/<string:roomName>')
def goToRoom(roomName):
    return render_template("room.html", roomName=roomName)


##########################
##  Username Socket Actions  ##
##########################

# return true if username does not already exist, create user and thhen false if it does
@socketio.on('does username exist')
def checkUsername(username):
    if username in usernames.values():
        return True
    else:
        global userId 
        usernames[userId] = username
        userId += 1
        return False

# Send user to the create username page if there's no username in localstorage
@socketio.on('no username')
def createUsername():
    return render_template("username.html")

##########################
##  Room Actions  ##
##########################
@socketio.on('show rooms')
def showRooms():
    # check if room list is empty
    if not roomsDict:
        return "empty"
    # return list of rooms names as strings
    return list(roomsDict.keys())

@socketio.on('does room exist')
# used to check if a room exists. Called both on load and periodically
def doesRoomExist(roomName):
    if roomName in roomsDict.keys():
        return True
    return False

@socketio.on('create room')
# only called when existing room check has previously been made, so can assume room doesn't exist
def createRoom(json):
    roomName = json['roomName']
    username = json['username']

    # create room object
    newRoom = Room(roomName,username)

    # add roomname to roomslist dict & broadcast new room for list
    roomsDict[roomName] = newRoom
    emit('update room list', broadcast=True)
    # TODO BROADCAST ROOM UPATE

@socketio.on('join room')
def joinRoom(data):
    join_room(data['roomName'])
    send(data['username'] + " has entered the room.", room=data['roomName'])

##########################
##  Chat Line Socket Actions  ##
##########################

@socketio.on('show current chats')
def showCurrentChats(room):
    # get room object
    # currentRoom = roomsDict[room['data']]

    # get all chats from room
    list = roomsDict[room['data']].getChatsList() 

    # TODO get chats for room
    # emit('get all', {'data': chatsList})
    return list

@socketio.on('new chat')
# data is a dict in the form {'username': username, 'chat': newLine, 'roomName': roomName}
def appendChat(data):
    # create reference to room object
    currentRoom = roomsDict[data['roomName']]
    
    # call addChat and add line
    currentRoom.addChat(data)

    # Broadcast clients in room to append the new line, rather than re-do whole list each time
    emit('new line', list(currentRoom.getLastChatLine()), room=data['roomName'])