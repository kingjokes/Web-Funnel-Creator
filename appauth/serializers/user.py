from rest_framework import serializers
from appauth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'dp', 'role')

    id = serializers.UUIDField(source='uid')

class TemplateOwner(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')

    id = serializers.UUIDField(source='uid')
    name = serializers.CharField(source='get_name')