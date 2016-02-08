function my_wall_post(id_btn, id_textbox, frm_id, url, div_append)
{
    var message = $("#"+id_textbox).val().trim().length
     if (message == 0) {
        $("#"+ frm_id + " .control-group").addClass("error")
        $("#"+ frm_id + " .control-group .controls span").html("This field is required").show()
     }
     if (message != 0) {
        $("#"+ frm_id + " .control-group").removeClass("error")
        $("#"+ frm_id + " .control-group .controls span").hide()
     }
     if (message > 500) {
        $("#"+ frm_id + " .control-group").addClass("error")
        $("#"+ frm_id + " .control-group .controls span").html("Message must be less than 500 character").show()
     }
     if (message != 0 && message < 500) {
         //disable the submit button to prevent duplicate submit
        $("#"+id_btn)
            .attr("disabled",true)
            .html("Submitting...")
            .removeClass("wall-button")
            .addClass("wall-button-submiting")
        $.ajax({
        type: 'post',
        url: $("#"+url).val(),
        data: $("#"+frm_id).serialize(),
        success:function(data) {
            $("#"+id_textbox).val(" ")
            $("."+div_append).prepend(data)
            $("#my-wall-no-message").hide()
            $("#"+id_btn)
                .removeClass("wall-button-submiting")
                .addClass("wall-button")
                .html("Submit")
            var appended_parent = $("#appended_parent").val()
            $("#"+appended_parent)
                .removeClass("my-wall-message-link")
                .addClass("wall_appended")
            $("#"+id_textbox).textntags("reset")
        }
        })
     }
}
