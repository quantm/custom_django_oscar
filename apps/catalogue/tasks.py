from celery.task import task
from apps.catalogue.models import Product

@task
def reset_buy_count_every_month():
    try:
        Product.objects.filter(buy_count_in_month__gt=0).update(buy_count_in_month = 0)
        return 'Success'
    except Exception, err:
        print err
        return 'Error'