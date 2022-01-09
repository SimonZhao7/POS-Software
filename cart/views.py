from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from items.models import Item, Date, Transaction, TransactionItem
from items.views import get_cart_count
from items.helpers import save_to_spreadsheet, get_spreadsheet_value
from decimal import Decimal

# Create your views here.
@login_required
def cart(request):
    cart = request.session.get('cart', {})

    # Setup Dict For View
    obj_dict = [[Item.objects.get(name=item_name), quantity] for item_name, quantity in cart.items()]
    total_items = sum(cart.values())
    total_cost = sum(item.price * quantity for item, quantity in obj_dict)
    date = Date.objects.get(date=timezone.now().date())
    
    if request.method == 'POST':
        spreadsheet_id = request.user.spreadsheet_id
        row = Date.objects.get(date=timezone.now().date()).spreadsheet_row
        
        # Create transaction
        transaction = Transaction.objects.create(
            total_cost=total_cost, 
            total_items=total_items, 
            date_occurred=date,
            time_occurred=timezone.now().time(),
        )
        
        for item, quantity in obj_dict:
            range = 'Sheet1!{col}{row}'.format(col=item.column, row=row)
            
            # Get spreadsheet count for item
            current_value = get_spreadsheet_value(spreadsheet_id, range)
            
            # Update spreadsheet count for item
            new_total = int(current_value[0]) + int(quantity)
            save_to_spreadsheet(spreadsheet_id, range, [new_total])
            
            # Add transaction item
            transaction_item = TransactionItem.objects.create(
                item=item,
                quantity=quantity
            )
            transaction_item.save()
            transaction.transaction_items.add(transaction_item)
        
        # Get spreadsheet totals 
        totals_range = 'Sheet1!O{row}:P{row}'.format(row=row)
        current_value = get_spreadsheet_value(spreadsheet_id, totals_range)
        current_value = ['$0.00', '0'] if current_value[0] == 0 else current_value
        
        current_revenue = Decimal(current_value[0][1:])
        current_total = int(current_value[1])
        
        # Update totals
        new_revenue = ['$' + str(current_revenue + total_cost), str(current_total + total_items)]
        save_to_spreadsheet(spreadsheet_id, totals_range, new_revenue)
        
        # Empty Cart and Refresh
        transaction.save()
        request.session['cart'] = {}
        return redirect('cart:view')
        
    return render(request, 'cart/view.html', {
        'items': obj_dict, 
        'cart_count': get_cart_count(request),
        'total_items': total_items,
        'total_cost': total_cost,
    })