from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class category(models.Model):
    name = models.CharField(max_length =20,unique = True)
    description = models.CharField(max_length =30)
    is_active = models.BooleanField(default =True)
    offer=models.DecimalField(max_digits=5, decimal_places=2,null=True)

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


