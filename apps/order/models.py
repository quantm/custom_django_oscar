from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.order.models import Order as CoreOrder
from apps.social.models import SocialPromote

class Order(CoreOrder):
    promote = models.ForeignKey(SocialPromote, related_name='fk_order_promote', null=True)

#Using at bottom file
