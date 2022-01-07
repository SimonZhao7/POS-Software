from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item
from .forms import AddItemsForm, RemoveItemForm, EditItemForm

# Create your views here.

def get_cart_count(request):
    cart = request.session.get('cart', {})
    return sum(cart.values())

@login_required
def view(request):
    items = Item.objects.all().order_by('column') # Items were created in reverse order
    return render(request, 'items/view.html', {'items': items, 'cart_count': get_cart_count(request)})

@login_required
def add(request, slug):
    try:
        item = Item.objects.get(pk=Item.get_id(slug))
    except:
        return render(request, '404.html', {'cart_count': get_cart_count(request)})
    
    form = AddItemsForm(item=item)
    if request.method == 'POST':
        form = AddItemsForm(request.POST, item=item)
        if form.is_valid():
            # Adds to cart
            form.save(request)
            return redirect('items:view')
    return render(request, 'items/add.html', {'form': form, 'cart_count': get_cart_count(request)})

@login_required
def remove(request, slug):
    try:
        item = Item.objects.get(id=Item.get_id(slug))
    except: 
        return render(request, '404.html', {'cart_count', get_cart_count(request)})
    
    form = RemoveItemForm(item=item, request=request)
    if request.method == 'POST':
        form = RemoveItemForm(request.POST, item=item, request=request)
        if form.is_valid():
            form.save(request)
            return redirect('cart:view')
    return render(request, 'items/remove.html', {'form': form, 'cart_count': get_cart_count(request)})

@login_required
def edit(request, slug):
    form = EditItemForm()
    context_data = {'form': form, 'cart_count': get_cart_count(request)}
    
    try:
        item = Item.objects.get(id=Item.get_id(slug))
    except:
        return render(request, '404.html', context_data)
    
    if request.method == 'POST':
        form = EditItemForm(request.POST)
        if form.is_valid():
            form.save(item)
            return redirect('items:view')
    return render(request, 'items/edit.html', context_data)