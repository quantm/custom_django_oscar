/**
 * Created by tqn on 1/13/14.
 */

function publish_action_link(app_id, action_link, callback) {

    var auth = FB.getAuthResponse();
    if(auth==null || auth == ''){
        sign_in_facebook();
        return;
    }

    FB.api(action_link, 'POST',
        {
            access_token: FB.getAuthResponse()['accessToken'],
            product: {
                app_id: app_id,
                type: 'product',
                title: "Smartphone 3G Nokia Lumia 720",
                url: 'http://demo-oscar.dev:8000/catalogue/kindle-best-selling-ereader-only-69_15/',
                image: "http://static.startup.uniweb.vn/media/images/products/2014/02/d5cf9c6eb5551dc8156e13e5c6aa6977.jpeg",
                description: "Smartphone 3G Nokia Lumia 720 Windows Phone 8"
            }
        },
        function(response) {
            // handle the response
            return callback(response);
        }
    );
}
