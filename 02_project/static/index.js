document.addEventListener('DOMContentLoaded', () => {
    /****************************
        VARIABLES
    */
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    var dfgd;

    /****************************
        USERNAME STUFF
    */
    // Check for username in localstorage. If no, send to create page
    if (!localStorage.getItem('username')) {
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








});