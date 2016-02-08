// JavaScript Document
$(function() {
    var id_comment
    $(".collection_comment").mouseover(function(){
        $(this).find(".btn_delete_comment").show();
        $(this).find(".btn_delete_comment").addClass("btn_delete_show");
    })
    .mouseout(function(){
        $(this).find(".btn_delete_comment").hide()
    })
    .find(".btn_delete_comment").click(function(){
           id_comment=$(this).attr("id").replace("btn_delete_","")
        })
    $("#btn_delete_comment").click(function(){
         $.ajax({
                async: false,
                type: "POST",
                data: {
                        'id_comment':id_comment
                    },
                beforeSend: function(xhr, settings) {
                         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                             // Only send the token to relative URLs i.e. locally.
                             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                         }
                    },
                url:'/collection/comment/delete/',
                success: function(data) {
                    $("#form_delete_comment").modal("hide")
                    $("#collection_comment_"+id_comment).empty()
                }
            })
    })
})//end $(function()


