$(function() {

    var content_id = "my_list";

    pagination( content_id, function( response ) {

    });

    remove_item( content_id, function( response ) {

        if( window.Masonry ){
            $("#" + content_id).masonry();
        }
    });

    sign_in_modal_init( function() {
        window.SCROLLER.is_scrolling = 1;
        $(document).scrollTop(0);
    });

})
