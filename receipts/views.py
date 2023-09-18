from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt
from receipts.forms import ReceiptForm
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