
var socket = io.connect('http://' + document.domain + ':5000' );

socket.on('connect', function () { console.log('connected!'); });

var user = null, password = null;

