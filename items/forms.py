from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction, Date, TransactionItem
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
        sold_today = 0
        all_today_trans = Transaction.objects.filter(date_occured__date=current_date)
        for item in all_today_trans:
            sold_today += item.transaction_item_set.filter(name=self.item.name).count()
        
        total_predicted_items = quantity + sold_today
        
        if total_predicted_items > self.item.max_quota:
            raise ValidationError('You have exceeded the max quota by ' + str(total_predicted_items - self.item.max_quota))
        
        
    def save(self, request):
        cart = request.session.get('cart', [])
        for i in range(self.cleaned_data['quantity']):
            new_trans_item = TransactionItem.objects.create(item=self.item)
            new_trans_item.save()
            cart.append(new_trans_item.pk)
        request.session['cart'] = cart
            