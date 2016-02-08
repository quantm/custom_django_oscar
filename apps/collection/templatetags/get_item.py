#__author__ = 'tqn'
from django import template
from django.template.loader import select_template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag(takes_context=True)
def render_video_player(context, collection_item):
    names = ['collection/view/_video_player.html']
    template_ = select_template(names)
    context['item'] = collection_item
    return template_.render(context)

@register.simple_tag(takes_context=True)
def render_tooltip_object(context, collection_item):
    names = ['collection/view/_item__tooltip_object.html']
    template_ = select_template(names)
    context['item'] = collection_item
    return template_.render(context)

@register.simple_tag(takes_context=True)
def render_collection_item_with_tooltip(context, collection_item):
    names = ['collection/view/_item__with_tooltip.html']
    template_ = select_template(names)
    context['item'] = collection_item
    return template_.render(context)

@register.simple_tag(takes_context=True)
def thumbnail_image_of_item(context, object, *args, **kwargs):
    names = ['collection/thumbnail_image_of_item.html']
    template_ = select_template(names)
    context['object'] = object
    return template_.render(context)

