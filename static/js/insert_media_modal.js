/**
 * Created by tqn on 1/22/14.
 */

function display_message( params ) {
    var message_modal = $("#message__modal");
    if (params.type == 'on' ) {
        message_modal.find('.modal-body .message').text( params.message );
        message_modal.modal('show');
    } else {
        message_modal.modal('hide');
    }
}

function do_choose_item_selected( selected ) {

    if ( selected[0].nodeValue == null ) {
        do_append_media_to_left_panel( selected );
        do_append_media_to_right_panel( selected );
        set_saved_flag(0);
    } else {
        var obj = jQuery.parseJSON( selected[0].nodeValue );
        display_message( { type: 'on', message: obj.message } );
    }
}

function do_append_media_to_right_panel(selected_obj) {
    var object = selected_obj.clone(),
        data_id = object.attr('data-id'),
        right_panel = $('#current_product_display'),
        check_exist = right_panel.find('div[data-id="'+data_id+'"]').length;

    if (check_exist == 0) {
        var new_id = 'media_' + (new Date).getTime()
        object.removeClass('selected not-clone').css({
            'float': 'left',
            'margin-right': '6px'
        }).attr('id', new_id);

        object.draggable({
            helper: "clone",
            scroll: false,
            start: function(e, ui){},
            drag: function(e, ui){},
            stop: function(e, ui){}
        });

        object.appendTo(right_panel);
    }
}

function do_append_media_to_left_panel(selected_obj) {

    var top_position = 0,
        left_position = 0,
        last_media_item = false,
        object = selected_obj.clone(),
        left_panel = $('#collection_left_panel'),
        best_w = selected_obj.find('img').attr('best-w'),
        best_h = selected_obj.find('img').attr('best-h'),
        new_id = 'dropped_cloned_' + (new Date).getTime(),
        z_index = left_panel.find('.abilities').length + 1;

    //Set object's image with the best default size
    object.find('.image_collection').css({
        'width': best_w +'px',
        'height': best_h +'px'
    });

    //Set position for object when append it to left panel

    if (left_panel.find('.media-item').length >0 ) {
        last_media_item = left_panel.find('.media-item').last()

        top_position = parseInt(last_media_item.css('top').replace(/px/g, ''))
        left_position = parseInt(last_media_item.css('left').replace(/px/g, '')) + last_media_item.width()

        if(parseInt(left_position) + parseInt(best_w) <= design_panel.sizes.width - 10) {
            left_position += 10
        }else {
            left_position = 0
            top_position += last_media_item.height() + 6
        }
    }

    //Change object style and remove selected class
    object.removeClass('selected').css({
        'float' : 'left',
        'width': 'auto',
        'height': 'auto',
        'position' : 'absolute',
        'left' : left_position+'px',
        'top' : top_position+ 'px',
        'z-index': z_index
    }).attr('id', new_id);

    //Set size for image to using when resizing
    object.find('img').css({'width': '100%', 'height': '100%'});

    //init draggable for this item
    object.setDraggable(best_w);

    //Append to left panel
    object.appendTo(left_panel);

    left_panel.children('#drag_announce').hide();
    left_panel.children('#toolbar_set').show('normal');
}

$(function() {
    insert_media_action('#btn_insert_media', do_choose_item_selected);
})