from celery.task import task
from django.db.models import Min, Max
from oscar.apps.catalogue.models import Product
import copy
from django.db.models import Q
from django.utils.translation import ugettext as _

@task
def update_the_best_price_for_product():
    try:
        products = Product.objects.all()
        for product in products:
            #Get all stocks of the product unless selected stock
            stock_records = product.stockrecords.filter(~Q(selected_partner=1))
            if len(stock_records) > 0:
                #Get min price value
                min_price = stock_records.aggregate(Min('price_excl_tax'))['price_excl_tax__min']
                #Select stock record with min price
                stock_records = stock_records.filter(price_excl_tax=min_price)
                if len(stock_records) > 1:
                    #Get max commission value
                    max_commission = stock_records.aggregate(Max('commission'))['commission__max']
                    #query stock record with max commission value and order ASC date create
                    stock_records = stock_records.filter(commission=max_commission).order_by('date_created')
                    #if have a lot stock equal
                    if len(stock_records) > 0:
                        #get the first value
                        selected = stock_records[0]
                    else:
                        selected = None
                elif len(stock_records) > 0:
                    selected = stock_records[0]
                else:
                    selected = None
                if selected is not None:
                    #Get old the best price
                    old_stocks = list(product.stockrecords.filter(selected_partner=1))
                    if old_stocks.__len__() > 0:
                        old_stocks[0].delete()
                    #Duplicate stock record
                    duplicate = copy.copy(selected)
                    duplicate.pk = None
                    duplicate.selected_partner = 1
                    duplicate.save()


        return _('Sending notification successfully')
    except IndexError:
        return None

