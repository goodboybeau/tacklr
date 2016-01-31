var socket = io.connect('http://' + document.domain + ':5000' );

socket.on('tweet', function(tweet){
  console.log('message: ' + tweet.id);
});

var ping = function(msg) {
  console.log('get tweet complete');
  socket.emit('get tweet complete', msg);
};

var success = function() {
    console.log('get tweet complete');
};

socket.on('connect', function() {
    console.log('on connect')
    setInterval( function() {
        console.log('getting tweet');
        socket.emit('get tweet', {}, success);
        }, 2000);

    console.log('setInterval for "get tweet" emission');
});