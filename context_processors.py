# import the settings file
from oscar.app import Shop
from settings import *
from django.conf import settings
from django.contrib.sites.models import Site
import urls

PROJECT_URL = urls


def settings_values(request):

    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'

    return {
        'AVATAR_DIR': AVATAR_DIR,
        'AVATAR_URL': AVATAR_URL,
        'STATIC_URL': STATIC_URL,
        'DISPLAY_NAME': scheme + request.get_host(),
        'DOMAIN_NAME': request.get_host(),
        'BASE_URL': scheme + request.get_host(),
        'FACEBOOK_APP_ID': settings.FACEBOOK_APPS['demo_oscar']['ID'],
    }

