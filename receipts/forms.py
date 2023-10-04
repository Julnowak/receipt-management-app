from django import forms
from .models import Receipt,Expense


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipt
        fields = ['receipt_name', 'receipt_img']


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['expense_name', 'is_recurrent','amount','category', 'group']
        labels = {'expense_name' : "Nazwa", 'is_recurrent':'Czy powtarzalny okresowo?',
                  'amount': "Wysokość",'category':'Kategoria', 'group':'Grupa'}

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
