document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    /* TODO
        - Add check for blank entry, or stop button until text is in it
        - user login stored as localstorage
        - existing chat pre-filled for when new browser session begins
        - Rooms (local storage + store list of rooms)
    */

    // If no username, show form to get one
    if (!localStorage.getItem('username')) {
        showUsername(true);
    } else {
        //show username and say hello
        let username = localStorage.getItem('username');
        document.getElementById('usernameh3').innerHTML='hello ' + username;
        // create ability to remove username (mostly for testing)
        document.getElementById('killUsername').onclick = () => {
            localStorage.removeItem('username');
            showUsername(false);
        };
        showUsername(false);
    }

    // Handle when a new username is submitted
    document.getElementById('createUsernameForm').onsubmit = () => {
        let username =  document.getElementById('createUsernameText').value;
// TODO
        // check if username already exists
        if (socket.emit('check username', {data:'test'})) {
            // add username to localstorage
            console.log('yaytrue');
        }
        else {
            console.log('boonoo');
        }

        localStorage.setItem('username',username);
        socket.emit('add username', {data: username});

        // Reset field to blank
        document.getElementById('createUsernameForm').value = '';
        // show hello
// TODO
        // stop form from submitting
        return false;

    };

    // Add new chat line to app when user submits
    document.getElementById('chat').onsubmit = () => {
        let new_chat = document.getElementById('chat-out').value;
        socket.emit('new chat', {data: new_chat});

        // Reset field to blank
        document.getElementById('chat-out').value = '';
        // stop form from submitting
        return false;
    };

    // When app sends new chat line, append this to existing chat
    socket.on('add chat line', (data) => {

        // convert timestamp to 'x time ago'
        let date = new Date();
        let timestamp = date.getTime();
        console.log(timestamp + ' stamp');

        let key = Object.keys(data)[0];
        console.log(key + ' key');
        let keynum = parseInt(key * 1000);

        let timePassed = timestamp - keynum;
        console.log(timePassed + ' timepassed');

        // append new chat line to list
        // let key = Object.keys(data)[0];
        let value = data[key];
        let ul = document.getElementById('chat-list');
        let li = document.createElement("li");
        li.appendChild(document.createTextNode(key + ', ' + value));
        ul.appendChild(li);
    });


    // func to show/hide create username code blocks
    // if no username, form to get username is shown
    // if username exists (or is entered) hello is shown instead
// REPLACE THIS WITH hasUsername. Include show below, plus fill in name
    function showUsername (onoff) {
        if (onoff) {
            document.getElementById('helloUsername').setAttribute('class','');
            document.getElementById('createUsername').setAttribute('class','collapse');
            return;
        }
        document.getElementById('helloUsername').setAttribute('class','collapse');
        document.getElementById('createUsername').setAttribute('class','');
    }


});