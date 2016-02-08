from django import template
from django.template.loader import render_to_string, select_template
import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_collection(context, product):
    names = ['catalogue/partials/product/upc-%s.html' % product.upc,
             'catalogue/partials/product/class-%s.html' % product.get_product_class().slug,
             'catalogue/partials/collection.html']
    template_ = select_template(names)
    # Ensure the passed product is in the context as 'product'
    context['product'] = product
    return template_.render(context)

@register.simple_tag(takes_context=True)
def append_item_to_right_panel(context, item_obj):
    names = ['collection/design/append_item_to_right_panel.html']
    template_ = select_template(names)
    # Ensure the passed product is in the context as 'product'
    context['item_obj'] = item_obj
    return template_.render(context)

@register.simple_tag(takes_context=True)
def render_item_no_style(context, collection_items):
    names = ['collection/design/collection_item_no_style.html']
    template_ = select_template(names)
    context['collection_items'] = collection_items
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_item_need_style(context, collection_items):
    names = ['collection/design/collection_item_need_style.html']
    template_ = select_template(names)
    context['collection_items'] = collection_items
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_user_template(context, user, type, form_url, header_text, button_text, selected_user, modal_element, _frm_class):
    names = ['collection/user_template.html']
    template_ = select_template(names)
    context['selected_user'] = user
    context['type'] = type
    context['header_text'] = header_text
    context['class'] = _frm_class
    context['form_url'] = form_url
    context['button_text'] = button_text
    context['my_event_selected_user'] = selected_user
    context['modal_element'] = modal_element
    context['avatar_dir'] = settings.AVATAR_DIR
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_alert(context, id, header_text, url, btn_text, type, modal,button_id):
    names = ['collection/alert.html']
    template_ = select_template(names)
    context['collection_id'] = id
    context['btn_text'] = btn_text
    context['modal'] = modal
    context['header_text'] = header_text
    context['url'] = url
    context['button_id'] = button_id
    context['type'] = type
    return template_.render(context)

@register.simple_tag(takes_context=True)
def render_collection_item(context, collection):
    names = ['collection/view/collection_item.html']
    template_ = select_template(names)
    context['collection'] = collection
    return template_.render(context)

@register.simple_tag(takes_context=True)
def render_collection_comment(context, parent):
    names = ['social/wall/my-wall-render-parent.html']
    template_ = select_template(names)
    context['parent'] = parent
    return template_.render(context)

@register.filter
def is_selected(user, users):
    return user.pk in users
