from django.db import models
from user.models import userdata 
# Create your models here.

class Wallet(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
        TRANSACTION_TYPE_CHOICES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
        ('Refund', 'Refund'),
        ('Point', 'Point'),
        )
        wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=10, decimal_places=2)
        transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
        date_created = models.DateTimeField(auto_now_add=True)

