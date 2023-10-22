from django.db import models
from django.contrib.auth.models import User
from categories.models import BaseCategories, SubCategories
from groups.models import CommonGroups
# Create your models here.


class ShoppingList(models.Model):
    """One of the user's shopping lists"""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class ListProduct(models.Model):
    selected_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    product = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.CharField(max_length=100, default="1szt.", blank=True, null=True)
    regards = models.TextField(max_length=400, blank=True, null=True)
    is_bought = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'list products'

    def __str__(self):
        return self.product


class SharedShoppingList(models.Model):
    """One of the user's shopping lists"""
    base_list = models.ForeignKey(ShoppingList, on_delete=models.SET_NULL, null=True)
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    is_in_realization = models.BooleanField(default=False)
    realizators = models.ManyToManyField(User, related_name="realizators")
    group = models.ForeignKey(CommonGroups, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.base_list