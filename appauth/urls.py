from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', views.UserView.as_view({'get': 'auth_user'}), name='auth_user'),
    path('auth/user/delete-item/', views.UserView.as_view({'post': 'delete_item'})),
    path('auth/user/dashboard/', views.UserView.as_view({'get': 'dashboard'})),

    # funnels
    path('funnels/create/', views.FunnelView.as_view({'post': 'create'})),
    path('funnels/publish-item/', views.FunnelView.as_view({'post': 'publish'})),
    path('funnels/users-funnels/<str:funnel_type>/', views.FunnelView.as_view({'get': 'get_user_funnels'})),
    path('funnels/get-pages/<str:funnel_type>/<str:funnel_id>/', views.FunnelView.as_view({'get': 'get_pages'})),
    path('funnels/get-index/<str:funnel_type>/<str:funnel_id>/', views.FunnelView.as_view({'get': 'get_index_page'})),
    path('funnels/get-funnel/<str:funnel_type>/<str:funnel_id>/', views.FunnelView.as_view({'get': 'get_funnel'})),
    path('funnels/set-index/', views.FunnelView.as_view({'post': 'set_index_page'})),
    path('funnels/create-page/', views.FunnelView.as_view({'post': 'create_page'})),
    path('funnels/load-page-data/<str:funnel_type>/<str:funnel_id>/<str:page_slug>/', views.FunnelView.as_view({'get': 'load_page_data'})),
    path('funnels/load-editor-data/<str:funnel_type>/<str:funnel_id>/', views.FunnelView.as_view({'get': 'load_editor_data'})),
    path('funnels/save-editor-data/', views.FunnelView.as_view({'post': 'save_editor_data'})),
    path('funnels/public-view/show/', views.PublicView.as_view({'get': 'get_public_item'})),
    path('funnels/public-view/load-templates/<str:cat>/', views.PublicView.as_view({'get': 'get_templates'})),
    path('funnels/public-view/get-index/<str:funnel_type>/<str:funnel_id>/', views.PublicView.as_view({'get': 'get_index'})),

    # form
    path('form/create/', views.FormView.as_view({'post': 'create'})),
    path('form/user-forms/', views.FormView.as_view({'get': 'get_user_forms'})),
]