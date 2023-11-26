from rest_framework import serializers
from appauth.models import Funnel, FunnelTemplate, Page
from .user import TemplateOwner

class FunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funnel
        fields = ('id', 'name', 'owner', 'base', 'published', 'created', 'pages')

    id = serializers.UUIDField(source='uid')
    owner = serializers.SlugRelatedField(slug_field="uid", read_only=True)
    created = serializers.CharField(source='created_at')
    pages = serializers.IntegerField(source='count_pages')

class TemplateSerializer(FunnelSerializer):
    class Meta:
        model = FunnelTemplate
        fields = ('id', 'name', 'creator', 'base', 'published', 'created', 'category')

    id = serializers.UUIDField(source='uid')
    pages = serializers.IntegerField(source='count_pages')
    creator = TemplateOwner(source='owner')

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'owner', 'slug', 'published', 'created', 'is_index')

    id = serializers.UUIDField(source='uid')
    owner = serializers.SlugRelatedField(slug_field="uid", read_only=True)
    created = serializers.CharField(source='created_at')
