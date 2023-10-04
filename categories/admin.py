from django.contrib import admin
from .models import BaseCategories, SubCategories


# Register your models here.

admin.site.register(BaseCategories)
admin.site.register(SubCategories)