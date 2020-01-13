import time

# Create class for Rooms
class Room:
    name = ""
    creator = ""
    chatsList = [] # contains chat lines as tuples with (username, chat line, time made)
    timeCreated = 0

    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.timeCreated = int(time.time() * 1000)
    
    # add a new chat line
    # ChatDetail dict will contain 'username', 'chat' values
    def addChat(self, chat):
        # get time now in javascript-friendly way
        timeNow = int(time.time() * 1000)

        # create new tuple and append to full chat list
        newLine = (chat["username"], chat["chat"], timeNow)
        self.chatsList.append(newLine)

    def getChatsList(self):
        return self.chatsList

    def getLatestChatsList(self):
        return self.chatsList[-1]

    def getName(self):
        return self.name

    def getCreator(self):
        return self.creator

    def getTimeCreated(self):
        return self.timeCreated