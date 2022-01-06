from django.db import models
from datetime import date

# Create your models here.
class Date(models.Model):
    date = models.DateField()
    spreadsheet_row = models.IntegerField()
    
    class Meta: 
        get_latest_by = date
    
    def get_slug(self):
        return self.pk + 645150167
    
    @staticmethod
    def get_id(slug):
        return int(slug) - 645150167
    
    def __str__(self):
        return str(self.date)
    
    
class Transaction(models.Model):
    total_cost = models.DecimalField(max_digits=100, decimal_places=2)
    time_occured = models.TimeField()
    date_occured = models.ForeignKey(Date, on_delete=models.CASCADE)
    
    def get_slug(self):
        return self.pk + 236396582
    
    @staticmethod
    def get_id(slug):
        return int(slug) - 236396582
    
    def __str__(self):
        return self.time_occured


# Static Model with only 12 objects
class Item(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    column = models.CharField(max_length=3)
    max_quota = models.IntegerField()
    
    def get_slug(self):
        return self.pk + 931834991

    def get_id(slug):
        return int(slug) - 931834991

    def __str__(self):
        return self.name
    

class TransactionItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)