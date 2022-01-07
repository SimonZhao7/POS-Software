from django.contrib import admin
from .models import Date, Transaction, Item, TransactionItem

# Register your models here.

admin.site.register(Date)
admin.site.register(Transaction)
admin.site.register(Item)
admin.site.register(TransactionItem)
