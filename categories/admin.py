from django.contrib import admin
from .models import BaseCategories, SubCategories, Product


# Register your models here.

admin.site.register(BaseCategories)
admin.site.register(SubCategories)
admin.site.register(Product)