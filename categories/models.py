from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class BaseCategories(models.Model):
    category_name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    date_added = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_owner')
    public = models.BooleanField(default=False)
    icon = models.CharField(max_length=1, default="", blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = 'Base categories'


class SubCategories(models.Model):
    subcategory_name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    date_added = models.DateField(auto_now_add=True)
    category = models.ForeignKey(BaseCategories, on_delete=models.CASCADE, null=True)
    slug = models.SlugField(unique=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subcategory_owner')
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.subcategory_name

