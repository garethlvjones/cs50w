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

    //call showrooms on load. Is this good practice?
    showRooms();

    // to catch broadcast of room update
    socket.on('update rooms', () => {
        showRooms();
    });

    // function to show rooms list
    function showRooms() {
        socket.emit('show rooms', function(data) {
            // this is pretty hacky (jsonify, then clear and start again), but rooms list isn't too long, so whatevs
            console.log(data);
            document.getElementById('rooms-list').innerHTML = "";
            let json = JSON.parse(data);
            json.forEach(element => {
                let li = document.createElement('li');
                li.innerHTML = 'room: ' + element.name + ' created by: ' + element.creator;
                li.id = element.name;
                document.getElementById('rooms-list').appendChild(li);
            });
        });
    }

    // create new room
    document.getElementById('new-room').onsubmit = () => {
        let newRoom = document.getElementById('room-name').value;

        socket.emit('does room exist', newRoom, function(data) {
            if (data) {
                // TODO: Show nice message to user to re-select or join 
                console.log('room does exist');
            } else {
                console.log('room does not exist');
                let username = localStorage.getItem('username');
                socket.emit('create room', {'roomName': newRoom, 'username': username}, function(data) {
                    let roomName = '/rooms/' + data.roomName;
                    window.location.assign(roomName);
                });
            }
        });

        // Clear contents & stop form from submitting
        document.getElementById('room-name').value = '';
        return false;
    }; 
});