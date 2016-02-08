from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, JSONPRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from apps.oscar_api import serializers
from core.models import User
from apps.common.decorator import *

class UserList(generics.ListAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    serializer_class = serializers.UserSerializer
    model = User


class UserDetail(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all()
