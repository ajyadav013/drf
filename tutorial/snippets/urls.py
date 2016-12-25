from django.conf.urls import (url, include)
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter
from snippets.views import (SnippetViewSet,  UserViewSet, api_root)

snippet_list = SnippetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

snippet_detail = SnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

snippet_highlight = SnippetViewSet.as_view({
    'get': 'highlight'
})

user_list = UserViewSet.as_view({
    'get': 'list'
})


user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})


router = SimpleRouter()
router.register(r'snippets', SnippetViewSet, base_name="snippet")
router.register(r'users', UserViewSet, base_name="user")

urlpatterns = format_suffix_patterns([
    url(r'^$', api_root),
    #url(r'^snippets/$', snippet_list, name='snippet-list'),
    #url(r'^snippets/(?P<pk>[0-9]+)/$', snippet_detail, name='snippet-detail'),
    # url(r'^snippets/(?P<pk>[0-9]+)/highlight/$',
    #    snippet_highlight, name='snippet-highlight'),
    #url(r'^users/$', UserList.as_view(), name='user-list'),
    #url(r'^users/(?P<pk>[0-9]+)/$', UserDetail.as_view())
    #url(r'^users/$', user_list, name='user-list'),
    #url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail')
])

urlpatterns += router.urls
