# Create your views here.

import json, settings, simplejson
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from django.template import RequestContext, loader
from django.contrib.auth import login, load_backend
from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from apps.products.views import save_product
from apps.collection.views.media import save_video, save_image
from apps.collection.views.list import add_product_to_list
from .forms import *


def build_url(view_name, post):
    return "%s#tagger:total=%s&idx=%s&loc=%s&caption=%s&video=%s&src=%s&title=%s" % (
        reverse_lazy(view_name),
        post.get('total'),
        post.get('idx'),
        post.get('loc'),
        post.get('caption'),
        post.get('video'),
        post.get('src'),
        post.get('title')
    )


def build_empty_content(request):

    template_file = loader.get_template('bookmarklet/empty_content.html')
    request_context = RequestContext(request,
                                     {
                                         'title': _("Couldn't find any good images on this page."),
                                         'message': [
                                             _('The images might not be large enough, or they might be protected or inside a web plugin.'),
                                             _('Try again on a different page.')
                                         ]
                                     })
    return template_file.render(request_context)


def build_message_content(request):

    if 'save_message' in request.session:
        template_file = loader.get_template('bookmarklet/message_content.html')
        request_context = RequestContext(request, {'message': request.session.get('save_message')})
        del request.session['save_message']
        return template_file.render(request_context)
    else:
        return None


def build_sign_in_form(request):

    form_name = 'sign-in-form'
    form_data = BookmarkLetSignInForm
    action_path = 'sign-in-action-path'
    message = ''
    if 'sign_in_message' in request.session:
        message = request.session.get('sign_in_message')
        del request.session['sign_in_message']

    template_file = loader.get_template('bookmarklet/sign_in_form.html')
    request_context = RequestContext(request,
                                     {
                                         'form': form_data,
                                         'message': message,
                                         'form_name': form_name,
                                         'action_path': action_path
                                     })
    return template_file.render(request_context)


def build_bookmark_let_form(request):

    form_name = 'save-form'
    form_data = BookmarkLetForm
    action_path = 'bookmark-let-save-path'

    template_file = loader.get_template('bookmarklet/form.html')
    request_context = RequestContext(request,
                                     {
                                         'form_name': form_name,
                                         'form': form_data,
                                         'action_path': action_path
                                     })
    return template_file.render(request_context)


def sign_in_page(request):
    form_content = build_sign_in_form(request)

    return render_to_response('bookmarklet/page.html',
                              {
                                  'page_title': 'Sign in Form',
                                  'form_content': form_content
                              }, context_instance=RequestContext(request))


def bookmark_let_page(request):

    form_content = build_sign_in_form(request)
    empty_content = build_empty_content(request)
    message_content = build_message_content(request)
    if request.user.is_authenticated():
        form_content = build_bookmark_let_form(request)

    return render_to_response('bookmarklet/page.html',
                              {
                                  'page_title': 'Bookmark Let Form',
                                  'form_content': form_content,
                                  'empty_content': empty_content,
                                  'message_content': message_content
                              }, context_instance=RequestContext(request))


def sign_in_action(request):

    if request.user.is_authenticated():
        return redirect(build_url('bookmark-let-page', request.POST))

    else:
        auth = 0
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if not hasattr(user, 'backend'):
                    for backend in settings.AUTHENTICATION_BACKENDS:
                        if user == load_backend(backend).get_user(user.pk):
                            user.backend = backend
                            break
                if hasattr(user, 'backend'):
                    login(request, user)

                auth = 1
                message = _("User is valid, active and authenticated")
            else:
                message = _("The password is valid, but the account has been disabled!")

        else:
            message = _("The username and password were incorrect.")

        if auth == 1:
            return redirect(build_url('bookmark-let-page', request.POST))
        else:
            request.session['sign_in_message'] = message
            return redirect(build_url('sign-in-page', request.POST))


def bookmark_let_save(request):
    if not request.user.is_authenticated():
        return redirect(build_url('sign-in-page', request.POST))

    if request.method == "POST":
        message = {
            'code': 0,
            'pro_link': '',
            'back_text': u'Back',
            'mes_box': u'<h1>The info invalid</h1>',
        }
        bookmark_let_form = BookmarkLetForm(request.POST or None)
        if bookmark_let_form.is_valid():
            if request.POST['video_code'] == u'null':
                is_product = int(request.POST.get('is_product'))
                if is_product == 1:
                    message = save_product(request)

                    if message['code'] == 1:
                        okay = True
                        try:
                            message['id'] = int(request.POST.get('lid'))
                            message['name'] = request.POST.get('lname')
                            message['type'] = 'list'
                            message['product_id'] = message.get('object_id')
                        except Exception, err:
                            okay = False
                        if okay:
                            add_product_to_list(request, message)
                else:
                    message = save_image(request)
            else:
                is_video = int(request.POST.get('is_video'))
                if is_video == 1:
                    message = save_video(request)
                else:
                    message = save_image(request)

        request.session['save_message'] = message
        return redirect(build_url('bookmark-let-page', request.POST))
    else:
        message = {'msg': "GET petitions are not allowed for this view."}
        return HttpResponse(json.dumps(message))

