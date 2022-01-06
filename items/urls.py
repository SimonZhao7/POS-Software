from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('', views.view, name='view'),
]