from itertools import chain
import json
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView,
                                  FormView, RedirectView)
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.db.models import get_model, Q
from oscar.views.generic import PostActionMixin
from oscar.apps.customer.utils import get_password_reset_url
from oscar.apps.customer.views import ProfileUpdateView as Core_ProfileUpdate
from oscar.core.loading import get_class, get_profile_class, get_classes
from apps.common.decorator import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, load_backend
from .mixins import PageTitleMixin, RegisterUserMixin
from settings import STATIC_URL, AVATAR_DIR, MEDIA_URL, AVATAR_URL
from core.models import User
from os.path import isfile

Dispatcher = get_class('customer.utils', 'Dispatcher')
EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes(
    'customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm',
                       'OrderSearchForm'])
ProfileForm = get_class('customer.forms', 'ProfileForm')
UserAddressForm = get_class('address.forms', 'UserAddressForm')
user_registered = get_class('customer.signals', 'user_registered')
Order = get_model('order', 'Order')
Line = get_model('basket', 'Line')
Basket = get_model('basket', 'Basket')
UserAddress = get_model('address', 'UserAddress')
Email = get_model('customer', 'Email')
ProductAlert = get_model('customer', 'ProductAlert')
CommunicationEventType = get_model('customer', 'CommunicationEventType')

# =======
# Account
# =======


class AccountSummaryView(RedirectView):
    """
    View that exists for legacy reasons and customisability. It commonly gets
    called when the user clicks on "Account" in the navbar, and can be
    overriden to determine to what sub-page the user is directed without
    having to change a lot of templates.
    """
    url = reverse_lazy(settings.OSCAR_ACCOUNTS_REDIRECT_URL)


class AccountRegistrationView(RegisterUserMixin, FormView):
    form_class = EmailUserCreationForm
    template_name = 'customer/registration.html'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return super(AccountRegistrationView, self).get(
            request, *args, **kwargs)

    def get_logged_in_redirect(self):
        return reverse('customer:summary')

    def get_form_kwargs(self):
        kwargs = super(AccountRegistrationView, self).get_form_kwargs()
        kwargs['initial'] = {
            'email': self.request.GET.get('email', ''),
            'redirect_url': self.request.GET.get(self.redirect_field_name, '')
        }
        kwargs['host'] = self.request.get_host()
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super(AccountRegistrationView, self).get_context_data(
            *args, **kwargs)
        ctx['cancel_url'] = self.request.META.get('HTTP_REFERER', None)
        return ctx

    def form_valid(self, form):
        self.register_user(form)
        return HttpResponseRedirect(
            form.cleaned_data['redirect_url'])


class AccountAuthView(RegisterUserMixin, TemplateView):
    """
    This is actually a slightly odd double form view
    """
    template_name = 'customer/login_registration.html'
    login_prefix, registration_prefix = 'login', 'registration'
    login_form_class = EmailAuthenticationForm
    registration_form_class = EmailUserCreationForm
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return super(AccountAuthView, self).get(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(AccountAuthView, self).get_context_data(*args, **kwargs)
        ctx.update(kwargs)

        # Don't pass request as we don't want to trigger validation of BOTH
        # forms.
        if 'login_form' not in kwargs:
            ctx['login_form'] = self.get_login_form()
        if 'registration_form' not in kwargs:
            ctx['registration_form'] = self.get_registration_form()
        return ctx

    def get_login_form(self, request=None):
        return self.login_form_class(**self.get_login_form_kwargs(request))

    def get_login_form_kwargs(self, request=None):
        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.login_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
        }
        if request and request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': request.POST,
                'files': request.FILES,
            })
        return kwargs

    def get_registration_form(self, request=None):
        return self.registration_form_class(
            **self.get_registration_form_kwargs(request))

    def get_registration_form_kwargs(self, request=None):
        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.registration_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
            }
        if request and request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': request.POST,
                'files': request.FILES,
                })
        return kwargs

    def post(self, request, *args, **kwargs):
        # Use the name of the submit button to determine which form to validate
        if u'login_submit' in request.POST:
            return self.validate_login_form()
        elif u'registration_submit' in request.POST:
            return self.validate_registration_form()
        return self.get(request)

    def validate_login_form(self):
        form = self.get_login_form(self.request)
        if form.is_valid():
            auth_login(self.request, form.get_user())

            if self.request.is_ajax():
               return HttpResponse(json.dumps({'code': 1, 'message': _('Successful')}), mimetype='application/json')
            else:
                return HttpResponseRedirect(form.cleaned_data['redirect_url'])

        if self.request.is_ajax():
            return HttpResponse(json.dumps(
                                {'code': 0, 'message': _('The email or password you entered is incorrect.')}),
                                mimetype='application/json')
        else:
            ctx = self.get_context_data(login_form=form)
            return self.render_to_response(ctx)

    def validate_registration_form(self):
        form = self.get_registration_form(self.request)
        if form.is_valid():
            self.register_user(form)
            return HttpResponseRedirect(form.cleaned_data['redirect_url'])

        ctx = self.get_context_data(registration_form=form)
        return self.render_to_response(ctx)


class LogoutView(RedirectView):
    url = reverse_lazy('promotions:home')
    permanent = False

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        response = super(LogoutView, self).get(request, *args, **kwargs)

        for cookie in settings.OSCAR_COOKIES_DELETE_ON_LOGOUT:
            response.delete_cookie(cookie)

        return response


# =============
# Profile
# =============

class ProfileView(PageTitleMixin, TemplateView):
    template_name = 'customer/profile/profile.html'
    page_title = _('Profile')
    active_tab = 'profile'

    def get_context_data(self, **kwargs):
        from os.path import isfile

        user = self.request.user
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        ctx['profile'] = self.get_profile_fields(user)
        img_resize = AVATAR_DIR + str(user.id) + '.png'

        if isfile(img_resize):
            ctx['img_resize'] = MEDIA_URL + 'upload/avatar/' + str(user.id) + '.png'
        else:
            ctx['img_resize'] = 'images/no_avatar.png'
        ctx['view_user'] = User.objects.get(pk=self.request.user.id)
        return ctx

    def get_profile_fields(self, user):
        field_data = []

        # Check for custom user model
        for field_name in User._meta.additional_fields:
            field_data.append(
                self.get_model_field_data(user, field_name))

        # Check for profile class
        profile_class = get_profile_class()
        if profile_class:
            try:
                profile = profile_class.objects.get(user=user)
            except ObjectDoesNotExist:
                profile = profile_class(user=user)

            field_names = [f.name for f in profile._meta.local_fields]
            for field_name in field_names:
                if field_name in ('user', 'id'):
                    continue
                field_data.append(
                    self.get_model_field_data(profile, field_name))

        return field_data

    def get_model_field_data(self, model_class, field_name):
        """
        Extract the verbose name and value for a model's field value
        """
        field = model_class._meta.get_field(field_name)
        if field.choices:
            value = getattr(model_class, 'get_%s_display' % field_name)()
        else:
            value = getattr(model_class, field_name)
        return {
            'name': getattr(field, 'verbose_name'),
            'value': value,
        }


class ProfileUpdateView(Core_ProfileUpdate):
    form_class = ProfileForm
    template_name = 'customer/profile/profile_form.html'
    communication_type_code = 'EMAIL_CHANGED'
    page_title = _('Edit Profile')
    active_tab = 'profile'

    def get_form_kwargs(self):
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Grab current user instance before we save form.  We may need this to
        # send a warning email if the email address is changed.
        try:
            old_user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            old_user = None
        form.save()

        # We have to look up the email address from the form's
        # cleaned data because the object created by form.save() can
        # either be a user or profile depending on AUTH_PROFILE_MODULE
        new_email = form.cleaned_data['email']
        new_profile_url = form.cleaned_data['profile_url']
        if old_user and new_email != old_user.email:
            # Email address has changed - send a confirmation email to the old
            # address including a password reset link in case this is a
            # suspicious change.
            ctx = {
                'user': self.request.user,
                'site': get_current_site(self.request),
                'reset_url': get_password_reset_url(old_user),
                'new_email': new_email,
                'new_profile_url': new_profile_url
            }
            msgs = CommunicationEventType.objects.get_and_render(
                code=self.communication_type_code, context=ctx)
            Dispatcher().dispatch_user_messages(old_user, msgs)

        messages.success(self.request, "Profile updated")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = ""
        check = User.objects.get(username=self.request.user)
        if check.profile_url:
            url = check.profile_url
        if not check.profile_url:
            url = check.username
        return reverse('view_user_profile_custom_url', kwargs={'username': str(url)})


class ChangePasswordView(PageTitleMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'customer/profile/change_password_form.html'
    communication_type_code = 'PASSWORD_CHANGED'
    page_title = _('Change Password')
    active_tab = 'profile'

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Password updated"))

        ctx = {
            'user': self.request.user,
            'site': get_current_site(self.request),
            'reset_url': get_password_reset_url(self.request.user),
            }
        msgs = CommunicationEventType.objects.get_and_render(
            code=self.communication_type_code, context=ctx)
        Dispatcher().dispatch_user_messages(self.request.user, msgs)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('customer:profile-view')


# =============
# Email history
# =============

class EmailHistoryView(PageTitleMixin, ListView):
    context_object_name = "emails"
    template_name = 'customer/email/email_list.html'
    paginate_by = 20
    page_title = _('Email History')
    active_tab = 'emails'

    def get_queryset(self):
        return Email._default_manager.filter(user=self.request.user)


class EmailDetailView(PageTitleMixin, DetailView):
    """Customer email"""
    template_name = "customer/email/email_detail.html"
    context_object_name = 'email'
    active_tab = 'emails'

    def get_object(self, queryset=None):
        """Return an order object or 404"""
        return get_object_or_404(Email, user=self.request.user,
                                 id=self.kwargs['email_id'])

    def get_page_title(self):
        """Append email subject to page title"""
        return u'%s: %s' % (_('Email'), self.object.subject)


# =============
# Order history
# =============

class OrderHistoryView(PageTitleMixin, ListView):
    """
    Customer order history
    """
    context_object_name = "orders"
    template_name = 'customer/order/order_list.html'
    paginate_by = 20
    model = Order
    form_class = OrderSearchForm
    page_title = _('Order History')
    active_tab = 'orders'

    def get(self, request, *args, **kwargs):
        if 'date_from' in request.GET:
            self.form = self.form_class(self.request.GET)
            if not self.form.is_valid():
                self.object_list = self.get_queryset()
                ctx = self.get_context_data(object_list=self.object_list)
                return self.render_to_response(ctx)
            data = self.form.cleaned_data

            # If the user has just entered an order number, try and look it up
            # and redirect immediately to the order detail page.
            if data['order_number'] and not (data['date_to'] or
                                             data['date_from']):
                try:
                    order = Order.objects.get(
                        number=data['order_number'], user=self.request.user)
                except Order.DoesNotExist:
                    pass
                else:
                    return HttpResponseRedirect(
                        reverse('customer:order',
                                kwargs={'order_number': order.number}))
        else:
            self.form = self.form_class()
        return super(OrderHistoryView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model._default_manager.filter(user=self.request.user)
        if self.form.is_bound and self.form.is_valid():
            qs = qs.filter(**self.form.get_filters())
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(OrderHistoryView, self).get_context_data(*args, **kwargs)
        ctx['form'] = self.form
        return ctx


class OrderDetailView(PageTitleMixin, PostActionMixin, DetailView):
    model = Order
    active_tab = 'orders'

    def get_template_names(self):
        return ["customer/order/order_detail.html"]

    def get_page_title(self):
        """
        Order number as page title
        """
        return u'%s #%s' % (_('Order'), self.object.number)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, user=self.request.user,
                                 number=self.kwargs['order_number'])

    def do_reorder(self, order):
        """
        'Re-order' a previous order.

        This puts the contents of the previous order into your basket
        """
        # Collect lines to be added to the basket and any warnings for lines
        # that are no longer available.
        basket = self.request.basket
        lines_to_add = []
        warnings = []
        for line in order.lines.all():
            is_available, reason = line.is_available_to_reorder(
                basket, self.request.strategy)
            if is_available:
                lines_to_add.append(line)
            else:
                warnings.append(reason)

        # Check whether the number of items in the basket won't exceed the
        # maximum.
        total_quantity = sum([line.quantity for line in lines_to_add])
        is_quantity_allowed, reason = basket.is_quantity_allowed(
            total_quantity)
        if not is_quantity_allowed:
            messages.warning(self.request, reason)
            self.response = HttpResponseRedirect(
                reverse('customer:order-list'))
            return

        # Add any warnings
        for warning in warnings:
            messages.warning(self.request, warning)

        for line in lines_to_add:
            options = []
            for attribute in line.attributes.all():
                if attribute.option:
                    options.append({
                        'option': attribute.option,
                        'value': attribute.value})
            basket.add_product(line.product, line.quantity, options)

        if len(lines_to_add) > 0:
            self.response = HttpResponseRedirect(reverse('basket:summary'))
            messages.info(
                self.request,
                _("All available lines from order %(number)s "
                  "have been added to your basket") % {'number': order.number})
        else:
            self.response = HttpResponseRedirect(
                reverse('customer:order-list'))
            messages.warning(
                self.request,
                _("It is not possible to re-order order %(number)s "
                  "as none of its lines are available to purchase") %
                {'number': order.number})


class OrderLineView(PostActionMixin, DetailView):
    """Customer order line"""

    def get_object(self, queryset=None):
        """Return an order object or 404"""
        order = get_object_or_404(Order, user=self.request.user,
                                  number=self.kwargs['order_number'])
        return order.lines.get(id=self.kwargs['line_id'])

    def do_reorder(self, line):
        self.response = HttpResponseRedirect(
            reverse('customer:order', args=(int(self.kwargs['order_number']),)))
        basket = self.request.basket

        line_available_to_reorder, reason = line.is_available_to_reorder(
            basket, self.request.strategy)

        if not line_available_to_reorder:
            messages.warning(self.request, reason)
            return

        # We need to pass response to the get_or_create... method
        # as a new basket might need to be created
        self.response = HttpResponseRedirect(reverse('basket:summary'))

        # Convert line attributes into basket options
        options = []
        for attribute in line.attributes.all():
            if attribute.option:
                options.append({'option': attribute.option,
                                'value': attribute.value})
        basket.add_product(line.product, line.quantity, options)

        if line.quantity > 1:
            msg = _("%(qty)d copies of '%(product)s' have been added to your basket") % {
                'qty': line.quantity, 'product': line.product}
        else:
            msg = _("'%s' has been added to your basket") % line.product

        messages.info(self.request, msg)


class AnonymousOrderDetailView(DetailView):
    model = Order
    template_name = "customer/anon_order.html"

    def get_object(self, queryset=None):
        # Check URL hash matches that for order to prevent spoof attacks
        order = get_object_or_404(self.model, user=None,
                                  number=self.kwargs['order_number'])
        if self.kwargs['hash'] != order.verification_hash():
            raise Http404()
        return order


# ------------
# Address book
# ------------

class AddressListView(PageTitleMixin, ListView):
    """Customer address book"""
    context_object_name = "addresses"
    template_name = 'customer/address/address_list.html'
    paginate_by = 40
    active_tab = 'addresses'
    page_title = _('Address Book')

    def get_queryset(self):
        """Return customer's addresses"""
        return UserAddress._default_manager.filter(user=self.request.user)


class AddressCreateView(PageTitleMixin, CreateView):
    form_class = UserAddressForm
    model = UserAddress
    template_name = 'customer/address/address_form.html'
    active_tab = 'addresses'
    page_title = _('Add a new address')

    def get_form_kwargs(self):
        kwargs = super(AddressCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(AddressCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _('Add a new address')
        return ctx

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' created") % self.object.summary)
        return reverse('customer:address-list')


class AddressUpdateView(PageTitleMixin, UpdateView):
    form_class = UserAddressForm
    model = UserAddress
    template_name = 'customer/address/address_form.html'
    active_tab = 'addresses'
    page_title = _('Edit address')

    def get_form_kwargs(self):
        kwargs = super(AddressUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(AddressUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = _('Edit address')
        return ctx

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' updated") % self.object.summary)
        return reverse('customer:address-list')


class AddressDeleteView(PageTitleMixin, DeleteView):
    model = UserAddress
    template_name = "customer/address/address_delete.html"
    page_title = _('Delete address?')
    active_tab = 'addresses'
    context_object_name = 'address'

    def get_queryset(self):
        return UserAddress._default_manager.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' deleted") % self.object.summary)
        return reverse('customer:address-list')


class AddressChangeStatusView(RedirectView):
    """
    Sets an address as default_for_(billing|shipping)
    """
    url = reverse_lazy('customer:address-list')

    def get(self, request, pk=None, action=None, *args, **kwargs):
        address = get_object_or_404(UserAddress, user=self.request.user,
                                    pk=pk)
        setattr(address, 'is_%s' % action, True)
        address.save()
        return super(AddressChangeStatusView, self).get(
            request, *args, **kwargs)


class ViewUserProfile(LoginRequiredMixin, PageTitleMixin, TemplateView):
    page_title = _('Profile View')
    active_tab = 'profile'

    def get(self, request, *args, **kwargs):
        user = self.kwargs['username']
        if user.isdigit():
            if len(User.objects.filter(Q(id=user) | Q(profile_url=user))) == 0:
                return redirect('customer:profile-view')
        else:
            if len(User.objects.filter(Q(username=user) | Q(profile_url=user))) == 0:
                return redirect('customer:profile-view')
        return super(ViewUserProfile, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from apps.social.function import is_friend, is_follower
        ctx = super(ViewUserProfile, self).get_context_data(**kwargs)
        user = self.kwargs['username']
        if user.isdigit():
            view_user = User.objects.get(Q(id=user) | Q(profile_url=user))
        else:
            view_user = User.objects.get(Q(username=user) | Q(profile_url=user))
        current_user = self.request.user

        ctx['friend'] = is_friend(user_self=current_user.id, user_obj=view_user.id)
        ctx['is_follower'] = is_follower(user_self=current_user.id, user_obj=view_user.id)
        ctx['is_current_user'] = False
        if view_user.id == current_user.id:
            ctx['is_current_user'] = True
        ctx['view_user'] = view_user

        return ctx

    def get_template_names(self):
        profile_user_url = User.objects.get(pk=self.request.user.id).profile_url
        user_obj = self.kwargs['username']
        if user_obj == self.request.user.username or user_obj == profile_user_url:
            'template for current user'
            template_name = 'customer/profile/profile.html'
        else:
            'template for friend of current user'
            template_name = 'customer/profile/profile_view.html'
        return template_name


def ajax_upload_avatar(request):
    from apps.common.functions import handle_uploaded_file

    user = request.user
    response = {
        'error': '',
        'original': '',
        'file_name': '',
        'path': AVATAR_URL
    }

    basewidth = 400
    if 'basewidth' in request.POST:
        basewidth = int(request.POST.get('basewidth'))

    file_name_prefix = str(user.id)
    if 'is_avatar' in request.POST:
        if int(request.POST.get('is_avatar')) == 0:
            file_name_prefix = 'insert_media_%s' % str(user.id)

    result = handle_uploaded_file(request.FILES.getlist('file'), AVATAR_DIR, file_name_prefix, 200, basewidth)
    if user.id is not None:
        if result == '' or result is None:
            response['original'] = file_name_prefix + '_original' + '.png'
            response['file_name'] = file_name_prefix + '.png'
        else:
            response['error'] = result
    else:
        response['error'] = 'Session time out, please login again'

    return HttpResponse(json.dumps(response))


def crop_avatar(request):
    from PIL import Image

    user = request.user
    left = request.POST['left']
    top = request.POST['top']
    width = request.POST['width']
    height = request.POST['height']
    if int(width) == 0 or int(height) == 0:
        left = 0
        top = 0
        width = 200
        height = 200

    if user.id:
        try:
            image = Image.open(AVATAR_DIR + str(user.id) + '.png')
            avatar = AVATAR_DIR + str(user.id) + '_avatar.png'

            box = (int(left), int(top), int(left) + int(width), int(top) + int(height))
            image = image.crop(box)

            image.save(avatar , "JPEG", quality=80, optimize=True, progressive=True)
            return redirect('customer:profile-view')
        except Exception, error:
            pass
    else:
        return redirect('/')


def sign_up_account_by_ajax(request):
    if request.is_ajax():
        email = request.POST.get('email')
        check_exist = User.objects.filter(email__exact=email)
        user = None
        if len(check_exist) == 0:
            #Build user param
            username = request.POST.get('username')
            username_exist = User.objects.filter(username__exact=username)
            if len(username_exist) > 0:
                username = '%s_%d' % (username, len(username_exist))
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = make_password(email)

            #Create
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.is_active = True
            new_user.fb_id = request.POST.get('id')
            new_user.save()

            user = new_user
        else:
            user = check_exist[0]

        #Login
        if not hasattr(user, 'backend'):
            for backend in settings.AUTHENTICATION_BACKENDS:
                if user == load_backend(backend).get_user(user.pk):
                    user.backend = backend
                    break
        if hasattr(user, 'backend'):
            login(request, user)

        message = {
            'code': 1,
            'message': _('Access OK'),
            'id': user.pk,
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'date_joined': user.date_joined.strftime('%m/%d/%Y'),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
    else:
        message = {'code': 0, 'message': _("Access denied")}
    return HttpResponse(json.dumps(message))

def ajax_check_logged(request):
    if request.user.is_authenticated():
        message = {
            'code': 1,
            'message': 'Access allow',
        }
    else:
        message = {
            'code': 0,
            'message': 'Access denied.',
        }
    return HttpResponse(json.dumps(message))