jQuery(function($){
    $(document)
    .on("click", "#my_wall_btn", function() {
            my_wall_post($(this).attr("id"), "my_wall_textarea", "frm_my_wall", "url_my_wall_save", "my_wall_wrapper")
    })
    .on("click", "#btn_my_wall_delete_message", my_wall_delete)
    .on("keypress", ".textarea_wall_post", my_wall_comment)
    .on("click", ".btn-delete-like a", set_delete_id)
    .on("keypress", "#my_wall_textarea", function(){
            //enable the submit button
            $("#my_wall_btn").attr("disabled", false);
            $(this).addClass("highlight")
        })
    .on("click", ".textarea_wall_post", function(){
            var id = $(this).attr("id").replace("textarea_wall_post","")
            $(this).addClass("highlight")
            hashtag($(this).attr('id'))
            $(".my_wall_text_comment_input #avatar_wrapper" + id).show()
            $(".my_wall_text_comment_input .control-group .controls #wrapper_textbox" + id + " div")
                .addClass("textbox_focus")
            $(".my_wall_text_comment_input #wrapper_textbox" + id).addClass("wrapper_textbox")
            $(this).focus()
    })
    .on ("blur", ".textarea_wall_post", function(){
            var id_blur = $(this).attr("id").replace("textarea_wall_post","")
            $(".my_wall_text_comment_input #avatar_wrapper" + id_blur).hide()
    })
    .ready(function(){
           hashtag("my_wall_textarea")
           $("#my_wall_btn").addClass("finished_hash_tag")
    })
})

function set_delete_id()
{
    $("#my_wall_delete_id").val($(this).attr('data-id'))
}

function my_wall_delete()
{
        $.ajax({
               type: 'post',
               url: $("#url_self_my_wall_delete").val(),
               data: {
                   'obj-id-message-delete':$("#my_wall_delete_id").val(),
                   'csrfmiddlewaretoken': $("#frm_my_wall input").val()
               },
                success:function(data) {
                    var return_delete_obj = jQuery.parseJSON(data),
                        delete_arr=return_delete_obj.delete_object,
                        return_delete_message = delete_arr[delete_arr.length-1]
                    $("#my_wall_delete_message").modal("hide")

                    //if not the user that create the message show the modal with error message
                    if (return_delete_message == "false") {
                        $("#my_wall_delete_message_permission").modal("show")
                    }

                    //if the user that create the message empty html node of the message
                    if (return_delete_message == "true") {
                        for (var j=0;j<delete_arr.length;j++){
                            $(".my_wall_wrapper #my-wall-post-"+delete_arr[j]).empty()
                            $("#my_wall_text_comment_input_"+delete_arr[j]).empty()
                        }
                    }
                    hashtag("my_wall_textarea")
                }
        })
}

function my_wall_comment(event)
{
    var id=$(this).attr("id"), parent_id = id.replace('textarea_wall_post_',''),
    comment_text = $(this).val().trim().length
    if (event.keyCode == 13 && comment_text != 0) {
        $(this).attr("disabled",true)
        $.ajax({
            type: 'post',
            url: $("#url_my_wall_save").val(),
            data: {
            'textbox_comment':$(this).val(),
            'message_id':parent_id,
            'csrfmiddlewaretoken':$("#frm_my_wall input").val()
            },
            success:function(data) {
            $("#my_wall_text_comment_input_"+parent_id).prev().append(data)
            $("#my-wall-no-message").empty()
            $("#"+id)
                .val(" ")
                .removeClass("my_wall_parent")
                .addClass("my_wall_child")
                .attr("disabled",false)
            }
        })
    }
}
