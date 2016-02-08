window.SCROLLER = { 
    is_scrolling: 1,
    current_page: 1,
    type: 0,
    get_url: function(){

        var page = this.current_page + 1,
            ajax_url = '';

        if(this.type == 0){
            ajax_url = "/products/view-product-of-page/" + page + "/";
        }

        if(this.type == 1){
            ajax_url = "/api/products/by-all-time/?format=html&page=" + page;
        }

        if(this.type == 2){
            ajax_url = "/api/products/by-month/?format=html&page=" + page;
        }

        if(window.location.pathname.indexOf("/products/my-products/") != -1){
            ajax_url = "/products/my-product-of-page/" + page + "/";
            var user_id = $('#view-user-profile').attr('data-view-user-id');
            if(user_id > 0) {
                ajax_url = "/products/my-product-of-page/" + page + "/?user_id=" + user_id;
            }
        }

        if(window.location.pathname.indexOf("/social/my-friends/") != -1){
            ajax_url = "/api/social/friends/?page=" + page + '&format=html';
            var user_id = $('#view-user-profile').attr('data-view-user-id');
            if(user_id > 0) {
                ajax_url = "/api/social/friends/"+ user_id +"/?page=" + page + '&format=html';
            }
        }

        return ajax_url;
    }
};
window.ACTION_NAME = "";
window.SHARE_INFO = {
    link: "",
    image_url: "",
    title: "",
    desc: "",
    caption: 'I love this'
};

window.CART_INFO = {
    action: "",
    csrfmiddlewaretoken: "",
    product_id: 0,
    quantity: 0
}

window.PLUS = {
    product_id: "",
    product_name: "",
    product_image: "",
    modal_id: "#ask_before_add_product_modal"
}

jQuery(function($){

    sign_in_modal_init(function(data){
        if (window.ACTION_NAME) {
            $.cookie("just_logged_in",true);
            $.cookie("action_name",window.ACTION_NAME);
            $.cookie("share_info",JSON.stringify(window.SHARE_INFO));
            $.cookie("cart_info",JSON.stringify(window.CART_INFO));
            $.cookie("plus", JSON.stringify(window.PLUS));
        }
        if (window.ACTION_NAME == 'detail') {
            remove_all_cookies_action();
            window.location.href = window.SHARE_INFO.link;
            return;
        }
        window.location.reload();
    });

	$( document ).on({
		click: click_prod,
		mouseenter: show_opacity,
		mouseleave: hide_opacity	
	}, 'a.prod-link');

    $( document ).on( "click", '#bt-share-fb',share_fb)
                 .on( "click", '#bt-share-tw',share_tw)
                 .on( "click", '#bt-share-gg',share_gg)
                 .on( "click", '#bt-share-tb',share_tb)
                 .on( "click", '#profile-avatar', edit_avatar)
                 .on( "click", '#sort-most-buy', sort_most_buy)
                 .on( "click", '#sort-most-buy-in-month', sort_most_buy_in_month)
                 .on('click', '#text_btn_save',save_promote)
                 .on('click','#add_to_promote',action_modal_text_promote)
                 .on('click', '#text_promote_media_preview', function(event){$('#text_promote_modal').modal('hide')})
                 .on('click', '#btn_remove_media', remove_promote_media);
    try{
        insert_media_action('#text_promote_media_preview', function(selected_obj){
            get_selected_media(selected_obj);
        });
        init_sign_in_facebook('login_facebook', function ( response_str ) {
            response_obj = jQuery.parseJSON(response_str);
            if (response_obj.code == 1) {
                $('.login-msg').html('Login success');
                if (window.ACTION_NAME) {
                    $.cookie("just_logged_in",true);
                    $.cookie("action_name",window.ACTION_NAME);
                    $.cookie("share_info",JSON.stringify(window.SHARE_INFO));
                    $.cookie("cart_info",JSON.stringify(window.CART_INFO));
                    $.cookie("plus", JSON.stringify(window.PLUS));
                }
                if (window.ACTION_NAME == 'detail') {
                    remove_all_cookies_action();
                    window.location.href = window.SHARE_INFO.link;
                    return;
                }
                window.location.reload();
            }else{
                $('.login-msg').html('Login fail');
                $this.removeAttr('disabled');
            }
        });
    }catch(err){
    }

    $(document).on('click','#add_to_my_list, #add_to_magazine', function(){
        do_add_product_to( $(this).attr( "add_to"), function( response ) {
            loading_modal( $( window.PLUS.modal_id).attr('id'), 'on' );
            response.product_id = window.PLUS.product_id;
            add_product_to_collection( response, function( response_returned ) {

                $(window.PLUS.modal_id).modal( 'hide' );
                processing_after_saved( response_returned );
            });

        });
    });

	if(window.Masonry){
        $('#prod-masonry').imagesLoaded(function(){
            $('#prod-masonry').fadeIn(800);
            window.MSNRY = $('#prod-masonry').masonry({
                columnWidth: 38,
                itemSelector: '.prod-item'
            })
        });
	}

    $('.total-page.loading').hide();
    $('.prod-mod .pager').show();

    set_action_after_login();

    $('#shareModal, #insert_media, #normal_modal').on('shown',remove_all_cookies_action);
    $(window).scroll(on_window_scroll);
});

$(window).on('load',function(){

});

function on_window_scroll() {	
	if  ($(window).scrollTop() >= ($(document).height() - $(window).height()) / 1.1 ) {
		var total_page = $('.total-page').attr('data-total-page');
        /* console.log(window.SCROLLER.current_page, window.SCROLLER.is_scrolling, total_page); */
		if ((window.SCROLLER.is_scrolling == 1) && (total_page > 1) && (window.SCROLLER.current_page < total_page)) {
			get_page_on_scroll();
		}
	}
}

function click_prod(event) {
    var a_link = $(this),
		is_logged_in = $(this).attr('osc-logged-in'),
		form_add_cart = $(this).find('form#add-to-cart'),
        product_image_url = a_link.find('img.thumbnail').attr('src');
        product_name = a_link.find('h3.title').html();

    if (is_logged_in == 1) {
	
        window.ACTION_NAME = "";
        remove_all_cookies_action();
        if ($(event.target).attr('osc-icon') == "cart") {
		
            event.preventDefault();
            $(event.target).addClass('loading');
            $.post(form_add_cart.attr('action'), form_add_cart.serialize(), function(data, textStatus, jqXHR){
                if(data != 'error'){
                    $('ul.cart').html(data);
                    $(".cart").find('button.dropdown-toggle').click();
                }else{
                    alert('Error add item cart');
                }
            })
            .fail(function(data) {
                alert('Error add item cart');
            })
            .always(function(){
                $(event.target).removeClass('loading');
            })
			
        }
        if ($(event.target).attr('osc-icon') == "share") {
            event.preventDefault();
            set_share_box(a_link);
            $('#shareModal').modal();
        }

		if ((event.target.id).match(/\plus-product-\d+/) != null) {
            window.PLUS.product_id = $(event.target).attr('data-id');
            window.PLUS.product_image = product_image_url;
            window.PLUS.product_name = product_name;
            set_modal_plus_button();
			return false;
		}

    }else{
	
        event.preventDefault();
        remove_all_cookies_action();
        if($(event.target).attr('osc-icon') == "cart"){
            window.CART_INFO.action = form_add_cart.attr('action');
            window.CART_INFO.product_id = form_add_cart.find('#id_product_id').val();
            window.CART_INFO.quantity = form_add_cart.find('#id_quantity').val();
            window.ACTION_NAME = "cart";
        }
        if ($(event.target).attr('osc-icon') == "share") {
            window.ACTION_NAME = "share";
            var pro_info = a_link.find('.prod-info').html();

            window.SHARE_INFO.image_url = product_image_url;
            window.SHARE_INFO.link = window.BASE_URL + a_link.attr('href');
            window.SHARE_INFO.title = a_link.find('h3.title').html();
            window.SHARE_INFO.pro_info = Base64.encode(pro_info);
        }
		if ($(event.target).attr('osc-icon') == "plus") {
			window.ACTION_NAME = "plus";
			window.PLUS.product_id = $(event.target).attr('data-id');
            window.PLUS.product_image = product_image_url;
            window.PLUS.product_name = product_name;

		}
        if (!$(event.target).attr('osc-icon') || $(event.target).attr('osc-icon') == "") {
            window.ACTION_NAME = "detail";
            window.SHARE_INFO.link = window.BASE_URL + a_link.attr('href');
        }

        $('#loginModal').modal();
    }
}

function show_opacity(event){
	var $this = $(this),
		height = $this.height(),
		div_order = $this.find('.prod-opacity'),
		div_info = $this.find('.prod-info'),
		icon_order = $this.find('.icon-shopping-cart'),
		icon_share = $this.find('.icon-share-alt'),
		icon_plus = $this.find('.icon-plus');

    if(icon_order){
        icon_order.show();
    }
    icon_share.show();
    div_order.show();
    div_order.height(height - 10);
    div_info.show();
    icon_plus.show();
}

function hide_opacity(event){
	var $this = $(this),
		div_order = $this.find('.prod-opacity'),
        div_info = $this.find('.prod-info'),
        icon_order = $this.find('.icon-shopping-cart'),
        icon_share = $this.find('.icon-share-alt'),
        icon_plus = $this.find('.icon-plus');

    if(icon_order){
        icon_order.hide();
    }

    icon_share.hide();
    div_order.css('display','none');
    div_info.hide();
    icon_plus.hide();
}

function set_share_box($this){
    var share_modal = $('#shareModal'),
        img_src = $this.find('img.thumbnail').attr('src'),
        pro_info = $this.find('.prod-info').html();

    share_modal.find('img.share-thumb').attr('src',img_src);
    share_modal.find('.share-text').html(pro_info);

    /* FB */
    window.SHARE_INFO.image_url = img_src;
    window.SHARE_INFO.link = window.BASE_URL + $this.attr('href');
    window.SHARE_INFO.title = $this.find('h3.title').html();

}

function set_share_popup_after_logged_in(img_src, pro_info){
    var share_modal = $('#shareModal');
    share_modal.find('img.share-thumb').attr('src',img_src);
    share_modal.find('.share-text').html(pro_info);
}

function set_action_after_login(){
    if($.cookie("just_logged_in")){
        if($.cookie("action_name") == "cart"){
            var cart_info = $.parseJSON($.cookie("cart_info")),
            action = cart_info.action;
            cart_info.csrfmiddlewaretoken = $.cookie("csrftoken");
            add_item_to_cart_after_login(action, cart_info);
            remove_all_cookies_action();
        }
		
        if($.cookie("action_name") == "share"){
            window.SHARE_INFO = $.parseJSON($.cookie("share_info"));
            set_share_popup_after_logged_in(window.SHARE_INFO.image_url, Base64.decode(window.SHARE_INFO.pro_info));
            $('#shareModal').modal();
        }
		
		if($.cookie("action_name") == "plus"){
			window.PLUS = $.parseJSON($.cookie("plus"));
            set_modal_plus_button()
        }
    }else{
        remove_all_cookies_action();
    }
}

function remove_all_cookies_action(){
    $.removeCookie("just_logged_in");
    $.removeCookie("action_name");
    $.removeCookie("share_info");
    $.removeCookie("cart_info");
	$.removeCookie("plus");
}

function add_item_to_cart_after_login(action, post_param){
    $.post(action, post_param, function(data, textStatus, jqXHR){
        if(data != 'error'){
            $('ul.cart').html(data);
            $(".cart").find('button.dropdown-toggle').click();
        }else{
            alert('Error add item cart');
        }
    })
    .fail(function(data) {
        alert('Error add item cart');
    })
}

function share_tw(event){
	event.preventDefault();
    window.open("https://twitter.com/intent/tweet?original_referer="+ window.BASE_URL + "&text="+ window.SHARE_INFO.title +"&url=" + window.SHARE_INFO.link + "&via=" + window.BASE_URL, "_blank", "toolbar=no, scrollbars=no, resizable=yes, width=500, height=300");
}

function share_gg(event){
	event.preventDefault();
    window.open("https://plus.google.com/share?url=" + window.SHARE_INFO.link,"_blank","toolbar=no, scrollbars=no, resizable=yes, width=500, height=500");
}

function share_tb(event){
	event.preventDefault();
    window.open("https://www.tumblr.com/share/link?url="+ encodeURIComponent(window.SHARE_INFO.link) + "&name="+ window.SHARE_INFO.title +"&description=" + window.SHARE_INFO.caption, "_blank", "toolbar=no, scrollbars=no, resizable=yes, width=500, height=440");
}


function share_fb(event){
	event.preventDefault();
	FB.ui({
		method: 'feed',
		name: window.SHARE_INFO.title,
		link: window.SHARE_INFO.link,
		picture: window.SHARE_INFO.image_url,
		caption: window.SHARE_INFO.caption,
		description: window.SHARE_INFO.desc,
        display: "popup",
		message: ''
	});
}

function get_page_on_scroll(){
    window.SCROLLER.is_scrolling = 0;

    var url = window.SCROLLER.get_url();

    $('.total-page.loading').show();
	
    $.get(url, function(data){
	
        var $moreBlocks = $($.parseHTML(data));

        window.MSNRY.append( $moreBlocks );
        $moreBlocks.hide();

        window.MSNRY.imagesLoaded(function(){
            $moreBlocks.show();
            window.MSNRY.masonry('appended', $moreBlocks );

            $('.total-page.loading').hide();
            window.SCROLLER.current_page = window.SCROLLER.current_page + 1;
            window.SCROLLER.is_scrolling = 1;
        });

    }).fail(function(){
		alert('Load page fail');
    })
}

function edit_avatar(event){
    $('#ImageUploadModal').modal();
}

function sort_most_buy(event){
    event.preventDefault();
    window.SCROLLER.current_page = 0;
    window.SCROLLER.type = 1;
    $('#prod-masonry').html('');
    window.MSNRY.masonry();
    get_page_on_scroll();
}

function sort_most_buy_in_month(event){
    event.preventDefault();
    window.SCROLLER.current_page = 0;
    window.SCROLLER.type = 2;
    $('#prod-masonry').html('');
    window.MSNRY.masonry();
    get_page_on_scroll();
}

function save_promote(event){
    var text_promote_modal = $('#text_promote_modal'),
        text = $('#text_promote').val(),
        $this = $(this);

    if($.trim(text) == ""){
        alert('Your text can not blank');
        return
    }

    post_data = $('#frm_save_promote').serialize();

    $this.attr('disabled','disabled');

    $.post('/social/save-promote/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            text_promote_modal.modal('hide');
        }else{
            alert(data.error);
            text_promote_modal.modal('hide');
        }
    },"json")
    .fail(function(data) {
        alert("Request fail");
    }).always(function(){
        $this.removeAttr('disabled');
    })
}

function set_modal_plus_button(){
    //Fix multiple modal
    //$.fn.modal.Constructor.prototype.enforceFocus = function () {};
    var normal_modal = $('#normal_modal'),
        text_promote_modal = $('#text_promote_modal');
    normal_modal.find('#message').hide()
    normal_modal.find('.normal-modal-title').html('Add Product To');
    normal_modal.find('#normal_modal_btn_ok').hide();
    normal_modal.find('.modal-body').html('<p id="list_function_of_btn_plus" style="text-align:center"><button id="add_to_promote" class="btn" disabled="">Loading</button> <button id="add_to_my_list" class="btn margin20" add_to="list">Add to my Lists</button> <button id="add_to_magazine" class="btn" add_to="collection">Add to my Magazines</button></p>');
    normal_modal.modal();
    check_product_ready_promote();
}

function action_modal_text_promote(){

    var normal_modal = $('#normal_modal'),
        text_promote_modal = $('#text_promote_modal');

    $('#insert_media').unbind('hide');
    $('#insert_media').on('hide', function(){
        text_promote_modal.modal();
    });
    normal_modal.modal('hide');
    text_promote_modal.modal();
}

function get_selected_media(selected_obj){
    var text_promote_modal = $('#text_promote_modal'),
        media_id = selected_obj.attr('data-id'),
        media_image = selected_obj.find('img.collection_thumbnail').attr('src');

    text_promote_modal.find('#text_promote_media_id').val(media_id);
    text_promote_modal.find('#text_promote_media_preview').html('<img src="'+media_image+'">');
    text_promote_modal.modal();
}

function check_product_ready_promote(){
    var post_data = {
        csrfmiddlewaretoken : $.cookie("csrftoken"),
        product_id: window.PLUS.product_id
    }
    $.post('/social/check-user-ready-promote-this-product/', post_data, function(data){
        return set_status_button_promote(data);
    },'json')
}

function set_status_button_promote(data_obj){
    var normal_modal = $('#normal_modal'),
        text_promote_modal = $('#text_promote_modal'),
        data = {
            product_id: window.PLUS.product_id,
            product_title: window.PLUS.product_name,
            product_image: window.PLUS.product_image,
            media_id: data_obj.media_id,
            media_type: data_obj.media_type,
            media_image: function(){
                if (data_obj.status == 1 && data_obj.media_id != "") {
                    return '<img src="'+data_obj.media_image+'">'
                }else{
                    return 'Click to add Media'
                }
            },
            media_title: data_obj.media_title,
            promote_text: data_obj.promote_text
        }


    if(data_obj.error == ""){
        text_promote_modal.find('#text_promote_media_id').val(data.media_id);
        text_promote_modal.find('#text_promote_media_preview').html(data.media_image);
        text_promote_modal.find('#text_promote').val(data.promote_text);
        text_promote_modal.find('#text_promote_product_id').val(data.product_id);
        text_promote_modal.find('h3.modal-title').html(data.product_title);
        text_promote_modal.find('.product_image').html('<img src="'+data.product_image+'">');
        if(data.media_id != ""){
            text_promote_modal.find('#btn_remove_media').show();
        }else{
            text_promote_modal.find('#btn_remove_media').hide();
        }
        if(data_obj.status == 0){
            normal_modal.find('#add_to_promote').text('Add to promote');
        }
        else{
            normal_modal.find('#add_to_promote').text('Update my offer');
        }
        normal_modal.find('#add_to_promote').removeAttr('disabled');
    }else{
        message_modal('normal_modal', {type : 'on', class : 'text-error', message: 'Can not get status this product'})
    }
}

function remove_promote_media(){
    var text_promote_modal = $('#text_promote_modal');
    text_promote_modal.find('#text_promote_media_preview').html('Click to add Media');
    text_promote_modal.find('#text_promote_media_id').val('');
}

function do_add_product_to( type, callback ) {
    var add_product_modal = $( window.PLUS.modal_id );

    add_product_modal.unbind( 'show' );
    $('#normal_modal').modal('hide');

    add_product_modal.on( 'show', function(  ) {

        var params = { type: type, load_callback: data_load_ready }

        init_add_product_to_collection( params, add_product_modal.find( '#form_content' ), function( response ) {

            return callback( response );
        });

        $("button#add_btn").unbind('click');

        loading_modal(add_product_modal.attr('id'), 'on');

    }).on( 'hide', function() {
        add_product_modal.find("#form_content .control-group").hide();

    });

    add_product_modal.modal();
}

function data_load_ready(args) {
    if( args != null ) {
        loading_modal($(window.PLUS.modal_id).attr('id'), 'off');
    }
}

function add_product_to_collection( params, callback ){

    add_facebook_access_token( params, function ( new_params ) {

        $.ajax({ // create an AJAX call...
            type: 'POST',
            url: '/collection/add-product-to-collection/',
            data: new_params,
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                     // Only send the token to relative URLs i.e. locally.
                     xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            },
            success: function ( response ) {
                loading_modal($( window.PLUS.modal_id).attr('id'), 'off');
            },
            error: function( jqxhr ) {

            }
        }).done(function( response ) {

            return callback( response );

        });
    });

}

function add_facebook_access_token( params, callback ) {
    var accessToken = null,
        auth = FB.getAuthResponse();
    if(auth != null && auth!= ''){
        params.fb_token = auth['accessToken'];
    }

    return callback( params );
}

function processing_after_saved( response ) {

    var message_modal = $("#add_product_modal_message");

    message_modal.find( '.modal-body .message-string' ).html( response.message );
    message_modal.find( '.modal-body .url-open-collection a' ).attr(
        {
            'href': response.link.url,
            'title': response.link.text
        }
    ).html( response.link.text );

    message_modal.modal('show').find('a.close-modal').click(function(){
        message_modal.modal('hide');
    });
}
