import settings, settings_local
from settings_local import STATIC_URL
from .function import *
import json
from datetime import *
from itertools import chain
from django.template import RequestContext
from django.db.models import get_model, Max, Q
from django.shortcuts import render_to_response, HttpResponse, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import (TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView,
                                  FormView, RedirectView)
from apps.social.models import *
from apps.social.forms import *
from apps.customer.mixins import PageTitleMixin
from apps.common.functions import OBJECT_TYPE, send_notification
from apps.common.decorator import LoginRequiredMixin
from oscar.core.loading import get_classes
from apps.customer.models import Notification
from django.utils.timezone import now
from settings import USER_ITEM_PER_PAGE, MY_WALL_POST_MESSAGE_PER_PAGE
from core.models import User
from apps.common.decorator import *

WishList = get_model('wishlists', 'WishList')
EventListForm, LineFormset = get_classes('customer.forms',
                                        ['MyEventListForm', 'LineFormset'])


def get_user(request):
    return render_to_response('social/user.html',
                              {
                                  'user': User.get_mention_list(request.GET['comment_object']),
                                  'arr_length': User.get_mention_list(request.GET['comment_object']).__len__()
                              }, context_instance=RequestContext(request))


def get_hashtag(request):
    query = 'SELECT * FROM social_hashtag WHERE name like %s'
    args = [str(request.GET['name'])+'%']
    return render_to_response('social/hashtag.html',
                              {
                                'hashtag': SocialHashTag.objects.raw(query, args),
                                'arr_length': len(list(SocialHashTag.objects.raw(query, args)))
                              }, context_instance=RequestContext(request))


class MyFriendList(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-friends"
    template_name = 'social/friend/my_friends.html'
    page_title = _('My Friends')
    model = SocialFriendShip

    def get_context_data(self, **kwargs):
        context = super(MyFriendList, self).get_context_data(**kwargs)
        friend_list = SocialFriendShip.get_friend_list(self.request.user)

        paginator = Paginator(friend_list, USER_ITEM_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            context['friends'] = paginator.page(page)
        except PageNotAnInteger:
            context['friends'] = paginator.page(1)
        except EmptyPage:
            context['friends'] = paginator.page(paginator.num_pages)

        return context


class FriendListOtherProfile(PageTitleMixin, ListView):
    context_object_name = active_tab = "my-friends"
    template_name = 'social/friend/friends_view.html'
    page_title = _('Friends List View')
    model = SocialFriendShip

    def get_context_data(self, **kwargs):
        context = super(FriendListOtherProfile, self).get_context_data(**kwargs)

        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        context['view_user'] = view_user

        friend_list = SocialFriendShip.get_friend_list(view_user)

        paginator = Paginator(friend_list, USER_ITEM_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            context['friends'] = paginator.page(page)
        except PageNotAnInteger:
            context['friends'] = paginator.page(1)
        except EmptyPage:
            context['friends'] = paginator.page(paginator.num_pages)

        return context


class MyEventListDetail(LoginRequiredMixin, PageTitleMixin, ListView):
    template_name = 'social/events/events_create_view.html'
    page_title = _('My Event Details')
    model = MyEvent

    def get_context_data(self, **kwargs):
        ctx = super(MyEventListDetail, self).get_context_data(**kwargs)
        user_id_array = [self.request.user.id]
        array_user_update = []
        qs_user_update = SocialFriendShip.get_event_participant(self.kwargs['event_id'])
        for id_user__update in list(qs_user_update):
            array_user_update.append(id_user__update.user_obj_id)
        for user_selected_update in MyEventObject.objects.filter(event_id=self.kwargs['event_id']):
                user_id_array.append(user_selected_update.user_share_id)
        ctx['header_text'] = "Participant"
        ctx['fields'] = MyEventCreateViewForm
        ctx['update'] = MyEvent.objects.filter(pk=self.kwargs['event_id'])
        ctx['user_array'] = qs_user_update
        ctx['user_array_update'] = array_user_update
        ctx['is_update'] = False
        ctx['is_new'] = True
        return ctx


@LoginRequired
def my_event_create_update(request, **kwargs):
    header_text = ""
    title = ""
    owner = ""
    user_id_array = [request.user.id]
    is_new = False
    user_update_array = []
    if len(MyEvent.objects.all()) != 0:
        if 'new' in kwargs:
            is_new = True
            title = "Create your event"
            create_or_update = SocialFriendShip.get_friend_list(request.user)
        if 'event_id' in kwargs:
            is_new = False
            create_or_update = SocialFriendShip.get_event_participant(kwargs['event_id'])
            update = MyEvent.objects.filter(pk=int(kwargs['event_id']))
            for user_ in update:
                owner = user_.user_id
            title = "Update your event"
            header_text = "Participant"
            for user_selected_update in MyEventObject.objects.filter(event_id=int(kwargs['event_id'])):
                user_id_array.append(user_selected_update.user_share_id)
        else:
            update = []
            user_id_array = []
            header_text = "Please choose participant"
    if len(MyEvent.objects.all()) == 0:
        update = []
        is_new = True
        user_id_array = []
        create_or_update = SocialFriendShip.get_friend_list(request.user)
        header_text = "Please choose participant"
        title = "Create your event"
    return render_to_response('social/events/events_create_view.html',
                              {'fields': MyEventCreateViewForm,
                               'update': update,
                               'owner': owner,
                               'is_new': is_new,
                               'page_title': title,
                               'static_url': STATIC_URL,
                               'is_update': True,
                               'is_save': True,
                               'log_id': request.user.id,
                               'header_text': header_text,
                               'user_array_friend': SocialFriendShip.get_friend_list(request.user),
                               'user_chk_array': user_id_array,
                               'user_array': create_or_update,
                               'length': len(SocialFriendShip.get_friend_list(request.user)),
                               'user_array_update': user_update_array
                               },
                              context_instance=RequestContext(request))


def delete_event(request):
    if 'my_event_id' in request.POST:
        MyEvent.objects.filter(pk=request.POST['my_event_id']).delete()
        Notification.objects.filter(object_id=request.POST['my_event_id'],
                                    type=OBJECT_TYPE._MY_EVENT_NOTIFICATION).delete()
        return redirect('/social/my-event/')


def delete_event_view(request, **kwargs):
    if 'event_id' in kwargs:
        return render_to_response('social/events/events_delete_view.html',
                                  {
                                      "id": kwargs['event_id'],
                                      "my_events": MyEvent.objects.get(pk=int(kwargs['event_id'])),
                                  },
                                  context_instance=RequestContext(request))


def save_event(request):
    if 'check_if_update' not in request.POST:
        name_empty = []
        post_selected_array = request.POST.getlist('my_event_selected_user_array[]')
        participant_quantity = int(request.POST['my_event_participant_quantity']) + 1
        if request.POST['name'] == "":
            check_name = False
            name_empty.append({
                "code": 0,
                "id": "id_name",
                "message": "Event name cannot be blank"
            })
        if request.POST['my_event_participant_quantity'] == '0':
            check_amount = False
            name_empty.append({
                "code": 0,
                "id": "participant",
                "message": "Please select at least one participant"
            })
        if request.POST['my_event_participant_quantity'] != '0':
            check_amount = True
            name_empty.append({
                "code": 2,
                "id": "participant",
                "message": ""
            })
        if request.POST['date_created'] == "":
            check_date_created = False
            name_empty.append({
                "code": 0,
                "id": "id_date_created",
                "message": "Date created cannot be blank"
            })
        if request.POST['date_created'] != "":
            check_date_created = True
            name_empty.append({
                "code": 2,
                "id": "id_date_created",
                "message": ""
            })
        if request.POST['name'] != "":
            if len(MyEvent.objects.filter(name=request.POST['name'])) != 0:
                check_name = False
                name_empty.append({
                    "code": 1,
                    "id": "id_name",
                    "message": "Event existence"
                })
            if len(MyEvent.objects.filter(name=request.POST['name'])) == 0:
                check_name = True
                name_empty.append({
                    "code": 2,
                    "id": "id_name",
                    "message": ""
                })

        if check_name and check_date_created and check_amount:
            obj_save = MyEvent(name=request.POST['name'], date_created=request.POST['date_created'],
                               description=request.POST['description'],
                               participants_amount=participant_quantity,
                               user=User.objects.get(pk=request.user.id))
            obj_save.save()
            name_empty.append({
                "code": "save_success"
            })
            last_event_id = MyEvent.objects.all().aggregate(Max("id"))
            object_event_id = last_event_id['id__max']
            my_event_user_share = post_selected_array[0].split(',')
            for my_event_share in my_event_user_share:
                obj_my_event_save = MyEventObject(event=MyEvent.objects.get(pk=object_event_id),
                                                  user_owner=request.user.id,
                                                  user_share_id=my_event_share,
                                                  is_shared=OBJECT_TYPE._MY_EVENT_NOTIFICATION
                                                  )
                obj_my_event_save.save()
            my_event_user_share_new_notification = post_selected_array[0].split(',')
            '''
            my_event_user_share_new_notification.append(request.user.id)
            '''
            for my_event_share_new_notification in my_event_user_share_new_notification:
                send_notification(sender_id=request.user.id, recipient_id=my_event_share_new_notification,
                                  object_id=object_event_id,
                                  type=OBJECT_TYPE._MY_EVENT_NOTIFICATION, mail=True)

    if 'check_if_update' in request.POST:
        name_empty = []
        array_user_do_update = []
        social_event_activity = MyEventObject.objects.filter(event=request.POST['id_update'])
        post_selected_update_array = request.POST.getlist('my_event_selected_user_array[]')
        my_event = MyEvent.objects.get(pk=request.POST['id_update'])
        my_event.name = request.POST['name']
        my_event.date_created = request.POST['date_created']
        my_event.description = request.POST['description']
        if request.POST['my_event_participant_quantity'] != '0':
            my_event.participants_amount = request.POST['my_event_participant_quantity']
        update_fields = ['name', 'date_created', 'description', 'participants_amount']
        array_user_do_update.append(my_event.user_id)
        for arr_user_do_update in social_event_activity:
            array_user_do_update.append(arr_user_do_update.user_share_id)
        for check_user_do_update in array_user_do_update:
            if check_user_do_update == request.user.id:
                my_event.save(update_fields=update_fields)
                name_empty.append({"code": "update_success"})
        if my_event.user_id != request.user.id:
            name_empty.append({
                "code": 4,
                "id": "id_update_name_permission",
                "message": "Permission Denied"
            })
        if request.POST['my_event_participant_quantity'] != '0':
            social_event_activity.delete()
            Notification.objects.filter(object_id=request.POST['id_update'],
                                        type=OBJECT_TYPE._MY_EVENT_NOTIFICATION).delete()
            my_event_user_share = post_selected_update_array[0].split(',')
            for my_event_share in my_event_user_share:
                obj_my_event_save = MyEventObject(event=MyEvent.objects.get(pk=request.POST['id_update']),
                                                  user_owner=request.user.id,
                                                  user_share_id=my_event_share,
                                                  is_shared=OBJECT_TYPE._MY_EVENT_NOTIFICATION)
                obj_my_event_save.save()
            '''
            my_event_user_share.append(request.user.id)
            '''
            for my_event_share_notification in my_event_user_share:
                Notification.objects.filter(object_id=request.POST['id_update'],
                                            type=OBJECT_TYPE._MY_EVENT_NOTIFICATION)
                send_notification(sender_id=request.user.id, recipient_id=my_event_share_notification,
                                  object_id=request.POST['id_update'],
                                  type=OBJECT_TYPE._MY_EVENT_NOTIFICATION, mail=True)
    return HttpResponse(json.dumps({'result': name_empty}))


class MyWallMessage(LoginRequiredMixin, ListView):
    context_object_name = 'parent'
    template_name = 'social/wall/my-wall-message.html'

    def get_context_data(self, **kwargs):
        context = super(MyWallMessage, self).get_context_data(**kwargs)
        context['child'] = SocialMessage.objects.exclude(message_id=0).order_by('-create_date')
        return context

    def get_queryset(self):
        return SocialMessage.objects.filter(message_id=0).order_by('-create_date')


@LoginRequired
def my_wall_save(request):
    my_wall_text = request.POST['textbox_comment']
    message_id = request.POST['message_id']
    array_notification = []
    'child node'
    if message_id != "0":
        'send notification to all user that participate in the conversation except the current user'
        message_notification = SocialMessage.objects.filter(Q(message_id=message_id, type=OBJECT_TYPE._MY_WALL_TYPE) |
                                                            Q(pk=message_id, type=OBJECT_TYPE._MY_WALL_TYPE)).values('object_id').distinct()
        for array_filter in message_notification:
            array_notification.append(array_filter['object_id'])
            'if sender id in notification array exclude it'
            if array_notification.count(request.user.id):
                index = array_notification.index(request.user.id)
                array_notification.pop(index)
            for wall_notification in array_notification:
                send_notification(sender_id=request.user.id,
                                  recipient_id=wall_notification,
                                  object_id=int(message_id),
                                  type=OBJECT_TYPE._MY_WALL_NOTIFICATION, mail=False)

        object_save = SocialMessage(content=my_wall_text,
                                    message_id=int(message_id),
                                    object_id=request.user.id,
                                    user=User.objects.get(pk=request.user.id),
                                    friend=User.objects.get(pk=request.user.id),
                                    type=OBJECT_TYPE._MY_WALL_TYPE)
        object_save.save()
        child_id = SocialMessage.objects.all().aggregate(Max("id"))['id__max']
        my_wall_child_row = SocialMessage.objects.filter(pk=child_id)
        get_mention_hashtag('client', OBJECT_TYPE._HASHTAG_MY_WALL_POST, my_wall_text, message_id,
                            "images/products/hash_tag_no_image.jpg",
                            request.user.id)
        return render_to_response('social/wall/my-wall-render-child.html',
                                  {
                                      "child": my_wall_child_row,
                                      "full_name": request.user.get_full_name(),
                                      "avatar": request.user.get_avatar_src_full_url()
                                  }, context_instance=RequestContext(request))

    'parent node'
    if message_id == "0":
        'object_id:user_id or collection_id'
        object_id = request.POST['object_id']
        is_friend_post = request.POST['is_friend_post']
        type = request.POST['type']
        if object_id == "0":
            obj_save = SocialMessage(content=my_wall_text,
                                     object_id=request.user.id,
                                     user=User.objects.get(pk=request.user.id),
                                     friend=User.objects.get(pk=request.user.id),
                                     type=type)
        if object_id != "0":
            if is_friend_post == "0":
                obj_save = SocialMessage(content=my_wall_text,
                                         object_id=object_id,
                                         user=User.objects.get(pk=request.user.id),
                                         friend=User.objects.get(pk=request.user.id),
                                         type=type)
            if is_friend_post == "1":
                obj_save = SocialMessage(content=my_wall_text,
                                         user=User.objects.get(pk=object_id),
                                         friend=User.objects.get(pk=request.user.id),
                                         type=type,
                                         object_id=OBJECT_TYPE._MY_WALL_OBJ_FRIEND_POST)
        obj_save.save()
        parent_id = SocialMessage.objects.all().aggregate(Max("id"))['id__max']
        my_wall_parent_row = SocialMessage.objects.filter(pk=parent_id)
        get_mention_hashtag('client', OBJECT_TYPE._HASHTAG_MY_WALL_POST, my_wall_text, parent_id,
                            "images/products/hash_tag_no_image.jpg", request.user.id)
        return render_to_response('social/wall/my-wall-render-parent.html',
                                  {
                                      "parent": my_wall_parent_row,
                                      "full_name": request.user.get_full_name(),
                                  },
                                  context_instance=RequestContext(request))


class MyWallConversationDetails(LoginRequiredMixin, ListView):
    page_title = _('My Wall Detail')
    model = SocialMessage

    def get_context_data(self, **kwargs):
        context = super(MyWallConversationDetails, self).get_context_data(**kwargs)
        message_post_list = SocialMessage.objects\
            .filter(Q(pk=self.kwargs['post_id']) | Q(message_id=self.kwargs['post_id']))
        context['wall_post_detail'] = message_post_list
        context['parent_id'] = self.kwargs['post_id']
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'social/wall/my-wall-post-message-per-page.html'
        else:
            template_name = 'social/wall/my-wall-post-detail.html'
        return template_name


class MyWallOtherProfile(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "wall"
    page_title = _('My Wall')
    model = SocialMessage

    def get_context_data(self, **kwargs):
        ctx = super(MyWallOtherProfile, self).get_context_data(**kwargs)
        user_friend_id = int(self.kwargs.get('user_friend_id'))
        parent = SocialMessage.objects.filter(message_id=0, user=user_friend_id).order_by('-create_date')
        paginator = Paginator(parent, MY_WALL_POST_MESSAGE_PER_PAGE)
        page = self.request.GET.get('page')
        try:
            ctx['parent'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['parent'] = paginator.page(1)
        except EmptyPage:
            ctx['parent'] = paginator.page(paginator.num_pages)
        ctx['child'] = SocialMessage.objects.exclude(message_id=0, user=user_friend_id).order_by('create_date')
        ctx['view_user'] = User.objects.get(pk=user_friend_id)
        ctx['user_friend_id'] = user_friend_id
        ctx['total_page'] = paginator.num_pages
        return ctx

    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'social/wall/my-wall-pagination-per-page.html'
        else:
            template_name = 'social/wall/my-wall-other-profile.html'
        return template_name


class MyWall(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "wall"
    page_title = _('My Wall')
    model = SocialMessage

    def get_context_data(self, **kwargs):
        ctx = super(MyWall, self).get_context_data(**kwargs)
        parent_list = SocialMessage.objects.filter(message_id=0, type=OBJECT_TYPE._MY_WALL_TYPE, user_id=self.request.user.id).order_by('-create_date')
        paginator = Paginator(parent_list, MY_WALL_POST_MESSAGE_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            ctx['parent'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['parent'] = paginator.page(1)
        except EmptyPage:
            ctx['parent'] = paginator.page(paginator.num_pages)

        ctx['child'] = SocialMessage.objects.exclude(message_id=0, type=OBJECT_TYPE._MY_WALL_TYPE, user_id=self.request.user.id).order_by('create_date')
        ctx['total_page'] = paginator.num_pages
        return ctx

    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'social/wall/my-wall-pagination-per-page.html'
        else:
            template_name = 'social/wall/my-wall.html'
        return template_name


def delete_my_wall_message(request):
    if request.is_ajax() and request.method == "POST":
        id = request.POST['obj-id-message-delete']
        return_arr_delete = []
        check_child_delete_permission = SocialMessage.objects.filter(pk=id, user=request.user.id)
        parent = SocialMessage.objects.filter(Q(pk=id) | Q(message_id=id)).values('id')
        for arr_delete in parent:
            return_arr_delete.append(arr_delete['id'])
        if check_child_delete_permission:
            SocialMessage.objects.filter(Q(pk=id) | Q(message_id=id)).delete()
            return_arr_delete.append("true")
        if not check_child_delete_permission:
            return_arr_delete.append("false")
    return HttpResponse(json.dumps({'delete_object': return_arr_delete}))


def my_event_user(request):
    if request.is_ajax():
        user_participant = request.get['user_participant']
    return render_to_response('social/events/render_user_participant.html',
                              {
                                  'participant': user_participant,
                              }, context_instance=RequestContext(request))


class MyEventListView(PageTitleMixin, ListView):
    context_object_name = active_tab = "events"
    template_name = 'social/events/events_list_view.html'
    page_title = _('My Events')
    model = MyEvent

    def get_queryset(self):
        event_id_1 = MyEvent.objects.filter(user=self.request.user.id).extra(select={'event_id': 'id'}).values('event_id')
        event_id_2 = MyEventObject.objects.filter(user_share_id=self.request.user.id).values('event_id')
        event_id = []
        for item in list(chain(event_id_1, event_id_2)):
            event_id.append(item['event_id'])
        object_collection = MyEvent.objects.filter(pk__in=list(set(event_id)))
        return object_collection

    def get_context_data(self, **kwargs):
        ctx = super(MyEventListView, self).get_context_data(**kwargs)
        return ctx


class MyEventListOtherProfileView(PageTitleMixin, ListView):
    context_object_name = active_tab = "events"
    template_name = 'social/events/events_list_view.html'
    page_title = _('My Events')
    model = MyEvent

    def get_context_data(self, **kwargs):
        ctx = super(MyEventListOtherProfileView, self).get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        view_user = User.objects.get(id=user_id)
        ctx['view_user'] = view_user
        return ctx

    def get_queryset(self):
        event_id_1 = MyEvent.objects.filter(user=self.kwargs['user_id']).extra(select={'event_id': 'id'}).values('event_id')
        event_id_2 = MyEventObject.objects.filter(user_share_id=self.request.user.id).values('event_id')
        event_id = []
        for item in list(chain(event_id_1, event_id_2)):
            event_id.append(item['event_id'])
        object_collection = MyEvent.objects.filter(pk__in=list(set(event_id)))
        return object_collection


def request_friend(request):
    #check current user is logged in
    current_user = request.user
    try:
        user_obj_id = request.POST['uid']
        action = request.POST['action']
        if current_user.id:
            req = False
            if action == "make_friend":
                req = _request_friend(user_self_id=current_user.id, user_obj_id=user_obj_id, subject='Request friend from '+ current_user.get_full_name())
            if action == "accept_request":
                req = _response_friend(user_self_id=current_user.id, user_obj_id=user_obj_id, subject=current_user.get_full_name() + ' accept friend with you')
            if action == "unfriend_request":
                req = _unfriend(user_self_id=current_user.id,user_obj_id=user_obj_id)
            if action == "delete_request":
                req = _delete_request(user_self_id=current_user.id, user_obj_id=user_obj_id)
            if action == "make_follow":
                req = _request_follow(user_self_id=current_user.id, user_obj_id=user_obj_id)
            if action == "unfollow":
                req = _request_unfollow(user_self_id=current_user.id, user_obj_id=user_obj_id)

            if req:
                return HttpResponse(json.dumps({'error':''}))
            else:
                return HttpResponse(json.dumps({'error':'1'}))
        else:
            return HttpResponse(json.dumps({'error':'1'}))
    except Exception, ex:
        return HttpResponse(json.dumps({'error':'1'}))


def _request_friend(user_self_id, user_obj_id, subject="Request friend"):
    if int(user_self_id) == int(user_obj_id):
        return False

    friend = is_friend(user_self_id, user_obj_id)
    try:
        if friend['is_friend'] or friend['ready_requested'] or friend['requested']:
            return False
        else:
            friendship = SocialFriendShip(user_self_id=user_self_id,user_obj_id=user_obj_id,type=OBJECT_TYPE._REQUEST_FRIEND)
            friendship.save()

            send_notification(recipient_id=user_obj_id, sender_id=user_self_id, object_id=user_self_id,
                              type=OBJECT_TYPE._REQUEST_FRIEND)

    except Exception, ex:
        return False
    return True


def _response_friend(user_self_id, user_obj_id, subject="Request friend"):
    if int(user_self_id) == int(user_obj_id):
        return False

    friend = is_friend(user_self_id, user_obj_id)
    try:
        if friend['is_friend'] or friend['requested']:
            return False
        if friend['ready_requested']:
            friendship = SocialFriendShip(user_self_id=user_self_id,user_obj_id=user_obj_id,type=OBJECT_TYPE._REQUEST_FRIEND)
            friendship.save()

            send_notification(recipient_id=user_obj_id, object_id=user_self_id,
                              type=OBJECT_TYPE._REQUEST_FRIEND)

    except Exception, ex:
        return False
    return True


def _unfriend(user_self_id, user_obj_id):
    if int(user_self_id) == int(user_obj_id):
        return False
    try:
        SocialFriendShip.objects.filter(user_self_id=user_self_id, user_obj_id=user_obj_id, type=OBJECT_TYPE._REQUEST_FRIEND).delete()
        SocialFriendShip.objects.filter(user_self_id=user_obj_id, user_obj_id=user_self_id,type=OBJECT_TYPE._REQUEST_FRIEND).delete()
    except Exception, ex:
        return False

    return True


def _delete_request(user_self_id, user_obj_id):
    if int(user_self_id) == int(user_obj_id):
        return False
    friend = is_friend(user_self_id, user_obj_id)
    try:
        if friend['is_friend'] or friend['requested']:
            return False
        if friend['ready_requested']:
            SocialFriendShip.objects.filter(user_self_id=user_obj_id, user_obj_id=user_self_id, type=OBJECT_TYPE._REQUEST_FRIEND).delete()
    except Exception, ex:
        return False

    return True


def _request_follow(user_self_id, user_obj_id):
    from apps.common.functions import notification_ready_unread
    if int(user_self_id) == int(user_obj_id):
        return False

    ready = is_follower(user_self_id, user_obj_id)

    try:
        if ready :
            return False
        else:
            SocialFriendShip(user_self_id=user_self_id,user_obj_id=user_obj_id,type=OBJECT_TYPE._REQUEST_FOLLOWER).save()
            ready_notify = notification_ready_unread(recipient_id=user_obj_id, sender_id=user_self_id, type=OBJECT_TYPE._REQUEST_FOLLOWER)
            if not ready_notify:
                send_notification(recipient_id=user_obj_id, sender_id=user_self_id, object_id=user_self_id,
                                  type=OBJECT_TYPE._REQUEST_FOLLOWER)
    except Exception, ex:
        return False

    return True


def _request_unfollow(user_self_id, user_obj_id):
    if int(user_self_id) == int(user_obj_id):
        return False

    ready = is_follower(user_self_id, user_obj_id)

    try:
        if ready :
            SocialFriendShip.objects.filter(user_self_id=user_self_id, user_obj_id=user_obj_id, type=OBJECT_TYPE._REQUEST_FOLLOWER).delete()

    except Exception, ex:
        return False

    return True


class ViewConnectedHashtag(PageTitleMixin, TemplateView):
    template_name = 'social/hashtag/hashtag_connected.html'

    def get_context_data(self, **kwargs):
        ctx = super(ViewConnectedHashtag, self).get_context_data(**kwargs)
        for obj_hash_tag in SocialHashTag.objects.filter(name=kwargs['hashtag']):
            hash_tag_id = obj_hash_tag.id

        query_bookmarklet = ' SELECT *, collection_media.image AS original' + \
                            ' FROM social_hashtag_object' + \
                            ' INNER JOIN collection_media ON collection_media.id = social_hashtag_object.object_id' + \
                            ' WHERE social_hashtag_object. TYPE =' + str(OBJECT_TYPE._HASHTAG_BOOKMARK_VIDEO) + \
                            ' AND social_hashtag_object.hashtag_id =' + str(hash_tag_id) + \
                            ' OR social_hashtag_object. TYPE =' + str(OBJECT_TYPE._HASHTAG_BOOKMARK_IMAGE) + \
                            ' AND social_hashtag_object.hashtag_id =' + str(hash_tag_id)

        query_dashboard = ' SELECT *, catalogue_product.slug AS product_slug, catalogue_product. ID AS product_id ' + \
                          ' FROM social_hashtag_object ' + \
                          ' INNER JOIN catalogue_product ON catalogue_product. ID = ' \
                          ' social_hashtag_object.object_id ' + \
                          ' INNER JOIN catalogue_productimage ON catalogue_productimage.product_id = ' \
                          ' social_hashtag_object.object_id ' + \
                          ' WHERE social_hashtag_object. TYPE = '+str(OBJECT_TYPE._HASHTAG_DASHBOARD_PRODUCT) +  \
                          ' AND social_hashtag_object.hashtag_id =' + str(hash_tag_id) + \
                          ' OR social_hashtag_object. TYPE = ' + str(OBJECT_TYPE._HASHTAG_BOOKMARK_PRODUCT) + \
                          ' AND social_hashtag_object.hashtag_id = ' + str(hash_tag_id)

        ctx['test1'] = query_bookmarklet
        ctx['test2'] = query_dashboard
        ctx['hash_tag_bookmark_let'] = SocialHashTagObject.objects.raw(query_bookmarklet)
        ctx['hash_tag_dashboard'] = SocialHashTagObject.objects.raw(query_dashboard, [str(hash_tag_id)])
        ctx['hashtag'] = kwargs['hashtag']
        return ctx


class HashtagList(PageTitleMixin, ListView):
    template_name = 'social/hashtag/hashtag_list.html'
    model = SocialHashTag

    def get_context_data(self, **kwargs):
        ctx = super(HashtagList, self).get_context_data(**kwargs)
        query_hash_tag = 'SELECT * FROM social_hashtag ORDER BY date_created DESC'
        ctx['hash_tag_list'] = SocialHashTag.objects.raw(query_hash_tag)
        return ctx


class TopHashTag(PageTitleMixin, ListView):
    template_name = 'social/hashtag/hashtag_popular.html'
    model = SocialHashTag

    def get_context_data(self, **kwargs):
        ctx = super(TopHashTag, self).get_context_data(**kwargs)
        query_top_hash_tag = 'select * from' \
                             '( SELECT sho.hashtag_id, "count"(*) as counting ' \
                             'from social_hashtag_object as sho ' \
                             'GROUP BY sho.hashtag_id ORDER BY "count"(*) DESC LIMIT 5) obj_hash_tag ' \
                             'INNER JOIN social_hashtag ON social_hashtag."id" = obj_hash_tag.hashtag_id ' \
                             'ORDER BY obj_hash_tag.counting DESC'
        ctx['top_connected_hashtag'] = SocialHashTag.objects.raw(query_top_hash_tag)

        return ctx


def get_mention_hashtag(dashboard, obj_type, description, object_id, object_thumb, u_id_login):
    none_html_str = ""
    if dashboard == "dashboard":
        none_html_str = description.replace("<p>", "").replace("</p>", "")
    if dashboard == "client":
        none_html_str = description
    text_arr = none_html_str.split(" ")
    for i in range(len(text_arr)):
        if text_arr[i].startswith("@"):
            SocialHashTag.save_mention(text_arr[i].replace("@", ""), u_id_login, object_id)
        if text_arr[i].startswith("#"):
            SocialHashTag.save_hashtag(text_arr[i].replace("#", ""), object_id, obj_type, object_thumb)
    return HttpResponse()

@LoginRequired
def save_promote(request):
    current_user = request.user
    data = {
        'error':''
    }
    try:
        if current_user.is_authenticated():
            product_id = request.POST['product_id']
            text = request.POST['text_promote']
            media_id = request.POST['media_id']

            social_promote = SocialPromote.objects.filter(product_id=product_id, user_id=current_user.id)
            if social_promote:
                social_promote.update(media=media_id, text=text, create_date=now())
                social_id = social_promote[0].id
            else:
                social = SocialPromote(product_id=int(product_id), user_id=current_user.id, media_id=int(media_id), text=text)
                social.save()
                social_id = social.pk

            try:
                get_mention_hashtag('client', OBJECT_TYPE._HASHTAG_PROMOTE_TEXT, text, social_id, None, current_user.id)
            except Exception, err:
                pass
        else:
            data['error'] = _('Please login')
    except Exception, err:
         data['error'] = _('Can not request right now, Please reload page and try again')

    return HttpResponse(json.dumps(data))

@LoginRequired
def check_user_ready_promote_this_product(request):
    current_user = request.user
    data = {
        'error':'',
        'status': 0,
        'product_id': '',
        'product_title': '',
        'media_id': '',
        'media_type': '',
        'media_image': '',
        'media_title': '',
        'promote_text': ''
    }
    try:
        product_id = request.POST['product_id']
        social_promote = SocialPromote.objects.filter(product_id=product_id, user_id=current_user.id)
        if social_promote:
            data['status'] = 1
            data['product_id'] = social_promote[0].product.id
            data['product_title'] = social_promote[0].product.get_title()
            data['promote_text'] = social_promote[0].text
            if social_promote[0].media:
                data['media_id'] = social_promote[0].media.id
                data['media_type'] = social_promote[0].media.type
                data['media_image'] = settings.STATIC_URL + 'media/' + str(social_promote[0].media.image)
                data['media_title'] = social_promote[0].media.title

    except Exception, err:
        data['error'] = _('Can not request right now, Please reload page and try again')

    return HttpResponse(json.dumps(data))