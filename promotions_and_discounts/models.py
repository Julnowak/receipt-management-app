from django.db import models
from categories.models import BaseCategories
# Create your models here.


class Shop(models.Model):
    shop_name = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True)
    link = models.CharField(max_length=2000,blank=True, null=True)
    promos_available = models.BooleanField(default=False)
    category = models.ManyToManyField(BaseCategories)

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        super(Shop, self).save(*args, **kwargs)
