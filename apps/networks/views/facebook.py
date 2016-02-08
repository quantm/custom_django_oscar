__author__ = 'tqn'

# Create your views here.
import json, urllib, urllib2, re, settings

from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import HttpResponse, render_to_response

from apps.common.decorator import *
from apps.networks.libraries.facebook import graph_api as facebook
from apps.collection.views.media import save_facebook_image
from apps.catalogue.models import ProductImage, Product
from apps.collection.models.collection import CollectionSet, CollectionSetElement

APP_ID = str(settings.FACEBOOK_APPS['demo_oscar']['ID'])
APP_PATH = str(settings.FACEBOOK_APPS['demo_oscar']['PATH'])

def publish_product_to_facebook_timeline(request, access_token, product):
    check_sign_in = check_access_token(access_token)
    if check_sign_in['status']:
        try:
            graph = facebook.GraphAPI(str(access_token))
            images = ProductImage.objects.filter(product=product).order_by('display_order')[:1].values('none_watermark')
            image_url = ''
            if len(images) > 0:
                image_url = images[0]['none_watermark']

            if request.is_secure():
                host = 'https://%s' % request.get_host()
            else:
                host = 'http://%s' % request.get_host()

            image_full_url = '%s%s%s' % (settings.STATIC_URL, 'media/', image_url)
            result = re.match('demo-oscar', request.get_host())
            if result is not None:
                image_full_url = '%s%s%s' % (host, '/media/', image_url)

            product_object = {
                'app_id': APP_ID,
                'type': "product",
                'url': '%s%s' % (host, product.get_absolute_url()),
                'title': product.get_title().encode('utf8'),
                'image': image_full_url,
                'site_name': "Demo Oscar"
            }

            result = graph.put_object("me", APP_PATH, product=json.dumps(product_object))
        except Exception, error:
            result = error
    else:
        result = check_sign_in

    return result

@LoginRequired
def add_this_product(request, signed_request):

    parse_signed = parse_signed_request(signed_request)
    #Get values
    access_token = parse_signed['oauth_token']

    product_url = parse_signed['objects'][0]['url']
    exp = product_url.split('_')
    product_id = int(exp[len(exp)-1].replace('/', ''))
    product = Product.objects.get(pk__exact=product_id)

    if request.is_secure():
        host = 'https://%s' % request.get_host()
    else:
        host = 'http://%s' % request.get_host()

    if request.user.is_authenticated():
        publish_product = publish_product_to_facebook_timeline(access_token, product, host)

        if 'id' in publish_product:
            #add this product to default list
            default_list = CollectionSet.objects.filter(user=request.user, default=True)
            if len(default_list) > 0:
                default_list = default_list[0]
            else:
                default_list = CollectionSet(name='Default', user=request.user)
                default_list.save()
            list_item = CollectionSetElement(product=product, set=default_list)
            list_item.save()

            result = {"success": True}
        else:
            result = {"redirect": product_url}
    else:
        result = {"redirect": '%s/accounts/login/' % host}

    return HttpResponse(json.dumps(result))

def parse_signed_request(signed_request):
    #Explode Url string
    explode = signed_request.split(".")[:2]
    payload = explode[1] + '=='
    #Decode url string
    payload_decode = payload.decode('base64')
    #Convert string to json
    data = json.loads(payload_decode)
    if data['algorithm'].upper() != 'HMAC-SHA256':
        #Unknown algorithm. Expected HMAC-SHA256
        return None

    return data

def check_logged(request):
    if request.is_ajax():
        access_token = request.GET.get('fb_token')
        result = check_access_token(access_token)
    else:
        result = {'message': _('GET petitions are not allowed for this view.')}
    return HttpResponse(json.dumps(result))

def check_access_token(access_token):

    args = {"access_token": access_token}
    post_data = urllib.urlencode({"access_token": access_token})

    response = None
    try:
        file = urllib2.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(args), post_data)
    except urllib2.HTTPError, e:
        response = json.loads(e.read())
    except TypeError:
        pass

    if response == None:
        result = {'status': True, 'message': _('OK')}
    else:
        result = {'status': False, 'message': response['error']['message']}

    return result

def fb_albums(request):
    result = {}
    access_token = str(request.GET.get('accessToken'))
    check_sign_in = check_access_token(access_token)
    if check_sign_in['status']:
        graph = facebook.GraphAPI(access_token)
        try:
            result = graph.request('/me/albums')
        except Exception, error:
            result = error

    return render_to_response('networks/facebook/albums_list.html',
                                  {
                                      'result': result,
                                      'auth': check_sign_in
                                  }, context_instance=RequestContext(request))


def handling_results(images=[]):
    results = []
    for item in images:
        try:
            item_data = {
                'id': item.get('id'),
                'title': item.get('id'),
                'thumbnail_url': item.get('source'),
                'original_url': item.get('images')[0].get('source'),
                'link': item.get('link'),
                'description': item.get('name')
            }
            results.append(item_data)
        except Exception, error:
            pass

    return results

def fb_open_album(request, album_id=None):

    access_token = str(request.GET.get('accessToken'))
    check_sign_in = check_access_token(access_token)
    if check_sign_in['status']:
        graph = facebook.GraphAPI(access_token)
        try:
            result = graph.request('/%s/photos' % album_id)
        except Exception, error:
            result = []
    data = handling_results(result.get('data'))
    return render_to_response('networks/facebook/album_detail.html',
                              {
                                  'show_up_to': True,
                                  'result': data,
                                  'album_id': album_id,
                                  'auth': check_sign_in
                              }, context_instance=RequestContext(request))

@LoginRequired
def fb_get_photo_and_save_to_media(request, photo_id=None):
    image = None
    message = {
        'code': 0,
        'type': 'image',
        'message': _("Image hasn't been saved"),
    }

    access_token = str(request.GET.get('accessToken'))
    check_sign_in = check_access_token(access_token)
    if check_sign_in['status']:
        graph = facebook.GraphAPI(access_token)
        try:
            result = graph.get_object(photo_id)
            album = graph.get_object(request.GET.get('album_id'))
            image_args = {
                'title': photo_id,
                'url': result['images'][0]['source'],
                'description': ''
            }
            if 'name' in album:
                image_args['title'] = album['name']
            if 'description' in album:
                image_args['description'] = album['description']

            image = save_facebook_image(image_args, request.user)
            if image:
                message['code'] = 1
        except Exception, error:
            message['code'] = 0
            message['message'] = error.message

        if message.get('code') == 1:
            return render_to_response('collection/media/add_media_return.html',
                                      {
                                          'media_obj': image,
                                          'message': message,
                                          'auth': check_sign_in
                                      }, context_instance=RequestContext(request))
        else:
            return HttpResponse(json.dumps(message))
    else:
        return HttpResponse(json.dumps(check_sign_in))