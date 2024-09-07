# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('user/register', views.register, name='user_register'),
#     path('user/add-product/', views.add_product, name='user_add-product'),
#     path('user/cart/', views.product_list, name='user_cart'),
#     path('user/add-to-cart/<int:product_id>/', views.add_to_cart, name='user_add-to-cart'),
#
#     path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
#
#     path('farms/', views.farm_list, name='farm_list'),  # List farms
#     path('farms/nearby', views.get_list_of_nearby_farms, name='get_list_of_nearby_farms')
# ]
from django.urls import path
from . import views
#from templates import store

urlpatterns = [
    # User registration and product management
    path('api/user/register/', views.register, name='user_register'),
    path('api/user/add-product/', views.add_product, name='user_add_product'),
    path('api/user/cart/', views.product_list, name='user_cart'),
    path('api/user/add-to-cart/<int:product_id>/', views.add_to_cart, name='user_add_to_cart'),

    # Seller dashboard
    path('api/seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),

    # Farm-related endpoints
    path('api/farms/', views.farm_list, name='farm_list'),  # List all farms
    path('api/farms/nearby/', views.get_list_of_nearby_farms, name='get_nearby_farms')
]
