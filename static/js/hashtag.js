function hashtag(id){
    var ajax_request = false;
    var ajax_request_hashtag = false;
    $('#'+id).addClass("highlight")
    $('#'+id).textntags({
        triggers: {
            '@': {
                uniqueTags   : true,
                syntax       : _.template('![<%= id %>:<%= type %>:<%= title %>]'),
                parser       : /(!)\[(\d+):([\w\s\.\-]+):([\w\s@\.,-\/#!$%\^&\*;:{}=\-_`~()]+)\]/gi,
                parserGroups : {id: 2, type: 3, title: 4}
            },
            '#': {
                uniqueTags   : true,
                syntax       : _.template('#[<%= id %>:<%= type %>:<%= title %>]'),
                parser       : /(#)\[(\d+):([\w\s\.\-]+):([\w\s@\.,-\/#!$%\^&\*;:{}=\-_`~()]+)\]/gi,
                parserGroups : {id: 2, type: 3, title: 4}
            }
        },
        onDataRequest:function (mode, query, triggerChar, callback) {
              if (triggerChar == '@')
              {
                    if(ajax_request) ajax_request.abort();
                    var array_comment = $("#"+id).val().split(" ")
                    for(var k=0;k<array_comment.length;k++)
                    {
                        if(array_comment[k].match(/@/g) && array_comment[k].length <= 50)
                        {
                            var obj_comment = array_comment[k].replace("@","")
                            var json_user='/social/getuser/?comment_object='+obj_comment
                            ajax_request = $.getJSON(json_user, function(responseData) {
                                auto_responseData = {'@':responseData}
                                query = query.toLowerCase();
                                var found = _.filter(auto_responseData[triggerChar], function(item) { return item.name.toLowerCase().indexOf(query) > -1; });
                                callback.call(this, found.splice(0,5));
                                ajax_request = false;
                            });
                        }
                    }
              }

              if(triggerChar == '#')
              {
                    if(ajax_request_hashtag) ajax_request_hashtag.abort();
                    var array_hash_tag = $("#"+id).val().split(" ")
                    for(var i=0;i<array_hash_tag.length;i++)
                    {
                        if(array_hash_tag[i].match(/#/g) && array_hash_tag[i].length <= 50)
                        {
                            var obj_hash_tag = array_hash_tag[i].replace("#","")
                            var json_hash_tag='/social/gethashtag/?name='+obj_hash_tag
                            ajax_request_hashtag = $.getJSON(json_hash_tag, function(responseData_hashtag) {
                                auto_responseData_hashtag = {'#':responseData_hashtag}
                                query = query.toLowerCase();
                                var found = _.filter(auto_responseData_hashtag[triggerChar], function(item) { return item.name.toLowerCase().indexOf(query) > -1; });
                                callback.call(this, found.splice(0,5));
                                ajax_request_hashtag = false;
                            });
                        }
                    }
              }
        }
    });
}
