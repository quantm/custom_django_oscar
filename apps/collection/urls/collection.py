from django.conf.urls import *
from apps.collection.views.collection import *

urlpatterns = patterns('apps.collection.views.collection',

   url(r'^list/$', CollectionListView.as_view(), name='collections'),
   url(r'^get/(?P<set_id>\d+)/$', 'collection_get', name='collection_get'),
   url(r'^save/$', 'collection_save', name='collection_save'),
   url(r'^view/$', ViewCollection.as_view(), name='collection_view'),

   url(r'^design/$', CollectionDesign.as_view(), name='collection_design'),
   url(r'^save_comment/$', 'save_comment', name='save_comment'),

   #Add product to Collection in front-end
   url(r'add-product-to-collection-form/$', MyCollectionForm.as_view(), name='add_product_to_collection_form'),
   url(r'add-product-to-collection/$', 'add_product_to_collection', name='add_product_to_collection'),
   url(r'preview/(?P<collection_id>\d+)/$', MyCollectionPreview.as_view(), name='preview_collection_before_go_design_page'),
   url(r'^gallery-save/$', 'gallery_save_into_collection', name='gallery_save_into_collection'),

   #Share
   url(r'^share/$', 'save_share_collection', name='save_share_collection'),
   url(r'^invite/$', 'save_invite_edit_collection', name='save_invite_edit_collection'),
   url(r'^delete/$', 'delete_collection', name='delete_collection'),
   url(r'^comment/delete/$', 'delete_comment', name='delete_comment'),

   url(r'^my-collections/$', MyCollectionView.as_view(), name='my-collections'),
   url(r'^my-collections/(?P<user_id>\d+)/$', MyCollectionView.as_view(), name='my-collections-other-profile'),

)