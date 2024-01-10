from django import forms
from .models import BaseCategories, SubCategories, Product


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = BaseCategories
        fields = ['category_name', 'color', 'icon', 'public']
        labels = {'category_name': "Nazwa kategorii",
                  'color': 'Kolor',
                  'icon': 'Ikona',
                  'public': 'Czy kategoria jest publiczna?'}
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'min-width: 300px; max-width: 600px; margin: auto;'
                         'border-color:black',
            }),
            'icon': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'min-width: 300px;max-width: 600px; margin: auto; border-color:black',
            }),

            'public': forms.CheckboxInput(attrs={
                'class': "form-check",
                'style': 'height:25px; width:25px;accent-color: black;'
                         'border-radius: 10px',
            })
        }


class NewSubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategories
        fields = ['subcategory_name','color', 'public']
        labels = {'subcategory_name': "Nazwa podkategorii",
                  'color': "Kolor",
                  'public': 'Czy podkategoria publiczna?'}
        widgets = {
                    'subcategory_name': forms.TextInput(attrs={
                        'class': "form-control",
                        'style': 'min-width: 300px; max-width: 600px; margin: auto;'
                                 'border-color:black',
                    }),

                    'public': forms.CheckboxInput(attrs={
                        'class': "form-check",
                        'style': 'height:25px; width:25px;accent-color: black;'
                                 'border-radius: 10px',
                    })
                }


class NewProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name']
        labels = {'product_name': "Nazwa produktu",}
        widgets = {
                    'product_name': forms.TextInput(attrs={
                        'class': "form-control",
                        'style': 'min-width: 300px; max-width: 600px; margin: auto;'
                                 'border-color:black',
                    }),
                }