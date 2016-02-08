from django.db.models.fields import IntegerField
from oscar.apps.customer.abstract_models import *


class Notification(AbstractNotification):
    object_id = IntegerField(max_length=125, blank=True, null=True)
    type = IntegerField(max_length=125, blank=True, null=True)