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
#     - owner can kill room
#     - hide chat in home room
#     - fix username check
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

# dict to hold usernames to stop duplicates
usernames = {}

###################
##    ROUTES     ##
###################

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/username') 
def username():
    return render_template("username.html")

##########################
##  Username Socket Actions  ##
##########################

# return true if username does not already exist, create user and thhen false if it does
@socketio.on('add user')
def checkUsername(username):
    if username in usernames.values():
        return False
    else:
        global userId 
        usernames[userId] = username
        return True



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
# roomName is string
def doesRoomExist(roomName):
    if roomName in roomsDict.keys():
        return True
    return False

@socketio.on('create room')
# only called when existing room check has previously been made, so can assume room doesn't exist
# json is in the form {roomName: roonmName, username: username}
def createRoom(json):
    roomName = json['roomName'] 
    username = json['username']

    # create room object
    newRoom = Room(roomName,username)

    # add roomname to roomslist dict & broadcast new room for list
    roomsDict[roomName] = newRoom
    emit('update room list', showRooms(), broadcast=True)
    emit('now join room', roomName)

    
@socketio.on('join room')
# data is strings in the form {roomName: roomName, username: username, oldRoomName: oldRoomName}
def joinRoom(data):
    username = data['username']
    oldRoom = data['oldRoomName']
    newRoom = data['roomName']
    newRoomObject = roomsDict[newRoom]
    
    # skip the leaving stuff if it's home room
    if (data['oldRoomName'] != "home"): 
        oldRoomObject = roomsDict[oldRoom]
        send(username + " has left the room", room=oldRoom)
        oldRoomObject.removeUser(username)
        leave_room(oldRoom)
        emit('update room users', oldRoomObject.getUsers(), room=oldRoom)

    join_room(newRoom)
    newRoomObject.addUser(username)
    emit('update room users', newRoomObject.getUsers(), room=newRoom)
    send(username + " has entered the room.", room=newRoom)
    emit('joined room', data, room=newRoom)
    emit('update room list', showRooms())
    emit('get all chat lines', roomsDict[newRoom].getChatsList())


##########################
##  Chat Line Socket Actions  ##
##########################

@socketio.on('new chat')
# data is a dict in the form {'username': username, 'chat': newLine, 'roomName': roomName}
def appendChat(data):
    # create reference to room object
    currentRoom = roomsDict[data['roomName']]
    
    # call addChat and add line
    currentRoom.addChat(data)

    # Broadcast clients in room to append the new line, rather than re-do whole list each time
    emit('new line', list(currentRoom.getLastChatLine()), room=data['roomName'])


if __name__ == "__main__":
    socketio.run(app, debug=True)