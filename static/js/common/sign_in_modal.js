/**
 * Created by tqn on 3/21/14.
 */

function sign_in_modal_init( callback ) {

    var login_modal_id = 'loginModal',
        login_form = $('#login_form');

    $( document ).on('click','#login-button', do_sign_in)
    .on( "keydown", '#login_form input#login-password, #login_form input#login-username', function( event ) {
        if(event.which == 13){
            do_sign_in();
        }
    });

    function login_in_form_validate() {
        var u = login_form.find('#login-username').val(),
            p = login_form.find('#login-password').val();

        if (u != '' && p != '') {
            login_form.find('.username-group').removeClass('error');
            login_form.find('.password-group').removeClass('error');
            return true;
        } else {
            if (u == '') {
                login_form.find('.username-group').addClass('error');
            } else {
                login_form.find('.username-group').removeClass('error');
            }
            if (p == '') {
                login_form.find('.password-group').addClass('error');
            } else {
                login_form.find('.password-group').removeClass('error');
            }

            return false;
        }
    }

    function do_sign_in(){
        var checking = login_in_form_validate(),
            login_modal = $('#' + login_modal_id);
        if (checking) {

            login_modal.find("#login-button").attr('disabled', true);
            loading_modal(login_modal.attr('id'), 'on');

            login_action(function( response ) {
                if (response.code == 1) {
                    login_modal.find('.login-msg').removeClass('text-error').hide();

                    login_modal.modal('hide');
                    return callback( response );
                } else {
                    login_modal.find('.login-msg').text(response.message).addClass('text-error').show();
                }
            });
        }
    }

    function login_action( callback ){

        var login_modal = $('#' + login_modal_id);

        $.ajax({
            type: 'POST',
            url: login_form.attr('action'),
            data: login_form.serialize(),
            error: function( response ) {
                loading_modal(login_modal_id, 'off');
                login_modal.find('.login-msg').html('Login fail');
                login_modal.find("#login-button").removeAttr('disabled');
            },
            success: function ( response ) {
                loading_modal(login_modal_id, 'off');
                login_modal.find('.login-msg').html('Login success');
                login_modal.find("#login-button").removeAttr('disabled');
                login_modal.find('form input[name="csrfmiddlewaretoken"]').val($.cookie('csrftoken'));
            }
        }).done(function( response ) {
            return callback( response );
        });

    }

    init_sign_in_facebook('login_facebook', function ( response_str ) {
        $('#' + login_modal_id).modal('hide');
    })
}