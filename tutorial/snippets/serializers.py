from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from rest_framework_extensions.serializers import (
    PartialUpdateSerializerMixin
)
from rest_framework_extensions.fields import ResourceUriField


class SnippetSerializer(PartialUpdateSerializerMixin, serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = ResourceUriField(view_name='snippet-highlight', read_only=True)
    # highlight = serializers.HyperlinkedIdentityField(
    #    view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner', 'title',
                  'code', 'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')


# class SnippetSerializer(serializers.ModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')

#     class Meta:
#         model = Snippet
#         fields = ('id', 'owner', 'title', 'code',
#                   'linenos', 'language', 'style')


# class UserSerializer(serializers.ModelSerializer):
#     snippets = SnippetSerializer(many=True)
#     # snippets = serializers.PrimaryKeyRelatedField(
#     #     many=True, queryset=Snippet.objects.all())

#     class Meta:
#         model = User
#         fields = ('id', 'username', 'snippets')
