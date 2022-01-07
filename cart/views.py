from django.shortcuts import render
from items.models import Item
from items.views import get_cart_count

# Create your views here.

def cart(request):
    cart = request.session.get('cart', {})

    # Setup Dict For View
    obj_dict = {quantity: Item.objects.get(name=item_name) for item_name, quantity in cart.items()}
    total_items = sum(obj_dict.keys())
    total_cost = sum([quantity * item.price for quantity, item in obj_dict.items()])
        
    return render(request, 'cart/view.html', {
        'items': obj_dict, 
        'cart_count': get_cart_count(request),
        'total_items': total_items,
        'total_cost': total_cost,
    })