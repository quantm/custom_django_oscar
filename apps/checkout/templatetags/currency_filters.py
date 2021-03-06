from decimal import Decimal as D, InvalidOperation

from django import template
from django.conf import settings
from babel.numbers import format_currency

register = template.Library()


@register.filter(name='currency')
def currency(value, currency=None):
    """
    Format decimal value as currency
    """
    try:
        value = D(value)
    except (TypeError, InvalidOperation):
        return u""
    # Using Babel's currency formatting
    # http://babel.pocoo.org/docs/api/numbers/#babel.numbers.format_currency
    kwargs = {
        'currency': currency if currency else settings.OSCAR_DEFAULT_CURRENCY,
        'format': getattr(settings, 'OSCAR_CURRENCY_FORMAT', None),
    }
    locale = getattr(settings, 'OSCAR_CURRENCY_LOCALE', None)
    if locale:
        kwargs['locale'] = locale

    return format_currency(value, **kwargs)
