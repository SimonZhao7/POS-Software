from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('', views.view, name='view'),
    path('add/<str:slug>/', views.add, name='add'),
    path('edit/<str:slug>/', views.edit, name='edit')
]