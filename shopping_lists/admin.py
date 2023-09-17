from django.contrib import admin
from .models import ShoppingList, Product

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(Product)