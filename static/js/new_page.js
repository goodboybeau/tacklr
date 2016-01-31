
var creds = null;

var retrieve_creds = function(){
    if(!email || !password)
    {
        email = $('#email').val(), password = $('#password').val() ;

        password = CryptoJS.SHA256(password);
        creds = {'email':email, 'password':password};
    }
}

var create_page_request = function(p) {
    if (!creds)
    {
        retrieve_creds();
    }

    return {req:{page:p}, auth:creds};
};

var do_page_request = function (page) {

    page_req = create_page_request(page);
    console.log('sending ' + JSON.stringify(page_req));

    socket.emit('page_request', page_req);
};


socket.on('page_response', function(page){
//    $('body').html(res.data);
//    return;
    var doc = document.open('text/html', 'replace');
    doc.write(page.data);
    doc.close();
});