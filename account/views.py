from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as login_user, logout as logout_user
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from items.models import Item
from django.conf import settings
from .setup import setup_api

# Create your views here.

def login(request):
    if request.user.is_authenticated: 
        return redirect('items:view')
    
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_user(request, user)
            return redirect('items:view')
    return render(request, 'account/login.html', {'form': form})
            
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():      
            # Setup the Spreadsheet
            service = setup_api(settings.SCOPES)

            sheet = service.spreadsheets()
            spreadsheet_body = {
                'properties': {
                    'title': 'Martin POS Spreadsheet'
                }
            }
            create_response = sheet.create(body=spreadsheet_body).execute()

            # Get spreadsheet id for setup
            spreadsheet_id = create_response.get('spreadsheetId')
            setup_range = 'Sheet1!A1:P1'
            
            # Setup items
            setup_cols = 'BCDEFGHIJKLM'
            setup_values = [['Date', '', 'Daily Revenue', 'Total Items']]
            
            for i in range(12, 0, -1):
                item_text = 'Item #' + str(i)
                
                new_item = Item.objects.create(name=item_text, column=setup_cols[i - 1], price='1.50', max_quota=50)
                new_item.save()
                
                setup_values[0].insert(1, item_text)

            update_body = {
                "range": setup_range, 
                "values": setup_values
            }

            # Setup values with update
            sheet.values().update(spreadsheetId=spreadsheet_id, range=setup_range, valueInputOption='USER_ENTERED', body=update_body).execute()
            form.save(spreadsheet_id) 
            return redirect('account:login')
    return render(request, 'account/register.html', {'form': form})

@login_required
def logout(request):
    logout_user(request)
    return redirect('account:login')