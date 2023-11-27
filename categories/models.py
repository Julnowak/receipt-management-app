from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class BaseCategories(models.Model):
    category_name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, default="#233423")
    date_added = models.DateField(auto_now_add=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='category_owner', blank=True, null=True)
    public = models.BooleanField(default=False)
    icon = models.CharField(max_length=2000, default="", blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = 'Base categories'


class SubCategories(models.Model):
    subcategory_name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    date_added = models.DateField(auto_now_add=True)
    icon = models.CharField(max_length=1500, default="", blank=True)
    category = models.ForeignKey(BaseCategories, on_delete=models.CASCADE, null=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subcategory_owner', blank=True, null=True)
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.subcategory_name


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)
    subcategory = models.ForeignKey(SubCategories, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.product_name
