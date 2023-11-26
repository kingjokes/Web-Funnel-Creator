from math import prod
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied

from .serializers import ProductSerializer, ProductListSerializer, ProductSearchSerializer
from .models import Product

import uuid

class PrivateProductViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer

    def create(self, request: Request) -> Response:
        data = request.data
        uid = data.get('id')

        if uid in ['undefined', None]:
            data['uid'] = uuid.uuid4()

        else:
            data['uid'] = uid

        data['owner'] = request.user
        if data.get('id'):
          del data['id']

        obj, created = Product.objects.update_or_create(defaults=data, uid=uid, owner=request.user)
        print('created ', created)

        return Response(obj.uid)

    def get_product(self, request, pid):
        
        try:
            # we'll check if param is a valid uuid
            # if it's not, then we'll fetch the product using slug field
            try:
                uuid.UUID(pid)
                product = Product.objects.get(uid=pid)

            except ValueError:
                product = Product.objects.get(slug=pid)

            if request.user == product.owner:
                serializer = ProductSerializer(product)
                return Response(serializer.data)

        except Product.DoesNotExist:
            raise NotFound

    def user_products(self, request):
        products = Product.objects.filter(owner=request.user)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    def delete_product(self, request):
        uid = request.data.get('id')
        
        try:
            product = Product.objects.get(uid=uid)
            if product.owner == request.user:
                product.delete()
                return Response(True)

            else:
                raise PermissionDenied

        except Product.DoesNotExist:
            raise NotFound

    def search_product(self, request, query=''):
        products = Product.objects.filter(owner = request.user)

        if query != '':
            products = products.filter(name__icontains=query)

        data = ProductSearchSerializer(products, many=True)

        return Response(data.data)

class PublicProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def single_product(self, request, slug):
        try:
            product = Product.objects.get(slug = slug)
            data = ProductSerializer(product)

            return Response(data.data)

        except Product.DoesNotExist:
            raise NotFound(detail="Product with slug: '"+slug+"' does not exist.")
