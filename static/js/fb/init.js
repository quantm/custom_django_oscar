/**
 * Created by tqn on 1/10/14.
 */
//console.log(fbAppId);

window.fbAsyncInit = function() {
    FB.init({
        appId : fbAppId, // App ID
        status : true,   // check login status
        cookie : true,   // enable cookies to allow the server to access the session
        xfbml : true     // parse page for xfbml or html5 social plugins like login button below
    });
    FB.Event.subscribe('auth.authResponseChange', function(response) {
    // Here we specify what we do with the response anytime this event occurs.
        if (response.status === 'connected') {
            // The response object is returned with a status field that lets the app know the current
            // login status of the person. In this case, we're handling the situation where they
            // have logged in to the app.
        } else if (response.status === 'not_authorized') {
            // In this case, the person is logged into Facebook, but not into the app, so we call
            // FB.login() to prompt them to do so.
            // In real-life usage, you wouldn't want to immediately prompt someone to login
            // like this, for two reasons:
            // (1) JavaScript created popup windows are blocked by most browsers unless they
            // result from direct interaction from people using the app (such as a mouse click)
            // (2) it is a bad experience to be continually prompted to login upon page load.
            FB.login();
        } else {
            // In this case, the person is not logged into Facebook, so we call the login()
            // function to prompt them to do so. Note that at this stage there is no indication
            // of whether they are logged into the app. If they aren't then they'll see the Login
            // dialog right after they log in to Facebook.
            // The same caveats as above apply to the FB.login() call here.
            FB.login();
        }
    });
};//END window.fbAsyncInit

//------------------------------------------------------------
(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s); js.id = id;
    js.src = "http://connect.facebook.net/en_US/all.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

//------------------------------------------------------------
function getAccessToken() {
    FB.api('/me', function(response) {
        var accessToken = FB.getAuthResponse()['accessToken'];
        return accessToken;
    });
}

//------------------------------------------------------------
function getUserAlbums(callback) {
    FB.api('/me/albums', function(response) {
        return callback(response);
    });
}

//------------------------------------------------------------
function sign_in_facebook(callback){
    var auth = FB.getAuthResponse();
    if(auth==null || auth == ''){
        FB.login(function(login_response) {
            if (login_response && !login_response.error) {
                return callback(login_response.authResponse);
            }
        }, {
            scope: 'email, user_likes, publish_actions, publish_stream, user_activities, publish_checkins, user_photos, friends_photos'
        });
    }else{
        return callback(auth);
    }
}

function init_sign_in_facebook( sign_in_facebook_id, callback ) {

    $( document ).on( "click", '#'+sign_in_facebook_id, function() {
        sign_in_facebook( function( login_response ) {
            sign_in_inside_site( function ( response ) {
                return callback( response );
            });
        });
    });

    function sign_in_inside_site( callback ){

        FB.api("/me",
            function (profile_response) {
                if (profile_response && !profile_response.error ) {
                    $.ajax({
                        type: 'POST',
                        url: '/accounts/sign-up/',
                        data: profile_response,
                        success: function ( response ) {
                            $("#loginModal").find('form input[name="csrfmiddlewaretoken"]').val($.cookie('csrftoken'));
                        },
                        error: function( jqXHR, settings ) {
                        }
                    }).done( function( response ) {
                        return callback( response );
                    });
                } else {
                    window.location.reload();
                }
            }
        );
    }//end function sign_in_inside_site
}//end init_sign_in_facebook
