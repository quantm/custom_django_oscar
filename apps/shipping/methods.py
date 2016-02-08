from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _

from oscar.apps.shipping.base import Base


class Free(Base):
    code = 'free-shipping'
    name = _('Free shipping')
    is_tax_known = True
    charge_incl_tax = charge_excl_tax = D('0.00')


class NoShippingRequired(Free):
    """
    This is a special shipping method that indicates that no shipping is
    actually required (eg for digital goods).
    """
    code = 'no-shipping-required'
    name = _('No shipping required')


class FixedPrice(Base):
    code = 'fixed-price-shipping'
    name = _('Fedex')

    def __init__(self, charge_excl_tax, charge_incl_tax):
        self.charge_excl_tax = charge_excl_tax
        if charge_incl_tax is not None:
            self.charge_incl_tax = charge_incl_tax
            self.is_tax_known = True

