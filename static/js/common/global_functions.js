// JavaScript Document
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getCookie(name) {
	 var cookieValue = null;
	 if (document.cookie && document.cookie != '') {
		 var cookies = document.cookie.split(';');
		 for (var i = 0; i < cookies.length; i++) {
			 var cookie = jQuery.trim(cookies[i]);
			 // Does this cookie string begin with the name we want?
			 if (cookie.substring(0, name.length + 1) == (name + '=')) {
				 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				 break;
			}
		}
	}
	return cookieValue;
}

function ajax_notifications() {
    var notify = $('a#notify-number');
    $.get('/accounts/ajax_notifications/', function(data){
        if(data.num_unread_notifications > 0){
            notify.attr('href','/accounts/notifications/inbox/').find('.number').html(data.num_unread_notifications).show();
        }
    },'json');
}

function loading_modal(modal_id, type) {
    var loading = $('#' + modal_id).find('.modal-footer .loading');
    if ( type == 'on' ) {
        loading.show();
    } else {
        loading.hide();
    }
}

/*
 TYPE: on or off.
 TYPE CLASS:
    - muted
    - text-warning
    - text-error
    - text-info
    - text-success
 MESSAGE: is string
 */
function message_modal(modal_id, params) {

    var message_box = $('#' + modal_id).find('.modal-footer .message');

    if ( params.type == 'on' ) {
        message_box.removeClass().addClass('message').addClass(params.class).text(params.message).show();
    } else {
        message_box.removeClass().addClass('message').hide().text();
    }
}

jQuery(function($){
    $.ajaxSetup({
        beforeSend: function(jqXHR, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                jqXHR.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        },
        complete: function( jqXHR, settings ) {

            if (jqXHR.status == 403) {

                if (this.refresh_login_error) {
                    window.location.reload();

                } else {
                    try {

                        var authentication = eval("(" + jqXHR.responseText.trim() + ")");

                        if (! authentication.auth) {
                            $("#loginModal").on({
                                shown: function() {
                                    $('.modal.fade.in').not("#loginModal").modal('hide');
                                }
                            })
                            .modal('show');
                        }
                    }
                    catch( err ) {

                    }
                }
            }
        }
    });
    setInterval(ajax_notifications, 1500000);
});

