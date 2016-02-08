from django.contrib import messages
from django.db.models import get_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from core.models import User

Partner = get_model('partner', 'Partner')
from oscar.apps.customer.utils import normalise_email
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.partners.views import PartnerListView as CorePartnerListView, \
                                                PartnerUserSelectView as CorePartnerUserSelectView, \
                                                PartnerUserLinkView as CorePartnerUserLinkView


class PartnerListView(CorePartnerListView):
    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_staff and current_user.is_superuser:
            qs = self.model._default_manager.all().exclude(id=0)
        else:
            qs = self.model.objects.filter(users=current_user)

        qs = self.sort_queryset(qs)
        self.description = _("All partners")
        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs
        data = self.form.cleaned_data
        if data['name']:
            qs = qs.filter(name__icontains=data['name'])
            self.description = _("Partners matching '%s'") % data['name']
            self.is_filtered = True
        return qs

    def sort_queryset(self, queryset):
        sort = self.request.GET.get('sort', None)
        allowed_sorts = ['name']
        if sort in allowed_sorts:
            direction = self.request.GET.get('dir', 'desc')
            sort = ('-' if direction == 'desc' else '') + sort
            queryset = queryset.order_by(sort)
        return queryset


class PartnerUserSelectView(CorePartnerUserSelectView):
    def get_context_data(self, **kwargs):
        ctx = super(PartnerUserSelectView, self).get_context_data(**kwargs)
        ctx['partner'] = self.partner
        ctx['form'] = self.form

        users_already_linked = Partner.objects.exclude(users__isnull=True).values('users')
        users_linked = []
        for item in users_already_linked:
            users_linked.append(item['users'])
        ctx['users_linked'] = users_linked

        return ctx

    def get_queryset(self):
        if self.form.is_valid():
            email = normalise_email(self.form.cleaned_data['email'])
            if self.request.user.is_staff and self.request.user.is_superuser:
                return User.objects.filter(is_active=True, email__icontains=email)
            else:
                return User.objects.filter(is_active=True, is_staff=False, is_superuser=False, email__icontains=email)
        else:
            return User.objects.none()


class PartnerUserLinkView(CorePartnerUserLinkView):
    def post(self, request, user_pk, partner_pk):
        user = get_object_or_404(User, pk=user_pk)
        partner = get_object_or_404(Partner, pk=partner_pk)
        name = user.get_full_name() or user.email
        if not partner.users.filter(pk=user_pk).exists():

            partners = Partner.objects.filter(users=user)
            if list(partners).__len__()>0:
                partners_names = []
                for pner in partners:
                    partners_names.append(pner.name)
                if partners_names.__len__() > 1:
                    msg_string = "User '%(name)s' are already linked to '%(partner_name)s'"
                else:
                    msg_string = "User '%(name)s' is already linked to '%(partner_name)s'"
                messages.error(
                request, _(msg_string) % {'name': name, 'partner_name': ', '.join(partners_names)})
            else:

                partner.users.add(user)
                messages.success(
                    request, _("User '%(name)s' was linked to '%(partner_name)s'") %
                    {'name': name, 'partner_name': partner.name})
        else:
            messages.error(
                request, _("User '%(name)s' is already linked to '%(partner_name)s'") %
                {'name': name, 'partner_name': partner.name})
        return HttpResponseRedirect(reverse('dashboard:partner-manage',
                                            kwargs={'pk': partner_pk}))