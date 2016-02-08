/**
 * Created by Tam on 1/6/14.
 */

jQuery(function($){
    $( document ).on( "click", '#accept_request', accept_friend_request)
                .on( "click", '#unfriend_request', unfriend_request)
                .on( "click", '#delete_request', delete_request)
                .on( "click", '#make_friend', make_friend_request)
                .on( "click", '#make_follow', make_follow)
                .on( "click", '#unfollow', unfollow);
});

function make_friend_request(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'make_friend',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            $this.text('Requested')
                .attr("disabled", "disabled")
                .removeAttr('id');
        }else{
            alert("Can't request right now, Please reload page and try again");
        }
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}

function accept_friend_request(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'accept_request',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            if(window.location.pathname == "/accounts/notifications/inbox/" || window.location.pathname == "/accounts/notifications/archive/"){
                $('#messages').html('<div class="alert alert-success" style="display: block"><a href="#" data-dismiss="alert" class="close">×</a><i class="icon-ok-sign"></i> Success</div>');
            }else{
                $this.text('Friend')
                    .attr('href','javascript:void(0)')
                    .removeClass('btn-info')
                    .addClass('btn-success')
                    .removeAttr('id');
                $('#delete_request').text('- Unfriend')
                    .attr('id','unfriend_request');
                }
        }else{
            alert("Can't request right now, Please reload page and try again");
        }
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}

function unfriend_request(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'unfriend_request',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        window.location.reload();
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}

function delete_request(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'delete_request',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            if(window.location.pathname == "/accounts/notifications/inbox/" || window.location.pathname == "/accounts/notifications/archive/"){
                $('#messages').html('<div class="alert alert-success"><a href="#" data-dismiss="alert" class="close">×</a><i class="icon-ok-sign"></i> Success</div>');
            }else{
                window.location.reload();
            }
        }else{
            alert("Can't request right now, Please reload page and try again");
        }
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}

function make_follow(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'make_follow',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            $this.text('Following').removeClass('btn-primary').addClass('btn-success').attr('id','unfollow');
        }else{
            alert("Can't request right now, Please reload page and try again");
        }
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}

function unfollow(event){
    event.preventDefault();
    $this = $(this);

    post_data = {
        action: 'unfollow',
        csrfmiddlewaretoken: $.cookie("csrftoken"),
        uid: $this.attr('data-request-friend-id')
    };

    $.post('/social/friendship/request/', post_data, function(data, textStatus, jqXHR){
        if(data.error == ""){
            $this.text('Follow').addClass('btn-primary').removeClass('btn-success').attr('id','make_follow');
        }else{
            alert("Can't request right now, Please reload page and try again");
        }
    },"json")
    .fail(function(data) {
        alert("Can't request right now, Please reload page and try again");
    })
}