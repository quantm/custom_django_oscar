// JavaScript Document

window.SCROLLER = {
    is_scrolling: 1,
    current_page: 1
};

//------------------------------------------------------------

jQuery(function($){
    set_delete_id()
})
$(function() {
    $(window).scroll(my_wall_on_window_scroll);
})

function my_wall_on_window_scroll()
{
    if  ($(window).scrollTop() >= ($(document).height() - $(window).height()) / 1.1 ) {
		var total_page = $("#pagination_total_page").val()
		if ((window.SCROLLER.is_scrolling == 1) && (total_page > 1) && (window.SCROLLER.current_page < total_page)) {
			my_wall_get_page_on_scroll();
		}
	}
}

function my_wall_get_page_on_scroll()
{
    window.SCROLLER.is_scrolling = 0;
    var page = window.SCROLLER.current_page + 1,
        url = $("#url_self_pagination").val()+"?page=" + page;
    set_delete_id()
    $(".my_wall_wrapper #my_wall_loading").removeClass("my_wall_loading")
    $.get(url, function(data){
        $('.my_wall_wrapper').append(data);
        $(".my_wall_wrapper #my_wall_loading").addClass("my_wall_loading")
        window.SCROLLER.current_page = window.SCROLLER.current_page + 1;
        window.SCROLLER.is_scrolling = 1;
    }).fail(function(){
		alert('Load page fail');
    })
}
