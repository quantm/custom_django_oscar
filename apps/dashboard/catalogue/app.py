#__author__ = 'tqn'
from oscar.apps.dashboard.catalogue.app import CatalogueApplication as CoreDashboardCatalogueApplication
from .views import ProductCreateUpdateView, ProductListView


class CatalogueApplication(CoreDashboardCatalogueApplication):
    product_createupdate_view = ProductCreateUpdateView
    product_list_view = ProductListView

application = CatalogueApplication()