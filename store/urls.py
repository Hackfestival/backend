from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('user/register', views.user_register, name='user_register'),
    path('user/login', views.user_login, name='user_login'),

    path('user/detail', views.user_detail, name='user_detail'),
    path('user/update', views.user_update, name='user_update'),
    path('user/delete', views.user_delete, name='user_delete'),

    path('user/cart/display', views.user_cart_list, name='user_cart_list'),
    #path('user/cart/list', views.user_cart_list, name='user_cart_list'),
    path('user/cart/add', views.user_cart_add, name='user_cart_add'),
    path('user/cart/remove', views.user_cart_remove, name='user_cart_remove'),
    path('user/cart/clear', views.user_cart_clear, name='user_cart_clear'),
    path('user/cart/checkout', views.user_cart_checkout, name='user_cart_checkout'),
    path('user/order/list', views.user_order_list, name='user_order_list'),
    path('user/cart/payment',views.user_cart_payment,name='user_cart_payment'),
    path('user/farm/nearby', views.user_farm_nearby, name='user_farm_nearby'),

    path('farm/list', views.farm_list, name='farm_list'),
    path('farm/<uuid:farm_uuid>/', views.farm_detail_view, name='farm_detail'),
    path('farm/<uuid:farm_id>/', views.farm_detail, name='farm_detail'),

    path('farm/detail', views.farm_detail, name='farm_detail'),
    path('farm/<uuid:farm_id>', views.farm_page, name='farm_page'),
    path('farm/update', views.farm_update, name='farm_update'),
    path('farm/delete', views.farm_delete, name='farm_delete'),

    path('farm/product/list', views.farm_product_list, name='farm_product_list'),
    path('farm/product/add', views.farm_product_add, name='farm_product_add'),
    path('farm/product/remove', views.farm_product_remove, name='farm_product_remove'),
    path('farm/product/update', views.farm_product_update, name='farm_product_update'),

    path('farm/order/list', views.farm_order_list, name='farm_order_list'),
    path('farm/order/detail', views.farm_order_detail, name='farm_order_detail'),
    path('farm/order/deliver', views.farm_order_deliver, name='farm_order_deliver'),


    path('product/list', views.product_list, name='product_list'),
]
