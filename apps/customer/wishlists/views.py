# -*- coding: utf-8 -*-
from django.db.models import get_model
from django.views.generic import ListView, FormView
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from apps.common.decorator import LoginRequiredMixin
from oscar.apps.customer.mixins import PageTitleMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from oscar.core.loading import get_classes
from oscar.apps.customer.wishlists.views import WishListListView as CoreWishListListView, WishListDetailView as CoreWishListDetailView
from core.models import User

WishList = get_model('wishlists', 'WishList')
Line = get_model('wishlists', 'Line')
Product = get_model('catalogue', 'Product')
WishListForm, LineFormset = get_classes('wishlists.forms',
                                        ['WishListForm', 'LineFormset'])


class WishListListViewOtherProfile(LoginRequiredMixin, CoreWishListListView):
    def get_template_names(self):
        self.template_name = 'customer/wishlists/wishlists_list_view.html'
        return self.template_name

    def get_queryset(self):
        return WishList.objects.filter(owner_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        ctx = super(WishListListViewOtherProfile, self).get_context_data(**kwargs)

        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        ctx['view_user'] = view_user
        return ctx


class WishListDetailViewOtherProfile(LoginRequiredMixin, PageTitleMixin, FormView):
    template_name = 'customer/wishlists/wishlists_detail_view.html'
    active_tab = "wishlists"
    form_class = LineFormset

    def dispatch(self, request, *args, **kwargs):
        view_user = User.objects.get(id=self.kwargs['user_id'])
        self.object = self.get_wishlist_or_404(self.kwargs['key'], view_user)
        return super(WishListDetailViewOtherProfile, self).dispatch(request, *args, **kwargs)

    def get_wishlist_or_404(self, key, user):
        wishlist = get_object_or_404(WishList, key=key)
        if wishlist.is_allowed_to_see(user):
            return wishlist
        else:
            raise Http404

    def get_page_title(self):
        return self.object.name

    def get_form_kwargs(self):
        kwargs = super(WishListDetailViewOtherProfile, self).get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(WishListDetailViewOtherProfile, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        ctx['view_user'] = view_user
        ctx['wishlist'] = self.object
        other_wishlists = view_user.wishlists.exclude(
            pk=self.object.pk)
        ctx['other_wishlists'] = other_wishlists
        return ctx

    def form_valid(self, form):
        for subform in form:
            if subform.cleaned_data['quantity'] <= 0:
                subform.instance.delete()
            else:
                subform.save()
        messages.success(self.request, _('Quantities updated.'))
        return HttpResponseRedirect(reverse('customer:wishlists-detail',
                                            kwargs= {'key': self.object.key}))
