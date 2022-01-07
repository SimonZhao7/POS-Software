from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Transaction, Date, TransactionItem, Item
from django.utils import timezone
from datetime import timedelta


class AddItemsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        super().__init__(*args, *kwargs)
        
    quantity = forms.IntegerField()
    
    def clean(self):
        quantity = self.cleaned_data['quantity']
        current_date = timezone.now().date()
        
        # Get or create 
        if Date.objects.exists():
            recent_date = Date.objects.latest('date')
            day_diff = current_date - recent_date.date 
            
            # Fill in the inactive days
            for day in range (day_diff.days):
                new_date = Date.objects.create(
                    date=recent_date.date + timedelta(days=1), 
                    spreadsheet_row=recent_date.spreadsheet_row + 1
                )
                new_date.save()
                recent_date = new_date
        else:
            new_date = Date.objects.create(date=current_date, spreadsheet_row=2)
        
        # Enforce Max Quota
        item_max_quota = self.item.max_quota
        all_today_trans = Transaction.objects.filter(date_occured__date=current_date)
        sold_today = sum([item.transaction_item_set.filter(name=self.item.name).count()] for item in all_today_trans)
        
        total_predicted_items = quantity + sold_today
        
        if total_predicted_items > item_max_quota:
            raise ValidationError('You have exceeded the max quota by ' + str(total_predicted_items - item_max_quota))
        return self.cleaned_data
        
    def save(self, request):
        item_name = self.item.name
        cart = request.session.get('cart', {})
        
        # Dict {item_name: quantity}
        cart[item_name] = cart.get(item_name, 0) + self.cleaned_data['quantity']
                
        request.session['cart'] = cart
        
        
class RemoveItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        self.cart = kwargs.pop('request').session.get('cart', {})
        super().__init__(*args, **kwargs)
        
    quantity = forms.IntegerField()
    
    def clean(self):
        quantity = self.cleaned_data['quantity']
        item_quantity = self.cart.get(self.item.name, 0)
        if item_quantity - quantity < 0:
            raise ValidationError('You removed more of this specific item than your cart contains')
        return self.cleaned_data
    
    def save(self, request):
        item_name = self.item.name
        cart = request.session.get('cart', {})
        
        cart[item_name] = cart.get(item_name, 0) - self.cleaned_data['quantity']
        
        # Remove completely if zero items
        if cart[item_name] == 0:
            del cart[item_name]
            
        request.session['cart'] = cart
            
class EditItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price', 'max_quota']
        
    def save(self, item):
        item.name = self.cleaned_data['name']
        item.price = self.cleaned_data['price']
        item.max_quota = self.cleaned_data['max_quota']
        item.save()
        return item