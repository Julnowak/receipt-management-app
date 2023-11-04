from django.contrib import admin
from .models import ShoppingList, ListProduct

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(ListProduct)

