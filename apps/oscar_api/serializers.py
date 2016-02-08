from apps.catalogue.models import Product
from apps.social.models import *
from rest_framework import serializers
from rest_framework import pagination
from core.models import User

class CustomPaginationSerializer(pagination.BasePaginationSerializer):
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')
    total_page = serializers.Field(source="paginator.num_pages")
    total_results = serializers.Field(source='paginator.count')

class ProductSerializer(serializers.ModelSerializer):
    price = serializers.Field(source='get_price')
    product_class = serializers.Field(source='get_product_class')
    product_url = serializers.Field(source='get_absolute_url')
    product_original_img = serializers.Field(source='get_original_img_url')
    product_thumb_img = serializers.Field(source='get_thumb_img_url')
    is_available_to_buy = serializers.Field(source='is_available_to_buy')

    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'description', 'date_created', 'date_updated', 'rating', 'buy_count_all_time', 'buy_count_in_month', 'product_class', 'product_url', 'product_original_img', 'product_thumb_img', 'is_available_to_buy')

    def to_native(self, product_obj):
        ret = super(ProductSerializer, self).to_native(product_obj)
        request = self.context['request']
        ret['is_authenticated'] = False
        if request.user.is_authenticated:
            ret['is_authenticated'] = True
        return ret


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')


class FriendShipListSerializer(serializers.ModelSerializer):
    user_obj = serializers.Field(source='to_json_obj')

    class Meta:
        model = SocialFriendShip
        fields = ('id', 'user_self', 'user_obj', 'type')


class FollowerListSerializer(serializers.ModelSerializer):
    user_self = serializers.Field(source='to_json_self')

    class Meta:
        model = SocialFriendShip
        fields = ('id', 'user_self', 'user_obj', 'type')



