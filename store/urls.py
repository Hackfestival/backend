from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('add_product/', views.add_product, name='add_product'),
    path('', views.product_list, name='product_list'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
]
