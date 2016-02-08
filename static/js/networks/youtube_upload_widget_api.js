/**
 * Created by tqn on 3/25/14.
 */
// 2. Asynchronously load the Upload Widget and Player API code.
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function youtube_upload_widget_init(widget_id, on_ReadyCallback, on_SuccessCallback, on_CompleteCallback) {
    // 3. Define global variables for the widget.
    //    The function loads the widget after the JavaScript code
    //    has downloaded and defines event handlers for callback
    //    notifications related to the widget.

    var widget = new YT.UploadWidget(widget_id, {
        width: 640,
        height: 390,
        events: {
            'onUploadSuccess': onUploadSuccess,
            'onProcessingComplete': onProcessingComplete,
            'onApiReady': onApiReady,
            'onStateChange': onStateChange
        }
    });


    // 4. This function is called when a video has been successfully uploaded.
    function onApiReady( event ) {
        widget.setVideoTitle($("#y_title").val());
        //widget.setVideoDescription(string)

        return on_ReadyCallback({state: '-1'});
    }

    // 5. This function is called when a video has been successfully uploaded.
    function onUploadSuccess( event ) {
        return on_SuccessCallback( event.data );

    }

    // 6. This function is called when a video has been successfully processed.
    function onProcessingComplete( event ) {
        return on_CompleteCallback( event.data );
    }

    // 7. This function is called when a video has been successfully uploaded.
    function onStateChange( event ) {
        return on_ReadyCallback(event.data);
    }

}
