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


class DetailsForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['group', 'regards', 'display_only']
        labels = {'group': 'Grupa', 'regards': 'Uwagi', 'display_only': 'Zablokować możliwość edycji?'}
        widgets = {
                    'group': forms.Select(attrs={
                        'class': "form-select",
                        'style': 'max-width: 300px; margin: auto; margin: 10px auto; border-color:black',
                    }),

                    'regards': forms.Textarea(attrs={
                        'class': "form-control",
                        'style': 'max-width: 300px; margin: auto; margin: 10px auto; border-color:black',
                    }),

                    'display_only': forms.CheckboxInput(attrs={
                        'class': "form-checkbox",
                        'style': 'width: 25px; min-height: 25px; accent-color: black;  margin: 10px auto; border-color:black',
                    })
        }


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

