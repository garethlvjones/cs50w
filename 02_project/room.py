import time

# Create class for Rooms
class Room:
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.timeCreated = int(time.time() * 1000)
        self.chatsList = []
    
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

    def getLastChatLine(self):
        return self.chatsList[-1]

    def getChatsPastThisTime(self, time):
        # time is in javascript format
        
# iterate backwards through list to get number which is equal OR lower. get n. get length


        return 1

    def getName(self):
        return self.name

    def getCreator(self):
        return self.creator

    def getTimeCreated(self):
        return self.timeCreated