import json
import random
from datetime import datetime
from django.views.decorators.http import require_http_methods

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, Product, Cart, CartItem, Farm, Order
from .forms import UserRegistrationForm, UserLoginForm, ProductForm, UserCartAddForm, UserUpdateForm, FarmUpdateForm
from . import common
from datetime import datetime, timedelta

@csrf_exempt
@require_http_methods(['GET'])
def home(request):
    if not request.user.is_authenticated:
        return render(request, 'store/index.html')
    else:
        c_user = CustomUser.objects.get(email=request.user)
        user_location = c_user.get_location()
        farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
        filtered_farm_list = []

        for frm in farms:
            var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
            if var < common.default_radius:
                filtered_farm_list.append(frm)

        return render(request, 'store/home_map.html', {"farms": filtered_farm_list})

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

            new_user.latitude = 49.4865
            new_user.longitude = 8.4700

            new_user.save()

            user_authenticated = authenticate(request, email=new_user.email, password=form.cleaned_data['password'])
            if user_authenticated:
                login(request, user_authenticated)
                # return redirect('home')
                return render(request, 'store/farm_list.html')
            return JsonResponse({'status': 'error', 'message': 'Authentication failed'})
        return JsonResponse({'status': 'error', 'message': 'Form is not valid', 'errors': form.errors})

    return render(request, 'store/user_register.html', {'form': UserRegistrationForm()})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user_authenticated = authenticate(request, email=email, password=password)

            if user_authenticated:
                login(request, user_authenticated)
                # return redirect('farm_list')
                return redirect('/')

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

    #return JsonResponse({'status': 'success', 'products': list(user_cart_items.values())})
    return render(request, 'store/user_cart_display.html', {'form': UserRegistrationForm()})

def cart_view(request):
    # Load the product data from a JSON file
    with open('store/fixtures/mock_data.json', 'r') as file:
        data = json.load(file)

    # Assuming products are stored in the 'products' key
    products = data['products']

    # Select three random products from the JSON data
    selected_products = random.sample(products, 3)

    # Calculate total cost
    cart_total = sum(product['price'] for product in selected_products)

    # Pass selected products and total cost to the template
    context = {
        'cart_items': selected_products,
        'cart_total': cart_total
    }

    return render(request, 'store/user_cart_display.html', context)
@csrf_exempt
@login_required
@require_http_methods(['GET', 'POST'])
def user_cart_payment(request):
    # Get the user's cart and cart items
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Check if the cart is empty
    if not cart_items.exists():
        return redirect('user_cart_list')

    # Calculate the total cost of the cart
    cart_total = sum(item.product.price * item.quantity for item in cart_items)

    # If this is a POST request (the user submits the payment form), we'll just mock the success
    if request.method == 'POST':
        # Simulate a successful payment (no actual payment processing here)
        return redirect('payment_success')

    # Render the mock payment page with the cart items and total
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/payment_page.html', context)


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

def farm_detail_view(request, farm_uuid):
    # Fetch the farm by UUID
    farm = get_object_or_404(Farm, farm_id=farm_uuid)
    
    # Fetch all products related to the farm
    products = Product.objects.filter(seller=farm)

    # Pass the farm and products to the template
    return render(request, 'store/farm_detail.html', {'farm': farm, 'products': products})

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


@csrf_exempt
@login_required
@require_http_methods(['GET'])
def farm_page(request, farm_id):
    try:
        farm = Farm.objects.get(farm_id=farm_id)
    except Farm.DoesNotExist:
        return redirect('home')

    products = farm.get_products()

    print(products)

    return render(request, 'store/farm_page.html', {'farm': farm, 'products': products})
def home_view(request):

    if not request.user.is_authenticated:
        return redirect('user_login')

    c_user = CustomUser.objects.get(email=request.user)
    user_location = c_user.get_location()
    farms = Farm.get_all_farms()  # Fetch farms for the logged-in user
    filtered_farm_list = []

    for frm in farms:
        var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
        if var < common.default_radius:
            filtered_farm_list.append(frm)

    return render(request, 'store/home_map.html', {"farms": filtered_farm_list})

@login_required
def farm_detail(request, farm_id):
    # Fetch the farm by its ID
    farm = get_object_or_404(Farm, farm_id=farm_id)

    return render(request, 'store/farm_detail.html', {'farm': farm, 'products': farm.get_products()})

@login_required
def cart_view(request):
    # Get the current user's cart
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=user_cart)

    # Add subtotal for each cart item (product price * quantity)
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity

    # Calculate the total cost
    cart_total = sum(item.subtotal for item in cart_items)

    # Pass selected products and total cost to the template
    context = {
        'selected_products': cart_items,
        'cart_total': cart_total
    }

    return render(request, 'store/user_cart_display.html', context)

def user_cart_checkout_dummy(request):
    # Dummy cart data
    cart_items = [
        {'product_id': 1, 'name': 'Apple', 'price': 2.5, 'quantity': 3, 'subtotal': 7.5},
    ]
    
    # Calculate total price
    total_price = sum(item['subtotal'] for item in cart_items)

    if request.method == "POST":
        # Dummy order confirmation and cart clearance
        return redirect('order_confirmation')  # Simulate successful order

    return render(request, 'store/user_checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def user_cart_confirm(request):
    # Dummy data for the confirmation page
    context = {
        'order_number': '123456',  # You can generate this dynamically
        'total_price': 150.00,     # Total amount from the order
        'delivery_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),  # Estimated delivery in 5 days
    }
    
    return render(request, 'store/user_cart_confirm.html', context)