from datetime import datetime
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, Product, Cart, CartItem, Farm, Order
from .forms import UserRegistrationForm, UserLoginForm, ProductForm, UserCartAddForm, UserUpdateForm, FarmUpdateForm
from . import common


@csrf_exempt
@require_http_methods(['GET'])
def home(request):
    if not request.user.is_authenticated:
        return render(request, 'store/index.html')
    else:
        user_ = CustomUser.objects.get(email=request.user)
        return render(request, 'store/home.html', {'user': user_, 'farms': Farm.get_all_farms()})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        new_user = None

        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            user_authenticated = authenticate(request, email=new_user.email, password=form.cleaned_data['password'])
            if user_authenticated:
                login(request, user_authenticated)
                return redirect('home')
            return JsonResponse({'status': 'error', 'message': 'Authentication failed'})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    return render(request, 'store/user_register.html', {'form': UserRegistrationForm()})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user_authenticated = authenticate(request, email=email, password=password)

            if user_authenticated:
                login(request, user_authenticated)
                return JsonResponse({'status': 'success', 'user_id': user_authenticated.user_id})

            return JsonResponse({'status': 'error', 'message': 'Authentication failed'})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    form = UserLoginForm()
    return render(request, 'store/user_login.html', {'form': form})


# store/views.py
@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def farm_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            farm = Farm.objects.get(farmer=request.user)
            if farm is None:
                return JsonResponse({'status': 'error', 'message': 'User is not a farmer'})

            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            stock = form.cleaned_data['stock']

            new_product = Product.objects.create(name=name, description=description, price=price, stock=stock, seller=farm)
            return JsonResponse({'status': 'success', 'product_id': new_product.product_id})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def user_cart_list(request):
    _user = CustomUser.objects.get(email=request.user)
    user_cart, created = Cart.objects.get_or_create(user=_user)

    user_cart_items = user_cart.list_items()

    return JsonResponse({'status': 'success', 'products': list(user_cart_items.values())})


@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def farm_product_list(request):
    if 'farm_id' not in request.POST:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    farm_id = request.POST['farm_id']
    farm = Farm.objects.get(farm_id=farm_id)

    if farm is None:
        return JsonResponse({'status': 'error', 'message': 'Farm not found'})

    return JsonResponse({'status': 'success', 'products': list(farm.get_products().values())})


# store/views.py
@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def user_cart_add(request):
    if request.method == 'POST':
        form = UserCartAddForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']

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
                return JsonResponse({'status': 'error', 'message': 'Product out of stock'})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    form = UserCartAddForm()
    return render(request, 'store/user_cart_add.html', {'form': form})


# store/views.py
@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
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

    return render(request, 'store/user_cart_remove.html')


@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def farm_list(request):
    farms = Farm.get_all_farms() # Fetch farms for the logged-in user
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'farms': list(farms.values())})

    return render(request, 'store/farm_list.html', {'farms': farms})


@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def user_farm_nearby(request):
    c_user = CustomUser.objects.get(email=request.user)
    user_location = c_user.get_location()
    farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
    filtered_farm_list = []

    for frm in farms:
        var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
        if var < common.default_radius:
            filtered_farm_list.append(frm)

    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'farms': [farm.as_json() for farm in filtered_farm_list]})

    return render(request, 'store/nearby_farm.html', {'farms': filtered_farm_list})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()

        return JsonResponse({'status': 'success', 'products': list(products.values())})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def farm_detail(request):
    if 'farm_id' not in request.POST:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    farm_id = request.POST['farm_id']
    farm = Farm.objects.get(farm_id=farm_id)

    if farm is None:
        return JsonResponse({'status': 'error', 'message': 'Farm not found'})

    return JsonResponse({'status': 'success', 'farm': farm.as_json()})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def user_detail(request):
    try:
        user = CustomUser.objects.get(email=request.user.email)
        return JsonResponse({'status': 'success', 'user': user.as_json()})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})


@csrf_exempt
@login_required
@require_http_methods(['GET', 'PUT'])
def user_update(request):
    user = CustomUser.objects.get(email=request.user)

    if request.method == 'PUT':
        form = UserUpdateForm(request.PUT)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.latitude = form.cleaned_data['latitude']
            user.longitude = form.cleaned_data['longitude']
            user.set_password(form.cleaned_data['password'])
            user.save()
            return JsonResponse({'status': 'success', 'user': user.as_json()})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    form = UserUpdateForm(initial={
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'latitude': user.latitude,
        'longitude': user.longitude
    })
    return render(request, 'store/user_update.html', {'form': form})


@csrf_exempt
@login_required
@require_http_methods(['DELETE'])
def user_delete(request):
    CustomUser.objects.get(email=request.user).delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@login_required
@require_http_methods(['DELETE'])
def user_cart_clear(request):
    Cart.objects.get(user=request.user).clear()
    return JsonResponse({'status': 'success'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def user_cart_checkout(request):
    cart = Cart.objects.get(user=request.user)

    order_id = cart.checkout()

    return JsonResponse({'status': 'success', 'order_id': order_id})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def user_order_list(request):
    orders = Order.objects.filter(user=request.user)

    return JsonResponse({'status': 'success', 'orders': list(orders.values())})


@csrf_exempt
@login_required
@require_http_methods(['DELETE'])
def farm_product_remove(request):
    if 'product_id' not in request.DELETE:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    product_id = request.DELETE['product_id']

    Product.objects.get(product_id=product_id).delete()

    return JsonResponse({'status': 'success', 'message': 'Product removed'})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def farm_product_update(request):
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


@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def farm_update(request):
    farm = Farm.objects.get(farmer=request.user)

    if request.method == 'POST':
        form = FarmUpdateForm(request.POST)
        if form.is_valid():
            farm.name = form.cleaned_data['name']
            farm.description = form.cleaned_data['description']
            farm.latitude = form.cleaned_data['latitude']
            farm.longitude = form.cleaned_data['longitude']
            farm.save()
            return JsonResponse({'status': 'success', 'farm': farm.as_json()})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    form = FarmUpdateForm(initial={
        'name': farm.name,
        'description': farm.description,
        'latitude': farm.latitude,
        'longitude': farm.longitude
    })
    return render(request, 'store/farm_update.html', {'form': form})


@csrf_exempt
@login_required
@require_http_methods(['DELETE'])
def farm_delete(request):
    try:
        Farm.objects.get(farmer=request.user).delete()
        return JsonResponse({'status': 'success'})
    except Farm.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Farm not found'})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def farm_order_list(request):
    farm = Farm.objects.get(farmer=request.user)

    orders = Order.objects.filter(product__seller=farm)

    return JsonResponse({'status': 'success', 'orders': list(orders.values())})


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def farm_order_detail(request):
    if 'order_id' not in request.GET:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    order_id = request.POST['order_id']
    order = Order.objects.get(order_id=order_id)

    return JsonResponse({'status': 'success', 'order': order.as_json()})


@csrf_exempt
@login_required
@require_http_methods(['POST'])
def farm_order_deliver(request):
    if 'order_id' not in request.POST:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    user_ = CustomUser.objects.get(email=request.user)

    order_id = request.POST['order_id']
    order = Order.objects.get(order_id=order_id)

    new_delivery = order.deliver(delivery_address=user_.get_location(), delivery_time=datetime.now(), delivery_fee=0)

    return JsonResponse({'status': 'success', 'delivery_id': new_delivery.delivery_id})

def home_view(request):
    c_user = CustomUser.objects.get(email=request.user)
    user_location = c_user.get_location()
    farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
    filtered_farm_list = []

    for frm in farms:
        var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
        if var < common.default_radius:
            filtered_farm_list.append(frm)

    context = {
        'filtered_farm_list': filtered_farm_list
    }

    return render(request, 'store/home_map.html', context)