/**
 * Created by tqn on 1/17/14.
 */

var $login_modal = $("#loginModal");
jQuery(function($){
    $( document ).on( "click", '#login-button', modal_sign_in_action);
    $login_modal.on('show', function(){
		$login_modal.find('.login-msg').hide();
	});
});

function modal_sign_in_action(){

    var $this = $(this),
        login_form = $login_modal.find('#login_form');

    $.post(login_form.attr('action'), login_form.serialize(), function(data, textStatus, jqXHR){
        if (data == 'success') {
            $('.login-msg').html('Login success');
            $login_modal.modal('hide');
        }
        if (data == 'error') {
            $('.login-msg').html('Login fail');
            $this.removeAttr('disabled');
        }
    })
    .fail(function(data) {
        alert('Error');
        $this.removeAttr('disabled');
    })
}
