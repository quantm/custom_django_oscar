import copy
from django.dispatch import receiver
from .models import StockRecord
from oscar.apps.partner.models import Partner
from django.db.models.signals import m2m_changed, post_save
from core.models import User

@receiver(m2m_changed, sender = Partner.users.through)
def change_staff_role_when_users_link_to_partner(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':# After data saved
        #Do something to set User.is_staff=True
        users_id = pk_set
        users_object = list(instance.users.all())
        for user in users_object:
            if user.is_staff==False:
                user.is_staff = True
                user.save()
    elif action == 'post_remove':
        for uid in pk_set:
            user = User.objects.get(id=uid)
            partner_related = list(Partner.objects.filter(users=user).values('id'))
            partner_ids = True
            for item in partner_related:
                if item['id'] != instance.id:
                    partner_ids = False
            if partner_ids:
                user.is_staff = False
                user.save()
    elif action == 'pre_clear':#Before user_id be remove out Partner
        #Do something to set User.is_staff=False
        users_object = list(instance.users.all())
        for user in users_object:
            #Check user will be delete is have relate with other partner
            partner_related = list(Partner.objects.filter(users=user).values('id'))
            partner_ids = True
            for item in partner_related:
                if item['id'] != instance.id:
                    partner_ids = False
            if partner_ids:
                user.is_staff = False
                user.save()

@receiver(post_save, sender=StockRecord)
def set_partner_win_when_the_first_price_of_product_created(sender, instance=None, created=False, **kwargs):
    if created is True:
        #get partners of this product
        partners_of_product = StockRecord.objects.filter(product=instance.product)
        #Check if this stock is the first
        if len(partners_of_product) == 1:
            if partners_of_product[0].pk == instance.pk:
                selected = partners_of_product[0]
                #Duplicate stock record
                duplicate = copy.copy(selected)
                duplicate.pk = None
                duplicate.selected_partner = 1
                duplicate.save()
