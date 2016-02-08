jQuery(function($){
$(document)
    .ready(function(){
        var max_height_value = 0,click_count = 0,
            top_height;
        $('#tabs').tab()
        $('#count').html($('#count_view').val())
        $('.list_designed_item > div[open-tooltip="1"]').popover({
            content:function() {
                return $(this).find('.item_tooltip').html()
            },
            html:true,
            placement:'right',
            trigger:'hover'
        })

        $("#list_designed_item").find(".abilities").each(function(){
            var height = $(this).css("height")
                height = height.replace("px","")
                height = parseInt(height)
            var top = $(this).css("top")
                top = top.replace("px","")
                top = parseInt(top)
            top_height = top+height
            if(max_height_value<top_height){
               max_height_value = top_height+300
            }
         })
        $("#list_designed_item").css("height",max_height_value);
    })
    .on("click","#btn_comment_right",function(){
        my_wall_post($(this).attr("id"), "right_text_comment", "comment_form", "url_collection_save_comment", "list_comment_item")
    })
    .on("keydown","#right_text_comment",function(){
            $("#btn_comment_right").attr("disabled",false)
    })
    .on("click", ".btn-delete-like a", set_collection_comment_id)
    .on("click", "#btn_my_wall_delete_message", collection_comment_delete)
    .on("click", "#btn_delete_collection", delete_collection)
    .on("click", "#btn_invite", invite)
    .on("click", "#btn_share", share)
    .on("click","#right_text_comment",function(){
        hashtag("right_text_comment")
        $("#btn_comment_right")
            .removeClass("wall-button")
            .addClass("after_initiate_hash_tag")
    })
})

function get_selected_user(user_array)
{
       var selected_user_array= []
       var j = 0
       for(var i=0;i<user_array.length;i++)
        {
            if(user_array[i].checked==true)
            {
                selected_user_array[j]=user_array[i].value;
				j++;
            }
        }
       return selected_user_array
}

function set_collection_comment_id()
{
    $("#collection_delete_id").val($(this).attr('data-id'))
}

function share()
{
    var user_array=document.getElementsByName("chk_share")
       $.ajax({
            async: false,
            type: "POST",
            dataType:"json",
			data: {
                    'post_selected_user_array[]':get_selected_user(user_array),
                    'set_id':$('#current_set_id').val()

                },
            beforeSend: function(xhr, settings) {
					 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
						 // Only send the token to relative URLs i.e. locally.
						 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
					 }
				},
			url:'/collection/share/',
            success: function(data) {
                $("#form_share").modal("hide")
                $("#form_shared").modal("show")
            }
    })
}
function invite()
{
    var user_invite_array=document.getElementsByName("chk_invite")
       $.ajax({
            async: false,
            type: "POST",
            dataType:"json",
			data: {
                    'post_selected_user_array[]':get_selected_user(user_invite_array),
                    'user_invite':$('#user_share').val(),
                    'set_id':$('#current_set_id').val()

                },
            beforeSend: function(xhr, settings) {
					 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
						 // Only send the token to relative URLs i.e. locally.
						 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
					 }
				},
			url:'/collection/invite/',
            success: function(data) {
                $("#form_invite").modal("hide")
                $("#form_invited").modal("show")
            }
       })
}

function delete_collection()
{
    $.ajax({
            async: false,
            type: "POST",
            dataType:"json",
			data: {
                    'set_id':$('#current_set_id').val()
                  },
            beforeSend: function(xhr, settings) {
					 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
						 // Only send the token to relative URLs i.e. locally.
						 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
					 }
				},
			url:'/collection/delete/',
            success: function(data) {
                $("#form_delete").modal("hide")
                $("#form_collection_deleted").modal("show")
                $("#btn_deleted").click(function(){
                    window.open('/collection/my-collections/','_parent')
                })
            }
    })
}

function collection_comment_delete()
{
        $.ajax({
               type: 'post',
               url: $("#url_self_collection_comment_delete").val(),
               data: {
                   'obj-id-message-delete':$("#collection_delete_id").val(),
                   'csrfmiddlewaretoken': $("#comment_form input").val()
               },
                success:function(data) {
                    var return_delete_obj = jQuery.parseJSON(data),
                        delete_arr=return_delete_obj.delete_object,
                        return_delete_message = delete_arr[delete_arr.length-1]
                    $("#my_wall_delete_message").modal("hide")

                    //if not the user that create the message show the modal with error message
                    if (return_delete_message == "false") {
                        $("#collection_comment_delete_message_permission").modal("show")
                    }

                    //if the user that create the message empty html node of the message
                    if (return_delete_message == "true") {
                        for (var j=0;j<delete_arr.length;j++){
                            $("#ajax_list_comment #my-wall-post-"+delete_arr[j]).empty()
                        }
                    }
                }
        })
}
