from django import forms
from .models import ShoppingList,Product


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['text']
        labels = {'text': ''}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product']
        labels = {'product': ''}
        widgets = {'product': forms.Textarea(attrs={'cols': 80})}
