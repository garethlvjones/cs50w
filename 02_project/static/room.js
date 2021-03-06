var roomName = window.location.pathname.replace("/rooms/","");

document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // store username to be used below
    var username = localStorage.getItem('username');

    socket.on('connect', () => {
        let data = {'roomName':roomName, 'username':username};

        // join the room on the server
        socket.emit('join room', data);
        
        // get any existing chat lines on start
        socket.emit('show current chats', {data: roomName}, (allChats) => {
            // clear chat lines first jic
            document.getElementById('chat-list').innerHTML = "";
            // set (or reset) chat line in localstorage to 0 on join
            localStorage.setItem(roomName, 0);
            // Add all existing chat lines
            allChats.forEach(element => {
                addChatLi(element);
            });
        });
    });

    /**************************** 
        CHAT UPDATES
    */

    // update when someone new joins the room
    socket.on('message',(data) => {
        document.getElementById('joiner').innerHTML = data;
    });

    // catch submit for chat line form
    document.getElementById('chat').onsubmit = () => {
        let newLine = document.getElementById('chat-out').value;
        socket.emit('new chat', {'username': username, 'chat': newLine, 'roomName': roomName});

        // Clear contents & stop form from submitting
        document.getElementById('chat-out').value = '';
        return false;
    };

    // append single chat line when a new entry is made
    socket.on('new line', (newChat) => {
        addChatLi(newChat);
    });

    // Show existing chat lines to user
    socket.on('get all', (allChats) => {
        allChats.data.forEach(element => {
            addChatLi(element);
        });
    });
});

// function to add a li for a chat element/s. Used by both allChats and add new line
function addChatLi(array) {
    let name = array[0];
    let chat = array[1];
    let chatTime = new Date(array[2]);
    let li = document.createElement('li');
    li.innerHTML = name + ':\t' + chat + '\t' + 'time: ' + chatTime;
    document.getElementById('chat-list').appendChild(li);
    // each time a line is added, update localStorage time value
    localStorage.setItem(roomName, chatTime);
}