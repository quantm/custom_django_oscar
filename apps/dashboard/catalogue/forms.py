__author__ = 'tqn'
from django import forms
from django.db.models import get_model
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from oscar.apps.dashboard.catalogue.forms import BaseStockRecordFormSet, StockRecordForm
from apps.partner.models import StockRecord, Partner


Product = get_model('catalogue', 'Product')

BaseStockRecordFormSet = inlineformset_factory(Product, StockRecord, form=StockRecordForm, extra=1)
class StockRecordFormSet(BaseStockRecordFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        self.user = user
        self.require_user_stockrecord = not user.is_staff
        self.product_class = product_class
        super(StockRecordFormSet, self).__init__(*args, **kwargs)
        self.set_initial_data()

    def set_initial_data(self):
        """
        If user has only one partner associated, set the first
        stock record's partner to it. Can't pre-select for staff users as
        they're allowed to save a product without a stock record.

        This is intentionally done after calling __init__ as passing initial
        data to __init__ creates a form for each list item. So depending on
        whether we can pre-select the partner or not, we'd end up with 1 or 2
        forms for an unbound form.
        """
        if self.require_user_stockrecord:
            try:
                user_partner = self.user.partners.get()
            except (Partner.DoesNotExist, MultipleObjectsReturned):
                pass
            else:
                partner_field = self.forms[0].fields.get('partner', None)
                if partner_field and partner_field.initial is None:
                    partner_field.initial = user_partner

    def _construct_form(self, i, **kwargs):
        """

        """
        kwargs['product_class'] = self.product_class
        kwargs['user'] = self.user
        stock_record_form = super(StockRecordFormSet, self)._construct_form(i, **kwargs)

        if self.user.is_staff and self.user.is_superuser:
            for field in stock_record_form.fields:
                stock_record_form.fields[field].widget = forms.widgets.HiddenInput()
        else:
            stock_record_form.fields['selected_partner'].widget = forms.widgets.HiddenInput()
            stock_record_form.fields['selected_partner'].initial = 0

            partner = Partner.objects.filter(users=self.user)
            if list(partner).__len__() > 0:
                stock_record_form.fields['partner'].queryset = partner
                stock_record_form.fields['partner'].widget = forms.widgets.HiddenInput()
                stock_record_form.fields['partner'].initial = list(partner)[0].pk

        return stock_record_form

    def get_queryset(self):
        """

        """
        if self.user.is_active and self.user.is_staff and not self.user.is_superuser:
            partner = Partner.objects.filter(users=self.user)
            qs = StockRecord.objects.filter(product=self.instance, partner=partner).exclude(selected_partner=1)
            #limit stock record form show with current partner
            if list(qs).__len__() > 0:
                #If current partner already input price, don't allow partner add more price
                self.extra = 0
            else:
                #If current not yet input price, show 1 stock record form
                self.extra = 1

            return qs
        else:
            self.extra = 0
            return super(StockRecordFormSet, self).get_queryset().order_by('-selected_partner', 'price_excl_tax')