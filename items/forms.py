from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Transaction, Date, Item
from django.utils import timezone
from datetime import timedelta
from account.setup import setup_api
from django.conf import settings


class AddItemsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
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
            for day in range(day_diff.days):
                new_date = Date.objects.create(
                    date=recent_date.date + timedelta(days=1), 
                    spreadsheet_row=recent_date.spreadsheet_row + 1
                )
                new_date.save()
                recent_date = self.save_to_spreadsheet(new_date)
        else:
            new_date = Date.objects.create(date=current_date, spreadsheet_row=2)
            self.save_to_spreadsheet(new_date)
        
        # Enforce Max Quota
        item_max_quota = self.item.max_quota
        all_today_trans = Transaction.objects.filter(date_occurred__date=current_date)
        sold_today = sum(sum(item.quantity for item in trans.transaction_items.filter(item__name=self.item)) for trans in all_today_trans)
        
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
        
    def save_to_spreadsheet(self, model):
        sheets = setup_api(settings.SCOPES).spreadsheets()
        
        spreadsheet_range = 'Sheet1!A{row}'.format(row=model.spreadsheet_row)
            
        update_body = {
            'range': spreadsheet_range,
            'values': [
                [model.date.strftime('%m/%d/%Y')]
            ]
        }
            
        sheets.values().update(
            spreadsheetId=self.user.spreadsheet_id, 
            range=spreadsheet_range,
            valueInputOption='USER_ENTERED',
            body=update_body
        ).execute()
        return model
        
        
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