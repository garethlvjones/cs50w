document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Handle when a new username is submitted
    document.getElementById('createUsernameForm').onsubmit = () => {
        var username =  document.getElementById('createUsernameText').value;
        // check if username already exists in application. boolean response
        socket.emit('does username exist', username, function(data) {
            if (data) {
                if (document.getElementById('bad username') === null) {
                    let badUsername = document.createElement('h3');
                    badUsername.id = 'bad username';
                    badUsername.innerHTML = 'Sorry, that username already exists, try again';
                    document.getElementById('usernameDoes').appendChild(badUsername);
                }
                document.getElementById('createUsernameText').value = '';
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
});