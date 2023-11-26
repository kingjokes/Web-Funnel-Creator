from rest_framework import serializers
from ecommerce.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 
            'name', 
            'desc', 
            'images', 
            'discount', 
            'price', 
            'discount_type', 
            'enable_discount', 
            'currency',
            'currency_display',
            'owner',
            'slug',
            'date'
        )

    id = serializers.UUIDField(source='uid')
    owner = serializers.CharField(source='get_owner')
    date = serializers.DateTimeField(source='created_at')

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'image', 'name', 'slug', 'date')

    id = serializers.UUIDField(source='uid')
    image = serializers.CharField(source='get_first_image')
    date = serializers.DateTimeField(source='created_at')

class ProductSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'id', 'slug')

    id = serializers.UUIDField(source='uid')