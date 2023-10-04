from django import forms
from .models import BaseCategories


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = BaseCategories
        fields = ['category_name', 'color', 'icon']

