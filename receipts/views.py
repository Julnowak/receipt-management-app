import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt, Guarantee, Expense
from receipts.forms import ReceiptForm, ExpenseForm, GuaranteeForm, HandReceiptForm
import pytesseract
from profile_mangement.models import ProfileInfo
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import re
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
    guarant = Guarantee.objects.filter(owner=request.user)
    left = []
    for guarantee in guarant:
       result = guarantee.end_date - datetime.date.today()
       if int(result.days) < 0:
           guarant.get(id=guarantee.id).delete()
           guarant.delete()
       else:
            left.append(result)
    guarant = Guarantee.objects.filter(owner=request.user)[:5]
    info = zip(guarant, left)
    context = {'receipts': receipts, 'expenses': expenses, 'guarantees': guarant, 'info': info,
               'flag': flag, 'flag_e': flag_e, 'flag_g': flag_g}
    return render(request, 'receipts/your_receipts.html', context)


@login_required
def new_receipt(request):
    profile = ProfileInfo.objects.get(user=request.user)
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)

        if form.is_valid():
            new_receipt = form.save(commit=False)
            new_receipt.owner = request.user
            new_receipt.save()
            profile.how_many_receipts += 1
            profile.save()
            return redirect('receipts:OCR_site', receipt_id=new_receipt.id)
    else:
        form = ReceiptForm()
    return render(request, 'receipts/new_receipt.html', {'form': form})


def costs_by_hand(request):
    profile = ProfileInfo.objects.get(user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.owner = request.user
            form.save()
            profile.how_many_expenses +=1
            profile.save()
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
    img = np.asarray(Image.open(f'media/{receipt.receipt_img}'))
    gray_image = cv2.cvtColor(img, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(gray_image, (15, 15), 0)
    # ret, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    plt.imshow(blur)
    plt.show()
    # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    # dilation = cv2.dilate(thresh, rect_kernel, iterations=1)
    #
    # contours, hierachy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # plt.imshow(cropped)
    # plt.show()

    context = {'receipt': receipt}
    return render(request, 'receipts/receipt_site.html', context)


@login_required
def new_guarantee(request):
    profile = ProfileInfo.objects.get(user=request.user)
    if request.method == 'POST':
        form = GuaranteeForm(request.POST, request.FILES)

        if form.is_valid():
            new_guar = form.save(commit=False)
            new_guar.owner = request.user
            new_guar.save()
            profile.how_many_guarantees +=1
            profile.save()
            return redirect('receipts:your_receipts')
    else:
        form = GuaranteeForm()
    context = {'form': form}

    return render(request, 'receipts/new_guarantee.html', context)


def receipts_page(request):
    receipts = Receipt.objects.filter(owner=request.user).order_by('-date_added')
    context = {'receipts': receipts}
    return render(request, 'receipts/receipts_page.html', context)


def expenses_page(request):
    expenses = Expense.objects.all(owner=request.user).order_by('-date_added')
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


def edit_expense(request, expense_id):
    exp = Expense.objects.get(id=expense_id)

    if request.method == 'POST':
        form = ExpenseForm(instance=exp, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('receipts:expense_site', expense_id=exp.id)
    else:
        form = ExpenseForm(instance=exp)

    context = {'expense':exp, 'form': form}
    return render(request, 'receipts/edit_expense.html', context)


def edit_guarantee(request,guarantee_id):
    guar = Guarantee.objects.get(id=guarantee_id)
    if request.method == 'POST':
        form = GuaranteeForm(instance=guar, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('receipts:guarantee_site', guarantee_id=guar.id)
    else:
        form = GuaranteeForm(instance=guar)
    context = {'form': form, 'guarantee': guar }
    return render(request, 'receipts/edit_guarantee.html', context)


def edit_receipt(request, receipt_id):
    rec = Receipt.objects.get(id=receipt_id)
    if request.method == 'POST':
        form = ReceiptForm(instance=rec, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('receipts:receipt_site', receipt_id=rec.id)
    else:
        form = ReceiptForm(instance=rec)
    context = {'form': form, 'receipt': rec}
    return render(request, 'receipts/edit_receipt.html', context)


def rotate(image, angle, center=None, scale=0.8):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated


def OCR_site(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)
    custom_config = r'--oem 1 --psm 6 -l pol'
    img = Image.open(f'media/{receipt.receipt_img}').convert('RGB')
    open_cv_image = np.array(img)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    rot = pytesseract.image_to_osd(img, output_type='dict')['orientation']
    if rot != 0:
        img = rotate(open_cv_image, rot)
        receipt.receipt_img = img
        receipt.save()
        plt.imshow(img)
        plt.show()
    text = pytesseract.image_to_string(img, config=custom_config)
    print(text)

    suma = "Nie udało się odczytać sumy z paragonu!"
    for elem in text.split("\n"):
        if "suma" in elem.lower() or "do zapłaty" in elem.lower() or "gotówka" in elem.lower():
            suma = elem
            try:
                if "," in suma:
                    s = re.findall(f"(\d+,\d+)", suma)[0]
                    receipt.amount = float(s.replace(",", "."))
                elif "." in suma:
                    s = re.findall(f"(\d+.\d+)", suma)[0]
                    receipt.amount = float(s)
                receipt.save()
            except:
                receipt.amount = 0.00
                receipt.save()

    img = cv2.imread(f'media/{receipt.receipt_img}', cv2.IMREAD_GRAYSCALE)

    if request.method == 'POST':
        form = ReceiptForm(instance=receipt, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('receipts:receipt_site', receipt_id=receipt.id)
    else:
        form = ReceiptForm(instance=receipt)
    context = {'form': form, 'receipt': receipt,'img': img, 'suma': suma}
    return render(request, 'receipts/OCR_site.html', context)