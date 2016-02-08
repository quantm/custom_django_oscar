from settings import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template import RequestContext
from apps.checkout.templatetags.currency_filters import currency
from lib import braintree
from fedex.services.rate_service import FedexRateServiceRequest
from fedex.config import FedexConfig
from decimal import Decimal as D

from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.checkout.views import ShippingMethodView as OscarShippingMethodView
from oscar.apps.checkout.views import ShippingAddressView as OscarShippingAddressView
from oscar.apps.payment.forms import BankcardForm
from apps.catalogue.models import Product

import logging
logging.basicConfig(level=logging.INFO)


class PaymentDetailsView(OscarPaymentDetailsView):
    def get_context_data(self, **kwargs):
        # Add bankcard form to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        ctx['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
        return ctx

    def post(self, request, *args, **kwargs):
        shipping = self.get_shipping_address(self.request.basket)
        #order_price = round(D(request.POST['total_price'])+D(fedex_price)+D('1.00'), 2)
        #request.POST['total_price']

        ##braintree gateway
        braintree.Configuration.configure(braintree.Environment.Sandbox,
                                          merchant_id="z3mss2xx8hpfjc39",
                                          public_key="fddpbjczc4qfjnq2",
                                          private_key="9883af47d9ab5e54a21df8a0d7120da1")
        result = braintree.Transaction.sale({
            "customer": {
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
                "company": "Braintree Payment Solutions",
                "email": self.request.user.email,
                "phone": "419-555-1234",
                "fax": "419-555-1235",
                "website": "https://www.braintreepayments.com"
            },
            "amount": request.POST['total_price'],
            "credit_card": {
                "number": request.POST['number'],
                "cvv": request.POST['ccv'],
                "expiration_month": request.POST['expiry_month_0'],
                "expiration_year": request.POST['expiry_month_1']
            },
            "shipping": {
                "first_name": shipping.first_name,
                "last_name": shipping.last_name,
                "company": "Braintree",
                "street_address": shipping.line1,
                "extended_address": shipping.line2,
                "locality": "Bartlett",
                "region": "IL",
                "postal_code": shipping.postcode,
                "country_name": "Viet Nam"
            },

            "billing": {
                "first_name": "John",
                "last_name": "Terry",
                "company": "Braintree",
                "street_address": "123 E Main St",
                "extended_address": "Suite 403",
                "locality": "Chicago",
                "region": "IL",
                "postal_code": "32135",
                "country_name": "United States of America"
            },
            "options": {"submit_for_settlement": True}}
        )

        if result.is_success:
            message = "<h1>Success! Transaction ID: {0}</h1>".format(result.transaction.id)
        else:
            message = "<h1>Error: {0}</h1>".format(result.message)

        ##end braintree

        error_response = self.get_error_response()
        if error_response:
                return error_response

        if self.preview:
                if request.POST.get('action', '') == 'place_order':
                    basket = request.basket
                    for line in basket.all_lines():
                        prod_id = line.product.id
                        quantity = line.quantity
                        prod_buy_count_all_time = line.product.buy_count_all_time
                        prod_buy_count_in_month = line.product.buy_count_in_month
                        Product.objects.filter(pk=prod_id).update(buy_count_all_time = (prod_buy_count_all_time + quantity), buy_count_in_month =  (prod_buy_count_in_month + quantity))

                    submission = self.build_submission()
                    return self.submit(**submission)
                return self.render_preview(request)

        return self.get(request, *args, **kwargs)


class ShippingAddressView(OscarShippingAddressView):
    def get(self, request, *args, **kwargs):
            return super(ShippingAddressView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(ShippingAddressView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            # Look up address book data
            address = self.get_available_addresses()
            kwargs['addresses'] = address
            if not address:
                kwargs['address_class'] = "in collapse"
            if address:
                kwargs['address_class'] = "collapse"
            address_class_bootstrap = self.request.POST.get('address_bootstrap_class', '')
            if address_class_bootstrap == "1":
                kwargs['address_class'] = "in collapse"
        return kwargs

    def post(self, request, *args, **kwargs):
            ctx = super(ShippingAddressView, self).post(request, *args, **kwargs)
            return ctx

    def get_success_url(self):
        return reverse('checkout:shipping-method')


class ShippingMethodView(OscarShippingMethodView):
        def get_context_data(self, **kwargs):
            kwargs = super(ShippingMethodView, self).get_context_data(**kwargs)
            return kwargs

        def get(self, request, *args, **kwargs):
            self._methods = self.get_available_shipping_methods()
            if len(self._methods) == 0:
                messages.warning(request, _("Shipping is unavailable for your chosen address - please choose another"))
                return HttpResponseRedirect(reverse('checkout:shipping-address'))
            elif len(self._methods) == 1:
                self.checkout_session.use_shipping_method(self._methods[0].code)
                for fedex in self._methods:
                    fedex_net_charge = fedex.charge_excl_tax
                ##shipping charge = fedex_charge + tax(1.00)
                fedex_ = D(fedex_net_charge)+D("1.00")
                return render_to_response('checkout/shipping_methods.html',
                                          {'methods': self._methods, 'fedex_net_charge': currency(fedex_)},
                                          context_instance=RequestContext(self.request))
            return super(ShippingMethodView, self).get(request, *args, **kwargs)

