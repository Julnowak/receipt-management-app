from django import forms
from .models import ShoppingList, ListProduct


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['text']
        labels = {'text': 'Nazwa listy:'}
        widgets = {
                    'text': forms.TextInput(attrs={
                        'class': "form-control",
                        'style': 'max-width: 300px; margin: auto; border-color:black',
                    })}


class ProductForm(forms.ModelForm):
    class Meta:
        model = ListProduct
        fields = ['product']
        labels = {'product': 'Nazwa produktu:'}
        widgets = {
            'product': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color:black',
            })}

