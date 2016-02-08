/**
 * Created by tqn on 3/18/14.
 */

function pagination ( content_id, callback) {

    window.SCROLLER = {
        is_scrolling: 1,
        current_page: 1
    };

    $( window ).scroll( function () {
        on_window_scroll( callback )
    } );

    $( window ).on( 'load',function(  ){
        $( '#' + content_id ).fadeIn( 800 );
        if( window.Masonry ){
            window.MSNRY = $( '#' + content_id ).masonry({
                columnWidth: 38,
                itemSelector: '.item'
            });
        }
    });

    function on_window_scroll( callback ) {

        if ($(window).scrollTop() >= ($(document).height() - $(window).height()) / 1.1 ) {

            var total_page = $('#total-page').attr('data-total-page'),
                link_load = $('#total-page').attr('data-load-more');

            if ( (window.SCROLLER.is_scrolling == 1) && (total_page > 1 ) &&
                (window.SCROLLER.current_page < total_page) ) {
                get_page_on_scroll( link_load, callback );
            }

        }
    }

    function get_page_on_scroll( link_load, callback ) {

        window.SCROLLER.is_scrolling = 0;
        $('.total-page.loading').show();

        $.ajax({
            type: 'GET',
            url: link_load + "?page=" + (parseInt(window.SCROLLER.current_page) + 1),
            refresh_login_error: true,
            error: function( response ) {
                $('.total-page.loading').hide();
            },
            success: function ( response ) {
                if( window.Masonry ){
                    var moreImages = $($.parseHTML( response ));
                    window.MSNRY.append( moreImages );
                    moreImages.hide();

                    window.MSNRY.imagesLoaded(function(){
                        moreImages.show();
                        window.MSNRY.masonry('appended', moreImages );
                    });
                } else {
                    $( '#' + content_id).append( response );
                }
            }
        })
        .done(function( response ) {
            $('.total-page.loading').hide();
            window.SCROLLER.is_scrolling = 1;
            window.SCROLLER.current_page = window.SCROLLER.current_page + 1;

            return callback( response );
        });

    }

}