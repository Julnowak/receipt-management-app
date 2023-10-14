from django import forms
from .models import BaseCategories, SubCategories


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = BaseCategories
        fields = ['category_name', 'color', 'icon', 'public']
        labels = {'category_name': "Nazwa kategorii",
                  'color': 'Kolor',
                  'icon': 'Ikona',
                  'public': 'Czy kategoria jest publiczna?'}


class NewSubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategories
        fields = ['subcategory_name', 'color', 'icon', 'category']
        labels = {'subcategory_name': "Nazwa podkategorii",
                  'category': "Kategoria",
                  'color': 'Kolor',
                  'icon': 'Ikona'}
