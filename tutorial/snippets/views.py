from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
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


class UserViewSet(viewsets.ModelViewSet):
    throttle_scope = 'sustained'  # sustained defined in settings.py
    #queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return User.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

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

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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
