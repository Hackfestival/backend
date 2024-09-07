from django.contrib import admin
from .models import Product, SellerProfile, BuyerProfile

admin.site.register(Product)
admin.site.register(SellerProfile)
admin.site.register(BuyerProfile)
