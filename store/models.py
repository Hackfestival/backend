import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change the related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change the related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_orders(self):
        return Order.objects.filter(user=self)
    
    def get_location(self):
        return self.latitude, self.longitude

    def as_json(self):
        return dict(
            user_id=self.user_id,
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            is_active=self.is_active,
            is_staff=self.is_staff,
            date_joined=self.date_joined,
            latitude=self.latitude,
            longitude=self.longitude
        )

    def __str__(self):
        return self.email


class Farm(models.Model):
    farm_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def get_location(self):
        return self.latitude, self.longitude

    @staticmethod
    def get_all_location():
        return list(Farm.objects.values_list('name', 'description','latitude', 'longitude'))
    
    @staticmethod
    def get_all_farms():
        return Farm.objects.all()

    def get_all_categories(self):
        return Category.objects.filter(product__seller=self).distinct()

    def get_products(self):
        return Product.objects.filter(seller=self)

    def as_json(self):
        return dict(
            farm_id=self.farm_id,
            farmer=self.farmer.email,
            name=self.name,
            description=self.description,
            latitude=self.latitude,
            longitude=self.longitude
        )

    def __str__(self):
        return self.name


class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(Farm, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()

            return True
        else:
            return False


class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def deliver(self, delivery_address, delivery_time, delivery_fee):
        return DeliveryOrder.objects.create(order=self, delivery_address=delivery_address, delivery_time=delivery_time, delivery_fee=delivery_fee)

    def as_json(self):
        return dict(
            order_id=self.order_id,
            user=self.user.email,
            created_at=self.created_at,
            delivered=DeliveryOrder.objects.filter(order=self).exists(),
            items=[item.as_json() for item in self.orderitem_set.all()]
        )


class OrderItem(models.Model):
    order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, default='kg')
    price = models.DecimalField(max_digits=10, decimal_places=2)


class DeliveryOrder(models.Model):
    delivery_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    delivery_time = models.DateTimeField()
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)


class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Each user has one cart
    created_at = models.DateTimeField(auto_now_add=True)

    def list_items(self):
        return self.cartitem_set.all()

    def checkout(self):
        new_order = Order.objects.create(user=self.user)

        for item in self.list_items():
            OrderItem.objects.create(order=new_order, product=item.product, quantity=item.quantity, unit=item.unit, price=item.product.price)

        self.list_items().delete()

        return new_order.order_id

    def __str__(self):
        return f'Cart of {self.user.username}'


class CartItem(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=10, default='kg')

    def __str__(self):
        return f'{self.quantity} {self.unit} x {self.product.name}'