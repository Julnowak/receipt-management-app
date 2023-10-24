import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt, Guarantee, Expense
from receipts.forms import ReceiptForm, ExpenseForm, GuaranteeForm, HandReceiptForm
import pytesseract
from PIL import Image
import cv2
from pytesseract import Output
import numpy as np


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


@login_required
def your_receipts(request):
    if len(Receipt.objects.filter(owner=request.user)) > 5:
        flag = True
    else:
        flag = False

    if len(Expense.objects.filter(owner=request.user)) > 5:
        flag_e = True
    else:
        flag_e = False

    if len(Guarantee.objects.filter(owner=request.user)) > 5:
        flag_g = True
    else:
        flag_g = False

    receipts = Receipt.objects.filter(owner=request.user).order_by("-date_added")[:5]
    expenses = Expense.objects.filter(owner=request.user).order_by("-date_added")[:5]
    guarantees = Guarantee.objects.filter(owner=request.user)[:5]
    left = []
    for guarantee in guarantees:
       result = guarantee.end_date - datetime.date.today()
       left.append(result)

    info = zip(guarantees, left)
    context = {'receipts': receipts, 'expenses': expenses, 'guarantees': guarantees, 'info': info,
               'flag': flag, 'flag_e': flag_e, 'flag_g': flag_g}
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

    suma = "Nie udało się odczytać sumy z paragonu!"
    for elem in text.split("\n"):
        if "suma" in elem.lower():
            suma = elem

    img = cv2.imread(f'media/{receipt.receipt_img}', cv2.IMREAD_GRAYSCALE)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # kernel = np.ones((5, 5), np.uint8)
    # kernel2 = np.ones((7, 7), np.uint8)
    # # img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    # t, img = cv2.threshold(img,1,255,cv2.THRESH_BINARY)
    # d = pytesseract.image_to_data(img, output_type=Output.DICT)
    # text = pytesseract.image_to_string(img, config=custom_config)
    # print(text)
    # n_boxes = len(d['level'])
    # for i in range(n_boxes):
    #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (10, 255, 0), 2)

    # img = cv2.resize(img, (960, 700))
    # plt.imshow(img, 'gray')
    # plt.show()

    context = {'receipt': receipt, 'text': text, 'suma': suma}
    return render(request, 'receipts/receipt_site.html', context)


@login_required
def new_guarantee(request):
    if request.method == 'POST':
        form = GuaranteeForm(request.POST, request.FILES)

        if form.is_valid():
            new_guar = form.save(commit=False)
            new_guar.owner = request.user
            new_guar.save()
            return redirect('receipts:your_receipts')
    else:
        form = GuaranteeForm()
    context = {'form': form}

    return render(request, 'receipts/new_guarantee.html', context)


def receipts_page(request):
    context = {}
    return render(request, 'receipts/receipts_page.html', context)


def expenses_page(request):
    expenses = Expense.objects.all()
    context = {'expenses': expenses}
    return render(request, 'receipts/expenses_page.html', context)


def expense_site(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    context = {'expense': expense}
    return render(request, 'receipts/expense_site.html', context)


def guarantee_site(request, guarantee_id):
    guarantee = Guarantee.objects.get(id=guarantee_id)
    context = {'guarantee': guarantee}
    return render(request, 'receipts/guarantee_site.html', context)


def receipt_by_hand(request):
    if request.method == 'POST':
        form = HandReceiptForm(request.POST, request.FILES)

        if form.is_valid():
            new_rec = form.save(commit=False)
            new_rec.owner = request.user
            new_rec.save()
            return redirect('receipts:your_receipts')
    else:
        form = HandReceiptForm()
    context = {'form':form}
    return render(request, 'receipts/receipt_by_hand.html', context)


def edit_expense(request,expense_id):
    exp = Expense.objects.get(id=expense_id)
    form = None
    context = {'form': form, 'expense':exp }
    return render(request, 'receipts/edit_expense.html', context)


def edit_guarantee(request,guarantee_id):
    guar = Guarantee.objects.get(id=guarantee_id)
    form = None
    context = {'form': form, 'guarantee': guar }
    return render(request, 'receipts/edit_guarantee.html', context)


def edit_receipt(request,receipt_id):
    rec = Receipt.objects.get(id=receipt_id)
    form = None
    context = {'form': form, 'receipt': rec}
    return render(request, 'receipts/edit_receipt.html', context)