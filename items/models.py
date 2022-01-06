from django.db import models

# Create your models here.
class Date(models.Model):
    date = models.DateField()
    spreadsheet_row = models.IntegerField()


class Transaction(models.Model):
    totalcost = models.DecimalField(max_digits=100, decimal_places=2)
    time_occured = models.ForeignKey(Date, on_delete=models.CASCADE)


class Item(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    column = models.CharField(max_length=3)
    max_quota = models.IntegerField()
    purchased_items = models.ManyToManyField(Transaction)
    
    
    def __str__(self):
        return self.name




