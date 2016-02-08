#__author__ = 'tqn'
from collections import namedtuple
from django.db.models import Max, Min
from oscar.apps.partner import strategy
from .models import StockRecord
import copy
from decimal import Decimal as D

# A container for policies
StockInfo = namedtuple('StockInfo', ['price', 'availability', 'stockrecord'])


class Base(object):
    """
    The base strategy class

    Given a product, strategies are responsible for returning a ``StockInfo``
    instance which contains:

    - The appropriate stockrecord for this customer
    - A pricing policy instance
    - An availability policy instance
    """

    def __init__(self, request=None):
        self.request = request
        self.user = None
        if request and request.user.is_authenticated():
            self.user = request.user

    def fetch(self, product, stockrecord=None):
        """
        Given a product, return a ``StockInfo`` instance.

        The ``StockInfo`` class is a named tuple with attributes:

        - ``price``: a pricing policy object.
        - ``availability``: an availability policy object.
        - ``stockrecord``: the stockrecord that is being used to calculate prices and

        If a stockrecord is passed, return the appropriate ``StockInfo``
        instance for that product and stockrecord is returned.
        """
        raise NotImplementedError(
            "A strategy class must define a fetch method "
            "for returning the availability and pricing "
            "information."
        )


class Selector(object):

    def strategy(self, request=None, user=None, **kwargs):
        """
        Return an instanticated strategy instance
        """
        # Default to the backwards-compatible strategy of picking the first
        # stockrecord.
        return TheBestStock(request)


class UseTheBestStockRecord(object):
    """
    Stockrecord selection mixin for use with the ``Structured`` base strategy.
    This mixin picks the first (normally only) stockrecord to fulfil a product.

    This is backwards compatible with Oscar<0.6 where only one stockrecord per
    product was permitted.
    """
    def select_stockrecord(self, product):
        try:
            stocks = StockRecord.objects.filter(product=product, selected_partner=1)
            return stocks[0]
        except IndexError:
            return None


class IncludingVAT(strategy.FixedRateTax):
    """
    Price policy to charge VAT on the base price
    """
    # We can simply override the tax rate on the core FixedRateTax.  Note
    # this is a simplification: in reality, you might want to store tax
    # rates and the date ranges they apply in a database table.  Your
    # pricing policy could simply look up the appropriate rate.
    rate = D('0.00')


class TheBestStock(UseTheBestStockRecord, IncludingVAT,strategy.StockRequired, strategy.Structured):
    """
    Typical US strategy for physical goods.  Note we use the ``DeferredTax``
    mixin to ensure prices are returned without tax.

    - Use first stockrecord
    - Enforce stock level
    - Taxes aren't known for prices at this stage
    """