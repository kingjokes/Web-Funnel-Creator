from django.urls import path
from . import views

urlpatterns = [
    path('products/save/', views.PrivateProductViewSet.as_view({'post': 'create'})),
    path('products/user-products/<str:pid>/', views.PrivateProductViewSet.as_view({'get': 'get_product'})),
    path('products/user-products/', views.PrivateProductViewSet.as_view({'get': 'user_products'})),
    path('products/delete/', views.PrivateProductViewSet.as_view({'post': 'delete_product'})),
    path('products/search-all/', views.PrivateProductViewSet.as_view({'get': 'search_product'})),
    path('products/search/<str:query>/', views.PrivateProductViewSet.as_view({'get': 'search_product'})),
    path('products/public/single/<str:slug>/', views.PublicProductViewSet.as_view({'get': 'single_product'})),
]