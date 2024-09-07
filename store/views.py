from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

from .models import CustomUser, Product, Cart, CartItem, OrderItem, Farm
from .forms import FarmForm
from . import common

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        CustomUser.objects.create_user(username=username, password=password, email = email)

        user_authenticated = authenticate(request, email=email, password=password)

        if user_authenticated:
            login(request, user_authenticated)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error'})
    elif request.method == 'GET':
        return render(request, 'store/register.html')
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        #seller = SellerProfile.objects.get(user=request.user)
        Product.objects.create(name=name, description=description, price=price, stock=stock, seller=seller)
        return redirect('seller_dashboard')

    return render(request, 'store/add_product.html')

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if product.stock > 0:
        cart_item.quantity += 1
        cart_item.save()
        product.reduce_stock(1)  # Reduce stock when added to cart
        return redirect('cart_detail')
    else:
        return render(request, 'store/out_of_stock.html')

@login_required
def seller_dashboard(request):
    #seller = SellerProfile.objects.get(user=request.user)
    # Get all the order items that contain the seller's products
    orders = OrderItem.objects.filter(product__seller=seller)
    return render(request, 'store/seller_dashboard.html', {'orders': orders})


#######################
######## Location CRUD
########################

@login_required
def farm_list(request):
    farms = Farm.get_all_farms() # Fetch farms for the logged-in user
    print(f"Farm: {farms}")
    return render(request, 'store/farm_list.html', {'farms': farms})

def get_list_of_nearby_farms(request):
    c_user = CustomUser.objects.get(email=request.user)
    print(f"req user: { request.user}")

    user_location = c_user.get_location()
    print(f"User location: {user_location}")

    farms = Farm.get_all_farms() # Fetch farms for the logged-in user

    filtered_farm_list = []

    for frm in farms:
        print(f"Farm: {frm.latitude},{frm.longitude}")
        print(f"User: {user_location}")
        var = common.haversine(frm.latitude, frm.longitude, user_location[0], user_location[1])
        print(f"{var:.2f} km")

        if(var < common.default_radius):
            print("added to list")
            filtered_farm_list.append(frm)

    return render(request, 'store/nearby_farm.html', {'farms': filtered_farm_list})
