
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# Seller profile
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=200)
    contact_info = models.TextField()

    def __str__(self):
        return self.store_name

# Buyer profile
class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()

    def __str__(self):
        return self.user.username

# Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError('Not enough stock available')

    class Category(models.Model):
        name = models.CharField(max_length=200)
        description = models.TextField()

        def __str__(self):
            return self.name

    def __str__(self):
        return self.name

    # Reduce stock when a product is sold
    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError('Not enough stock available')
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(default=2,max_digits=10, decimal_places=2)
    #TOTAL PRICE DEFAULT=????????
    created_at = models.DateTimeField(default=timezone.now)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user has one cart
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'