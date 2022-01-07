from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from items.models import Item, Date
from items.views import get_cart_count
from account.setup import setup_api
from decimal import Decimal

# Create your views here.

@login_required
def cart(request):
    cart = request.session.get('cart', {})

    # Setup Dict For View
    obj_dict = {quantity: Item.objects.get(name=item_name) for item_name, quantity in cart.items()}
    total_items = sum(obj_dict.keys())
    total_cost = sum([quantity * item.price for quantity, item in obj_dict.items()])
    
    if request.method == 'POST':
        spreadsheet_id = request.user.spreadsheet_id
        sheets = setup_api(settings.SCOPES).spreadsheets()
        row = Date.objects.get(date=timezone.now().date()).spreadsheet_row
        
        for quantity, item in obj_dict.items():
            range = 'Sheet1!{col}{row}'.format(col=item.column, row=row)
            
            # Get spreadsheet count for item
            current_value = sheets.values().get(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueRenderOption='FORMATTED_VALUE'
            ).execute().get('values', [[0]])[0][0]
            
            # Update spreadsheet count for item
            update_body = {
                'range': range,
                'values': [
                    [int(current_value) + int(quantity)]
                ]
            }
            
            sheets.values().update(
                spreadsheetId=spreadsheet_id, 
                range=range,
                valueInputOption='USER_ENTERED',
                body=update_body
            ).execute()
        
        # Get spreadsheet totals 
        totals_range = 'Sheet1!O{row}:P{row}'.format(row=row)
        current_value = sheets.values().get(
            spreadsheetId=spreadsheet_id,
            range=totals_range,
            valueRenderOption='FORMATTED_VALUE'
        ).execute().get('values', [['$0', '0']])[0]
        
        current_revenue = Decimal(current_value[0][1:])
        current_total = int(current_value[1])
        
        # Update totals
        update_body = {
            'range': totals_range,
            'values': [
                ['$' + str(current_revenue + total_cost), str(current_total + total_items)]
            ]
        }
        
        sheets.values().update(
            spreadsheetId=spreadsheet_id, 
            range=totals_range,
            valueInputOption='USER_ENTERED',
            body=update_body
        ).execute()
        
        # Empty Cart and Refresh
        request.session['cart'] = {}
        return redirect('cart:view')
        
        
    return render(request, 'cart/view.html', {
        'items': obj_dict, 
        'cart_count': get_cart_count(request),
        'total_items': total_items,
        'total_cost': total_cost,
    })