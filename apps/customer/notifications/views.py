from django.utils.timezone import now
from oscar.apps.customer.notifications.views import NotificationListView as CoreNotificationListView
from django.db.models import get_model
import settings
Notification = get_model('customer', 'Notification')


class NotificationListView(CoreNotificationListView):
    model = Notification
    template_name = 'customer/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    page_title = "Notifications"
    active_tab = 'notifications'

    def get_context_data(self, **kwargs):
        ctx = super(NotificationListView, self).get_context_data(**kwargs)
        ctx['list_type'] = self.list_type
        ctx['share'] = settings.CONFIG_SHARE
        ctx['invite'] = settings.CONFIG_INVITE
        return ctx


class InboxView(NotificationListView):
    list_type = 'inbox'

    def get_queryset(self):
        qs = self.model._default_manager.filter(
            recipient=self.request.user,
            location=self.model.INBOX)
        # Mark unread notifications so they can be rendered differently...
        for obj in qs:
            if not obj.is_read:
                setattr(obj, 'is_new', True)
        # ...but then mark everything as read.
        self.mark_as_read(qs)
        return qs

    def mark_as_read(self, queryset):
        unread = queryset.filter(date_read=None)
        unread.update(date_read=now())

def ajax_notifications(request):
    import json
    from django.shortcuts import HttpResponse
    ctx = {}
    if request.user and request.user.is_authenticated():
        num_unread = Notification.objects.filter(
            recipient=request.user, date_read=None).count()
        ctx['num_unread_notifications'] = num_unread
    return HttpResponse(json.dumps(ctx))
