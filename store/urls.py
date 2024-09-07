from django.urls import path
from . import views

urlpatterns = [
    path('user/register', views.register, name='user_register'),
    path('user/add-product/', views.add_product, name='user_add-product'),
    path('user/cart/', views.product_list, name='user_cart'),
    path('user/add-to-cart/<int:product_id>/', views.add_to_cart, name='user_add-to-cart'),

    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),

    path('location/', views.location_list, name='location_list'),  # List all locations
    path('location/create/', views.create_location, name='create_location'),  # Create a new location
    path('location/edit/<int:pk>/', views.update_location, name='update_location'),  # Update a location
    path('location/delete/<int:pk>/', views.delete_location, name='delete_location'),  # Delete a location
]
