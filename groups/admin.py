from django.contrib import admin
from .models import CommonGroups

# Register your models here.


class CommonGroupsAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['group_name'],
    }


admin.site.register(CommonGroups)
