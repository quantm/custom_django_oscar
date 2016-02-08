var user_db_checked = document.getElementsByName("chk_my_event_select_participant")
$(document).ready(function(){
     $('#id_date_created')
        .datepicker({ format: 'yyyy-mm-dd',
                    todayHighlight: true
        });
    $("#my_event_select_participant_modal").click(function(){
        $("#participant_error .modal-header .close").html("x")
        $("#participant_error .modal-footer").show()
        $("#participant_create_participant_selected .modal-body label").remove();
    })

    $("#participant_error .modal-header .close").html(" ")

    $("#btn_edit_participant").click(function(){
        for(var k=0;k<user_db_checked.length;k++){
           $("#selected_edit_update_"+user_db_checked[k].value).prop("checked", true)
        }
        $("#form_edit_participant .modal-footer").show()
    })

})

function get_final_selected_user()
{
    var my_event_div_selected_user = []
    $("#my_event_div_selected_user").find("input").each(function(){
           my_event_div_selected_user.push($(this).val())
    })
    return my_event_div_selected_user
}

function set_check_box_stat(check)
{
    if(check != null)
    {
        for(var i=0;i<check.length;i++){
                //$("#selected_edit_update_"+check[i]).prop("checked", true)
                $("#selected_db_update_"+check[i]).hide()
                //$("#my_event_div_selected_user").append("<input type='hidden' class='my_event_hidden_user' name='my_event_hidden_user' value="+check[i]+">")
        }
    }
}
