#__author__ = 'tqn'
import json
from django.db.models import Count
from django.shortcuts import redirect, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext as _
from apps.common.decorator import *
from django.views.generic import ListView, DetailView, DeleteView
from oscar.apps.customer.mixins import PageTitleMixin
from apps.collection.models.collection import CollectionSet, CollectionSetElement
from apps.common.decorator import LoginRequiredMixin
from .collection import get_or_create_collection
from core.models import User

class MyListProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    model = CollectionSet
    context_object_name = active_tab = "my-list"
    template_name = 'collection/my_list/index.html'
    page_title = _('My List')
    paginate_by = 15

    def get_template_names(self):
        if self.request.is_ajax():
            return 'collection/my_list/my_list_items.html'
        else:
            return 'collection/my_list/index.html'

    def get_context_data(self, **kwargs):
        return super(MyListProfile, self).get_context_data(**kwargs)

    def get_queryset(self):
        return CollectionSet.objects.annotate(num_product=Count('collectionsetelement')).filter(user=self.request.user, type='list').order_by('-create')


class MyListOtherProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    model = CollectionSet
    context_object_name = active_tab = "my-list"
    template_name = 'collection/my_list/profile_vew.html'
    page_title = _('My List')

    def get_context_data(self, **kwargs):
        context = super(MyListOtherProfile, self).get_context_data(**kwargs)

        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user

        if 'object_list' in kwargs:
            context['my_list'] = kwargs['object_list']
        else:
            context['my_list'] = None
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        return CollectionSet.objects.annotate(num_product=Count('collectionsetelement')).filter(user=view_user, type='list')

class MyListDetail(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-list"
    page_title = ''
    model = CollectionSetElement
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(MyListDetail, self).get_context_data(**kwargs)
        context['list_obj'] = CollectionSet.objects.get(pk=int(self.kwargs['pk']))

        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return 'collection/my_list/detail_list_items.html'
        else:
            return 'collection/my_list/detail.html'

    def get_queryset(self):
        return CollectionSetElement.objects.filter(set_id=int(self.kwargs['pk']))



class MyListOtherProfileDetail(LoginRequiredMixin, PageTitleMixin, DetailView):
    context_object_name = active_tab = "my-list"
    page_title = ''
    model = CollectionSet
    template_name = 'collection/my_list/detail_view.html'

    def get_context_data(self, **kwargs):
        context = super(MyListOtherProfileDetail, self).get_context_data(**kwargs)
        user_id = self.request.GET['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user
        context['items'] = CollectionSetElement.objects.filter(set_id=self.kwargs['pk'])
        return context

class MyListDelete(LoginRequiredMixin, PageTitleMixin, DeleteView):
    model = CollectionSet
    success_url = reverse_lazy('my-list-profile')
    template_name = 'collection/my_list/confirm_delete.html'
    page_title = _('Delete List')
    context_object_name = active_tab = "my-list"

    def get_context_data(self, **kwargs):
        return super(MyListDelete, self).get_context_data(**kwargs)

@LoginRequired
def my_list_delete(request, pk=None):
    if request.is_ajax():
        message = {"code": 0, "message": _("Access denied")}
        list_obj = CollectionSet.objects.filter(pk=pk)
        if len(list_obj) > 0:
            current_user_id = request.user.id
            if list_obj[0].user.id == current_user_id:
               list_obj.delete()
               message = {"code": 1, "message": _("Successful")}
    else:
        message = {"message": _("GET petitions are not allowed for this view.")}
    return HttpResponse(json.dumps(message), mimetype='application/json')

@LoginRequired
def my_list_remove_item(request, list_pk=None, item_id=None):

    if request.is_ajax():
        message = {"code": 0, "message": _("Access denied")}
        list_obj = CollectionSet.objects.filter(pk=list_pk)
        if len(list_obj) > 0:
            current_user_id = request.user.id
            if list_obj[0].user.id == current_user_id:
               CollectionSetElement.objects.filter(set_id=list_pk, pk=item_id).delete()
               message = {"code": 1, "message": _("Successful")}

    else:
        message = {"message": _("GET petitions are not allowed for this view.")}
    return HttpResponse(json.dumps(message), mimetype='application/json')

@LoginRequired
def add_product_to_list(request, *args):
    try:
        collection = get_or_create_collection(request, args[0])
        p_id = int(args[0].get('product_id'))
        products_in_list = CollectionSetElement.objects.filter(object_id=p_id, type='product', set=collection).values('object_id')
        if {'object_id': p_id} not in products_in_list:
            item = CollectionSetElement(object_id=p_id, set=collection, type='product', style='', class_name='')
            item.save()
    except Exception, err:
        pass