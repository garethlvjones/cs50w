document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    /****************************
        USERNAME STUFF
    */
    // Check for username in localstorage. If no, fill middle area with username field
    if (!localStorage.getItem('username')) {
        // TODO: FILL BODY WITH USERNAME STUFF
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
        // TODO: UPDATE BODY AREA WITH USERNAME STUFF
    };
    
    /****************************
        ROOM/NAV STUFF
    */

    socket.on('connect', () => {
        socket.emit('show rooms', (data) => {
            updateRoomList(data);
        });
    });

    socket.on('update room list', () => {
        socket.emit('show rooms', (data) => {
            updateRoomList(data);
        });
    });

    // create new room
    document.getElementById('new-room').onsubmit = () => {
        let newRoom = document.getElementById('room-name').value;
        // first check that room doesn't already exist. data returns boolean
        socket.emit('does room exist', newRoom, function(data) {
            if (data) {
                // true: room does exist
                // TODO: Show nice message to user to re-select or join 
                console.log('room does exist');
            } else {
                // false: room does not exist
                let username = localStorage.getItem('username');
                // create room store on the app
                socket.emit('create room', {'roomName': newRoom, 'username': username});
                // re-call function to update rooms listing to add new one
                socket.emit('show rooms', (data) => {
                    updateRoomList(data);
                });
                let roomURL = '/rooms/' + newRoom;
                window.location.assign(roomURL);
            }
        });
        // Clear contents & stop form from submitting
        document.getElementById('room-name').value = '';
        return false;
    };
});

/****************************
    GENERAL FUNCTIONS
*/
function updateRoomList(data) {
    if (data === "empty") {
        document.getElementById('rooms-list').innerHTML = "No rooms yet. Create one!";
    } else {
        // this is pretty hacky (jsonify, then clear and start again), but rooms list isn't too long, so whatevs
        document.getElementById('rooms-list').innerHTML = "";
        // let json = JSON.parse(data);
        data.forEach(element => {
            let li = document.createElement('li');
            li.innerHTML = '<a class="nav-link list-group-item" id=' + element + ' href="/rooms/' + element + '">' + element + '</a>';
            // if in room, set that nav item to be disabled
            document.getElementById('rooms-list').appendChild(li);
            if (roomName) {
                console.log('trying to delink room');
                console.log(roomName);
                document.getElementById(roomName).classList.add('disabled');
            }
        });
    }
}