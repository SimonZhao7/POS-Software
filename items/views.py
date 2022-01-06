from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Item

# Create your views here.

@login_required
def view(request):
    items = Item.objects.all().order_by('column') # Items were created in reverse order
    return render(request, 'items/view.html', {'items': items})