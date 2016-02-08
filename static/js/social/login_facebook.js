$(document).ready(function(){
    init_sign_in_facebook('login_facebook', function ( response ) {
        window.open('/accounts/profile/','_parent')
    });
})
