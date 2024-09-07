from django.urls import path
from . import views

urlpatterns = [
    path('user/register', views.register, name='user_register'),
    path('user/add-product/', views.add_product, name='user_add-product'),
    path('user/cart/', views.product_list, name='user_cart'),
    path('user/add-to-cart/<int:product_id>/', views.add_to_cart, name='user_add-to-cart'),

    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('farm/<uuid:farm_id>/products/', views.farm_product_list, name='farm_product_list'),

]
