var request;
$(document).ready(function(){
    if($("#check_if_update").val() == 1){
        $("#id_name").val($("#update_name").val())
        $("#id_date_created").val($("#update_date_created").val())
        $("#id_description").val($("#update_description").val())
    }
    $(".modal-footer").hide();

    //my event create - get user id from modal
    $("#btn_my_event_select_participant").click(function(){
        var user_my_event_create_selected = $(".chk_my_event_add_create")
        var arr_participant_insert_db = my_event_get_final_selected_user(user_my_event_create_selected)
        if(arr_participant_insert_db != null){
            $("#participant_error_text").hide()
        }
        $("#participant_error").modal("hide")
        $("#participant_create_participant_selected .modal-header .close").html("")
        $("#participant_create_participant_selected").addClass("header_display_block")
        for(var k=0;k<arr_participant_insert_db.length;k++){
                var img_path = $("#participant_error #bootstrap_label_user_"+arr_participant_insert_db[k]+" img").attr("src")
                $("#participant_create_participant_selected .modal-body").append('<label title="User'+arr_participant_insert_db[k]+'" id="bootstrap_label_user_'+arr_participant_insert_db[k]+'" class="child">' +
                    '<img src="'+img_path+'" class="comment_avatar" title="User'+arr_participant_insert_db[k]+'">' +
                    '<input type="checkbox" value="'+arr_participant_insert_db[k]+'" name="chk_my_event_select_participant" id="selected_db_update_'+arr_participant_insert_db[k]+'" class="participant_create_append_selected" style="display: none;">'+
                    '</label>')
        }

    })

    //creator update event
    $("#btn_event_update").click(function(){
        var user_array = document.getElementsByName('chk_my_event_select_participant'),
            user = get_final_participant(user_array),
            index_search = user.indexOf(parseInt($("#log_id").val()))
        if(index_search!=-1){user.splice(index_search, 1);}
        $("#my_event_selected_user_array").val(user)
        $("#my_event_participant_quantity").val(get_final_participant(user_array).length)
        ajax_call()
    })

    //new event
    $('#btn_new_event').click(function(){
        var user_array = $(".participant_create_append_selected")
        $("#my_event_selected_user_array").val(get_final_participant(user_array))
        $("#my_event_participant_quantity").val(get_final_participant(user_array).length)
        ajax_call()
    })

function ajax_call()
{
                    request=$.ajax({
                    async: false,
                    dataType: "json",
                    type: $("#frm_my_event_post").attr('method'),
                    url: $("#frm_my_event_post").attr('action'),
                    data: $("#frm_my_event_post").serialize(),
                beforeSend: function(xhr, settings) {
                    $("#btn_new_event").html("Saving...")
                    $("#btn_event_update").html("Saving...")
                },
                success: function (data) {
                    for(var h=0;h<data.result.length;h++)
                    {
                        if(data.result[h].code != 2){
                            if(data.result[h].id == "participant"){
                            $("#"+data.result[h].id+"_error").addClass("participant-error");
                            }
                            else if (data.result[h].id != "participant"){
                             $("#"+data.result[h].id+"_error").addClass("error");
                            }
                            $("#"+data.result[h].id+"_error_text").show();
                            $("#"+data.result[h].id+"_error_text").html(data.result[h].message);
                        }
                        if(data.result[h].code == 2){
                            $(".alert").hide()
                            if(data.result[h].id == "participant"){
                            $("#"+data.result[h].id+"_error").removeClass("participant-error");
                            }
                            else if (data.result[h].id != "participant"){
                             $("#"+data.result[h].id+"_error").removeClass("error");
                            }
                            $("#"+data.result[h].id+"_error_text").hide();
                        }
                        if(data.result[h].code == 4){
                            $("#my_event_update_message_permission .modal-footer").show()
                            $("#my_event_update_message_permission").modal("show")
                        }
                        if(data.result[h].code == "update_success" || data.result[h].code == "save_success"){
                            window.open("/social/my-event/","_parent")
                        }
                    }
                },
                error: function(data) {

                }
        }).done(function(){
                    request = null
                    $("#btn_new_event").html("Save")
                    $("#btn_event_update").html("Save")
        })
}

    //update participant select or un select
    $("#btn_event_participant").click(function(){
        var user_checkbox_node_list = document.getElementsByName("chk_event_participant"), user_db_checked = document.getElementsByName("chk_my_event_select_participant"),
            user_edit_select = my_event_get_final_selected_user(user_checkbox_node_list),
            user_edit_un_select = my_event_get_final_un_selected_user(user_checkbox_node_list),
            user_object = []
            //console.log("Selected:"+user_edit_select)
            //console.log("Un Selected:"+user_edit_un_select)
        for(var k=0;k<user_db_checked.length;k++){
           user_object.push(parseInt(user_db_checked[k].value))
        }

        for(var k=0;k<user_edit_select.length;k++){
            if($.inArray(user_edit_select[k],user_object) == -1){
                var img_path = $("#form_edit_participant #bootstrap_label_user_"+user_edit_select[k]+" img").attr("src")
                $("#participant_error .modal-body").append('<label title="User'+user_edit_select[k]+'" id="bootstrap_label_user_'+user_edit_select[k]+'" class="child">' +
                    '<img src="'+img_path+'" class="comment_avatar" title="User 10">' +
                    '<input type="checkbox" value="'+user_edit_select[k]+'" name="chk_my_event_select_participant" id="selected_db_update_'+user_edit_select[k]+'" class="" style="display: none;">'+
                    '</label>')
            }
        }

        for(var p=0;p<user_edit_un_select.length;p++){
            if($.inArray(user_edit_un_select[p],user_object) != -1){
                $("#participant_error .modal-body #bootstrap_label_user_"+user_edit_un_select[p]).remove()
            }
        }
        $("#form_edit_participant").modal("hide")
         $("#my_event_selected_user_array").val( get_final_participant(user_db_checked))
        $("#participant_error").removeClass("header_display_none")
    })
})


function get_final_participant(array_user)
{
    var final_participant = []
    for(var t=0;t<array_user.length;t++){
        final_participant.push(parseInt(array_user[t].value))
    }
    return final_participant
}

function my_event_get_final_selected_user(user_array)
{
       var selected_user_array= []
       var d = 0
       for(var e=0;e<user_array.length;e++)
        {
            if(user_array[e].checked==true)
            {
                selected_user_array[d]=parseInt(user_array[e].value);
				d++;
            }
        }
       return selected_user_array
}

function my_event_get_final_un_selected_user(user_array)
{
       var un_selected_user_array= []
       var j = 0
       for(var i=0;i<user_array.length;i++)
        {
            if(user_array[i].checked==false)
            {
                un_selected_user_array[j]=parseInt(user_array[i].value);
				j++;
            }
        }
       return un_selected_user_array
}

function update_hide_checkbox(user_array_update,type)
{
    if(type == "update"){
        $("#btn_edit_participant").removeClass('display_none')
        $("#btn_edit_participant").addClass('participantupdate')
    }
    if(type == "details"){
            for(var k=0;k<=user_array_update.length;k++){
                $("#selected_db_update_"+user_array_update[k]).hide();
            }
    }
}