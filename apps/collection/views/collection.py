import json, datetime, settings, math
from io import StringIO
from itertools import chain
from django.shortcuts import redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import ListView, FormView
from django.shortcuts import render_to_response, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max

from oscar.apps.customer.mixins import PageTitleMixin
from apps.collection.models.collection import *
from apps.collection.forms.collection import CollectionForm
from apps.common.functions import *
from apps.common.decorator import *
from apps.social.models import SocialFriendShip, SocialMessage
from apps.catalogue.models import ProductImage
from settings import PRODUCT_ITEM_PER_PAGE, COLLECTION_ITEM_PER_PAGE
from core.models import User
from apps.networks.views.facebook import publish_product_to_facebook_timeline


class ViewCollection(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = 'collection'
    template_name = 'collection/view/index.html'
    page_title = _("Collection view")

    def get_context_data(self, **kwargs):
        context = super(ViewCollection, self).get_context_data(**kwargs)
        collection_id = self.request.GET.get('set_id', '')
        collection_user = CollectionSet.objects.get(id=collection_id)

        context['collection_name'] = CollectionSet.objects.filter(id=collection_id)
        context['comment_list'] = CollectionComment.objects.filter(set_id=collection_id)
        context['user_name'] = User.objects.filter(id=collection_user.user_id)
        context['user_array'] = SocialFriendShip.get_friend_list(self.request.user)
        context['id_user_comment'] = self.request.user.id
        context['set_id'] = collection_id
        context['avatar'] = collection_user.user.get_avatar_src_full_url()
        context['parent'] = SocialMessage.objects.filter(object_id=collection_id,
                                                         type=OBJECT_TYPE._COLLECTION_TYPE).order_by('-create_date')
        context['full_name'] = self.request.user.get_full_name()
        return context

    def get_queryset(self):
        collection_id = self.request.GET.get('set_id', '')
        qs = CollectionSetElement.objects.filter(set_id=collection_id).exclude(style='').order_by('id')
        return qs


class CollectionDesign(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = 'collection'
    template_name = 'collection/design/index.html'
    page_title = _("Collection design")
    model = CollectionSet

    def get_context_data(self, **kwargs):
        context = super(CollectionDesign, self).get_context_data(**kwargs)

        context['right_items'] = None
        context['collection_items'] = None
        context['current_collection'] = None

        #if 'set_id' in self.request.GET
        collection_id = self.request.GET.get('set_id', '')
        if collection_id is not None and collection_id != "":
            if collection_id.isnumeric() and collection_id > 0:
                collections = CollectionSet.objects.filter(pk=collection_id)
                if len(collections) > 0:
                    collection_obj = collections[0]
                    context['current_collection'] = collection_obj
                    collection_items = CollectionSetElement.objects.filter(set=collection_obj)

                    #get collection items to display on left panel
                    context['collection_items'] = collection_items.exclude(style='')

                    #get item to display on right panel
                    context['right_items'] = collection_items.distinct('object_id')

        return context

class CollectionListView(LoginRequiredMixin, ListView):
    template_name = 'collection/design/collections_of_open_modal.html'
    model = CollectionSet
    context_object_name = 'collections'

    def get_context_data(self, **kwargs):
        context = super(CollectionListView, self).get_context_data(**kwargs)
        context['collections'] = CollectionSet.objects.filter(user=self.request.user, type='collection', status__in=['p', 'd']).order_by('id')
        return context

    def get_queryset(self):
        qs = super(CollectionListView, self).get_queryset().order_by('id')
        return qs


class MyCollectionView(LoginRequiredMixin, PageTitleMixin, ListView):
    context_object_name = active_tab = "my-collections"
    page_title = _("My Collections")
    template_name = 'collection/my_collections.html'
    model = CollectionSet
    paginate_by = COLLECTION_ITEM_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super(MyCollectionView, self).get_context_data(**kwargs)
        user_id = self.request.user.id
        try:
            user_id = self.kwargs['user_id']
        except Exception, err:
            pass

        current_user = User.objects.get(pk=user_id)

        context['view_user'] = current_user

        collections_id1 = CollectionSet.objects.filter(user=current_user).exclude(type='list').extra(select={'set_id': 'id'}).values('set_id')
        collections_id2 = CollectionSetEdit.objects.filter(editor=current_user, is_edited=1).values('set_id')
        collections_id = []
        for item in list(chain(collections_id1, collections_id2)):
            collections_id.append(item['set_id'])
        object_collection = CollectionSet.objects.filter(pk__in=list(set(collections_id)))
        paginator = Paginator(object_collection, MyCollectionView.paginate_by)
        page = self.request.GET.get('page')
        try:
            collection = paginator.page(page)
        except PageNotAnInteger:
            collection = paginator.page(1)
        except EmptyPage:
            collection = paginator.page(paginator.num_pages)
        context['my_collection'] = collection
        return context

    def get_queryset(self):
        return super(MyCollectionView, self).get_queryset().order_by('-create')

    def get_template_names(self):
        self.template_name = 'collection/my_collections.html'
        user_id = None
        try:
            user_id = self.kwargs['user_id']
        except Exception, err:
            pass
        if user_id:
            self.template_name = 'collection/my_collections_view.html'

        return self.template_name


@LoginRequired
def collection_get(request, set_id=None):
    current_collection = CollectionSet.objects.get(pk=set_id)
    collection_items = CollectionSetElement.objects.filter(set=current_collection).exclude(style='').order_by('id')

    return render_to_response('collection/design/collection_item_need_style.html',
                              {
                                  'current_collection': current_collection,
                                  'collection_items': collection_items
                              }, context_instance=RequestContext(request))

@LoginRequired
def save_share_collection(request):
    if request.method == "POST" and request.is_ajax():
        selected_user_array = request.POST.getlist('post_selected_user_array[]', '')
        set_id = request.POST.get('set_id', '')
        share_from_user_id = request.user.id
        for share_u in selected_user_array:
            send_notification(sender_id=share_from_user_id, recipient_id=share_u, object_id=set_id,
                              type=OBJECT_TYPE._SHARE_COLLECTION)
    return HttpResponse(json.dumps(selected_user_array))


@LoginRequired
def save_invite_edit_collection(request):
    if request.method == "POST" and request.is_ajax():
        selected_user_array = request.POST.getlist('post_selected_user_array[]', '')
        set_id = request.POST.get('set_id', '')
        share_from_user_id = request.user.id
        for share_u in selected_user_array:
            send_notification(sender_id=share_from_user_id, recipient_id=share_u, object_id=set_id,
                              type=OBJECT_TYPE._INVITE_COLLECTION, mail=True)
            qs_co_edit = CollectionSet.objects.filter(id=set_id, user_id=share_u)
            if not qs_co_edit:
                CollectionSetEdit(editor=User.objects.get(pk=share_u),
                                  set=CollectionSet.objects.get(pk=set_id),
                                  creator_id=share_from_user_id, is_edited=0).save()

        return HttpResponse(json.dumps(selected_user_array))

@LoginRequired
def collection_save(request):
    message = {"code": 0, "id": 0, "link": '', "message": _("")}
    collection_form = CollectionForm(request.POST or None)
    if not collection_form.is_valid():
        message["message"] = _("Values invalid")
    else:
        collection_id = int(request.POST.get('pk'))
        str_name = request.POST.get('name')
        status = str(request.POST.get('status'))
        new_collection = False

        #If pk is None or is 0, we create new collection
        if collection_id == 0:
            collection = CollectionSet(name=str_name, user=request.user, type='collection', status=status)
            collection.save()
            collection_id = collection.pk
            new_collection = True

        users_can_update = list(CollectionSetEdit.objects.filter(set_id=collection_id).values('editor'))
        creator = CollectionSet.objects.get(pk=collection_id)
        users_can_update.append({'editor': creator.user.id})

        if {'editor': request.user.id} in users_can_update:
            if new_collection is False:
                collection = CollectionSet.objects.get(pk=collection_id)
                collection.name = str_name
                collection.status = status

                update_fields = ['name', 'status']
                collection.save(update_fields=update_fields)

                if creator.user.id != request.user.id:
                    user_updated_collection_after_invited(collection, request.user)

            #Delete all item of Collection
            CollectionSetElement.objects.filter(set=collection).delete()

            #Start add items to collection
            objects = []
            for item in request.POST.getlist('items[]'):
                io_item = StringIO(item)
                item_value = json.load(io_item)

                content = item_value['text']
                if item_value['type'] == 'video':
                    video_info = CollectionMedia.objects.get(pk=int(item_value["obj"]))
                    content = video_info.code

                #using to update collection thumb when collection be create
                if item_value['type'] != 'text':
                    objects.append({'id': int(item_value["obj"]), 'type': item_value['type']})

                collection_item = CollectionSetElement(object_id=int(item_value["obj"]), set=collection, type=item_value['type'], style=item_value['style'], class_name=item_value['class'], content=content)
                collection_item.save()

            #Update Thumbnail for collection if it is the new
            if len(objects) > 0:
                if objects[0]['type'] == 'product':
                    thumb = ProductImage.objects.filter(product_id=objects[0]['id'])[0]
                    thumb_url = thumb.none_watermark
                else:
                    thumb = CollectionMedia.objects.get(pk=objects[0]['id'])
                    thumb_url = thumb.image

                collection.thumb = thumb_url
                collection.save(update_fields=['thumb'])

            message = {
                "code": 1,
                "id": collection.pk,
                "link": '<a class="data-dismiss-modal" href="%s" target="_blank">%s</a>' % ('/collection/view/?set_id=%d' % collection.pk, _('Click here to view collection')),
                "message": _('Collection has been saved.')
            }
        else:
            message["message"] = _("Access denied.")

    return HttpResponse(json.dumps(message), mimetype='application/json')


@LoginRequired
def save_comment(request):
        object_id = request.POST['current_set_id']
        content = request.POST['text_comment']
        comment = SocialMessage(content=content, object_id=object_id,
                                type=OBJECT_TYPE._COLLECTION_TYPE,
                                user=User.objects.get(pk=request.user.id))
        comment.save()
        return_object_id = SocialMessage.objects.all().aggregate(Max("id"))['id__max']
        object_row = SocialMessage.objects.filter(pk=return_object_id)
        return render_to_response('social/wall/my-wall-render-parent.html',
                                  {
                                      "parent": object_row,
                                      "full_name": request.user.get_full_name()
                                  },
                                  context_instance=RequestContext(request))


def get_or_create_collection(request, *args):
    arg = args[0]

    try:
        c_id = int(arg.get('id'))

        if c_id == 0:
            c_name = arg.get('name')
            p_id = int(arg.get('product_id'))
            c_type = str(arg.get('type'))
            c_status = 'p'
            if c_type == 'collection':
                c_status = 'c'

            thumb = ProductImage.objects.filter(product_id=p_id)[0]
            thumb_string = thumb.none_watermark

            collection = CollectionSet(name=c_name, user=request.user, type=c_type, thumb=thumb_string, status=c_status)
            collection.save()
        else:
            collection = CollectionSet.objects.get(pk=c_id)

    except Exception, err:
        collection = None

    return collection

@LoginRequired
def add_product_to_collection(request):
    collection = get_or_create_collection(request, request.POST)
    try:
        p_id = int(request.POST.get('product_id'))
        product = Product.browsable.base_queryset().get(pk=p_id)
        products_in_collection = CollectionSetElement.objects.filter(object_id=p_id, type='product', set=collection).values('object_id')

        if {'object_id': p_id} not in products_in_collection:

            str_style = u""
            str_class = u"abilities not-clone shop"
            collection_items = CollectionSetElement.objects.filter(set=collection)
            if str(collection.status) == 'c' and str(collection.type) == 'collection':
                str_style = u'position: relative; float: left; z-index: %d;' % (len(collection_items)+1)

            item = CollectionSetElement(object_id=p_id, set=collection, type='product', style=str_style, class_name=str_class)
            item.save()

            msg = '<b>%s</b> %s %s ' % (product.get_title(), _('has been added to'), collection.name)

            if collection.type == 'list' and 'fb_token' in request.POST:
                #Publish this product to Facebook
                fb_token = str(request.POST.get('fb_token'))
                publish_product_to_facebook_timeline(request, fb_token, product)

        else:
            msg = '<b>%s</b> %s %s ' % (product.get_title(), _('already exist in'), collection.name)

        if collection.type == 'list':
            link = {'url': '/collection/my-list/%d/' % collection.pk, 'text': _('Click here to view list')}
        else:
            link = {'url': '/collection/preview/%d/' % collection.pk, 'text': _('Click here to view collection')}

        response = {
            "code": 1,
            "collection_id": collection.pk,
            "link":  link,
            "message": msg
        }


    except Exception, err:
        response = {"code": 0, "link": {}, "message": _("AJAX post invalid")}

    return HttpResponse(json.dumps(response), mimetype='application/json')


def user_updated_collection_after_invited(collection, user_editing):
    collection_updated = CollectionSetEdit.objects.get(set_id=collection.id, editor_id=user_editing.id)
    collection_updated.is_edited = 1
    update_fields = ['is_edited', 'editor_id']
    collection_updated.save(update_fields=update_fields)


@LoginRequired
def gallery_save_into_collection(request):
    collection_id = request.POST.get('collection_id')
    new_name = request.POST.get('new_name')
    collection_obj = CollectionSet.objects.get(pk=collection_id)
    collection_obj.name = new_name
    collection_obj.save(update_fields=['name'])

    return redirect('/collection/design/?set_id=%d' % collection_obj.pk)


class MyCollectionForm(LoginRequiredMixin, FormView):
    template_name = 'collection/forms/my_list_collection_form_of_add_product_modal.html'
    form_class = CollectionForm
    success_url = ''

    def get_context_data(self, **kwargs):
        context = super(MyCollectionForm, self).get_context_data(**kwargs)

        type = self.request.GET.get('type')

        collections = CollectionSet.objects.filter(user=self.request.user, type=type).exclude(status='e').order_by('-create')
        context['collections'] = collections

        if str(type) == 'list':
            form_name = u'List'
        else:
            form_name = u'Collection'
        context['form_name'] = form_name

        return context

    def form_valid(self, form):
        return super(MyCollectionForm, self).form_valid(form)


class MyCollectionPreview(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'collection_preview'
    template_name = 'collection/preview_before_go_design_page.html'

    def get_context_data(self, **kwargs):
        context = super(MyCollectionPreview, self).get_context_data(**kwargs)

        context['collection_preview'] = CollectionSet.objects.get(pk=int(self.kwargs['collection_id']))
        context['products'] = Product.browsable.base_queryset().filter(pk__in=kwargs['object_list'])

        return context

    def get_queryset(self):
        return CollectionSetElement.objects.filter(set_id__exact=int(self.kwargs['collection_id']), type='product').values('object_id')


@LoginRequired
def delete_comment(request):
    if request.is_ajax():
        delete_qs = CollectionComment.objects.filter(id=request.POST['id_comment']).delete()
        return HttpResponse(json.dumps(delete_qs))


@LoginRequired
def delete_collection(request):
    if request.is_ajax():
        delete_qs = CollectionSet.objects.filter(id=request.POST['set_id']).delete()
        return HttpResponse(json.dumps(delete_qs))
