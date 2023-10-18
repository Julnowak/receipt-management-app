from django.contrib import admin
from .models import ShoppingList, Product,SharedShoppingList

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(Product)
admin.site.register(SharedShoppingList)

