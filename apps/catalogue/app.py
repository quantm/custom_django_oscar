from oscar.apps.catalogue.app import CatalogueApplication
from django.conf.urls import patterns, url, include

from apps.catalogue import views

class OverriddenCatalogueApplication(CatalogueApplication):
    # Specify new view for catalogue
    '''index_view = views.ProductListView
    detail_view = views.ProductDetailView
    '''
application = OverriddenCatalogueApplication()
