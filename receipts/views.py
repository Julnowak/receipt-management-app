from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt
from receipts.forms import ReceiptForm, ExpenseForm
# Create your views here.


@login_required
def your_receipts(request):
    receipts = Receipt.objects.all()
    context = {'receipts': receipts}
    return render(request, 'receipts/your_receipts.html', context)


@login_required
def new_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('your_receipts')
    else:
        form = ReceiptForm()
    return render(request, 'receipts/new_receipt.html', {'form': form})


def costs_by_hand(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            cost = form.save(commit=False)
            print(cost)
            cost.owner = request.user
            form.save()
            return redirect('receipts:your_receipts')
    else:
        form = ExpenseForm()

    context = {'form': form }
    return render(request, 'receipts/costs_by_hand.html', context)