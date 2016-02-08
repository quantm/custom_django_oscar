function set_mention_hashtag_link(id){
    if($("#"+id).html() != null)
    {
        if($("#"+id).html().match(/@/g) || $("#"+id).html().match(/#/g)){
            var array_comment = $("#"+id).html().split(" ")
            for(var z=0;z<array_comment.length;z++){
                    if(array_comment[z].match(/@/g)){
                       var username = array_comment[z].replace("@","")
                       var link_profile = array_comment[z].replace(array_comment[z],'<a href=/accounts/profile/'+username+'>'+array_comment[z]+'</a>')
                       var link_profile_comment_text=$("#"+id).html().replace(array_comment[z],link_profile)
                       $("#"+id).html(link_profile_comment_text)
                    }
                    if(array_comment[z].match(/#/g)){
                       var hashtag = array_comment[z].replace("#","")
                       var link_hashtag = array_comment[z].replace(array_comment[z],'<a href=/social/hashtag/'+hashtag+'>'+array_comment[z]+'</a>')
                       var link_hashtag_comment_text=$("#"+id).html().replace(array_comment[z],link_hashtag)
                       $("#"+id).html(link_hashtag_comment_text)
                    }
            }
        }
    }
}