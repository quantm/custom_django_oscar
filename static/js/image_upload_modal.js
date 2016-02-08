/**
 * Created by Tam on 2/11/14.
 */
var image_upload_modal = $("#ImageUploadModal");
jQuery(function($){

    $( document ).on( "change", '#select-file', preview_upload_avatar);
    //Upload Function
    $(document).on({
        submit: function(event){
            event.preventDefault();
            $this = $(this);
            var is_avatar = 1;
            if($("#ImageUploadModal").hasClass('insert-media')) {
                is_avatar = 0;
            }
            $(this).ajaxSubmit({
                dataType: 'json',
                data: {basewidth: 400, is_avatar: is_avatar},
                beforeSubmit: function(arr, $form, options) {
                    image_upload_modal.find('.loading').show();
                    if(navigator.userAgent.indexOf('MSIE') == -1){
                        if (arr[1].value.type != 'image/png' && arr[1].value.type != 'image/jpeg' && arr[1].value.type != 'image/gif'){
                            reset_form_data_when_error('Error image type');
                            return false;
                        }
                    }
                },
                success: function(data){
                    if(data.error == ''){

                        $('#save-avatar').removeAttr('disabled');
                        image_upload_modal.find('.loading').hide();

                        var is_avatar = $('#ImageUploadModal').find('#is_avatar').val(),
                            img_path = window.STATIC_URL + data.path + data.file_name + "?t=" +(new Date()).getTime();

                        $('img#preview_upload').attr('src', img_path);
                        $('img#preview_avatar').attr('src', img_path);

                        if(parseInt(is_avatar) == 0) {
                            image_upload_modal.find('.preview-text, img.preview.insert-media').show({
                                'complete': function() {
                                    timeout = setTimeout(function() {
                                        var image_w = $('img#preview_upload').width(),
                                            image_h = $('img#preview_upload').height();

                                        $("#crop-left").val(0);
                                        $("#crop-top").val(0);
                                        $("#crop-width").val(image_w);
                                        $("#crop-height").val(image_h);

                                        window.IMG_SELECT.setOptions({
                                            enable: true,
                                            show: true,
                                            aspectRatio: "width:height"
                                        });
                                        window.IMG_SELECT.setSelection(0, 0, image_w, image_h);
                                        window.IMG_SELECT.update();
                                    }, 300);
                                }
                            });
                        }else {
                            $('.nav .avatar.small').attr('src', img_path)
                        }
                    }else{
                        reset_form_data_when_error(data.error);
                    }
                },
                error: function(){
                    reset_form_data_when_error('Upload error');
                }
            });
        }
    },'#form-upload-image');

    $('#ImageUploadModal').on({
        show: function() {
            image_upload_modal.find('form#save-crop .message').removeClass('text-error').html('').hide();
        },
        shown: function() {
             if (window.IMG_SELECT){
                window.IMG_SELECT.setOptions({enable: true, show: true});
                window.IMG_SELECT.update();
             }else{
                window.IMG_SELECT = $('img#preview_upload').imgAreaSelect({
                    instance: true,
					aspectRatio: "1:1",
                    minWidth: 200,
                    minHeight: 200,
                    handles: true,
                    onSelectEnd: function (img, selection) {
                        window.SEL = selection;
                        $('#crop-left').val(selection.x1);
                        $('#crop-top').val(selection.y1);
                        $('#crop-width').val(selection.width);
                        $('#crop-height').val(selection.height);
                    },
                    onSelectChange 	: preview_select_img,
                    x1: 0, y1: 0, x2: 200, y2: 200
                });
             }
        },
        hide: function(){
            if(window.IMG_SELECT){
                window.IMG_SELECT.setOptions({disable: true, hide: true});
                window.IMG_SELECT.update();
            }
        }
    });

})

function reset_form_data_when_error(message) {
    image_upload_modal.find('.preview-text, .loading').hide();
    image_upload_modal.find('#form-upload-image')[0].reset();
    image_upload_modal.find('#preview_upload').attr('src', '');
    image_upload_modal.find('form#save-crop .message').addClass('text-error').html(message).show();
}

function preview_upload(file_upload) {
    if (typeof(FileReader) != 'undefined') {
        var fr = new FileReader(),
            file = file_upload.files.item(0)

        if (file.type.substr(0,5) != 'image') {
            reset_form_data_when_error('This file is not an image');
            return false
        }

        fr.readAsDataURL(file);
        fr.addEventListener("load", function(event){
            $('img#preview_upload').attr('src', this.result);
            $('img#preview_avatar').attr('src', this.result);

            if(!image_upload_modal.hasClass('insert-media')) {
                setTimeout(function(){
                    window.IMG_SELECT.setOptions({enable: true, show: true});
                    window.IMG_SELECT.update();
                },500)
            }
        })
        return true
    } else {
        return false
    }
}

function preview_select_img(img, selection) {
    if (!selection.width || !selection.height)
        return;
    var scaleX = 200 / selection.width;
    var scaleY = 200 / selection.height;

    $('img#preview_avatar').css({
        width: Math.round(scaleX * $(img).width()),
        height: Math.round(scaleY * $(img).height()),
        marginLeft: -Math.round(scaleX * selection.x1),
        marginTop: -Math.round(scaleY * selection.y1)
    });
}

function preview_upload_avatar(){
    image_upload_modal.find('form#save-crop .message').removeClass('text-error').html('').hide();
    window.IMG_SELECT.setOptions({hide: true});
    window.IMG_SELECT.update();

    preview_upload(this);
    $('#form-upload-image').submit();
    $('#save-avatar').attr('disabled', 'disabled');
}