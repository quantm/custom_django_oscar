// JavaScript Document
var top_menu = $('#toolbar_set'),
    left_menu = $('#vertical_left_toolbar'),
    save_modal = $('#collection_modal_save'),
    open_modal = $('#open_collections_modal'),
    confirm_modal = $('#collection_modal_message_confirm'),
    design_panel = get_design_panel('#collection_left_panel');

$(function() {

    var flags = get_flags_value();

    //set draggable for items in right panel
    $( "#current_product_display > .abilities" ).draggable({
        helper: "clone",
        scroll: false
    });

    //set droppable for left_panel
    design_panel.obj.droppable({
        accept: ".abilities",
        drop: function( event, ui ) {
            dropped_item(ui);
        }
    });

    //if collection be redirect from Gellary page and it not have style,
    // so we need set style to display for nice
    if (flags.style == 0) {
        reset_style_items_to_can_set_abilities_when_display_from_gallery();
    }

    //when document ready, if collection saved, we hide save draft button
    if (flags.saved == 1 ) {
        left_menu.find("#save_draft").attr('disabled', true);
    }

    design_panel.obj.scroll(function() {
        $(this).scrollLeft(0);
    });

    display_items_when_open_collection_from_gallery();

    sign_in_modal_init(function(){});

    $( document)

    .on('click', '#' + top_menu.attr('id') + ' .btn', function() {
        toolbar_bind_click_action($(this));
    })

    .on('click', '#' + left_menu.attr('id') + ' .btn', function() {
        left_toolbar_menu_click_action($(this));
    })

    .on('submit', '#' + save_modal.attr('id') + ' #collection_form', function() {
        save_collection_submit_form();
        return false;
    })

    .on('click', '#' + open_modal.attr('id') + ' .box-content a', function( event ) {
        event.preventDefault();
        loading_modal(open_modal.attr('id'), 'on');
        collection_display_after_open_from_popup($(this));
    })

    .on('click', '#' + confirm_modal.attr('id') + ' #no', do_action_when_user_answer_no)

    .on('click', '#' + confirm_modal.attr('id') + ' #yes-btn', do_action_when_user_answer_yes)

    .on('click', '.modal.fade a.data-dismiss-modal', function() {
        var modals = $(this).parents('.modal.fade');
        modals.modal('hide');
    });


});

$.fn.hasScrollBar = function() {
    return this.get(0).scrollHeight > this.height();
}

$.fn.rotationDegrees = function () {
    var angle = 0,
        matrix = this.css("-webkit-transform") ||
        this.css("-moz-transform")    ||
        this.css("-ms-transform")     ||
        this.css("-o-transform")      ||
        this.css("transform");
    if (typeof matrix === 'string' && matrix !== 'none') {
        var values = matrix.split('(')[1].split(')')[0].split(','),
            a = values[0],
            b = values[1],
            angle = Math.round(Math.atan2(b, a) * (180/Math.PI));
    }

    return angle;
};

$.fn.rotatedSize = function(angle) {
    var rads = angle * Math.PI / 180,
        cosA = Math.cos(rads),
        sinA = Math.sin(rads),
        width = this.width(),
        height = this.height(),

        rotatedWidth = Math.round(width * Math.abs(cosA) + height * Math.abs(sinA)),
        rotatedHeight = Math.round(width * Math.abs(sinA) + height * Math.abs(cosA)),
        rotSize = { 'width': rotatedWidth, 'height': rotatedHeight };

    return rotSize;
}

$.fn.setDraggable = function(minus_width) {

    var minus_w = parseInt(this.width());

    if (minus_width != null) {
        minus_w = minus_width
    }

    var right_containment = design_panel.position.left + design_panel.sizes.width - minus_w;
    if (design_panel.obj.hasScrollBar()) {
        right_containment -= 5;
    }

    this.draggable({
        scroll: true,
        stop: function() {
            set_saved_flag(0);
            $(this).setRotatable()
                   .setResizable()
                   .setSelected();
        },
        containment: [
            design_panel.position.left,
            design_panel.position.top,
            right_containment,
            'auto'
        ]
    }).bind({
        click: function() {
            $(this).setRotatable()
                   .setResizable()
                   .setSelected();
        }
    });

    return this;
}

$.fn.setRotatable = function () {
    //init rotatable for object
    if (this.find('.ui-rotatable-handle').length == 0 && this.attr('data-type') != 'video') {
        this.rotatable({angle: parseFloat(this.rotationDegrees()) * (Math.PI/180)});
    }

    return this;
}

$.fn.setResizable = function () {

    if (this.find('.ui-resizable-handle').length == 0) {
        if (this.attr('data-type') == 'text') {
            this.resizable({
                stop: function() {
                    set_saved_flag(0);
                }
            });
        } else {
            this.find('.image_collection').resizable({
                aspectRatio: true,
                minHeight: this.find('img').attr('min-d'),
                minWidth: this.find('img').attr('min-w'),
                start: function( event, ui ) {
                    $(this).find('img').css({'max-width':'none'});
                },
                resize: function( event, ui ) {
                    $(this).parent('.abilities').css({
                        'width':'auto',
                        'height':'auto'
                    });

                    $(this).children('img').css({
                        "width" : "100%",
                        "height": "100%"
                    });
                },
                stop: function( event, ui ) {
                    set_saved_flag(0);
                    $(this).parent().setContainment();
                }
            });
        }

    }

    return this;
}

//limit space size of item can move as parent element
$.fn.setContainment = function () {

    var angle = this.rotationDegrees(),
        right_containment = design_panel.position.left + design_panel.sizes.width;

    if ($.inArray(angle, [-90, 0, 90, 180]) == -1) {
        right_containment -= this.width();
    } else {
        right_containment -= parseInt(this.outerWidth(true));
        //minus pedding of the image collection children
        var padding_left = '',
            padding_right = '';

        if (!this.hasClass('my-text')) {
            padding_left = this.children('.image_collection').css('padding-left').replace(/px/g, ''),
            padding_right = this.children('.image_collection').css('padding-right').replace(/px/g, '');
        }

        if (padding_left != '') {
            right_containment -= parseInt(padding_left)
        }

        if (design_panel.obj.hasScrollBar()) {
            right_containment -= 15;
        }
    }

    //re-config containment info
    this.draggable({
        containment: [design_panel.position.left, design_panel.position.top, right_containment, 'auto']
    });

    return this;
}

$.fn.setSelected = function () {

    //Remove selected
    design_panel.obj.children('.abilities').removeClass('selected').find('.ui-resizable-handle, .ui-rotatable-handle').hide();
    //reset selected
    this.addClass('selected').find('.ui-resizable-handle, .ui-rotatable-handle').show();

    if (this.attr('data-type') == 'video') {
        top_menu.find("#flop, #flip, #clone").attr("disabled", true);

    } else if (this.attr('data-type') == 'text') {
        top_menu.find("#clone").removeAttr("disabled");
        top_menu.find("#flop, #flip").attr("disabled", true);

    } else {
        top_menu.find("#flop, #flip, #clone").removeAttr("disabled");
    }

    return this;
}

$.fn.getDatas = function () {

    var my_text = '',
        object_id = 0,
        ele_class = this.attr('class'),
        ele_style = 'position: absolute; ',
        ele_type = this.attr('data-type'),

        degrees = this.rotationDegrees(),
        angle = parseFloat(degrees) * (Math.PI/180);

    if (ele_type != 'text') {
        object_id = this.find('.object-id-value').val();
    } else {
        my_text = this.find('.text-editable').html();
    }

    ele_style += 'top: '+ this.css('top') +'; ';
    ele_style += 'left: '+ this.css('left') +'; ';
    ele_style += 'z-index: '+ this.css('z-index') +'; ';

    if (this.attr('data-type') != 'video') {
        ele_style += 'transform: rotate('+ angle +'rad); ';
        ele_style += '-o-transform: rotate('+ angle +'rad); ';
        ele_style += '-ms-transform: rotate('+ angle +'rad); ';
        ele_style += '-moz-transform: rotate('+ angle +'rad); ';
        ele_style += '-webkit-transform: rotate('+ angle +'rad); ';
    }

    if (this.hasClass('my-text')) {
        ele_style += 'width: '+ this.width() +'px; ';
        ele_style += 'height: '+ this.height() +'px; ';
    } else {
        ele_style += 'width: '+ this.children('.image_collection').width() +'px; ';
        ele_style += 'height: '+ this.children('.image_collection').height() +'px; ';
    }

    ele_class = $.trim(ele_class.replace(/ui-draggable|ui-resizable|selected/g,''));

    return {
        type: ele_type,
        style: ele_style,
        class: ele_class,
        obj: object_id,
        text: my_text
    }
}

function get_flags_value() {
    var flags = $('#collection_flags');

    return {
        obj: flags,
        link: flags.attr('link'),
        c_id: parseInt(flags.val()),
        saved: parseInt(flags.attr('saved')),
        style: parseInt(flags.attr('style')),
        next_action: flags.attr('next_action')
    }
}

function get_design_panel(id) {
    var panel = $(id),
        border = {
            top: parseInt(panel.css('border-top-width').replace(/px/g, '')),
            right: parseInt(panel.css('border-right-width').replace(/px/g, '')),
            bottom: parseInt(panel.css('border-bottom-width').replace(/px/g, '')),
            left: parseInt(panel.css('border-left-width').replace(/px/g, ''))
        };

    return {
        id: id,
        obj: panel,
        sizes: {
            width: parseInt(panel.width()),
            height: parseInt(panel.height())
        },
        border: border,
        position: panel.position()
    }

}

function dropped_item(ui) {
    var object = ui.draggable;
    if (! ui.helper.hasClass('not-clone')) {
        var object = ui.draggable.clone();
        do_append_item_to_left_panel_when_drag_from_right_panel(object, ui.helper)
    } else {
        object.setResizable()
              .setRotatable();
    }
    set_saved_flag(0);
    top_menu.show('500');
    $('#drag_announce').hide('500');
    object.setSelected();
}

function save_collection_submit_form() {
    var flags = get_flags_value();

    do_save_collection( function( response ) {
        if (flags.next_action == 'new') {
            set_new_collection();
        } else if (flags.next_action == 'open') {
            window.open(flags.link + response.id);
        }

    });
}

function messageModal(type, message) {
    var message_modal = $('#collection_modal_message');
    if (type != null) {
        message = message_modal.find('.modal-body .' + type).text();
    }

    message_modal.modal('show').find('.modal-body').html(message)
}

function set_saved_flag( value ) {
    var flags = get_flags_value();

    flags.obj.attr('saved', value);

    design_panel.obj.find('#drag_announce').hide('500');

    top_menu.show('500');

    if (value == 1) {
        left_menu.find("#open").removeAttr('disabled');
        left_menu.find("#save_draft").attr('disabled', true);
    } else {
        left_menu.find("#open").attr('disabled', true);
        left_menu.find("#save_draft").removeAttr('disabled');
    }
    left_menu.find("#new").removeAttr('disabled');
    left_menu.find("#view").removeAttr('disabled');
}

function delete_action(elem_list, selected_id) {
    var z_index = parseInt($('#' + selected_id).css('z-index'));
    elem_list.each(function(i) {
        var i_z_index = parseInt($(this).css('z-index'));
        if (i_z_index > z_index) {
            $(this).css('z-index', i_z_index-1)
        }
    });
    $("#" + selected_id).remove();
}

function forwards_or_backwards_action(option, elem_list, selected_id) {
    //case option = 1: 'forwards';
    //case option = 0: 'backwards';

    var id_list = [],
        next_z_index = 0,
        min_z_index = 1,
        max_z_index = elem_list.length,
        current_z_index = parseInt($('#' + selected_id).css('z-index'));

    id_list[0] = selected_id;

    elem_list.each( function(i) {
        id_list[$(this).css('z-index')] = $(this).attr('id');
    });

    if (option == 1) {
        if (current_z_index != max_z_index && id_list.length > 1) {
            $('#'+id_list[current_z_index + 1]).css({'z-index':current_z_index});
            $('#'+id_list[current_z_index]).css({'z-index':current_z_index+1});
        }

    } else if(option == 0) {
        if (current_z_index != min_z_index && id_list.length > 1) {
            $('#'+id_list[current_z_index - 1]).css({'z-index':current_z_index});
            $('#'+id_list[current_z_index]).css({'z-index':current_z_index-1});
        }
    }


}

function clone_action(selected_id) {

    var new_id = 'dropped_cloned_' + (new Date).getTime(),
        element = $('#'+selected_id),
        old_top = parseInt(element.css('top').replace(/px/g, '')) + 15,
        old_left = parseInt(element.css('left').replace(/px/g, '')) + 15,
        new_object = element.clone();

    new_object.attr('id', new_id)
    .css({
         'position' : 'absolute',
         'left' : old_left +'px',
         'top' : old_top +'px',
         'z-index': design_panel.obj.children('.abilities').length + 1
    }).appendTo(design_panel.obj);

    new_object.find('.ui-resizable-handle, .ui-rotatable-handle').remove();

    new_object
        .setDraggable(0)
        .setRotatable()
        .setResizable()
        .setContainment()
        .setSelected();
}

function flop_or_flip_actions(selected_id, request) {

    var parent = $('#'+selected_id),
        element = parent.find('img'),
        current_stat = element.css('transform');

    switch (request) {
        case "flip":
            if (current_stat == '' || current_stat == null || current_stat == 'none') {
                element.css('transform','matrix(1, 0, 0, 1, 0, 0)');
                element.css('transform','matrix(-1, 0, 0, -1, 0, 0)');
                parent.addClass('flip-one').removeClass('flip-second');
            } else if (current_stat == 'matrix(1, 0, 0, 1, 0, 0)') {
                element.css('transform','matrix(-1, 0, 0, -1, 0, 0)');
                parent.addClass('flip-one').removeClass('flip-second');
            } else {
                element.css('transform','matrix(1, 0, 0, 1, 0, 0)');
                parent.addClass('flip-second').removeClass('flip-one');
            }
        break;
        case "flop":
            if (current_stat == '' || current_stat == null || current_stat == 'none') {
                element.css('transform','matrix(1, 0, 0, 1, 0, 0)');
                element.css('transform','matrix(-1, 0, 0, 1, 0, 0)');
                parent.addClass('flop-one').removeClass('flop-second');
            } else if (current_stat=='matrix(1, 0, 0, 1, 0, 0)') {
                element.css('transform','matrix(-1, 0, 0, 1, 0, 0)');
                parent.addClass('flop-one').removeClass('flop-second');
            } else {
                element.css('transform','matrix(1, 0, 0, 1, 0, 0)');
                parent.addClass('flop-second').removeClass('flop-one');
            }
        break;
    }
}

//set position when open collection from gallery, to have style absolute to save
function reset_style_items_to_can_set_abilities_when_display_from_gallery() {

    var products = design_panel.obj.children('.abilities');

    for (var i = products.length-1; i >= 0; i--) {
        var element = $(products[i]), position = element.position();
        if ($(element).css('position') == 'relative') {
            $(element).css({
                'position': 'absolute',
                'left': position.left + 'px',
                'top': position.top + 'px',
                'float':''
            });
        }
    }
}

function collection_display_after_open_from_popup(object) {

    var flags = get_flags_value();

    flags.obj.val(object.attr('pk'))
    save_modal.find('#id_name').val(object.attr('data-name'));
    design_panel.obj.find('#drag_announce').hide('500');
    design_panel.obj.children('.abilities, .collection-empty').remove();

    $.ajax({
        type: 'GET',
        url: object.attr('href'),
        success: function( response ) {

            //Show toolbar
            top_menu.show('500');

            //Hide loading icon
            loading_modal(open_modal.attr('id'), 'off');
            open_modal.modal('hide');
        }
    }).done(function( response ) {
        design_panel.obj.append(response);

        //Update the image site by parent div size
        design_panel.obj.children('.abilities').each(function( i ) {

            var str_width = parseInt($(this).css('width').replace(/px/g, '')),
                str_height = parseInt($(this).css('height').replace(/px/g, ''));

            if ($(this).hasClass('shop')) {
                $(this).children('.image_collection').css({"width" : str_width + "px", "height" : str_height + "px"});
                $(this).css({'width' : 'auto', 'height' : 'auto'});
                $(this).find('img').css({'width' : '100%', 'height' : '100%'});
            }

            $(this).setDraggable(0)
                   .setContainment();

        });
    });

}

function save_collection(collection_name, status, callback) {

    var items = [],
        flags = get_flags_value();

    design_panel.obj.children('.abilities').each(function(i) {
        var item = $(this).getDatas();
        items[i] = JSON.stringify(item);
    });

    $.ajax({
        type: 'POST',
        url: '/collection/save/',
        data: {
            pk: flags.c_id,
            name: collection_name,
            'items[]': items,
            status: status
        }
    }).done(function( response ) {
        return callback(response);
    });

}

function do_view_and_publish_action() {
    var flags = get_flags_value();

    if (design_panel.obj.children('.abilities').length > 0) {

        //Check current connection had saved
        if (parseInt(flags.saved) == 1) {
            //if not yet save
            window.open(flags.link + flags.c_id);
        } else {
            //Call saving confirm form and question Do you want save before to view?
            confirm_modal.modal('show');
        }

    } else {
        messageModal('empty');
    }
}

function do_save_draft() {
    var flags = get_flags_value();

    if (design_panel.obj.children('.abilities').length > 0) {

        var collection_name = save_modal.find('#id_name').val();

        if (collection_name == '') {
            save_modal.modal('show');
            flags.obj.attr('next_action', 'keep');
        } else {
            //don't show saving form again when it already saved
            do_save_collection( function(response) {
                messageModal(null, response.message + ' ' + response.link);
            });
        }

    } else {
        messageModal('empty');
    }
}

function auto_set_position_dropped_from_available_items(ui_helper) {

    var minus_top = 0,
        minus_left = 25,
        offset_top = parseInt(design_panel.obj.scrollTop()) + parseInt(ui_helper.offset().top),
        helper_padding_top = ui_helper.find('.image_collection').css('padding-top').replace(/px/g, '');

    if (ui_helper.find('img').width() > ui_helper.find('img').height()) {
        minus_top = parseInt(ui_helper.find('.image_collection').outerHeight()) + 4;
    } else {
        minus_top = parseInt(ui_helper.find('.image_collection').height()) - 20;
    }

    if (helper_padding_top != 'undefined') {
        minus_top -= parseInt(helper_padding_top);
    }


    return {
        left: parseInt(ui_helper.offset().left) - minus_left,
        top: parseInt(offset_top) - minus_top
    };
}

//Load gallery/collection after click on the Gallery from MY LIST, so need set draggable, resizable and rotatable for all items when document ready.
function display_items_when_open_collection_from_gallery() {

    var flags = get_flags_value();

    design_panel.obj.children('.abilities').each( function() {

        $(this).setDraggable(0);
        $(this).one('mousedown', function() {
            $(this).setContainment()
        });

        if (flags.style == 1 && $(this).hasClass('shop')) {
            $(this).find(".image_collection").css({
                'height': $(this).height() + 'px',
                'width': $(this).width() + 'px'
            });

            $(this).css({
                'height': 'auto',
                'width': 'auto'
            });
        }
    });
}

function open_list_collections_on_modal() {

    open_modal.modal('show');
    loading_modal(open_modal.attr('id'), 'on');

    $.ajax({
        type: 'GET',
        url: '/collection/list/'
    }).done(function( response ) {
        loading_modal(open_modal.attr('id'), 'off');
        open_modal.children('.box-content').html(response);
    });
}

function do_append_item_to_left_panel_when_drag_from_right_panel(new_object, helper) {

    var new_id = 'dropped_' + (new Date).getTime(),
        item_index = design_panel.obj.children('.abilities').length + 1,
        position = auto_set_position_dropped_from_available_items(helper),
        best_default_width = new_object.find('img').attr('best-w'),
        best_default_height = new_object.find('img').attr('best-h');

    new_object.appendTo(design_panel.obj)
        .attr('id', new_id)
        .addClass('not-clone item-' + item_index)
        .css({
            'position': 'absolute',
            'left': position.left + 'px',
            'top': position.top + 'px',
            'z-index':item_index
    });

    new_object.setDraggable(best_default_width);

    if (new_object.attr('data-type') != 'video') {
        new_object.rotatable();
    }

    new_object.setResizable();

    new_object.find('img').css({
        'width': best_default_width +'px',
        'height': best_default_height +'px'
    });
}

//Do actions of top menu toolbar
function toolbar_bind_click_action(object) {

    var request = object.attr('id'),
        elem_list = design_panel.obj.children('.abilities'),
        selected = design_panel.obj.children('.selected');

    if (selected.length == 0) {
        messageModal('un-select');
    } else {

        var selected_id = selected.attr('id');
        set_saved_flag(0);

        switch (request) {
            case 'remove':
                delete_action(elem_list, selected_id);
            break;

            case 'clone':
                clone_action(selected_id);
            break;

            case 'forwards':
                forwards_or_backwards_action(1, elem_list, selected_id);
            break;

            case 'backwards':
                forwards_or_backwards_action(0, elem_list, selected_id);
            break;

            default :
                flop_or_flip_actions(selected_id, request);
                break;
        }
    }
}

//Do action when user answer No of fonfirm modal
function do_action_when_user_answer_no(event) {

    var flags = get_flags_value();

    confirm_modal.modal('hide');

    if (flags.next_action == 'new') {
        set_new_collection();

    } else {
        //Check already saved, pk=0 it mean not yet save
        if (flags.c_id == 0) {
            //Save Draft before to view if the first design
            do_save_collection( function(response) {
                window.open(flags.link + response.id);
            });
        } else {
            window.open(flags.link + flags.c_id);
        }
    }

    event.preventDefault();
}

//Do action when user answer Yes of confirm modal
function do_action_when_user_answer_yes() {
    var flags = get_flags_value();

    if (flags.c_id == 0) {
        //- need show saving form when save in the first time
        //- or after view but not accept save then click save again.
        save_modal.modal('show');

    } else {
        loading_modal(confirm_modal.attr('id'), 'on');
        //don't show saving form again when it already saved
        do_save_collection( function(response) {

            loading_modal(confirm_modal.attr('id'), 'off');
            confirm_modal.modal('hide');

            if (flags.next_action == 'new') {
                set_new_collection();
            } else if (flags.next_action == 'open') {
                window.open(flags.link + response.id);
            }

        });
    }
}

//Set new collection form
function set_new_collection() {

    var flags = get_flags_value();

    //Hide top menu buttons
    top_menu.hide('normal');

    //set collection's id is 0
    flags.obj.val(0)

    //set collection's name id null
    save_modal.find('#id_name').attr('value', '');

    //set next action after collection saved
    flags.obj.attr('next_action', 'keep');

    //remove all data inside design panel
    design_panel.obj.children('.abilities').remove();
    design_panel.obj.children('#drag_announce').show('normal');

    //reset status of buttons in left menu
    left_menu.find("#open").removeAttr('disabled');
    left_menu.find("#new, #view, #save_draft").attr('disabled', true);
}

//do actions of left menu toolbar
function left_toolbar_menu_click_action(object) {

    var menu_id = object.attr('id'),
        flags = get_flags_value();

    switch ( menu_id ) {
        case 'new':
            if (flags.saved == 0) {
                flags.obj.attr('next_action', 'new');
                confirm_modal.modal('show');
            } else {
                set_new_collection();
            }
            object.attr('disabled', true);

            break;

        case 'open':
            open_list_collections_on_modal();
            break;

        case 'save_draft':

            object.attr('disabled', true);
            save_modal.find('#status').val('d');
            flags.obj.attr('next_action', 'keep');
            do_save_draft();

            break;

        case 'view':
            save_modal.find('#status').val('p');
            flags.obj.attr('next_action', 'open');
            do_view_and_publish_action();

            break;

        default:
            return false;
            break;
    }
}

function do_save_collection(callback) {

    var flags = get_flags_value(),
        status = save_modal.find('#status').val(),
        name = save_modal.find('#id_name').val();

    save_collection(name, status, function( response ) {
        flags.obj.val( response.id );
        save_modal.modal('hide');
        set_saved_flag(1);

        if (response.code == 0) {
            messageModal(null, response.message);
        } else {
            return callback(response)
        }
    });

}