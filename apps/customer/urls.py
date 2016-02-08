#__author__ = 'Tam'
from django.conf.urls import *
from .views import *
from notifications.views import ajax_notifications
from wishlists.views import *

urlpatterns = patterns('apps.customer.views',
    url(r'^ajax-upload-avatar', 'ajax_upload_avatar', name='ajax_upload_avatar'),
    url(r'^crop-avatar', 'crop_avatar', name='crop_avatar'),
    url(r'^ajax_notifications', ajax_notifications, name='ajax_notifications'),
    url(r'^accounts/sign-up/$', 'sign_up_account_by_ajax', name='ajax-sign-up-account'),
    url(r'^logged/$', 'ajax_check_logged', name='ajax-check-logged'),
    url(r'^wishlists-user-view/(?P<user_id>\d+)/$', WishListListViewOtherProfile.as_view(), name='wishlist-list-view-other-profile'),
    url(r'^wishlists-user-detail-view/(?P<key>[a-z0-9]+)/(?P<user_id>\d+)/$', WishListDetailViewOtherProfile.as_view(), name='wishlist-list-detail-view-other-profile'),
    url(r'^(?P<username>.*)/$', ViewUserProfile.as_view(), name='view_user_profile_custom_url'),
)




