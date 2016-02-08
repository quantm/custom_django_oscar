
window.MY_TEXT = {
    editor_obj: null
};

jQuery(function($){
    $(document).on({
        click: text_tool_click
    },'.text-tool');

    $(document).on({
        click: left_panel_click
    }, design_panel.id);

    $(document).on({
        click: my_text_click
    },'.my-text');

    $(document).on({
        dblclick: my_editor_click
    },'.text-editable');
});

function text_tool_click(){
    var $this = $(this);
    $this.toggleClass('active');

    if($this.hasClass('active')){
        design_panel.obj.css('cursor','text');
        remove_all_text_draggable_resizable_rotatable();
    }else{
        destroy_all_editor();
    }
}

function left_panel_click(event){
    if( $('.text-tool').hasClass('active')){
        if ( event.target == this || $(event.target).parent().parent().hasClass('shop')) {
            if ( MY_TEXT.editor_obj == null ) {
                var new_id = 'dropped_cloned_' + (new Date).getTime(),
                    html_template = '<div id="'+new_id+'" data-type="text" class="abilities not-clone my-text draggable" style="position: absolute; z-index: 2"><div class="text-editable">Type your text here</div></div>',
                    obj_append = $( $.parseHTML(html_template)),
                    my_text = obj_append.find('.text-editable');

                $(this).append(obj_append);
                obj_append.css({top: (event.pageY - 100), left: (event.pageX - 20), zIndex: get_total_items_on_left_panel()});

                my_text.attr('contenteditable', true);

                MY_TEXT.editor_obj =  my_text.ckeditor(function(){
                    select_all_cktext(MY_TEXT.editor_obj);
                }).editor;

                my_text.focus();

                set_saved_flag(0);
            }else{
                destroy_all_editor();
            }
        }
    }
}

function my_editor_click(){
    var my_obj = this;

    if( $('.text-tool').hasClass('active') ){
        init_editor(my_obj);
    }else{
        var $text_tool = $('.text-tool');

        $text_tool.toggleClass('active');

        if($text_tool.hasClass('active')){
            design_panel.obj.css('cursor','text');
            remove_all_text_draggable_resizable_rotatable();
        }else{
            destroy_all_editor();
        }
        init_editor(my_obj);
    }
}

function my_text_click(){
    if( ! $('.text-tool').hasClass('active') ){

        $(this).setSelected()
               .setResizable()
               .setRotatable();
    }
}

function destroy_all_editor(){

    $('.text-tool').removeClass('active');

    if (MY_TEXT.editor_obj) {
        if($.trim(MY_TEXT.editor_obj.getData()) == ""){
            $(MY_TEXT.editor_obj.editable().$).parent().remove();
        }
        MY_TEXT.editor_obj.destroy();
        MY_TEXT.editor_obj = null;
    }

    $('.text-editable').removeAttr('contenteditable');
    design_panel.obj.css('cursor','auto');

    set_draggable();
}

function init_editor(my_obj){
    remove_all_text_draggable_resizable_rotatable();

    if (MY_TEXT.editor_obj) {
        $('.text-editable').removeAttr('contenteditable');
        MY_TEXT.editor_obj.destroy();
    }

    $(my_obj).attr('contenteditable', true);
    MY_TEXT.editor_obj = $(my_obj).ckeditor().editor;

    $(my_obj).focus();
}

function remove_all_text_draggable_resizable_rotatable(){
    $('.my-text').each(function(i, el){
        var my_text = $(el);
        if ( my_text.hasClass('ui-draggable') ) {
            try{
                my_text.draggable('destroy');
            }catch (err){

            }
        }
        if( my_text.hasClass('ui-resizable') ){
            try{
                my_text.resizable('destroy');
            }catch (err){

            }
        }
        my_text.find('.ui-rotatable-handle').hide();
    });
}

function select_all_cktext(editor){
    var editable = editor.editable(),
        range = editor.createRange();
    range.selectNodeContents( editable );
    range.select();
    editor.forceNextSelectionCheck();
    editor.selectionChange();
}

function get_total_items_on_left_panel(){
    $items = design_panel.obj.find('.abilities');
    return $items.length;
}

function set_draggable(){
    $('.my-text').draggable({
        stop: function() {
            set_saved_flag(0);
        }
    });
}

function set_resizable_rotatable($my_obj){
    if($my_obj.hasClass('my-text')){
        var resizable_obj = $my_obj.find('.ui-resizable-handle'),
        rotatable_obj = $my_obj.find('.ui-rotatable-handle');
        if (resizable_obj.length == 0) {
            $my_obj.resizable({
                stop: function() {
                    set_saved_flag(0);
                }
            });
        }

        if( rotatable_obj.length == 0 ){
           $my_obj.rotatable();
        }
    }
}