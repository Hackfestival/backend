from django.contrib import admin
from .models import CustomUser, Farm, Product, Category, Order, OrderItem, Cart, CartItem, DeliveryOrder

admin.site.register([CustomUser, Farm, Product, Category, Order, OrderItem, Cart, CartItem, DeliveryOrder])