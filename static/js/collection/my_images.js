// JavaScript Document
var view_modal = $("#view_image_modal");

//------------------------------------------------------------	
$(function() {

    var content_id = "my_images";

    view_modal.on('hide', function() {});

    $( document ).on( "click", '#' + content_id + ' img', view_image);

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


})//end $(function() {


function view_image(event){
    event.preventDefault();

    var data_id = $(this).attr('data-id')
        current_image = $('#image_'+data_id),
        preview_url = current_image.children('a').attr('href');

    view_modal.find('#img_preview').attr('src', preview_url);
    view_modal.find('#myModalLabel').html(current_image.children('a').attr('title'));

    view_modal.modal('show');

}