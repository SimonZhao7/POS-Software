from typing import ItemsView
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as login_user

# Create your views here.

def login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_user(request, user)
        return redirect('/') # Temp placeholder
    return render(request, 'account/login.html', {'form': form})
            
def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('account:login')
    return render(request, 'account/register.html', {'form': form})