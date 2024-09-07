from . import common
from .models import Farm
from .models import OrderItem
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from django.contrib.auth import authenticate, login
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Product
from django.shortcuts import render


def home(request):
    return render(request, 'store/home.html')


@api_view(['POST'])
def register(request):
    if request.user.is_authenticated:
        return Response({'status': 'error', 'message': 'Already authenticated'}, status=400)

    data = request.data  # Parse incoming JSON data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type')  # 'buyer' or 'seller'

    if username and email and password:
        user = CustomUser.objects.create_user(username=username, password=password, email=email)
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return Response({'status': 'success'})
        else:
            return Response({'status': 'error', 'message': 'Authentication failed'}, status=400)
    return Response({'status': 'error', 'message': 'Invalid data'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is logged in
def add_product(request):
    data = request.data  # Parse incoming JSON data
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')

    if not name or not description or not price or not stock:
        return Response({'status': 'error', 'message': 'Invalid data'}, status=400)

    # Assume seller is the logged-in user (or use a seller profile model)
    seller = request.user
    Product.objects.create(name=name, description=description, price=price, stock=stock, seller=seller)

    return Response({'status': 'success', 'message': 'Product added successfully'})


# def add_product(request):
#     data = request.data  # Parse incoming JSON data
#     name = data.get('name')
#     description = data.get('description')
#     price = data.get('price')
#     stock = data.get('stock')
#
#     if not name or not description or not price or not stock:
#         return Response({'status': 'error', 'message': 'Invalid data'}, status=400)
#
#     # Assume seller is the logged-in user (or use a seller profile model)
#     seller = request.user
#     Product.objects.create(name=name, description=description, price=price, stock=stock, seller=seller)
#
#     return Response({'status': 'success', 'message': 'Product added successfully'})


# def register(request):
#     if request.user.is_authenticated:
#         return redirect('home')
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         user_type = request.POST['user_type']  # buyer or seller
#         user = CustomUser.objects.create_user(username=username, password=password, email = email)
#
#         u = authenticate(request, email=email, password=password)
#
#         if u:
#             login(request, u)
#             return JsonResponse({'status': 'success'})
#
#         return JsonResponse({'status': 'error'})
#
#     return render(request, 'store/register.html')

# def add_product(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#
#     if request.method == 'POST':
#         name = request.POST['name']
#         description = request.POST['description']
#         price = request.POST['price']
#         stock = request.POST['stock']
#         #seller = SellerProfile.objects.get(user=request.user)
#         Product.objects.create(name=name, description=description, price=price, stock=stock, seller=seller)
#         return redirect('seller_dashboard')

# return render(request, 'store/add_product.html')


@api_view(['GET'])
def product_list(request):
    products = Product.objects.all().values('id', 'name', 'description', 'price', 'stock')
    return Response(list(products))  # Convert QuerySet to a list of dictionaries


# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'store/product_list.html', {'products': products})

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#
#     if product.stock > 0:
#         cart_item.quantity += 1
#         cart_item.save()
#         product.reduce_stock(1)  # Reduce stock when added to cart
#         return redirect('cart_detail')
#     else:
#         return render(request, 'store/out_of_stock.html')


@api_view(['POST'])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if product.stock > 0:
        cart_item.quantity += 1
        cart_item.save()
        product.reduce_stock(1)  # Assuming a method on the product to reduce stock
        return Response({'status': 'success', 'message': 'Item added to cart'})
    else:
        return Response({'status': 'error', 'message': 'Product is out of stock'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is logged in
def seller_dashboard(request):
    # Assuming seller is the logged-in user
    seller = request.user
    orders = OrderItem.objects.filter(product__seller=seller).values('id', 'product__name', 'quantity', 'order__status')

    # Convert QuerySet to a list of dictionaries
    return Response({'orders': list(orders)})


# def seller_dashboard(request):
#     # seller = SellerProfile.objects.get(user=request.user)
#     # Get all the order items that contain the seller's products
#     orders = OrderItem.objects.filter(product__seller=seller)
#     return render(request, 'store/seller_dashboard.html', {'orders': orders})


#######################
######## Location filters
########################


@api_view(['GET'])
def farm_list(request):
    farms = Farm.get_all_farms().values('id', 'name', 'location', 'latitude', 'longitude')

    # Return the farm list as JSON
    return Response({'farms': list(farms)})


# def farm_list(request):
#     farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
#     print(f"Farm: {farms}")
#     return render(request, 'store/farm_list.html', {'farms': farms})


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is logged in
def get_list_of_nearby_farms(request):
    c_user = CustomUser.objects.get(email=request.user.email)
    user_location = c_user.get_location()  # Assume this returns a tuple of (latitude, longitude)

    farms = Farm.get_all_farms().values('id', 'name', 'latitude', 'longitude')
    filtered_farm_list = []

    for farm in farms:
        distance = common.haversine(farm['latitude'], farm['longitude'], user_location[0], user_location[1])
        print(f"Distance with {farm['name']} : {distance:.2f} km")

        if distance < common.default_radius:
            filtered_farm_list.append(farm)

    return Response({'nearby_farms': filtered_farm_list})

# def get_list_of_nearby_farms(request):
#     c_user = CustomUser.objects.get(email=request.user)
#
#     user_location = c_user.get_location()
#
#     farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
#
#     filtered_farm_list = []
#
#     for frm in farms:
#         var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
#         print(f"Distance wit {frm.name} : {var:.2f} km")
#
#         if (var < common.default_radius):
#             filtered_farm_list.append(frm)
#
#     return render(request, 'store/nearby_farm.html', {'farms': filtered_farm_list})
