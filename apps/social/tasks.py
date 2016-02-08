from celery.task import task
from datetime import *
from apps.social.models import MyEvent
from apps.common.functions import OBJECT_TYPE, send_notification

@task
def my_event_every_day_send_notification():
    try:
        day_send_notification = date.today()+timedelta(days=1)
        obj_my_event = MyEvent.objects.filter(myeventobject__update=str(day_send_notification))
        for celery_my_event_notification in obj_my_event:
            send_notification(recipient_id=celery_my_event_notification.user_share_id,
                              sender_id=celery_my_event_notification.user_id,
                              object_id=celery_my_event_notification.event_id,
                              type=OBJECT_TYPE._CELERY_EVENT_NOTIFICATION,
                              mail=False)
        obj_self_event = MyEvent.objects.filter(myeventobject__update=str(day_send_notification))\
                                .distinct().extra(select={'user_id_obj': 'user_id'})
        for celery_self_event in obj_self_event:
            send_notification(recipient_id=celery_self_event.user_id_obj,
                              sender_id=celery_self_event.user_id_obj,
                              object_id=celery_self_event.event_id, type=OBJECT_TYPE._CELERY_EVENT_NOTIFICATION,
                              mail=False)
        return 'Success'
    except Exception, err:
        print err
        return 'Error'