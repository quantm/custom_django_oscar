from oscar.apps.basket.app import BasketApplication as CoreBasketApplication

from apps.basket import views


class BasketApplication(CoreBasketApplication):
    add_view = views.BasketAddView
    summary_view = views.BasketView

application = BasketApplication()