from django.db import models
from django.contrib.auth.models import User
from categories.models import BaseCategories, SubCategories
from groups.models import CommonGroups


class ShoppingList(models.Model):
    """One of the user's shopping lists"""

    text = models.CharField(max_length=150)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    regards = models.TextField(max_length=250, blank=True, null=True)
    realizators = models.ManyToManyField(User, related_name="realizators", default=owner)
    group = models.ForeignKey(CommonGroups, on_delete=models.SET_NULL, blank=True, null=True)
    display_only = models.BooleanField(default=False)
    logs = models.TextField(default='')

    def __str__(self):
        if len(self.text) > 30:
            return self.text[:30] + "..."
        else:
            return self.text

    def full_name(self):
        return self.text


class ListProduct(models.Model):
    product = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.CharField(max_length=100, default="1szt.", blank=True, null=True)
    regards = models.TextField(max_length=400, blank=True, null=True)
    is_bought = models.BooleanField(default=False)
    by_who = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'list products'

    def __str__(self):
        return self.product
