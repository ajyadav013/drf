from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import datetime
from django.core.cache import cache
from django.utils.encoding import force_text


from rest_framework import (renderers, viewsets, generics, permissions)
from rest_framework.decorators import (
    api_view, detail_route, parser_classes, throttle_classes, permission_classes, authentication_classes)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser
from rest_framework.throttling import (UserRateThrottle)
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.key_constructor.constructors import (
    DefaultKeyConstructor)
from rest_framework_extensions.key_constructor.bits import (
    KeyBitBase,
    RetrieveSqlQueryKeyBit,
    ListSqlQueryKeyBit,
    PaginationKeyBit
)

from snippets.models import Snippet
from snippets.serializers import (SnippetSerializer, UserSerializer)
from snippets.permissions import IsOwnerOrReadOnly


@api_view(['GET'])
@parser_classes((JSONParser,))
@throttle_classes([UserRateThrottle])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, BasicAuthentication))
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })


class UpdatedAtKeyBit(KeyBitBase):

    def get_data(self, **kwargs):
        key = 'api_updated_at_timestamp'
        value = cache.get(key, None)
        if not value:
            value = datetime.datetime.utcnow()
            cache.set(key, value=value)
        return force_text(value)


# default key bit constructor 3 cheez leke (unique_method_id, format, language) ek dictionary banata hai fir uska md5 checksum karta hai aur woh return karta hai jo store hota hai cache me
# yeh apna custom keybit constructor hai
# idhar hum usko 3 values se karre(retrieve_sql, updated_at)
# updated at value upar calculate hoti hai

# working:
# ab jab bhi list ya retrieve call hota hai tab apna custom constructor call hoga, fir usme ki values(list k liye list_sql, pagination, updated_at aur retrieve k liye retrieve_sql, updated_at) fetch hogi
# ab apna updated_at wala call hoga jo cache me se key dekhega aur agar nai hoga toh naya banayega datetime leke aur fir woh as a string return kar dega
# fir apna custom cnstructor ne jo default ko inherit kiya hai, usse yeh values pass karega jo md5 checksum banake dega
# ab fetch karte time agar backend me stored value match karega yeh
# checksum se means data change nai hua hai, aur bina sql query mare data
# return karega, aur agar dono checksum alag rahe(jab post ya update ya
# delete action karte hai tab naya value store ho jata hai jo models.py me
# likha hai implementation -> post ya delete action k signal pe naya cache
# set karna)
# And that's it. When any model changes then value in cache by key
# api_updated_at_timestamp will be changed too. After this every key
# constructor, that used UpdatedAtKeyBit, will construct new keys and
# @cache_response decorator will cache data in new places.


class CustomObjectKeyConstructor(DefaultKeyConstructor):
    retrieve_sql = RetrieveSqlQueryKeyBit()
    updated_at = UpdatedAtKeyBit()


class CustomListKeyConstructor(DefaultKeyConstructor):
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = UpdatedAtKeyBit()

    print("List SQL", list_sql)
    print("pagination", pagination)
    print("updated_at", updated_at)


class UserViewSet(viewsets.ModelViewSet):
    throttle_scope = 'sustained'  # sustained defined in settings.py
    #queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return User.objects.all()

    @cache_response(key_func=CustomListKeyConstructor())
    def list(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @cache_response(key_func=CustomObjectKeyConstructor())
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)


class SnippetViewSet(viewsets.ModelViewSet):
    #queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    parser_classes = (JSONParser, )
    # or ur custom throttle class which accepts (self, request, view) and
    # returns a boolean value
    throttle_classes = (UserRateThrottle,)
    #throttle_scope = 'burst'

    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        return Snippet.objects.all()

    @cache_response(key_func=CustomListKeyConstructor())
    def list(self, request):
        queryset = self.get_queryset()
        serializer = SnippetSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def get(self, request, format=None):
    #     print("get------------", request)
    #     content = {
    #         # `django.contrib.auth.User` instance.
    #         'user': unicode(request.user),
    #         'auth': unicode(request.auth),  # None
    #     }
    #     return Response(content)
    # def get_object(self):
    #     print(
    #         "------------------------------------------------------------------------------")
    #     obj = get_object_or_404(Snippet.objects.all())
    #     self.check_object_permissions(self.request, obj)
    #     return obj

        #----------------------------------------------------------------------
        # class SnippetHighlight(generics.GenericAPIView):
        #     queryset = Snippet.objects.all()
        #     renderer_classes = (renderers.StaticHTMLRenderer, )

        #     def get(self, request, *args, **kwargs):
        #         snippet = self.get_object()
        #         return Response(snippet.highlighted)

        # class SnippetList(generics.ListCreateAPIView):
        #     permission_classes = (IsOwnerOrReadOnly, )
        #     queryset = Snippet.objects.all()
        #     serializer_class = SnippetSerializer

        #     def perform_create(self, serializer):
        #         serializer.save(owner=self.request.user)

        # class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
        #     queryset = Snippet.objects.all()
        #     serializer_class = SnippetSerializer

        # class UserList(generics.ListAPIView):
        #     queryset = User.objects.all()
        #     serializer_class = UserSerializer

        # class UserDetail(generics.RetrieveAPIView):
        #     queryset = User.objects.all()
        #     serializer_class = UserSerializer

        #----------------------------------------------------------------------

        # from django.shortcuts import render

        # from django.views.decorators.csrf import csrf_exempt
        # from rest_framework.views import APIView
        # from rest_framework.response import Response
        # from rest_framework import (mixins, generics)
        # from snippets.models import Snippet
        # from snippets.serializers import SnippetSerializer

        # #@csrf_exempt

        # class SnippetList(APIView):
        #     """
        #     List all code snippets, or create a new snippet.
        #     """

        #     def get(self, request, format=None):
        #         snippets = Snippet.objects.all()
        #         serializer = SnippetSerializer(snippets, many=True)
        #         return Response(serializer.data)

        #     def post(self, request, format=None):
        #         serializer = SnippetSerializer(data=request.data)
        #         if serializer.is_valid():
        #             serializer.save()
        #             return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors,
        # status=status.HTTP_400_BAD_REQUEST)

        # class SnippetDetail(APIView):

        #     def get_object(self, pk):
        #         try:
        #             snippet = Snippet.objects.get(pk=pk)
        #         except Snippet.DoesNotExist:
        #             return Response(sattus=status.HTTP_404_NOT_FOUND)

        #     def get(self, request, pk, format=None):
        #         snippet = self.get_object(pk)
        #         serializer = SnippetSerializer(snippet)
        #         return Response(serializer.data)

        #     def put(self, request, pk, format=None):
        #         #data = JSONParser().parse(request)
        #         snippet = self.get_object(pk)
        #         serializer = SnippetSerializer(snippet, data=request.data)
        #         if(serializer.is_valid()):
        #             serializer.save()
        #             return Response(serializer.data)
        # return Response(serializer.errors,
        # status=status.HTTP_400_BAD_REQUEST)

        #     def delete(self):
        #         snippet = self.get_object(pk)
        #         snippet.delete()
        #         return Response(status=status.HTTP_204_NO_CONTENT)

        #----------------------------------------------------------------------

        # from snippets.models import Snippet
        # from snippets.serializers import SnippetSerializer
        # from rest_framework import mixins
        # from rest_framework import generics

        # class SnippetList(mixins.ListModelMixin,
        #                   mixins.CreateModelMixin,
        #                   generics.GenericAPIView):
        #     queryset = Snippet.objects.all()
        #     serializer_class = SnippetSerializer

        #     def get(self, request, *args, **kwargs):
        #         return self.list(request, *args, **kwargs)

        #     def post(self, request, *args, **kwargs):
        #         return self.create(request, *args, **kwargs)

        # class SnippetDetail(mixins.RetrieveModelMixin,
        #                     mixins.DestroyModelMixin,
        #                     mixins.UpdateModelMixin,
        #                     generics.GenericAPIView):

        #     queryset = Snippet.objects.all()
        #     serializer_class = SnippetSerializer

        #     def get(self, request, *args, **kwargs):
        #         return self.retrieve(request, *args, **kwargs)

        #     def delete(self, request, *args, **kwargs):
        #         return self.destroy(request, *args, **kwargs)

        #     def put(self, request, *args, **kwargs):
        #         return self.destroy(request, *args, **kwargs)

        #----------------------------------------------------------------------
