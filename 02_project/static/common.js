document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    /****************************
        USERNAME STUFF
    */
    // Check for username in localstorage. If no, send to create page
    if (!localStorage.getItem('username')) {
        window.location.assign('username');
    } else {
        // say hello to user
        let hello = document.createElement('h3');
        hello.innerHTML = 'Hello ' + localStorage.getItem('username');
        document.getElementById('helloUsername').appendChild(hello);
    }
    // allow user to kill username (for testing only?)
    document.getElementById('killUsername').onclick = () => {
        localStorage.removeItem('username');
        // send them to create new username
        window.location.assign('username');
    };
    
    /****************************
        ROOM STUFF
    */
    socket.on('connect', () => {
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

function updateRoomList(data) {
    if (data === "empty") {
        document.getElementById('rooms-list').innerHTML = "No rooms yet. Create one!";
    } else {
        // this is pretty hacky (jsonify, then clear and start again), but rooms list isn't too long, so whatevs
        document.getElementById('rooms-list').innerHTML = "";
        // let json = JSON.parse(data);
        data.forEach(element => {
            let li = document.createElement('li');
            // TODO: Check for current room name, don't make it a link 
            li.innerHTML = '<a href="/rooms/' + element + '">' + element + '</a>';
            li.id = element;
            document.getElementById('rooms-list').appendChild(li);
        });
    }
}