from django.db import models
from product.models import products
from user.models import userdata

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    product_info = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    selected_size = models.CharField(max_length=10, null=True)
    subtotal = models.IntegerField(default=0)
    

# class CartItms(models.Model):
#     user_id = models.ForeignKey(userdata, on_delete=models.CASCADE)
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
