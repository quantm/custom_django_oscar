#__author__ = 'tqn'
import re
from django import template


register = template.Library()

@register.filter
def replace(string, args):
    args = args.split(':')
    search  = args[0]
    replace = args[1]

    return string.replace(search, replace)

@register.filter
def max_size(image):
    base_width = 800
    if hasattr(image, 'width'):
        percent_width = (base_width/float(image.width))
        h_size = int((float(image.height)*float(percent_width)))
    else:
        h_size = 800

    return '%dx%d' % (base_width, h_size)

@register.filter
def match(pattern, string):
    result = re.match(pattern, string)
    if result is None:
        return False
    else:
        return True
