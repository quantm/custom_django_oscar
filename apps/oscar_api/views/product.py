from rest_framework import generics
from rest_framework.response import Response
from oscar.apps.catalogue.models import Product
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from settings import PRODUCT_ITEM_PER_PAGE
from apps.oscar_api import serializers

class ProductList(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer
    paginate_by = PRODUCT_ITEM_PER_PAGE
    pagination_serializer_class = serializers.CustomPaginationSerializer

    def get_queryset(self):
        products = Product.browsable.base_queryset().filter(stockrecords__isnull=False).distinct()
        return products

class ProductDetail(generics.RetrieveAPIView):
    model = Product
    serializer_class = serializers.ProductSerializer

class ProductListOrderByBuyAllTime(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer
    paginate_by = PRODUCT_ITEM_PER_PAGE
    pagination_serializer_class = serializers.CustomPaginationSerializer
    template_name = 'catalogue/products/ajax_sort_by_buy_count.html'

    renderer_classes = (JSONRenderer, JSONPRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer,)

    def get_queryset(self):
        products = Product.browsable.base_queryset().filter(stockrecords__isnull=False).order_by('-buy_count_all_time').distinct()
        return products

class ProductListOrderByBuyInMonth(generics.ListAPIView):
    serializer_class = serializers.ProductSerializer
    paginate_by = PRODUCT_ITEM_PER_PAGE
    pagination_serializer_class = serializers.CustomPaginationSerializer
    template_name = 'catalogue/products/ajax_sort_by_buy_count.html'

    renderer_classes = (JSONRenderer, JSONPRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer,)

    def get_queryset(self):
        products = Product.browsable.base_queryset().filter(stockrecords__isnull=False).order_by('-buy_count_in_month').distinct()
        return products

