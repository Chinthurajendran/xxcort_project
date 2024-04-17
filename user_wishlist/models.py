from django.db import models
from product.models import products
from user.models import userdata 


# Create your models here.

class user_wishlist(models.Model):
    user_info = models.ForeignKey(userdata,on_delete = models.CASCADE)
    product = models.ForeignKey(products,on_delete = models.CASCADE)