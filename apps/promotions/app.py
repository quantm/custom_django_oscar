#__author__ = 'Tam'
from oscar.apps.promotions.app import PromotionsApplication as CorePromotionsApplication
'''from apps.catalogue.views import ProductListView'''

class PromotionsApplication(CorePromotionsApplication):
    '''home_view  = ProductListView'''
application = PromotionsApplication()