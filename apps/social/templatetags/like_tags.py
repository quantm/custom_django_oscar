from django import template
from django.template.loader import render_to_string, select_template
from apps.social.models import SocialLike
from apps.common.models import OBJECT_TYPE

register = template.Library()

@register.simple_tag(takes_context=True)
def render_like_btn(context, object):
    names = ['social/like/btn_like.html',]
    template_ = select_template(names)
    request = context['request']
    current_user = request.user
    object_type_code = None
    object_id = object.pk
    context['object_id'] = object_id
    object_type = object._meta.object_name

    if object_type == 'SocialPromote':
        object_type_code = OBJECT_TYPE._LIKE_PROMOTE_PRODUCT
    elif object_type == 'User':
        object_type_code = OBJECT_TYPE._LIKE_USER
    elif object_type == 'CollectionSet':
        object_type_code = OBJECT_TYPE._LIKE_MAGAZINE
    elif object_type == 'SocialMessage':
        object_type_code = OBJECT_TYPE._LIKE_COMMENT

    context['object_type'] = object_type_code
    context['is_liked'] = SocialLike.is_liked(object_id, current_user.id, object_type_code)
    context['like_count'] = SocialLike.get_like_count(object_id, object_type_code)
    return template_.render(context)
