/**
 * Created by tqn on 3/17/14.
 */


function remove_item( content_id, callback ) {

	var message_confirm = $("#message_confirm"),
        message_modal = $("#message_modal");

	$( document ).on( "click", '#' + content_id +' .item .icon-remove', function() {

        var data_parent = $(this).attr('data-parent');

        do_remove( $(this), function( response ) {

            message_confirm.modal('hide');
            if( response.code == 1 ) {
                $("#" + data_parent).remove();
            } else {
                message_modal.find('.modal-body .message').text( response.message );
                message_modal.modal('show');
            }

            return callback( response );

        });
    });

	//unbind click for modal
	message_confirm.on( 'hide', function(  ){
		message_confirm.find( 'button.btn, a.btn' ).unbind( 'click' );
	});

    //Do remove click
    function do_remove( jObject, callback ){

        var url_remove = jObject.attr( 'data-link' );

        //Show confirm
        message_confirm.modal( 'show' ).find( 'button#yes-btn' ).one( 'click', function(  ){
            loading_modal( message_confirm.attr('id'), 'on' );
            remove_media_item( url_remove, function( response ) {

                return callback( response );

            });

        });
    }

    //Remove
    function remove_media_item( url_remove, callback ){

        $.ajax({
            type: 'POST',
            url: url_remove,
            success: function ( response ) {
                loading_modal( message_confirm.attr('id'), 'off' );
            },
            error: function( jqXHR ) {
                if (jqXHR.status != 403) {
                    var response = eval("(" + jqXHR.responseText.trim() + ")");
                    response.code = jqXHR.status;
                    return callback( response );
                }
            }
       }).done(function( data ) {

            return callback( data );

       });
    }

}
