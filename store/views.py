from crypt import methods
from datetime import datetime
from itertools import product

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, Product, Cart, CartItem, Farm, Order
from . import common


@csrf_exempt
def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        new_user = CustomUser.objects.create_user(username=username, password=password, email=email)

        user_authenticated = authenticate(request, email=email, password=password)

        if user_authenticated:
            login(request, user_authenticated)
            return JsonResponse({'status': 'success', 'user_id': new_user.user_id})

        return JsonResponse({'status': 'error'})
    elif request.method == 'GET':
        return render(request, 'store/register.html')
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        if not {'email', 'password'}.issubset(request.POST.keys()):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        email = request.POST['email']
        password = request.POST['password']

        user_authenticated = authenticate(request, email=email, password=password)

        if user_authenticated:
            login(request, user_authenticated)
            return JsonResponse({'status': 'success', 'user_id': user_authenticated.user_id})

        return JsonResponse({'status': 'error'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_product_add(request):
    if request.method == 'POST':
        farm = Farm.objects.get(farmer=request.user)

        if farm is None:
            return JsonResponse({'status': 'error', 'message': 'User is not a farmer'})

        if {'name', 'description', 'price', 'stock'}.issubset(request.POST.keys()):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']

        new_product = Product.objects.create(name=name, description=description, price=price, stock=stock, seller=farm)
        return JsonResponse({'status': 'success', 'product_id': new_product.product_id})

    return render(request, 'store/add_product.html')


@csrf_exempt
@login_required
def user_cart_list(request):
    _user = CustomUser.objects.get(email=request.user)
    user_cart, created = Cart.objects.get_or_create(user=_user)

    user_cart_items = user_cart.list_items()

    return JsonResponse({'status': 'success', 'products': list(user_cart_items.values())})


@csrf_exempt
@login_required
def farm_product_list(request):
    if request.method == 'POST':
        if 'farm_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        farm_id = request.POST['farm_id']
        farm = Farm.objects.get(farm_id=farm_id)

        if farm is None:
            return JsonResponse({'status': 'error', 'message': 'Farm not found'})

        return JsonResponse({'status': 'success', 'products': list(farm.get_products().values())})


@csrf_exempt
@login_required
def user_cart_add(request):
    if request.method == 'POST':
        if 'product_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        product_id = request.POST['product_id']

        selected_product = Product.objects.get(product_id=product_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=selected_product)

        if selected_product.stock > 0:
            if not selected_product.reduce_stock(1):
                return JsonResponse({'status': 'error', 'message': 'Product out of stock'})

            if created:
                cart_item.quantity = 1
            else:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})
        else:
            return render(request, 'store/out_of_stock.html')

    return render(request, 'store/add_to_cart.html')


@csrf_exempt
@login_required
def user_cart_remove(request):
    if request.method == 'POST':
        if 'product_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        product_id = request.POST['product_id']

        selected_product = Product.objects.get(product_id=product_id)

        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product=selected_product)

        if cart_item.quantity > 0:
            selected_product.stock += 1
            selected_product.save()

            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()

            return JsonResponse({'status': 'success', 'message': 'Product removed from cart'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Product not in cart'})

    return render(request, 'store/remove_from_cart.html')


@csrf_exempt
@login_required
def farm_list(request):
    farms = Farm.get_all_farms() # Fetch farms for the logged-in user
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'farms': list(farms.values())})

    return render(request, 'store/farm_list.html', {'farms': farms})


@csrf_exempt
@login_required
def user_farm_nearby(request):
    c_user = CustomUser.objects.get(email=request.user)

    user_location = c_user.get_location()

    farms = Farm.get_all_farms() # Fetch farms for the logged-in user

    filtered_farm_list = []

    for frm in farms:
        var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
        print(f"Distance wit {frm.name} : {var:.2f} km")

        if var < common.default_radius:
            print("added to list")
            filtered_farm_list.append(frm)

    return render(request, 'store/nearby_farm.html', {'farms': filtered_farm_list})

@csrf_exempt
@login_required
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()

        return JsonResponse({'status': 'success', 'products': list(products.values())})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def farm_detail(request):
    if request.method == 'POST':
        if 'farm_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        farm_id = request.POST['farm_id']
        farm = Farm.objects.get(farm_id=farm_id)

        if farm is None:
            return JsonResponse({'status': 'error', 'message': 'Farm not found'})

        return JsonResponse({'status': 'success', 'farm': farm.as_json()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_detail(request):
    if request.method == 'GET':
        user = CustomUser.objects.get(email=request.user)

        return JsonResponse({'status': 'success', 'user': user.as_json()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_update(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(email=request.user)

        if not {'username', 'email', 'password', 'first_name', 'last_name', 'latitude', 'longitude'}.issubset(request.POST.keys()):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.latitude = request.POST['latitude']
        user.longitude = request.POST['longitude']

        user.save()

        return JsonResponse({'status': 'success', 'user': user.as_json()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_delete(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(email=request.user)

        user.delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_cart_clear(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)

        cart.clear()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_cart_checkout(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)

        order_id = cart.checkout()

        return JsonResponse({'status': 'success', 'order_id': order_id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def user_order_list(request):
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user)

        return JsonResponse({'status': 'success', 'orders': list(orders.values())})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_product_remove(request):
    if request.method == 'POST':
        if 'product_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        product_id = request.POST['product_id']

        selected_product = Product.objects.get(product_id=product_id)

        selected_product.delete()

        return JsonResponse({'status': 'success', 'message': 'Product removed'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_product_update(request):
    if request.method == 'POST':
        if not {'product_id', 'name', 'description', 'price', 'stock'}.issubset(request.POST.keys()):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        product_id = request.POST['product_id']
        selected_product = Product.objects.get(product_id=product_id)

        selected_product.name = request.POST['name']
        selected_product.description = request.POST['description']
        selected_product.price = request.POST['price']
        selected_product.stock = request.POST['stock']

        selected_product.save()

        return JsonResponse({'status': 'success', 'message': 'Product updated'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_update(request):
    if request.method == 'POST':
        farm = Farm.objects.get(farmer=request.user)

        if not {'name', 'description', 'latitude', 'longitude'}.issubset(request.POST.keys()):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        farm.name = request.POST['name']
        farm.description = request.POST['description']
        farm.latitude = request.POST['latitude']
        farm.longitude = request.POST['longitude']

        farm.save()

        return JsonResponse({'status': 'success', 'farm': farm.as_json()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_delete(request):
    if request.method == 'POST':
        farm = Farm.objects.get(farmer=request.user)

        farm.delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_order_list(request):
    if request.method == 'GET':
        farm = Farm.objects.get(farmer=request.user)

        orders = Order.objects.filter(product__seller=farm)

        return JsonResponse({'status': 'success', 'orders': list(orders.values())})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_order_detail(request):
    if request.method == 'POST':
        if 'order_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        order_id = request.POST['order_id']
        order = Order.objects.get(order_id=order_id)

        return JsonResponse({'status': 'success', 'order': order.as_json()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
@login_required
def farm_order_deliver(request):
    if request.method == 'POST':
        if 'order_id' not in request.POST:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        user_ = CustomUser.objects.get(email=request.user)

        order_id = request.POST['order_id']
        order = Order.objects.get(order_id=order_id)

        new_delivery = order.deliver(delivery_address=user_.get_location(), delivery_time=datetime.now(), delivery_fee=0)

        return JsonResponse({'status': 'success', 'delivery_id': new_delivery.delivery_id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
