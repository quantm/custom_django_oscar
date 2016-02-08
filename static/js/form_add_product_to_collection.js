/**
 * Created by tqn on 3/7/14.
 */

/*
 - TYPE:        List or Magazines
 - APPEND TO:   jQuery object to display html form
 - CALLBACK:    Is function to do when click Add button

 */

function init_add_product_to_collection( params, appendto, callback ) {

    if( params.load_callback != null ) {
        var ready_callback = params.load_callback;
        delete params['load_callback']
    }

    $.ajax( {
        type: 'GET',
        url: "/collection/add-product-to-collection-form/",
        data: params,
        error: function( jqxhr ) {

        },
        success: function ( data_returned ) {
            if( ready_callback != null ) {
                return ready_callback( data_returned );
            }
        }
    } ).done(function( data_response ) {

        try {
            appendto.html( data_response );
            appendto.find( '#add_btn' ).click( function(  ) {

                add_product_validate_form( function( response ) {

                    response.type = params.type;

                    return callback( response );

                });

            });
        }
        catch( err ) {

        }

    } );

    $( document ).on( "click", 'button#create_btn', function( event ) {

        add_text_to_option( function(  ) {
            display_create_new_form( 'hide' );
            appendto.find( '#add_btn' ).removeAttr( 'disabled' );
        });

    }).on( "change", 'select#my_collections', function( event ) {

        var selected = $(this).find("option:selected"),
            new_option = selected.attr("new"),
            option_value = selected.val();

        if ( parseInt( new_option ) == 1 ) {

            appendto.find('#add_btn').attr( 'disabled', 'disabled' );
            display_create_new_form( 'show' );

        } else {

            appendto.find( '#add_btn' ).removeAttr( 'disabled' );
            display_create_new_form( 'hide' );
        }

    });

    function display_create_new_form( status ) {

        var new_form = appendto.find( '#create_new_form'),
            add_form = appendto.find( '#add_form' );

        if( status == 'show' ) {
            new_form.show( 'fast' );

        } else {
            new_form.hide( 'fast' );
            add_form.show( 'fast' );

        }

    }

    function add_text_to_option( local_callback ) {

        appendto.find( '#my_collections option[value="0"]').remove();

        var name = appendto.find( "input#collection_name" ).val(),
            selected = appendto.find( "#my_collections option:selected" );
        if( name == '' ) {
            appendto.find('#create_new_form').addClass( 'error' );
            return false;
        } else {
            appendto.find('#create_new_form').removeClass( 'error' );
        }

        selected.before('<option new="0" value="0">'+name+'</option>');

        appendto.find( '#my_collections option[value="0"]').attr('selected', true);

        return local_callback(  );
    }

    function add_product_validate_form( local_callback ) {

        var selected = appendto.find( "#my_collections option:selected" );
        if( selected.val() == -1) {
            appendto.find( '#create_new_form' ).addClass( 'error' );
        } else {
            var data = { id: selected.val(), name: selected.text() }
            return local_callback( data );
        }

    }

}
