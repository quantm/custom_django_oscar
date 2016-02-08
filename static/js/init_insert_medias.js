/**
 * Created by tqn on 1/23/14.
 */
var networks = ['youtube', 'vine', 'instagram', 'pinterest', 'flickr', 'photobucket'];

function insert_media_action(insert_media_btn, callback) {

    window.TAB_ACTIVE = {
        type: '',
        tab: null,
        content: null
    };
    window.SCROLL_OPTION = {
        is_scrolling: 1,
        current_page: 1
    };
    window.UPLOAD = {
        preview: true
    };

    var insert_media_modal = $('#insert_media'),
        image_upload_modal = $("#ImageUploadModal");

    $( document )

    .on( "click", insert_media_btn, function() {
        insert_media_modal.modal('show');

    })
    .on( "click", '#tabs ul li', function() {
        //When click on tab link
        window.TAB_ACTIVE.type = $(this).attr('data-type');
        reset_buttons_menu($(this));
    })
    .on( "click", '#toolbar-header .menu-buttons button', function() {
        //When click on the menu button
        $('#facebook_up_to').hide();
        switch_button_menu(insert_media_modal, $(this));
        loading_modal(insert_media_modal.attr('id'), 'off');
        message_modal(insert_media_modal.attr('id'), {type: 'off'});

    })
    .on( "click", 'button#back_my_videos, button#back_my_images', function() {
        //When click on My Videos or My Images button

        var data = {page: 1, type: 'video'};
        if ($(this).attr('id') == 'back_my_images') {
            data['type'] = 'image'
        }

        loading_modal(insert_media_modal.attr('id'), 'on');
        ajax_load_media(insert_media_modal, data, function() {});

    })

    .on( "click", '.insert-media-modal button.submit', function() {
        //Show loading when do submit anywhere

        $(this).attr('disabled', true)
        loading_modal(insert_media_modal.attr('id'), 'on');

    })

    .on( "click", 'button#add_video_from_url', function() {
        //When click button Add to add YouTube's video from url
        add_video(insert_media_modal);

    })

    .on( "click", 'button#search_videos', function( event ) {
        //Do search YouTube's videos When click Search button

        search_videos(insert_media_modal, function ( response ) {
            ajax_load_media(
                insert_media_modal,
                { page: 1, type: response.type, keywords: response.keywords },
                function( responese ) {
                    $(event.target).removeAttr('disabled');
                }
            );
        });

    })

    .on( "keypress", 'input#keywords', function( event ) {
        //Search YouTube videos when enter textbox

        if ( event.which == 13 ) {

            event.preventDefault();
            $(event.target).next().attr('disabled','disabled');

            search_videos( insert_media_modal, function ( response ) {
                ajax_load_media(
                    insert_media_modal,
                    { page: 1, type: response.type, keywords: response.keywords },
                    function( responese ) {
                        $(event.target).next().removeAttr('disabled');
                    }
                );
            });
        }

    })

    .on( "click", 'button#make_video', function() {
        get_youtube_upload_widget_form();

    })

    .on( "click", 'button#create_new_video', function() {
        // When click Capture a new video we set preview is false, to if video processed then don't preview
        window.UPLOAD.preview = false;

        get_youtube_upload_widget_form();

    })

    .on( "click", '#add_image_open_modal', function() {
        //When click Add an image button
        insert_media_modal.modal('hide');
        image_upload_modal.modal('show');
    })

    .on( "submit", '#save-crop', function( event ) {

        save_image_and_crop(insert_media_modal, image_upload_modal, function() {
            image_upload_modal.modal('hide');
            loading_modal(image_upload_modal.attr('id'), 'off');
            image_upload_modal.find('#save-avatar').removeAttr('disabled');
        });
    })

    .on( "click", '#browse_facebook', function() {
        //When click Browse Facebook photos

        browse_facebook_action('/networks/fb/albums/', insert_media_modal, function() {
            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.find('#browse_facebook').attr('disabled', 'disabled');
            insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');
        });

    })

    .on( "click", '#browse_facebook_up_to', function() {
        //Up to Browse Facebook images
        $(this).attr('disabled', true);
        insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');

        browse_facebook_action('/networks/fb/albums/', insert_media_modal, function() {

            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.find('#browse_facebook').attr('disabled', 'disabled');
            insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');
            $('#facebook_up_to').hide().find('#browse_facebook_up_to').removeAttr('disabled');

        });
    })

    .on( "click", '#albums a', function( event ) {
        //Add image on Facebook to site
        event.preventDefault();

        var open_link = '/networks/fb/album/' + $( event.target ).attr('data-id') + '/';
        browse_facebook_action(open_link, insert_media_modal, function() {

            set_selected_for_media_item(insert_media_modal, null);
            $('#facebook_up_to').show().find('#browse_facebook_up_to').removeAttr('disabled');

        });
    })

    .on( "click", 'button.btn-search.submit', function() {
        //Search Instagram, Pinterest, Flickr, Photobucket images when click Search button

        search_action(insert_media_modal, $(this).prev(), 1);
    })

    .on( "keypress", 'input.text-search.keywords', function( event ) {
        //Search Vine, Instagram, Pinterest, Flickr, Photobucket images when enter textbox

        if ( event.which == 13 ) {

            $(event.target).next().attr('disabled','disabled');
            loading_modal(insert_media_modal.attr('id'), 'on');
            search_action(insert_media_modal, $(this), 1);
        }
    })

    .on( "click", '.insert-media-modal div.abilities', function() {
        //When click on media item

        set_selected_for_media_item(insert_media_modal, $(this));

    })

    .on( "click", 'button#insert_media_ok_btn', function( event ) {

        $(event.target).attr('disabled','disabled');
        do_ok_action_of_insert_medias( insert_media_modal, callback );
    })

    .on( "dblclick", '.ui-tabs-panel .abilities img', function() {

        preview_medias($(this));

    });

    //Check  has Scroll of selector
    $.fn.hasScrollBar = function() {
        return this.get(0).scrollHeight > this.height();
    }

    toggle_insert_medias_modal_display(insert_media_modal);

    trigger_scroll(insert_media_modal);

    toggle_upload_image_function(image_upload_modal, insert_media_modal);

}

function get_youtube_video_id( url) {

    if(url === null) {
        return "";
    }
    var results = url.match("[\\?&]v=([^&#]*)");
    return ( results === null ) ? null : results[1];
}

function load_media(insert_media_modal, type) {
    insert_media_modal.find('#tabs').tabs( {
        create: function( event, ui ) {
        },

        beforeLoad: function( event, ui ) {

            loading_modal(insert_media_modal.attr('id'), 'on');
            message_modal(insert_media_modal.attr('id'), {type: 'off'});

            window.SCROLL_OPTION.current_page = 1;
            window.TAB_ACTIVE.tab = ui.tab;
            window.TAB_ACTIVE.content = ui.panel;
            window.TAB_ACTIVE.type = ui.tab.attr('data-type');

            reset_buttons_menu(ui.tab);

        },

        load: function( event, ui ) {

            insert_media_modal.find('.modal-body').scrollTop(0);
            set_selected_for_media_item(insert_media_modal, null);
            loading_modal(insert_media_modal.attr('id'), 'off');

        },

        activate: function( event, ui ) {

            //update when TabContent using cache
            window.TAB_ACTIVE.tab = ui.newTab;
            window.TAB_ACTIVE.content = ui.newPanel;
            window.SCROLL_OPTION.ajax_url = ui.newTab.find('a').attr('href');

            $('#' + ui.oldTab.attr('toolbar')).hide();
            $('#' + ui.newTab.attr('toolbar')).show();

        }
    });
}

function reset_buttons_menu(ui_Tab) {
    var buttons = $('#' + ui_Tab.attr('toolbar')).find('.menu-buttons button');

    $('#facebook_up_to').hide();
    buttons.removeAttr('disabled');
    buttons.first().attr('disabled', true);
    $("#toolbar-header .data-form").children().hide();

}

function set_selected_for_media_item(insert_media_modal, media_obj) {
    var tab_content = window.TAB_ACTIVE.content,
        first_selector = tab_content.find('.abilities').first();

    insert_media_modal.find('.abilities').removeClass('selected');
    if(media_obj == null) {
        first_selector.addClass('selected');
    }else {
        media_obj.addClass('selected');
    }
    insert_media_modal.find('#insert_media_ok_btn').removeAttr('disabled');
}

function ajax_load_media(insert_media_modal, params, callback) {

    var tab_content = window.TAB_ACTIVE.content,
        load_url = window.TAB_ACTIVE.tab.find('a').attr('href'),
        new_params = {page: params.page, keywords: params.keywords};

    if ( jQuery.inArray(params.type, networks) !=-1 ) {
        load_url = '/networks/'+params.type+'/search/';
    }

    $.ajax({
        type: 'GET',
        url: load_url,
        data: new_params,
        beforeSend: function( xhr, settings ) {
            window.SCROLL_OPTION.is_scrolling = 0;
            loading_modal(insert_media_modal.attr('id'), 'on');
            message_modal(insert_media_modal.attr('id'), {type: 'off'});
        },
        success: function (data_returned) {
            window.SCROLL_OPTION.is_scrolling = 1;
            window.SCROLL_OPTION.current_page = params.page;
            tab_content.find('#paging_'+(params.page-1)).remove();
            loading_modal(insert_media_modal.attr('id'), 'off');

            window.TAB_ACTIVE.type = params.type;

            window.TAB_ACTIVE.content.find('#my_images_toolbar #search_form #search_text').next().removeAttr('disabled');
        },
        error: function( jqXHR, settings ) {
            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.modal('hide');
        }
    }).done(function( data_returned ) {
        if( params.page==1 ) {
            tab_content.html(data_returned);
            set_selected_for_media_item(insert_media_modal, null);
            insert_media_modal.find('.modal-body').scrollTop(0);
        }else {
            tab_content.append(data_returned);
        }

        return callback(data_returned);
    });
}

function save_youtube_video(insert_media_modal, youtube_url, callback) {

    var insert_video_form = $("#insert_video_form"),
        video_id = get_youtube_video_id(youtube_url),
        get_video_url = 'http://gdata.youtube.com/feeds/api/videos/' + video_id + '?v=2&alt=jsonc';

    $.ajax({
        type: "GET",
        url: get_video_url,
        beforeSend: function ( data_return ) {
            insert_media_modal.find("button#add_video_from_url").attr('disabled', 'disabled');
            insert_media_modal.find("button#search_videos").attr('disabled', 'disabled');
            insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');
        },
        success: function ( data_return ) {
            insert_media_modal.find("#insert_video_form").removeClass('error');

        },
        error: function( data_return ) {
            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.find("#insert_video_form").addClass('error');
            message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: $('#youtube_video_url').attr('message')});

            insert_media_modal.find("button#add_video_from_url").removeAttr('disabled');
            insert_media_modal.find("button#search_videos").removeAttr('disabled');
            insert_media_modal.find('#insert_media_ok_btn').removeAttr('disabled');
        }
    }).done(function( data_return ) {
        var post_data = {
            video_code: video_id,
            title: data_return.data.title,
            is_video: 1,
            image: data_return.data.thumbnail.hqDefault,
            description: data_return.data.title
        }
        post_media_data_to_save(post_data, function (response) {
            return callback(response);
        });
    });
}

function append_media(insert_media_modal, media_type, response) {
    var data_obj = {},
        parse_error = false;
    try {
        var data_obj = jQuery.parseJSON(response);
    }
    catch(err) {
        //Handle errors here
        parse_error = true;
    }

    if(parse_error) {
        var tab_content = window.TAB_ACTIVE.content;

        //data returned is html
        if(media_type == 'image') {
            insert_media_modal.modal('show');
        }else {
            $("button#add_video_from_url").removeAttr('disabled');
            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.find('#insert_media_ok_btn').removeAttr('disabled');
        }

        //
        tab_content.find('.abilities').removeClass('selected');
        tab_content.find('.add-media-header').after(response);

        //Refresh contents
        ajax_load_media(insert_media_modal, {page: 1, type: media_type}, function() {});

        //Remove message when empty
        tab_content.find('h3.empty').remove();

    }else {
        //data returned is json message
        reset_form_data_when_error(data_obj.message)
    }
}

function post_media_data_to_save(post_data, callback) {

    var post_url = '/collection/media/add/';

    $.ajax({
        type: "POST",
        url: post_url,
        data: post_data
    }).done(function( data_return ) {
        return callback(data_return);
    });
}

function do_ok_action_of_insert_medias(insert_media_modal, callback) {

    if (insert_media_modal.find('.selected').length == 0) {
        alert("No item selected");
        return false;
    } else {
        loading_modal(insert_media_modal.attr('id'), 'on');
    }

    var selected = insert_media_modal.find('.selected'),
        temp_networks = networks;
        temp_networks.push("facebook");

    if (window.TAB_ACTIVE.type == 'youtube') {
        var toolbar_id = window.TAB_ACTIVE.tab.attr('toolbar'),
        active_btn = $('#' + toolbar_id).find('.menu-buttons button[disabled="disabled"]');

        if ( active_btn.attr('id') == 'make_video') {

            yuw_do_save_video(selected, function( response ) {

                var response_html = jQuery.parseHTML( response.trim() );
                insert_media_modal.modal('hide');
                return callback($(response_html[0]), insert_media_modal);

            });
        } else {
            var video_url = 'http://www.youtube.com/watch?v='+ selected.attr('data-id');
            save_youtube_video(insert_media_modal, video_url, function ( response ) {

                var response_html = jQuery.parseHTML( response.trim() );
                insert_media_modal.modal('hide');
                return callback($(response_html[0]), insert_media_modal);
            });
        }




    } else if(window.TAB_ACTIVE.type == 'vine') {

        save_video(selected, function(data_response) {
            insert_media_modal.modal('hide');
            var response_html = jQuery.parseHTML( data_response.trim() );
            return callback($(response_html[0]), insert_media_modal);
        });


    } else if(jQuery.inArray(window.TAB_ACTIVE.type, temp_networks) !=-1) {

        save_image(selected, function(data_response) {
            insert_media_modal.modal('hide');
            var response_html = jQuery.parseHTML( data_response.trim() );
            return callback($(response_html[0]), insert_media_modal);
        });

    } else {

        insert_media_modal.modal('hide');
        return callback(selected, insert_media_modal);

    }
}

function save_image( selected, callback ) {
    var data = selected.find('input.object-id-value'),
    params = {
        is_video: 0,
        title: data.attr('data-title'),
        image: data.attr('data-url'),
        description: data.attr('data-desc')
    };

    post_media_data_to_save(params, callback);
}

function save_video( selected, callback ) {
    var data = selected.find('input.object-id-value'),
    params = {
        vine: true,
        id: data.attr('data-video'),
        title: data.attr('data-title'),
        image: data.attr('data-image'),
        description: data.attr('data-desc')
    };

    $.ajax({
        type: "POST",
        url: '/collection/media/save/video/',
        data: params
    }).done(function( data_return ) {
        return callback(data_return);
    });
}

function toggle_insert_medias_modal_display(insert_media_modal) {

    insert_media_modal.on({
        show: function() {
            message_modal(insert_media_modal.attr('id'), {type: 'off'});
            if ( window.TAB_ACTIVE.tab !== null) {
                ajax_load_media(
                    insert_media_modal,
                    {page: 1, type: window.TAB_ACTIVE.tab.attr('data-type')},
                    function() {
                        reset_buttons_menu(window.TAB_ACTIVE.tab);
                    }
                );

            } else {
                load_media(insert_media_modal, 'video');
            }

        },
        shown: function() {
            var modal_body = insert_media_modal.find('.modal-body');
            if(modal_body.hasScrollBar()){
                modal_body.scrollTop(0);
            }
        },
        hide: function() {
            insert_media_modal.find('#insert_media_ok_btn').unbind('click');
            loading_modal(insert_media_modal.attr('id'), 'off');
            message_modal(insert_media_modal.attr('id'), {type: 'off'});
            insert_media_modal.find('#insert_video_form').removeClass('error').find('#youtube_video_url').val('');

            insert_media_modal.find("button#add_video_from_url").removeAttr('disabled');
            insert_media_modal.find("button#search_videos").removeAttr('disabled');
            insert_media_modal.find('#insert_media_ok_btn').removeAttr('disabled');


            if ( window.TAB_ACTIVE.content !== null) {
                window.TAB_ACTIVE.content.html('');
            }
        }
    });
}

function trigger_scroll(insert_media_modal) {

    insert_media_modal.find('.modal-body #tabs .medias-tab-content').scroll(function () {

        var total_page = window.TAB_ACTIVE.content.find('.total_page').attr('data-total-page');

        if($(this).scrollTop() >= ($(this).get(0).scrollHeight - $(this).get(0).offsetHeight - 50)) {
            if ((window.SCROLL_OPTION.is_scrolling == 1) && (total_page > 1) &&
                (window.SCROLL_OPTION.current_page < total_page)) {

                var of_page = window.SCROLL_OPTION.current_page + 1;

                switch ( window.TAB_ACTIVE.type ) {
                    case 'youtube' :
                        search_videos(insert_media_modal, function ( response ) {
                            ajax_load_media(
                                insert_media_modal,
                                {page: of_page, type: response.type, keywords: response.keywords},
                                function() {}
                            );
                        });
                        break;

                    case 'video' :
                    case 'image' :
                        ajax_load_media(
                            insert_media_modal,
                            {page: of_page, type: window.TAB_ACTIVE.type},
                            function() {}
                        );
                        break;

                    default :

                        var toolbar_id = window.TAB_ACTIVE.tab.attr('toolbar'),
                            keywords = $('#' + toolbar_id).find('input.text-search.keywords');

                        search_action(insert_media_modal, keywords, of_page);

                        break;
                }
            }
        }
    });
}

function toggle_upload_image_function(image_upload_modal, insert_media_modal) {

    image_upload_modal.on({
        show: function() {
            image_upload_modal.find('#myModalLabel').html('Upload Image');
            image_upload_modal.find('#save-avatar').attr('disabled','disabled');
            image_upload_modal.find('#is_avatar').attr('value',0);
            image_upload_modal.addClass('insert-media').find('.preview').addClass('insert-media');

            image_upload_modal.find('.preview-text, .loading, img.preview.insert-media').hide();
        },

        shown: function() {
            if (window.IMG_SELECT){
                window.IMG_SELECT.setOptions({hide: true});
                window.IMG_SELECT.update();
            }

            image_upload_modal.find('form#save-crop').attr('action', '').on('submit', function( event ) {
                event.preventDefault();
            }).submit(function( event ) {
                event.preventDefault();
            });
        },

        hide: function() {

            image_upload_modal.find('form#save-crop').unbind('submit');
            image_upload_modal.find('#preview_upload').attr('src', '');
            image_upload_modal.find('#preview_avatar').attr('src', '');
            image_upload_modal.find('#form-upload-image')[0].reset();

            insert_media_modal.modal('show');
            insert_media_modal.find('#save-crop').unbind('submit');
        }
    });
}

function add_video(insert_media_modal) {


    var video_url = insert_media_modal.find('#youtube_video_url'),
        insert_video_form = insert_media_modal.find('#insert_video_form'),
        search_video_form = insert_media_modal.find('#search_video_form');

    search_video_form.removeClass('active, error').find('input[type="text"]').val('');
    insert_video_form.addClass('active');

    if(video_url.val()=='') {
        insert_video_form.addClass('error');
        insert_media_modal.find("button#add_video_from_url").removeAttr('disabled');
        loading_modal(insert_media_modal.attr('id'), 'off');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: video_url.attr('message')});
    }else {
        window.TAB_ACTIVE.type = 'video';
        insert_video_form.removeClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'off'});
        save_youtube_video(insert_media_modal, video_url.val(), function(response) {
            append_media(insert_media_modal, 'video', response)
        });
    }
}

function search_videos(insert_media_modal, callback) {

    var keywords = insert_media_modal.find('#keywords'),
        check = keywords.val().match(/(\w+){3}/g),
        insert_video_form = insert_media_modal.find('#insert_video_form'),
        search_video_form = insert_media_modal.find('#search_video_form');

    insert_video_form.removeClass('active, error').find('input[type="text"]').val('');
    search_video_form.addClass('active');

    if (keywords.val() != '') {
        search_video_form.removeClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'off'});
        insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');

        return callback({type: 'youtube', keywords: keywords.val()});
    } else {
        search_video_form.addClass('error');
        insert_media_modal.find("button#search_videos").removeAttr('disabled');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: keywords.attr('message')});
    }
}

function send_request(load_url, params, callback) {

    $.ajax({
        type: 'GET',
        url: load_url,
        data: params
    }).done(function( data_returned ) {
        return callback(data_returned);
    });
}

function append_albums_to_tab_content(response, albums, callback) {
    var tab_content = window.TAB_ACTIVE.content;
    tab_content.find("#albums a").unbind('click');
    tab_content.html(albums);

    return callback(response);
}

function browse_facebook_action(load_url, insert_media_modal, callback) {

    loading_modal(insert_media_modal.attr('id'), 'on');
    sign_in_facebook(function(login_response) {
        send_request(load_url, login_response, function(data_response) {
            append_albums_to_tab_content(login_response, data_response, function() {
                window.TAB_ACTIVE.type = 'facebook'

                loading_modal(insert_media_modal.attr('id'), 'off');
                insert_media_modal.find('#browse_facebook').attr('disabled', 'disabled');
                //insert_media_modal.find('#back_my_images').removeAttr('disabled');

                return callback(login_response, data_response)
            });
        })
    });
}

function save_facebook_image(load_url, insert_media_modal, callback) {

    sign_in_facebook(function(login_response) {
        send_request(load_url, login_response, function(data_response) {

            window.TAB_ACTIVE.type = 'facebook'

            loading_modal(insert_media_modal.attr('id'), 'off');
            insert_media_modal.find('#back_my_images').removeAttr('disabled');
            insert_media_modal.find('#browse_facebook').attr('disabled', 'disabled');

            return callback(data_response)
        })
    });
}

function form_display_toggle( form_id, insert_media_modal, type, br ) {

    if (type == 'show') {
        insert_media_modal.find(form_id).show();

        $(form_id).find('input.text-search').focus();
        $('#'+ $(form_id).attr('bnt-id')).attr('disabled', 'disabled');

    } else {
        insert_media_modal.find(form_id).hide();
        $('#'+ $(form_id).attr('bnt-id')).removeAttr('disabled');
    }
}

function save_image_and_crop(insert_media_modal, image_upload_modal, callback) {
    var post_data = {
        cp: 1,
        video_code: null,
        title: "Default",
        is_video: 0,
        image: image_upload_modal.find('#preview_upload').attr('src'),
        description: null,
        crop: JSON.stringify({
            left: image_upload_modal.find("#crop-left").val(),
            top: image_upload_modal.find("#crop-top").val(),
            width: image_upload_modal.find("#crop-width").val(),
            height: image_upload_modal.find("#crop-height").val(),
            img_width: image_upload_modal.find('#preview_upload').width(),
            img_height: image_upload_modal.find('#preview_upload').height()
        })
    };

    loading_modal(image_upload_modal.attr('id'), 'on');
    image_upload_modal.find('#save-avatar').attr('disabled','disabled');

    post_media_data_to_save(post_data, function( response ) {
        append_media(insert_media_modal, 'image', response);

        return callback( response );
    });
}

function do_check_before_search(keywords, is_tag, callback) {

    var check = keywords.match(/(\w+){3}/g);

    if(check != null) {
        if ( !is_tag || (is_tag && check.length == 1) ) {
            return callback({code: 1, keywords: check.join(' ')});
        } else {
            return callback({code: 0});
        }
    } else {
        return callback({code: 0});
    }
}

function do_search_on_instagram(insert_media_modal, callback) {

    var tags_obj = window.TAB_ACTIVE.content.find('#my_images_toolbar #search_form #search_text'),
        check = tags_obj.val().match(/(\w+){3}/g);
    if(check) {
        if(check.length == 1 ) {
            tags_obj.parent().removeClass('error');
            tags_obj.next().attr('disabled','disabled');
            return callback({type: 'instagram', keywords: check.join(' ')});
        } else {
            tags_obj.parent().addClass('error');
            message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: tags_obj.attr('instagram-msg')});
        }
    } else {
        tags_obj.parent().addClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: tags_obj.attr('instagram-msg')});
    }
}

function do_search_on_pinterest(insert_media_modal, callback) {
    var keywords = window.TAB_ACTIVE.content.find('#my_images_toolbar #search_form #search_text'),
        check = keywords.val().match(/(\w+){3}/g);

    if(check) {
        keywords.parent().removeClass('error');
        keywords.next().attr('disabled','disabled');
        return callback({type: 'pinterest', keywords: check.join(' ')});
    } else {
        keywords.parent().addClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: keywords.attr('pinterest-msg')});
    }
}

function do_search_on_flickr(insert_media_modal, callback) {
    var keywords = window.TAB_ACTIVE.content.find('#my_images_toolbar #search_form #search_text'),
        check = keywords.val().match(/(\w+){3}/g);

    if(check) {
        keywords.parent().removeClass('error');
        keywords.next().attr('disabled','disabled');
        return callback({type: 'flickr', keywords: check.join(' ')});
    } else {
        keywords.parent().addClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: keywords.attr('flickr-msg')});
    }
}

function do_search_on_photobucket(insert_media_modal, callback) {

    var tags_obj = window.TAB_ACTIVE.content.find('#my_images_toolbar #search_form #search_text'),
        check = tags_obj.val().match(/(\w+){3}/g);
    if(check) {
        if(check.length == 1 ) {
            tags_obj.parent().removeClass('error');
            tags_obj.next().attr('disabled','disabled');
            return callback({type: 'photobucket', keywords: check.join(' ')});
        } else {
            tags_obj.parent().addClass('error');
            message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: tags_obj.attr('instagram-msg')});
        }
    } else {
        tags_obj.parent().addClass('error');
        message_modal(insert_media_modal.attr('id'), {type: 'on', class: 'text-error', message: tags_obj.attr('instagram-msg')});
    }
}

function switch_button_menu(insert_media_modal, button) {
    var parent_form_obj = button.parent().parent(),
        owner_form_obj = $('#' + button.attr('data-form'));

    //Set disable for active button
    button.attr('disabled', 'disabled');
    //enable another button
    button.parent().children().not(button).removeAttr('disabled');
    //set disabled OK button
    insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');
    //remove some tag using for message
    window.TAB_ACTIVE.content.children().remove();
    //hide message modal if it has
    message_modal(insert_media_modal.attr('id'), {type: 'off'});

    //hide all form
    parent_form_obj.find('.search_form').hide();

    //re-init search form
    owner_form_obj.removeClass('error');
    owner_form_obj.find("#search_text").val('');
    owner_form_obj.find("button#search_button").removeAttr('disabled');

    //show active form
    owner_form_obj.show();
}

function search_action(insert_media_modal, keywords, page) {

    var is_tag = false,
        toolbar_id = window.TAB_ACTIVE.tab.attr('toolbar'),
        active_btn = $('#' + toolbar_id).find('.menu-buttons button[disabled="disabled"]'),
        type = active_btn.attr('host');

    if ( jQuery.inArray(type, ['instagram', 'photobucket', 'vine']) != -1) {
        is_tag = true;
    }
    loading_modal(insert_media_modal.attr('id'), 'on');

    do_check_before_search( keywords.val(), is_tag, function( response ) {

        if (response.code == 0) {
            keywords.parent().addClass('error');
            keywords.next().removeAttr('disabled');

            message_modal(
                insert_media_modal.attr('id'),
                {
                    type: 'on',
                    class: 'text-error',
                    message: keywords.attr(type+ '-msg')
                }
            );
            loading_modal(insert_media_modal.attr('id'), 'off');

        } else {
            keywords.parent().removeClass('error');

            keywords.next().attr('disabled', true);

            var params = {page: page, keywords: response.keywords, type: type};
            ajax_load_media( insert_media_modal, params, function() {
                keywords.next().removeAttr('disabled');
                loading_modal(insert_media_modal.attr('id'), 'off');
            } );
        }
    });
}

function get_youtube_upload_widget_form() {

    var insert_media_modal = $('#insert_media');

    window.TAB_ACTIVE.type = 'youtube';
    window.TAB_ACTIVE.content.children().remove();
    loading_modal(insert_media_modal.attr('id'), 'on');
    message_modal(insert_media_modal.attr('id'), {type: 'off'});
    insert_media_modal.find('#insert_media_ok_btn').attr('disabled', 'disabled');

    send_request("/networks/youtube/upload-widget/", {}, function( response ) {

        window.UPLOAD.preview = true;
        window.TAB_ACTIVE.content.html( response );
        //window.TAB_ACTIVE.content.find("#my_images_toolbar").after( response );

        youtube_upload_widget_init('new_video_widget', yuw_do_on_ready, yuw_do_on_success, yuw_do_on_complete)

    });
}

function yuw_do_on_ready( data ) {

    var insert_media_modal = $('#insert_media'),
        video_title = $("#make_video_frm #y_title");

    if (data.state == -1) {
        loading_modal(insert_media_modal.attr('id'), 'off');
    }

    if (data.state == 5) {
        var data = {
            type: 'on',
            class: 'text-warning',
            message: video_title.attr('message')
        };
        message_modal(insert_media_modal.attr('id'), data);
    }
}

function yuw_show_message_when_video_processing() {
    //When video uploaded, we set preview is true to when video processed, it will preview for user
    window.UPLOAD.preview = true;

    var make_video_form = $("#make_video_form"),
        insert_media_modal = $('#insert_media');

    loading_modal(insert_media_modal.attr('id'), 'on');
    message_modal(insert_media_modal.attr('id'), {type: 'off'});

    make_video_form.find("#new_video_widget").hide();
    make_video_form.find("#make_video_message").show();

}

function yuw_do_on_success( response ) {

    var make_video_form = $("#make_video_form"),
        new_video = make_video_form.find('#new_video_data'),
        get_video_url = 'http://gdata.youtube.com/feeds/api/videos/' + response.videoId + '?v=2&alt=jsonc';

    new_video.val(response.videoId).attr('data-id', response.videoId).addClass('selected');

    yuw_show_message_when_video_processing();

    send_request(get_video_url, {}, function( data_response ) {

        var v_title = data_response.data.title,
            v_description = data_response.data.description,
            v_thumbnail = data_response.data.thumbnail.hqDefault;

        new_video.attr('data-desc', v_description).attr('data-thumb', v_thumbnail);

        $("#make_video_frm").find('#y_title').val(v_title);

        $('#insert_media').find('#insert_media_ok_btn').removeAttr('disabled');

    });
}

function yuw_do_on_complete( response ) {

    //When video processed, if Preview flag is true, we display video's player and update Preview is false
    var make_video_form = $("#make_video_form"),
        insert_media_modal = $('#insert_media');

    message_modal(insert_media_modal.attr('id'), {type: 'off'});
    make_video_form.find("#make_video_message").hide();
    make_video_form.find("#new_video_player").show();

    if (window.UPLOAD.preview) {

        var player = new YT.Player('new_video_player', {
            height: 390,
            width: 640,
            videoId: response.videoId,
            events: {
                'onReady': function(event) {
                    loading_modal(insert_media_modal.attr('id'), 'off');
                },
                'onStateChange': function (event) {

                }
            }
        });

        window.UPLOAD.preview = false;
    }
}

function yuw_do_save_video(selected, callback) {

    var video_title = $("#make_video_frm").find('#y_title'),
        data = {
            id: selected.attr('data-id'),
            title: video_title.val()
        };

    //When user click OK button, if Preview is true, it mean video not yet previewed
    if (window.UPLOAD.preview) {
        //set Preview is false to when video processed it will not display player
        window.UPLOAD.preview = false;

    } else {
        data['image'] = selected.attr('data-thumb')

    }

    $.ajax({
        type: 'POST',
        url: '/collection/media/save/video/',
        data: data
    }).done(function( response ) {
        //When saved video, always update Preview is true, it mean set back default
        window.UPLOAD.preview = true;

        return callback(response);
    });

}

function preview_medias(img_object) {

    var preview_modal = $("#preview_modal"),
        obj_title = img_object.attr('title').trim(),
        preview_url = img_object.attr('preview-url').trim(),
        media_type = $('#tabs ul li.ui-tabs-active').attr('data-type');

    //If user not yet closed Preview modal before open next time
    if (preview_modal.hasClass('in')) {
        return false;
    }

    //Bind Preview modal display status
    preview_modal.on({
        show: function() {
            //Set default text when waiting data loaded
            var modal_title = preview_modal.find('.modal-header h3');
            modal_title.text(obj_title);

            //Display loading modal when Preview modal be shown
            loading_modal(preview_modal.attr('id'), 'on');
        },
        hide: function() {
            //remove all sub container of preview div
            preview_modal.find('.modal-body .preview').empty();

            //Hide all preview DOM
            preview_modal.find('.modal-body .preview').hide();

            //In case YouTube, we re-init the DOM html to can playing next time
            var new_player = $('<div id="youtube_player" class="player"></div>');
            new_player.appendTo(preview_modal.find('.modal-body .video-preview'));

            //In case Vine
            //Remove all player has 'clone' class but skip vine_player
            preview_modal.find('.modal-body #vine-preview .clone').remove();

            //Make sure hide loading modal when Preview modal closed
            loading_modal(preview_modal.attr('id'), 'off');
        }
    })
    .modal('show');

    if (media_type == 'image') {
        //Init image DOM object to display in Preview modal
        var new_image = img_object.clone();

        //Update src of image
        new_image.attr('src', preview_url);

        //Make sure image-preview content is empty before display image
        preview_modal.find('.modal-body .image-preview').empty();

        //Apply image to display
        new_image.appendTo(preview_modal.find('.modal-body .image-preview'));

        //And show it
        preview_modal.find('.modal-body .image-preview').show();

        //Bind image loaded to hide loading modal
        new_image.on('load', function(event) {

            //Hide loading modal
            loading_modal(preview_modal.attr('id'), 'off');
        });


    } else {

        if (img_object.attr('alt') == 'vine') {

            var vine_preview = preview_modal.find('.modal-body #vine-preview'),
                temp_player = preview_modal.find('.modal-body #vine-preview #vine_player');

            //Update src for player
            temp_player.find('source').attr('src', preview_url);

            //Init new player to display instead of display vine_player
            var player = temp_player.clone();

            //Add playing id to make sure 1 id
            //Add class to remove it when modal closed
            player.attr('id', 'playing').addClass('clone');

            //Apply player to Vine preview container
            vine_preview.append(player.show()).show();

            //Bind player loaded to hide loading modal
            player.on("loadeddata", function () {

                //Hide loading modal
                loading_modal(preview_modal.attr('id'), 'off');
            });

        } else {

            var player = new YT.Player('youtube_player', {
                height: 315,
                width: 560,
                videoId: preview_url,
                playerVars: {
                    rel: 0,
                    autoplay: 1,
                    showinfo: 0
                },
                events: {
                    //When YouTube player ready loaded data and can play,
                    'onReady': function( event ) {

                        //Show YouTube player
                        preview_modal.find('.modal-body .video-preview').show();

                        //hide loading modal
                        loading_modal(preview_modal.attr('id'), 'off');
                    }
                }
            });
        }
    }
}