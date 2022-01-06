from django.db import models

# Create your models here.
class Date(models.Model):
    date = models.DateField()


class Transactions(models.Model):
    totalcost = models.DecimalField(max_digits=100, decimal_places=2)
    time_occured = models.ForeignKey(Date, on_delate=models.CASCADE)


class Items(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    column = models.CharField(max_length=3)
    max_quota = models.IntegerField()
    purchased_items = models.ForeignKey(Transactions, on_delete=models.CASCADE)




