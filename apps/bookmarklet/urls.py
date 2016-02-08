#__author__ = 'tqn'
from compressor.utils.stringformat import selftest
from django.conf.urls import *

urlpatterns = patterns('apps.bookmarklet.views',
   url(r'^form/$', 'bookmark_let_page', name='bookmark-let-page'),
   url(r'^sign-in-form/$', 'sign_in_page', name='sign-in-page'),
   url(r'^sign-in/$', 'sign_in_action', name='sign-in-action-path'),
   url(r'^save/$', 'bookmark_let_save', name='bookmark-let-save-path'),
)


