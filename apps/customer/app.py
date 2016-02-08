from apps.customer import views
from apps.customer.notifications import views as notification_views
from django.conf.urls import patterns, url
from oscar.apps.customer.app import CustomerApplication as CoreCustomerApplication


class CustomerApplication(CoreCustomerApplication):
    login_view = views.AccountAuthView
    profile_view = views.ProfileView
    notification_inbox_view = notification_views.InboxView
    profile_update_view = views.ProfileUpdateView
application = CustomerApplication()