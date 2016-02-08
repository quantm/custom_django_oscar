/**
 * Created by Tam on 3/11/14.
 */

jQuery(function($){
    $(document).on('click','.wrapper-like',like_this)
});

function like_this(event){
    event.preventDefault();
    var this_object = $(this),
        action = this_object.attr('data-action'),
        type = this_object.attr('data-object-type'),
        object_id = this_object.attr('data-object-id'),
        $target = $(event.target),
        like_text = this_object.find('.like-text').attr('data-like-text'),
        unlike_text = this_object.find('.like-text').attr('data-unlike-text'),
        like_count_object = this_object.find('.like-count');

    post_param = {
        csrfmiddlewaretoken : $.cookie("csrftoken"),
        action: action,
        type: type,
        object: object_id
    }

    if($target.hasClass('like-text')){
        $.post('/api/social/like/', post_param, function(data){
            if (data.error == "" && data.action !== "") {
                this_object.attr('data-action', data.action);
                if (data.action == "like") {
                    $target.text(like_text);
                    like_count_object.text(data.count)
                } else if (data.action == "unlike") {
                    $target.text(unlike_text);
                    like_count_object.text(data.count)
                }
            }
        },'json')
    }
}

