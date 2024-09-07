from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        user_cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart_item_count': user_cart.cartitem_set.count()}
    return {'cart_item_count': 0}
