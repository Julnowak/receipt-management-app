import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Receipt, Guarantee, Expense
from receipts.forms import ReceiptForm, ExpenseForm, GuaranteeForm, HandReceiptForm
import pytesseract
from profile_mangement.models import ProfileInfo
from categories.models import Product
from PIL import Image
import matplotlib.pyplot as plt
from receipts.image_processing import *
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

from django.db.models import CharField
from django.db.models.functions import Lower

CharField.register_lookup(Lower)


def OCR_site(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)

    img = Image.open(f'media/{receipt.receipt_img}').convert('RGB')
    img = np.array(img)
    img = remove_noise(img)
    img = thresholding(get_grayscale(img))


    width = img.shape[1]
    height = img.shape[0]
    text=''

    p = 0
    i = height // 3
    custom_config = r'--oem 1 --psm 6 -l pol'

    text += pytesseract.image_to_string(img, config=custom_config)
    angle, img = correct_skew(img)
    print(angle)


    # img = cv2.fastNlMeansDenoisingColored(img, None, 9, 6, 7, 21)


    ratio = img.shape[0] / 2000.0
    img_resize = imutils.resize(img, height=2000)


    img_array = np.array(img_resize)

    if np.mean(img_array[:, :]) < 200:
        blurred_image = cv2.GaussianBlur(erode(img_resize), (3, 3), 0)
        edged_img = cv2.Canny(blurred_image, 80, 200)
        pts = np.argwhere(edged_img > 0)

        # Finding the min and max points
        y1, x1 = pts.min(axis=0)
        y2, x2 = pts.max(axis=0)

        # Crop ROI from the givn image
        output_image = img_resize[y1:y2, x1:x2]
        org = output_image
    else:
        org = img_resize

    img = thresholding(org)
    height, width = img.shape[0], img.shape[1]

    p = 0
    i = int(height / 3)
    num = 0
    custom_config = r'--oem 1 --psm 6 -l pol'

    while num != 3:
        if num == 2:
            cropped_image = img[p:, :]
        else:
            cropped_image = img[p:i, :]
        p = i
        i += height // 3
        num += 1
        text += pytesseract.image_to_string(cropped_image, config=custom_config)

    p = 0
    i = int(height / 2)
    num = 0

    text += pytesseract.image_to_string(img, config=custom_config)
    while num != 2:
        if num == 1:
            cropped_image = img[p:, :]
        else:
            cropped_image = img[p:i, :]
        p = i
        i += height // 2
        num += 1
        text += pytesseract.image_to_string(cropped_image, config=custom_config)


    suma = "Nie udało się odczytać sumy z paragonu!"
    list_of_prod = []
    for elem in text.split("\n"):
        for e in elem.split(" "):
            prod = Product.objects.filter(product_name__unaccent__lower__trigram_similar=e)
            print(prod)

            # zakładam że znajdzie jeden
            if prod and prod[0] not in receipt.products.all():
                receipt.products.add(prod[0].id)

        if re.match(f"(\d+-\d+-\d+)",elem) or re.match(f"(\d+.\d+.\d+)",elem):
            date_string = re.findall(f"(\d+-\d+-\d+)", elem)
            if date_string:
                date_string = date_string[0]
                print(date_string[5:3])
                y = int(date_string[6:11])
                m = int(date_string[3:5])
                d = int(date_string[:2])

                if y > datetime.date.today().year:
                    y = datetime.date.today().year

                if m > 12:
                    m = datetime.date.today().month

                if d > 31:
                    m = datetime.date.today().day

                date_bought = datetime.date(y, m, d)
                receipt.date_of_receipt_bought = date_bought

        if "suma" in elem.lower() or "do zapłaty" in elem.lower() or "gotówka" in elem.lower():
            suma = elem

            if "," in suma:
                s = re.findall(f"(\d+,\d+)", suma)[0]
                receipt.amount = float(s.replace(",", "."))
            elif "." in suma:
                s = re.findall(f"(\d+.\d+)", suma)[0]
                receipt.amount = float(s)
            else:
                receipt.amount = 0.00

            receipt.receipt_text_read_by_OCR = text

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


def receipt_data_read(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)
    context = {'receipt': receipt}
    return render(request, 'receipts/receipt_data_read.html', context)