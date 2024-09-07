from django.contrib import admin
from .models import CustomUser, Farm, Product, Category, Order, OrderItem, Cart, CartItem, DeliveryOrder

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CustomUser)
admin.site.register(Farm)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(DeliveryOrder)
