from oscar.app import Shop
from .checkout.app import application as checkout_app
from .catalogue.app import application as catalogue_app
from .dashboard.app import application as dashboard_app
from .promotions.app import application as promotions_app
from .basket.app import application as basket_app
from .customer.app import application as customer_app


class overriddenShop(Shop):
    # Specify a local checkout app where we override the payment details view
    checkout_app = checkout_app
    catalogue_app = catalogue_app
    dashboard_app = dashboard_app
    promotions_app = promotions_app
    basket_app = basket_app
    customer_app = customer_app

shop = overriddenShop()