from rest_framework import serializers
from appauth.models import Form

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ('id', 'name', 'ftype', 'owner')

    id = serializers.UUIDField(source='uid')
