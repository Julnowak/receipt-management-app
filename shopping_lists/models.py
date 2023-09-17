from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ShoppingList(models.Model):
    """One of the user's shopping lists"""

    text = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Product(models.Model):
    selected_list = models.ForeignKey(ShoppingList,on_delete=models.CASCADE)
    product = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'products'

    def __str__(self):
        return self.product
