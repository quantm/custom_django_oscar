from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.partner.abstract_models import AbstractStockRecord
from django.core.validators import MaxValueValidator, MinValueValidator

class StockRecord(AbstractStockRecord):
    #selected_partner = [0 or 1]
    selected_partner = models.IntegerField(default=0)
    #commission = [0 : 100]
    commission = models.DecimalField(
        _("Commission"), blank=True, default=0, max_digits=12, decimal_places=2, validators=[MinValueValidator(0.00), MaxValueValidator(100.00)])
    class Meta:
        unique_together = ('product', 'partner', 'partner_sku', 'selected_partner')

#Using at bottom file
from .receivers import *
