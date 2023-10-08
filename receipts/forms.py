import decimal

from django import forms
from .models import Receipt,Expense


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipt
        fields = ['receipt_name', 'receipt_img']


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['expense_name', 'is_recurrent','amount','category', 'group', 'number', 'time_stamp']
        labels = {'expense_name' : "Nazwa", 'is_recurrent':'Czy powtarzalny okresowo?',
                  'amount': "Wysokość",'category':'Kategoria', 'group':'Grupa',
                  'number': "Powtarzalny co:", 'time_stamp': "Okres czasu",
                  }
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin: auto',
                'min': 0,
            })
        }

    def clean(self):
        # data is feteched using the super function of django
        super(ExpenseForm, self).clean()

        amount = self.cleaned_data.get('amount')

        if amount < 0.00:
            self._errors['receiver'] = self.error_class([
                'Nie można podać kwoty mniejszej od 0'
            ])

        return self.cleaned_data

