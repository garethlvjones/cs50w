document.addEventListener('DOMContentLoaded', () => {
    /****************************
        VARIABLES
    */
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    /****************************
        USERNAME STUFF
    */
    // Check for username in localstorage. If no, send to create page
    if (!localStorage.getItem('username')) {
        // TODO: Change to fill main window
        window.location.assign('username');
    } else {
        // say hello to user
        let hello = document.createElement('p');
        hello.innerHTML = 'Hello ' + localStorage.getItem('username');
        document.getElementById('helloUsername').appendChild(hello);
    }
    // allow user to kill username (for testing only?)
    document.getElementById('killUsername').onclick = () => {
        localStorage.removeItem('username');
        // send them to create new username
        window.location.assign('username');
    };

     // Handle when a new username is submitted
     document.getElementById('createUsernameForm').onsubmit = () => {
        var username =  document.getElementById('createUsernameText').value;
        // check if username already exists in application. boolean response
        socket.emit('add user', username, (data) => {
            if (!data) {
                if (document.getElementById('bad username') === null) {
                    let badUsername = document.createElement('h3');
                    badUsername.id = 'bad username';
                    badUsername.innerHTML = 'Sorry, that username already exists, try again';
                    document.getElementById('usernameDoes').appendChild(badUsername);
                }
                // TODO NOT NEEDED? document.getElementById('createUsernameText').value = '';
            } else {
                localStorage.setItem('username', username);
                // send user to main window, now that username is set
                window.location.assign('/');
            }
        });
       // empty form text field & stop from submitting
        document.getElementById('createUsernameForm').value = '';
        return false;
    };

    /****************************
        ROOM/NAV STUFF
    */

    // Set user's room if not already set
    if (!localStorage.getItem('roomName')) {
        localStorage.setItem('roomName', 'home');
    }
    // On connect, get rooms list
    // data is returned as string list
    socket.on('connect', () => {
        socket.emit('show rooms', data => {
            updateRoomList(data);
        });

        // handle server restarting when user in a named room (DEBUG ONLY?)
        let roomName = localStorage.getItem('roomName');
        socket.emit('does room exist', roomName, (data) => {
            if (!data) {
                localStorage.setItem('roomName', 'home');
            }
        });
    });

    // When room is added, this is called to update the list
    // data is a list of room strings in the form [item, item, item, item]
    socket.on('update room list',(data) => {
        updateRoomList(data);
    });

    // create new room
    document.getElementById('new-room').onsubmit = () => {
        let newRoom = document.getElementById('room-name').value;
        // first check that room doesn't already exist. data returns boolean
        socket.emit('does room exist', newRoom, (data) => {
            if (data) {
                // TODO: Show nice message to user to re-select or join 
                console.log('room does exist');
            } else {
                // false: room does not exist
                let username = localStorage.getItem('username');
                // create room store on the app
                socket.emit('create room', {'roomName': newRoom, 'username': username});
            }
        });
        // Clear contents & stop form from submitting
        document.getElementById('room-name').value = '';
        return false;
    };

    // called after user has created room
    // data is a roomname string
    socket.on('now join room', (data) => {
        socket.emit('join room',{
            'roomName': data, 
            'username': localStorage.getItem('username'), 
            'oldRoomName': localStorage.getItem('roomName')
        });
    });

    // called after user has joined room on server
    // data is in the form {roomName: roomName, username: username, oldRoomName: oldRoomName}
    socket.on('joined room', (data) => {
        document.getElementById('roomName').innerHTML = 'Room: ' + data.roomName;
        localStorage.setItem('roomName', data.roomName);
    });

    socket.on('update room users', (data) => {
        let userList = document.getElementById('users');
        userList.innerHTML = '';
        data.forEach(element => {
            let li = document.createElement('li');
            li.innerHTML = element;
            userList.appendChild(li);
        });
    });

    function updateRoomList(data) {
        if (data === "empty") {
            document.getElementById('rooms-list').innerHTML = "No rooms yet. Create one!";
        } else {
            document.getElementById('rooms-list').innerHTML = "";
            data.forEach(element => {
                let currentRoomName = localStorage.getItem('roomName');
                let li = document.createElement('li');
                li.classList.add('nav-item');
                if (currentRoomName === element) {
                    document.getElementById('rooms-list').appendChild(li);
                    li.classList.add('nav-link', 'active');
                    li.innerHTML = element;
                } else {
                    li.innerHTML = '<a class="nav-link" id=' + element + ' href="#">' + element + '</a>';
                    document.getElementById('rooms-list').appendChild(li);
                    document.getElementById(element).addEventListener("click", () => {
                        socket.emit('join room', {'roomName': element, 'username': localStorage.getItem('username'), 'oldRoomName': currentRoomName}); 
                    });
                }
            });
        }
    }

    /****************************
        CHAT STUFF
    */

    // update when someone new joins the room
    socket.on('message',(data) => {
        document.getElementById('joiner').innerHTML = data;
    });

    // catch submit for chat line form
    document.getElementById('chat').onsubmit = () => {
        let newLine = document.getElementById('chat-out').value;
        socket.emit('new chat', {'username': localStorage.getItem('username'), 'chat': newLine, 'roomName': localStorage.getItem('roomName')});

        // Clear contents & stop form from submitting
        document.getElementById('chat-out').value = '';
        return false;
    };

    // Show existing chat lines to user
    // allChats is an array of chat lines in the form [user, chatline, time]
    socket.on('get all chat lines', (allChats) => {

        // first clear out any existing chat lines
        document.getElementById('chat-list').innerHTML = '';

        if (allChats.length > 0) {
            allChats.forEach(element => {
                addChatLi(element);
            });
        }
    });

    // append single chat line when a new entry is made
    socket.on('new line', (newChat) => {
        addChatLi(newChat);
    });

    // function to add a li for a chat element/s. Used by both allChats and add new line
    function addChatLi(array) {
        let name = array[0];
        let chat = array[1];
        let chatTime = new Date(array[2]);
        let li = document.createElement('li');
        li.innerHTML = name + ':\t' + chat + '\t' + 'time: ' + chatTime;
        document.getElementById('chat-list').appendChild(li);
    }
});

