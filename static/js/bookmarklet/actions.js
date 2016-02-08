
jQuery(function( $ ){

    var args = {},
        hash,
        save_form = $('#save-form');

	if(/^#tagger:/.test(hash=location.hash)) args = unparam(location.hash.substr(8));

    if( location.hash ) {
        store_args_data( args );
    }

	onMessage( args, save_form );

    if( 'postMessage' in window ){
		$( window ).on( 'message', function( event ) {
			var args = unparam( event.originalEvent.data );

			onMessage( args, save_form );
		});
	} else {
		(function(  ){
			if( location.hash == hash || !/^#tagger:/.test( hash=location.hash ) ) return setTimeout( arguments.callee, 100 );
			var args = unparam( hash.replace(/^#tagger:/, '') );
			onMessage( args, save_form );
		})();
	}

    $( document )
        .ready( function(  ) {
            load_add_product_to_my_list_form( save_form, args );
        })
        .on( 'click', '#submit', function( event ) {
            var id_is_product = save_form.find("#id_is_product option:selected"),
                my_list = save_form.find("#my_collections option:selected");

            if ( id_is_product.val() == 1 && my_list.length > 0 ) {
                if ( my_list.val() != -1 ) {

                    $( document ).find( 'form #lid' ).val( my_list.val() );
                    $( document ).find( 'form #lname' ).val( my_list.text() );

                } else {

                    save_form.find("#create_new_form").addClass("error");
                    alert("Create list before.");
                    return false;
                }
            }
            $(this).attr('disabled','disabled').text('Sending');
            $("#id_description_wrapper .controls .textntags-wrapper #id_bookmark_description ")
                .textntags('reset', function(data) {});
            save_form.submit();
        })
        .on('click', 'a.img-pick', function( event ) {
            previous_or_next_image( args, $(this) )

        })
        .on('click', '.close_box, .close', function( event ) {
            send( {cmd:'close'}, args );
            return false;

        })
        .on('click', '.finished', function( event ) {
            setTimeout( function(  ){ send({cmd:'close'}, args) }, 100 );

        })
        .on('click', '#btn_come_back', function( event ) {
            come_back_form();

        })
        .on('change', '#id_is_product', function( event ) {
            load_add_product_to_my_list_form( save_form, args );

        });
});

function load_add_product_to_my_list_form ( save_form, args ) {
    var is_product_selected = save_form.find("#id_is_product option:selected")
    if ( args.caption == 'image' && parseInt(is_product_selected.val()) == 1 ) {

        var append_to = save_form.find("#is_product_append_controls");
        init_add_product_to_collection( {type: 'list'}, append_to, function( response ) {

        });

        save_form.find("#is_product_append_controls").show();

    } else {

        save_form.find("#is_product_append_controls").hide();

    }
}


// send data to parent window
function send( data, args ){

    var p = window.parent,
        d = $.param( data ),
        u = args.loc + '#tagger:' + d,
        l = args.loc.match(/^https?:\/\/[^\/]+/)[0];

    try{
        p.postMessage( d, l )
    } catch( e1 ){
        try{
            p.location.replace( u )
        }catch( e ){
            p.location.href = u
        }
    };
}

// unparam
function unparam( s ) {
    var a={},i,c;s=s.split('&');for(i=0,c=s.length;i<c;i++)if(/^([^=]+?)(=(.*))?$/.test(s[i]))a[RegExp.$1]=decodeURIComponent(RegExp.$3||'');return a

}

function onMessage( args, form_obj ) {

    args.total = parseInt( args.total ) || 0;
    args.idx = parseInt( args.idx ) || 0;

    // no image...
    if( args.total == 0 ) {
        $(document).find('#form_content').hide();
        $(document).find('#empty_content').show();
        $(document).find('.footer .submit-button #submit').hide();
        $(document).find('.footer .submit-button #close_btn').show();

        return $('form.no_image').show().siblings('form').hide() && resize();
    }


    form_obj.find('#id_title').val( args.title );
    form_obj.find('#f-tag_url').val( args.loc );
    form_obj.find('a.img-pick').addClass('disabled');

    if( args.idx > 0 ) {
        form_obj.find('a.img-pick[did="0"]').removeClass('disabled');
    }

    if( args.idx < args.total - 1 ) {
        form_obj.find('a.img-pick[did="1"]').removeClass('disabled');
    }

    form_obj.show().siblings('form').hide();
    form_obj.find('#f-picked-image').load( resize ).attr( 'src', args.src ).attr( 'idx',args.idx );
    form_obj.find('#id_image').val( args.src );

    if( args.caption=='image' ) {
        form_obj.find('#id_is_product_wrapper').show();
        form_obj.find('#id_is_video_wrapper').hide();
        form_obj.find('#caption').removeClass('video-caption').addClass('image-caption');
    } else {
        form_obj.find('#id_is_product_wrapper').hide();
        form_obj.find('#id_is_video_wrapper').show();
        form_obj.find('#caption').html('').removeClass('image-caption').addClass('video-caption');
    }

    form_obj.find('#id_video_code').val( args.video );

    store_args_data(args);
}

function resize(  ) {
    var $main = $('#main'), $win = $(window);
    function ask(  ) {
        //send({ cmd: 'resize', h: $main.height() });
        setTimeout(function(  ) {
            if($win.height() < $main.height()) resize();
        }, 100);
    };
    setTimeout( ask, 1 );
}

function previous_or_next_image( args, object ) {
    var did = parseInt(object.attr('did')),
        idx = parseInt($('#f-picked-image').attr('idx'))||0;
    if( object.hasClass('disabled') ) {
        return false;
    }
    idx += did?1:-1;
    send( {cmd:'index',idx:idx}, args );
    return false;
}

//Get cookie for post event
function getCookie( name ) {
     var cookieValue = null;
     if ( document.cookie && document.cookie != '' ) {
         var cookies = document.cookie.split( ';' );
         for ( var i = 0; i < cookies.length; i++ ) {
             var cookie = jQuery.trim(cookies[i]);
             // Does this cookie string begin with the name we want?
             if ( cookie.substring(0, name.length + 1) == (name + '=') ) {
                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                 break;
            }
        }
    }
    return cookieValue;
 }

function come_back_form() {
    $('.content #message_content').hide();
    $('.content #form_content').show();
    $('.footer .submit-button .submit').show();
    $('.content .textntags-beautifier div').empty();
    $('.content .textntags-beautifier div strong span').html("");
    /*
    $('#form_content #id_description')
        .val("test")
        .textntags('reset', function(data) {});
    */
}


function save( form_obj, callback ) {

    var params = {title: '', image: ''},
        allow_submit = true,
        idx = parseInt(form_obj.find('#f-picked-image').attr('idx'))||0;

    for( var x in params ) {
        if( params.hasOwnProperty( x ) ) {
            var value = $.trim(form_obj.find('#id_'+x).val());
            if(value!='') {
                params[x] = value
                form_obj.find('#id_'+x).removeClass('error-field');
            } else {
                allow_submit = false;
                form_obj.find('#id_'+x).addClass('error-field');
            }
        }
    }

    if( allow_submit ) {
        post_to_server( form_obj, function( response ) {
            return callback( response );
        })
    }
}

function post_to_server( form_obj, callback ) {

    $.ajax({
        dataType: "json",
        type: form_obj.attr('method'),
        url: form_obj.attr('action'),
        data: form_obj.serialize(),
        beforeSend: function(xhr, settings) {
             if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                 // Only send the token to relative URLs i.e. locally.
                 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
             }
        }
   }).done( function( response ) {
        return callback( response );
   });
}

function store_args_data( args ) {
    $( document ).find( 'form #caption' ).val( args.caption );
    $( document ).find( 'form #idx' ).val( args.idx );
    $( document ).find( 'form #loc' ).val( args.loc );
    $( document ).find( 'form #src' ).val( args.src );
    $( document ).find( 'form #title' ).val( args.title );
    $( document ).find( 'form #total' ).val( args.total );
    $( document ).find( 'form #video' ).val( args.video );
}