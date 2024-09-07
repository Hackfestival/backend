from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, Product, Cart, CartItem, OrderItem, Farm


def farm_product_list(request, farm_id):
    # Get the specific farm
    farm = get_object_or_404(Farm, farm_id=farm_id)

    # Get all products associated with this farm
    products = Product.objects.filter(seller=farm)

    # Pass the farm and products to the template
    context = {
        'farm': farm,
        'products': products
    }

    return render(request, 'farm_product_list.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']  # buyer or seller
        user = CustomUser.objects.create_user(username=username, password=password)

        return redirect('login')

    return render(request, 'store/register.html')

def add_product(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        seller = CustomUser.objects.get(user=request.user)
        #________________________CustomUser
        Product.objects.create(name=name, description=description, price=price, stock=stock, seller=seller)
        return redirect('seller_dashboard')

    return render(request, 'store/add_product.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

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

def seller_dashboard(request):
    seller = CustomUser.objects.get(user=request.user)
    #_______________CustomUser
    # Get all the order items that contain the seller's products
    orders = OrderItem.objects.filter(product__seller=seller)
    return render(request, 'store/seller_dashboard.html', {'orders': orders})
