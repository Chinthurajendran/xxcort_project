from django.db import models
from category.models import category

# Create your models here.

class products(models.Model):
    name = models.CharField(max_length =100,unique = True)
    code = models.CharField(max_length=20)
    image1 = models.ImageField(upload_to='image',null=True)
    image2 = models.ImageField(upload_to='image',null=True)
    image3 = models.ImageField(upload_to='image',null=True)
    product_type = models.ForeignKey(category,on_delete=models.CASCADE)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True)
    product_description = models.CharField(max_length = 500)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    offer = models.IntegerField(default = None)
    small  =models.IntegerField(default = None)
    medium  =models.IntegerField(default = None)
    large  =models.IntegerField(default = None)
    stock = models.IntegerField(default = 0)
    offer_price = models.DecimalField(max_digits=7,decimal_places=2,default = None)



    def stock_for_size(self, size):
        if size == 'small':
            return self.small
        elif size == 'medium':
            return self.medium
        elif size == 'large':
            return self.large
        else:
            return 0
        
    def save(self, *args, **kwargs):
        # Calculate total stock
        total_stock = sum(filter(None, [self.small, self.medium, self.large]))
        self.stock = total_stock
        super().save(*args, **kwargs)


    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name




