from django import template
from django.template.loader import render_to_string, select_template
import re,HTMLParser

register = template.Library()


@register.simple_tag(takes_context=True)
def render_connected_hash_tag(context, product):
    names = ['social/hashtag/hashtag_connected_template.html']
    template_ = select_template(names)
    context['product'] = product
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_list_hash_tag(context, hashtag):
    names = ['social/hashtag/hashtag_list_template.html']
    template_ = select_template(names)
    context['hashtag'] = hashtag
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_wall_post(context, content):
    names = ['social/wall/template/render_wall_post.html']
    template_ = select_template(names)
    context['content'] = content
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_popular_hash_tag(context, hashtag):
    names = ['social/hashtag/hashtag_popular_template.html']
    template_ = select_template(names)
    context['hashtag'] = hashtag
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_delete_permission(context):
    names = ['social/wall/template/delete_permission.html']
    template_ = select_template(names)
    return template_.render(context)


@register.filter
def match(pattern, string):
    result = re.search(pattern, string)
    if result is None:
        return False
    else:
        return True

@register.filter
def render_wall_content(string):
    listitem = []

    if re.search('\n', string) and re.search(" ", string):
        array_element = string.split("\n")
        for i in range(len(array_element)):
            if array_element[i].startswith("http"):
                listitem.append({'value': array_element[i], 'key': 'http', 'br': True})

            elif array_element[i].startswith("#"):
                listitem.append({'value': array_element[i], 'key': 'hash_tag', 'br': True})

            elif array_element[i].startswith("@"):
                listitem.append({'value': array_element[i], 'key': 'mention', 'br': True})

            else:
                listitem.append({'value': array_element[i], 'key': ''})

    if re.search(" ", string) and not re.search("\n", string):
        array_element = string.split(" ")
        for i in range(len(array_element)):
            if array_element[i].startswith("http"):
                listitem.append({'value': array_element[i], 'key': 'http', 'br': False})

            elif array_element[i].startswith("#"):
                listitem.append({'value': array_element[i], 'key': 'hash_tag', 'br': False})

            elif array_element[i].startswith("@"):
                listitem.append({'value': array_element[i], 'key': 'mention', 'br': False})

            else:
                listitem.append({'value': array_element[i], 'key': ''})
    return listitem

@register.filter
def get_username_from_mention(args):
    return args.replace("@", "")


@register.filter
def get_hash_tag_link(args):
    return args.replace("#", "")














