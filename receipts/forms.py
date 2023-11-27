import decimal

from django import forms
from .models import Receipt,Expense, Guarantee


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipt
        fields = ['receipt_name', 'receipt_img','amount','receipt_info','group','products','date_of_receipt_bought',
                  'receipt_categories','shop']
        labels = {'receipt_name': 'Nazwa', 'receipt_img': 'Zdjęcie',
                  'amount': 'Wartość','receipt_info': 'Dodatkowe informacje',
                  'group': 'Grupa','products': 'Produkty','shop': 'Sklep'}
        widgets = {
            'products': forms.SelectMultiple(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_info': forms.Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'group': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_img': forms.FileInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'amount': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
                'id': 'num',
                'min': 0,
            }),

            'shop': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'date_of_receipt_bought': forms.DateInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_categories': forms.SelectMultiple(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),
        }


class HandReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['receipt_name', 'receipt_img','amount','receipt_info','group','products','shop']
        labels = {'receipt_name': 'Nazwa', 'receipt_img': 'Zdjęcie','shop': 'Sklep',
                  'amount': 'Wartość','receipt_info': 'Dodatkowe informacje',
                  'group': 'Grupa','products': 'Produkty'}
        widgets = {
            'products': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_info': forms.Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'group': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'shop': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),

            'receipt_img': forms.FileInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
            }),
            'amount': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',
                'format': '%.2f',
                'min': 0,
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_name', 'is_recurrent','amount','category', 'group', 'number', 'time_stamp']
        labels = {'expense_name' : "Nazwa", 'is_recurrent':'Czy powtarzalny okresowo?',
                  'amount': "Wysokość", 'category':'Kategoria', 'group':'Grupa',
                  'number': "Powtarzalny co:", 'time_stamp': "Okres czasu",
                  }
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black; border-color: black',
                'min': 0,
            }),
            'category': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black; border-color: black',}),

            'is_recurrent': forms.CheckboxInput(attrs={
                'class': "checkbox",
                'style': "width: 30px; border-color: black",
                'id': "is_rec"
            }),

            'expense_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',}),

            'group': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',}),

            'time_stamp': forms.Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px; margin: auto; border-color: black',}),

            'number': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto; border-color: black',}),

        }

    def clean(self):
        super(ExpenseForm, self).clean()

        amount = self.cleaned_data.get('amount')

        if amount < 0.00:
            self._errors['receiver'] = self.error_class([
                'Nie można podać kwoty mniejszej od 0'
            ])

        return self.cleaned_data


class GuaranteeForm(forms.ModelForm):
    class Meta:
        model = Guarantee
        fields = ['guarantee_name', 'end_date','regards']
        labels = {'guarantee_name': 'Nazwa', 'end_date' : 'Data zakończenia', 'regards': 'Uwagi'}

        widgets = {
            'guarantee_name': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; border-color: black'
            }),

            'end_date': forms.SelectDateWidget(empty_label=("Wybierz rok", "Wybierz miesiąc", "Wybierz dzień"),
                                               months={
                                                   1: "Styczeń",
                                                   2: "Luty",
                                                   3: "Marzec",
                                                   4: "Kwiecień",
                                                   5: "Maj",
                                                   6: "Czerwiec",
                                                   7: "Lipiec",
                                                   8: "Sierpień",
                                                   9: "Wrzesień",
                                                   10: "Październik",
                                                   11: "Listopad",
                                                   12: "Grudzień"
                                                    },
                                               attrs={
                'class': "form-control",
                'style': 'max-width: 200px; border-color: black'
            }),
            'regards': forms.Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 350px; border-color: black'
            })
        }