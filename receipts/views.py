import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt, Guarantee, Expense
from receipts.forms import ReceiptForm, ExpenseForm
import pytesseract
from PIL import Image
import cv2
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Create your views here.


@login_required
def your_receipts(request):
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    left = None
    for guarantee in guarantees:
        left = guarantee.end_date - datetime.date.today()
    context = {'receipts': receipts, 'expenses': expenses, 'guarantees': guarantees, 'time_left': left}
    return render(request, 'receipts/your_receipts.html', context)


@login_required
def new_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)

        if form.is_valid():
            new_receipt = form.save(commit=False)
            new_receipt.owner = request.user
            new_receipt.save()
            return redirect('receipts:your_receipts')
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


@login_required
def guarantees(request):
    guarantees = Guarantee.objects.filter(owner=request.user)
    left = None
    for guarantee in guarantees:
        left = guarantee.end_date - datetime.date.today()
    context = {'guarantees': guarantees, 'time_left': left}
    return render(request, 'receipts/guarantees.html', context)


@login_required
def receipt_site(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)
    custom_config = r'--oem 1 --psm 6 -l pol'

    text = pytesseract.image_to_string(Image.open(f'media/{receipt.receipt_img}'), config=custom_config)
    print(text)
    context = {'receipt': receipt, 'text': text}
    return render(request, 'receipts/receipt_site.html', context)


@login_required
def new_guarantee(request):
    context = {}
    return render(request, 'receipts/new_guarantee.html', context)

