from django.contrib import admin
from .models import ShoppingList, ListProduct,SharedShoppingList

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(ListProduct)
admin.site.register(SharedShoppingList)

