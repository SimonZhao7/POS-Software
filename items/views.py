from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item
from .forms import AddItemsForm

# Create your views here.

@login_required
def view(request):
    items = Item.objects.all().order_by('column') # Items were created in reverse order
    return render(request, 'items/view.html', {'items': items})

@login_required
def add(request, slug):
    try:
        item = Item.objects.get(pk=Item.get_id(slug))
    except:
        return redirect('items:view')
    
    form = AddItemsForm(item=item)
    if request.method == 'POST':
        form = AddItemsForm(request.POST, item=item)
        if form.is_valid():
            # Adds to cart
            form.save(request)
            return redirect('items:view')
    return render(request, 'items/add.html', {'form': form})