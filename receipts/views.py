import datetime
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import Receipt, Guarantee, Expense
from groups.models import CommonGroups
from receipts.forms import ReceiptForm, ExpenseForm, GuaranteeForm, HandReceiptForm
from categories.models import Product
from django.contrib import messages
import re
from categories.models import BaseCategories
from django.shortcuts import get_object_or_404
from pdf2image import convert_from_path
import calendar
from collections import Counter
from promotions_and_discounts.models import Shop
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from receipts.OCR_algorithm import *
from django.db.models import CharField
from django.db.models.functions import Lower

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\path\to\poppler-xx\bin"

CharField.register_lookup(Lower)


def month_map(name):
    month = {
        'stycznia': 1,
        'lutego': 2,
        'marca': 3,
        'kwiecietnia': 4,
        'maja': 5,
        'czerwca': 6,
        'lipca': 7,
        'sierpnia': 8,
        'września': 9,
        'października': 10,
        'listopada': 11,
        'grudzieńa': 12
    }
    return month[name]

########## STRONA GŁÓWNA ##########
@login_required
def your_receipts(request):
    if len(Receipt.objects.filter(owner=request.user, is_deleted=False)) > 5:
        flag = True
    else:
        flag = False

    if len(Expense.objects.filter(owner=request.user, is_deleted=False)) > 5:
        flag_e = True
    else:
        flag_e = False

    if len(Guarantee.objects.filter(owner=request.user, is_deleted=False)) > 5:
        flag_g = True
    else:
        flag_g = False

    receipts = Receipt.objects.filter(owner=request.user,is_deleted=False).order_by("-id")[:5]
    expenses = Expense.objects.filter(owner=request.user,is_deleted=False).order_by("-id")[:5]
    guarant = Guarantee.objects.filter(owner=request.user,is_deleted=False)
    left = []
    flags = []
    for guarantee in guarant:
        result = guarantee.end_date - datetime.date.today()
        if int(result.days) < 0:
            g = guarant.get(id=guarantee.id)
            g.is_deleted = True
            g.save()
        else:
            left.append(result)

            if int(result.days) < 3:
                flags.append(True)
            else:
                flags.append(False)
    guarant = Guarantee.objects.filter(owner=request.user,is_deleted=False)[:5]

    info = zip(guarant, left, flags)
    info = sorted(list(info), key=lambda x: x[1], reverse=False)
    context = {'receipts': receipts, 'expenses': expenses, 'guarantees': guarant, 'info': info,
               'flag': flag, 'flag_e': flag_e, 'flag_g': flag_g}
    return render(request, 'receipts/your_receipts.html', context)


########## OPŁATY ##########
@login_required
def costs_by_hand(request):

    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
            flag = request.POST['flag']
    else:
        flag = None

    if 'group' in request.GET:
        group = get_object_or_404(CommonGroups, id=int(request.GET['group']))
    elif 'group' in request.POST:
            group = get_object_or_404(CommonGroups, id=int(request.POST['group']))
    else:
        group = None

    groups = CommonGroups.objects.filter(members__username=request.user.username)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            if form.data['group']:
                g = groups.get(id=int(form.data['group']))
                if g.can_receipts_be_added:
                    suma = sum(list(i[0] for i in g.expense_set.values_list('amount'))) + sum(
                        list(i[0] for i in g.receipt_set.values_list('amount')))
                    if (g.limit and float(suma) + float(form.data['amount']) <= g.limit) or not g.limit:
                        cost.owner = request.user
                        form.save()
                        messages.success(request, f"Dodano opłatę.")
                        if flag == "group":
                            return redirect('groups:group_receipts_and_expenses', group_id=group.id)
                        else:
                            return redirect('receipts:your_receipts')
                    else:
                        messages.error(request, f"Przekroczono limit grupy.")
                else:
                    messages.error(request, f"Dana grupa nie przyjmuje już opłat.")
            else:
                cost.owner = request.user
                form.save()
                messages.success(request, f"Dodano opłatę.")
                return redirect('receipts:your_receipts')
    else:
        form = ExpenseForm()

    context = {'form': form, 'group': group, 'flag': flag}
    return render(request, 'receipts/costs_by_hand.html', context)


@login_required
def add_expense_from_grouppage(request, group_id):
    return redirect('{}?flag=group&group={}'.format(reverse('receipts:costs_by_hand'), group_id))


@login_required
def add_expense_from_mainpage(request):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:costs_by_hand')))

@login_required
def expenses_page(request):
    expenses = Expense.objects.filter(owner=request.user, is_deleted=False).order_by('-date_added')
    only_starred = request.GET.get('only_starred', False)
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    name = request.GET.get('name', '')
    from_number = request.GET.get('from_number', '')
    to_number = request.GET.get('to_number', '')

    if request.POST:
        if 'only_starred_lists' in request.POST:
            only_starred = request.POST['only_starred_lists']
            if only_starred == 'on':
                only_starred = 'True'
            else:
                only_starred = 'False'

        else:
            only_starred = 'False'

        if 'from_date' in request.POST:
            if request.POST['from_date']:
                from_date = request.POST['from_date']
                from_date = datetime.date(int(from_date[:4]),int(from_date[5:7]),int(from_date[8:10]))

        if 'to_date' in request.POST:
            if request.POST['to_date']:
                to_date = request.POST['to_date']
                to_date = datetime.date(int(to_date[:4]), int(to_date[5:7]), int(to_date[8:10]))

        if 'name' in request.POST:
            name = request.POST['name']

        if 'from_number' in request.POST:
            from_number = request.POST['from_number']

        if 'to_number' in request.POST:
            to_number = request.POST['to_number']

    if only_starred == 'True':
        expenses = expenses.filter(is_starred=True)

    if from_date and to_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]),int(month_map(lst[1])),int(lst[0]))
        except:
            pass
        if from_date == to_date:
            expenses = expenses.filter(date_added__range=[from_date, (to_date + datetime.timedelta(days=1))])
        else:
            expenses = expenses.filter(date_added__range=[from_date, to_date])
    elif from_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]), int(month_map(lst[1])), int(lst[0]))
        except:
            pass
        expenses = expenses.filter(date_added__range=[from_date,datetime.date.today()])

    if name:
        expenses = expenses.filter(expense_name__contains=name)

    if from_number and to_number:
        expenses = expenses.filter(amount__range=[from_number, to_number])

    page_number = request.GET.get('page', 1)
    p = Paginator(expenses, 6)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'expenses': expenses, 'pages': pages, 'only_starred': only_starred,'to_date': to_date,
               'from_date':from_date, }
    return render(request, 'receipts/expenses_page.html', context)


# Strona opłat i jej warianty
@login_required
def expense_site(request, expense_id):
    if 'flag' in request.GET:
        flag = request.GET['flag']
    else:
        flag = None

    if 'group' in request.GET:
        group = get_object_or_404(CommonGroups, id=int(request.GET['group']))
    else:
        group = None

    expense = Expense.objects.get(id=expense_id)
    context = {'expense': expense, 'user': request.user, 'flag': flag, 'group': group }
    return render(request, 'receipts/expense_site.html', context)


@login_required
def expense_site_from_mainpage(request, expense_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:expense_site', kwargs={'expense_id': expense_id})))


@login_required
def expense_site_from_grouppage(request, expense_id, group_id):
    return redirect('{}?flag=group&group={}'.format(reverse('receipts:expense_site',kwargs={'expense_id':expense_id}), group_id))


@login_required
def change_expense_starred_status(request, expense_id):

    expense = get_object_or_404(Expense, pk=expense_id)
    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
        flag = request.POST['flag']
    else:
        flag = None

    if 'group' in request.GET:
        group = get_object_or_404(CommonGroups, id=int(request.GET['group']))
    elif 'group' in request.POST:
        group = request.POST['group']
    else:
        group = None
    if expense.is_starred:
        expense.is_starred = False
    else:
        expense.is_starred = True
    expense.save()
    print(flag)
    if flag == "group":
        return redirect('{}?flag=group&group={}'.format(reverse('receipts:expense_site_from_grouppage',kwargs={'expense_id':expense_id}), int(group.id)))
    elif flag == "mainpage":
        return redirect('{}?flag=mainpage'.format(reverse('receipts:expense_site_from_mainpage', kwargs={'expense_id': expense_id})))
    else:
        return redirect('receipts:expense_site', expense_id=expense.id)


@login_required
def change_expense_starred_status_fromgroup(request, expense_id, group_id):
    return redirect('{}?flag=group&group={}'.format(reverse('receipts:change_expense_starred_status',kwargs={'expense_id':expense_id}), group_id))


@login_required
def change_expense_starred_status_mainpage(request, expense_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:change_expense_starred_status',kwargs={'expense_id':expense_id})))


# Strona edycji opłat i jej warianty
@login_required
def edit_expense(request, expense_id):
    exp = Expense.objects.get(id=expense_id)
    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
        flag = request.POST['flag']
    else:
        flag=None

    if 'group' in request.GET:
        group = get_object_or_404(CommonGroups, id=int(request.GET['group']))
    elif 'group' in request.POST:
        group = request.POST['group']
    else:
        group = None

    if request.method == 'POST':
        form = ExpenseForm(instance=exp, data=request.POST)
        if form.is_valid():
            form.save()
            if flag == "group":
                return redirect('receipts:expense_site_from_grouppage', expense_id=exp.id, group_id= int(group))
            elif flag == "mainpage":
                            return redirect('receipts:expense_site_from_mainpage', expense_id=exp.id)
            else:
                return redirect('receipts:expense_site', expense_id=exp.id)
    else:
        form = ExpenseForm(instance=exp)

    context = {'expense': exp, 'form': form, 'flag': flag, 'group': group}
    return render(request, 'receipts/edit_expense.html', context)


@login_required
def edit_expense_group(request, expense_id, group_id):
    return redirect('{}?flag=group&group={}'.format(reverse('receipts:edit_expense',kwargs={'expense_id':expense_id}), group_id))


@login_required
def edit_expense_mainpage(request, expense_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:edit_expense',kwargs={'expense_id':expense_id})))


@login_required
def delete_expense(request, expense_id):
    exp = Expense.objects.get(id=expense_id)
    exp.is_deleted = True
    exp.save()
    return redirect("receipts:expenses_page")


@login_required
def delete_expense_group(request, expense_id, group_id):
    exp = Expense.objects.get(id=expense_id)
    exp.is_deleted = True
    exp.save()
    return redirect("groups:group_receipts_and_expenses", group_id=group_id)


@login_required
def expense_settings(request):
    context = {'user': request.user}
    return render(request, 'receipts/expense_settings.html', context)


########## GWARANCJE ##########
@login_required
def guarantees(request):
    guarantees = Guarantee.objects.filter(owner=request.user, is_deleted=False)
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    name = request.GET.get('name', '')
    from_number = request.GET.get('from_number', '')
    to_number = request.GET.get('to_number', '')

    # POTRZEBA DOSTOSOWANIA PAGINATORA
    if request.POST:

        if 'from_date' in request.POST:
            if request.POST['from_date']:
                from_date = request.POST['from_date']
                from_date = datetime.date(int(from_date[:4]),int(from_date[5:7]),int(from_date[8:10]))

        if 'to_date' in request.POST:
            if request.POST['to_date']:
                to_date = request.POST['to_date']
                to_date = datetime.date(int(to_date[:4]), int(to_date[5:7]), int(to_date[8:10]))

        if 'name' in request.POST:
            name = request.POST['name']

        if 'from_number' in request.POST:
            from_number = request.POST['from_number']

        if 'to_number' in request.POST:
            to_number = request.POST['to_number']

    if from_date and to_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]),int(month_map(lst[1])),int(lst[0]))
        except:
            pass
        if from_date == to_date:
            guarantees = guarantees.filter(date_added__range=[from_date, (to_date + datetime.timedelta(days=1))])
        else:
            guarantees = guarantees.filter(date_added__range=[from_date, to_date])
    elif from_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]), int(month_map(lst[1])), int(lst[0]))
        except:
            pass
        guarantees = guarantees.filter(date_added__range=[from_date,datetime.date.today()])

    if name:
        guarantees = guarantees.filter(guarantee_name__contains=name)

    if from_number and to_number:
        guarantees = guarantees.filter(amount__range=[from_number, to_number])

    left = []
    flags = []
    for guarantee in guarantees:
        result = guarantee.end_date - datetime.date.today()
        if int(result.days) < 0:
            g = guarantees.get(id=guarantee.id)
            g.is_deleted = True
            g.save()
        else:
            left.append(result)

            if int(result.days) < 3:
                flags.append(True)
            else:
                flags.append(False)

    info = zip(guarantees, left, flags)
    info = sorted(list(info), key=lambda x: x[1], reverse=False)

    page_number = request.GET.get('page', 1)
    p = Paginator(info, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'to_date': to_date,
               'from_date':from_date,'from_number':from_number,'to_number': to_number, 'name': name,
               'guarantees': guarantees, 'time_left': left,'pages': pages, 'info': info}
    return render(request, 'receipts/guarantees.html', context)


@login_required
def new_guarantee(request):

    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
        flag = request.POST['flag']
    else:
        flag = None

    if request.method == 'POST':
        form = GuaranteeForm(request.POST, request.FILES)

        if form.is_valid():
            new_guar = form.save(commit=False)
            new_guar.owner = request.user
            new_guar.save()
            if flag == "mainpage":
                return redirect('receipts:your_receipts')
            else:
                return redirect('receipts:guarantees')
    else:
        form = GuaranteeForm()
    context = {'form': form, 'flag': flag}
    return render(request, 'receipts/new_guarantee.html', context)


@login_required
def new_guarantee_from_mainpage(request):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:new_guarantee')))


@login_required
def edit_guarantee(request, guarantee_id):
    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
        flag = request.POST['flag']
    else:
        flag = None

    guar = Guarantee.objects.get(id=guarantee_id)
    if request.method == 'POST':
        form = GuaranteeForm(instance=guar, data=request.POST)
        if form.is_valid():
            form.save()
            if flag == "mainpage":
                return redirect('receipts:guarantee_site_from_mainpage', guarantee_id=guar.id)
            else:
                return redirect('receipts:guarantee_site', guarantee_id=guar.id)
    else:
        form = GuaranteeForm(instance=guar)
    context = {'form': form, 'guarantee': guar, 'flag': flag}
    return render(request, 'receipts/edit_guarantee.html', context)


def edit_guarantee_mainpage(request, guarantee_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:edit_guarantee', kwargs={"guarantee_id": guarantee_id})))


@login_required
def delete_guarantee(request, guarantee_id):
    guar = Guarantee.objects.get(id=guarantee_id)
    guar.is_deleted = True
    guar.save()
    return redirect("receipts:guarantees")


@login_required
def delete_guarantee_mainpage(request, guarantee_id):
    guar = Guarantee.objects.get(id=guarantee_id)
    guar.is_deleted = True
    guar.save()
    return redirect("receipts:your_receipts")


@login_required
def guarantee_settings(request):
    context = {'user': request.user}
    return render(request, 'receipts/guarantee_settings.html', context)


# Strona gwarancji i jej warianty
@login_required
def guarantee_site(request, guarantee_id):
    guarantee = Guarantee.objects.get(id=guarantee_id)
    if 'flag' in request.GET:
        flag = request.GET['flag']
    else:
        flag = None
    context = {'guarantee': guarantee, 'days_left': (guarantee.end_date - datetime.date.today()).days,
               'user': request.user, 'flag': flag}
    return render(request, 'receipts/guarantee_site.html', context)


@login_required
def guarantee_site_from_mainpage(request, guarantee_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:guarantee_site', kwargs={"guarantee_id": guarantee_id})))


# Poprawić oblicznie
@login_required
def elongate_guarantee(request, guarantee_id):
    guarantee = Guarantee.objects.get(id=guarantee_id)

    if 'flag' in request.GET:
        flag = request.GET['flag']
    elif 'flag' in request.POST:
        flag = request.POST['flag']
    else:
        flag = None

    if request.POST:
        type_of_number = request.POST.get('type_of_number')
        number = request.POST.get('number')
        if type_of_number == 'dni':
            guarantee.end_date += datetime.timedelta(days=int(number))
        elif type_of_number == 'miesięcy':
            years = int(number) // 12
            months = int(guarantee.end_date.month) + int(number) % 12
            if months > 12:
                years += months // 12
                months = months % 12
            guarantee.end_date = datetime.date(int(guarantee.end_date.year) + years,
                                               months, int(guarantee.end_date.day))
        elif type_of_number == 'lat':
            guarantee.end_date = datetime.date(int(guarantee.end_date.year) + int(number), int(guarantee.end_date.month), int(guarantee.end_date.day))
        guarantee.save()
        if flag == "mainpage":
            return redirect('receipts:guarantee_site_from_mainpage', guarantee_id=guarantee_id)
        else:
            return redirect('receipts:guarantee_site', guarantee_id=guarantee_id)
    context = {'guarantee': guarantee,'user': request.user,'guarantee_id': guarantee_id, 'flag': flag}
    return render(request, 'receipts/elongate_guarantee.html', context )


@login_required
def elongate_guarantee_mainpage(request, guarantee_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:elongate_guarantee', kwargs={"guarantee_id": guarantee_id})))


########## PARAGONY ##########
@login_required
def receipt_site(request, receipt_id):
    flag = None
    group = None
    if 'flag' in request.GET:
        flag = request.GET['flag']

    if 'group' in request.GET:
        group = get_object_or_404(CommonGroups, id=int(request.GET['group']))

    receipt = get_object_or_404(Receipt, id=receipt_id)
    categs = receipt.receipt_categories.all()
    prods = receipt.products.all()
    guars = receipt.guarantee_set.all()

    context = {'receipt': receipt, 'receipt_categoreis': categs, 'receipt_products': prods, 'user': request.user,
                'guarantees': guars, 'flag': flag, 'group': group}
    return render(request, 'receipts/receipt_site.html', context)


@login_required
def receipt_site_from_mainpage(request, receipt_id):
    return redirect('{}?flag=mainpage'.format(reverse('receipts:receipt_site',kwargs={'receipt_id': receipt_id})))


@login_required
def receipt_site_from_grouppage(request, receipt_id, group_id):
    return redirect('{}?flag=group&group={}'.format(reverse('receipts:receipt_site',kwargs={'receipt_id': receipt_id}), group_id))


@login_required
def new_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            new_receipt = form.save(commit=False)
            new_receipt.owner = request.user
            new_receipt.save()
            return redirect('receipts:OCR_site', receipt_id=new_receipt.id)
    else:
        form = ReceiptForm()
    return render(request, 'receipts/new_receipt.html', {'form': form})


@login_required
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


@login_required
def change_receipt_starred_status(request, receipt_id):
    receipt = get_object_or_404(Receipt, pk=receipt_id)
    if receipt.is_starred:
        receipt.is_starred = False
    else:
        receipt.is_starred = True
    receipt.save()
    return redirect("receipts:receipt_site", receipt_id=receipt.id)


@login_required
def receipts_page(request):
    receipts = Receipt.objects.filter(owner=request.user, is_deleted=False).order_by('-date_added')
    only_starred = request.GET.get('only_starred', False)
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    name = request.GET.get('name', '')
    from_number = request.GET.get('from_number', '')
    to_number = request.GET.get('to_number', '')

    # POTRZEBA DOSTOSOWANIA PAGINATORA
    if request.POST:
        if 'only_starred_lists' in request.POST:
            only_starred = request.POST['only_starred_lists']
            if only_starred == 'on':
                only_starred = 'True'
            else:
                only_starred = 'False'

        else:
            only_starred = 'False'

        if 'from_date' in request.POST:
            if request.POST['from_date']:
                from_date = request.POST['from_date']
                from_date = datetime.date(int(from_date[:4]),int(from_date[5:7]),int(from_date[8:10]))

        if 'to_date' in request.POST:
            if request.POST['to_date']:
                to_date = request.POST['to_date']
                to_date = datetime.date(int(to_date[:4]), int(to_date[5:7]), int(to_date[8:10]))

        if 'name' in request.POST:
            name = request.POST['name']

        if 'from_number' in request.POST:
            from_number = request.POST['from_number']

        if 'to_number' in request.POST:
            to_number = request.POST['to_number']

    if only_starred == 'True':
        receipts = receipts.filter(is_starred=True)

    if from_date and to_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]),int(month_map(lst[1])),int(lst[0]))
        except:
            pass
        if from_date == to_date:
            receipts = receipts.filter(date_added__range=[from_date, (to_date + datetime.timedelta(days=1))])
        else:
            receipts = receipts.filter(date_added__range=[from_date, to_date])
    elif from_date:
        try:
            lst = from_date.split()
            from_date = datetime.date(int(lst[2]), int(month_map(lst[1])), int(lst[0]))
        except:
            pass
        receipts = receipts.filter(date_added__range=[from_date,datetime.date.today()])

    if name:
        receipts = receipts.filter(receipt_name__contains=name)

    if from_number and to_number:
        receipts = receipts.filter(amount__range=[from_number, to_number])

    page_number = request.GET.get('page', 1)
    p = Paginator(receipts, 6)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'receipts': receipts, 'pages': pages, 'only_starred': only_starred,'to_date': to_date,
               'from_date':from_date,'from_number':from_number,'to_number': to_number, 'name': name }
    return render(request, 'receipts/receipts_page.html', context)


@login_required
def receipt_by_hand(request):
    groups = CommonGroups.objects.filter(members__username=request.user.username)
    if request.method == 'POST':
        form = HandReceiptForm(request.POST, request.FILES)

        if form.is_valid():
            g = groups.get(id=int(form.data['group']))
            new_rec = form.save(commit=False)

            if g.can_receipts_be_added:
                suma = sum(list(i[0] for i in g.expense_set.values_list('amount'))) + sum(
                    list(i[0] for i in g.receipt_set.values_list('amount')))
                if g.limit and float(suma) + float(form.data['amount']) <= g.limit:
                    new_rec.owner = request.user
                    form.save()
                    new_rec.save()
                    messages.success(request, f"Dodano opłatę.")
                    return redirect('receipts:your_receipts')
                elif not g.limit:
                    new_rec.owner = request.user
                    form.save()
                    new_rec.save()
                    messages.success(request, f"Dodano opłatę.")
                    return redirect('receipts:your_receipts')
                else:
                    messages.error(request, f"Przekroczono limit grupy.")
    else:
        form = HandReceiptForm()
    context = {'form': form}
    return render(request, 'receipts/receipt_by_hand.html', context)


@login_required
def delete_receipt(request, receipt_id):
    rec = Receipt.objects.get(id=receipt_id)
    rec.is_deleted = True
    rec.save()
    return redirect("receipts:receipts_page")


@login_required
def OCR_site(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)

    if request.method == 'POST':
        form = ReceiptForm(instance=receipt, data=request.POST)

        # Weź dzisiejszą datę
        ##### GUARANTEE PART #####
        y = datetime.date.today().year
        m = datetime.date.today().month
        d = datetime.date.today().day

        guar_date_num = int(request.POST['input_guarant'])
        guar_date_type = request.POST['select_guarant']

        new_y = y
        new_m = m
        new_d = d
        if guar_date_num > 0:
            if guar_date_type == 'dni':
                new_d = d + guar_date_num
                if new_d > 28:
                    # luty przestępny
                    if m == 2 and y%4 == 0:
                        if new_d > 29:
                            new_d = new_d - 29
                            new_m = m + 1
                        else:
                            new_d = new_d - 28
                            new_m = m + 1
                    if new_d > 30 and m in [4,6,9,11]:
                        new_d = new_d - 30
                        new_m = m + 1

                    if new_d > 31 and m in [1,3,5,7,8,10]:
                        new_d = new_d - 31
                        new_m = m + 1

                    if new_d>31 and m == 12:
                        new_d = new_d - 31
                        new_m = m + 1
                        new_y = y + 1

            elif guar_date_type == 'miesięcy':
                new_m = m + guar_date_num
                new_y = y
                if new_m > 12:
                    new_y = y + new_m // 12
                    new_m = new_m % 12

            else:
                new_y = y + guar_date_num

            new_date = datetime.date(new_y, new_m, new_d)
        #########################

        if form.is_valid():
            form.save()
            if guar_date_num > 0:
                new_guar = Guarantee.objects.create(guarantee_name=receipt.receipt_name,
                                                    end_date=new_date,
                                                    owner=request.user)
                new_guar.receipt = receipt
                new_guar.save()
            return redirect('receipts:receipt_site', receipt_id=receipt.id)
    else:
        if receipt.receipt_img and (".pdf" in receipt.receipt_img.url or ".png" in receipt.receipt_img.url
                                    or ".jpg" in receipt.receipt_img.url):
            if ".pdf" in receipt.receipt_img.url:
                img = convert_from_path(f'media/{receipt.receipt_img}',
                                        poppler_path=r"..\ZebragonApp\poppler-23.11.0\Library\bin")
                new_name = 'images/' + receipt.receipt_img.url[14:len(receipt.receipt_pdf.url) - 4] + '.jpg'
                img[0].save(f'media/{new_name}', 'JPEG')
                receipt.receipt_img = new_name

            img = cv2.imread(f'media/{receipt.receipt_img}')
            print('START')
            main_price, dat_dat, shop_shop, category, cases = make_OCR(img)
            print("STOP")
            try:
                receipt.amount = float(main_price.replace(",", "."))
            except:
                receipt.amount = 0.00

            try:
                receipt.date_of_receipt_bought = dat_dat
            except:
                receipt.date_of_receipt_bought = datetime.date.today()

            for prod in receipt.products.all():
                receipt.receipt_categories.add(prod.subcategory.category)

            try:
                print(shop_shop)
                receipt.shop = Shop.objects.get(shop_name=shop_shop.capitalize())
            except:
                receipt.shop = None
            receipt.save()

            if receipt.shop is None:
                receipt.shop = Shop.objects.get(shop_name='Inne')

            if receipt.shop:
                for cat in receipt.shop.category.all():
                    receipt.receipt_categories.add(cat)

            receipt.save()
            form = ReceiptForm(instance=receipt)
        else:
            return redirect('receipts:new_receipt')

    context = {'form': form, 'receipt': receipt, 'img': img, 'suma': main_price}
    return render(request, 'receipts/OCR_site.html', context)


@login_required
def receipt_data_read(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id,is_deleted=False)
    context = {'receipt': receipt}
    return render(request, 'receipts/receipt_data_read.html', context)


@login_required
def receipt_settings(request):
    context = {'user': request.user}
    return render(request, 'receipts/receipt_settings.html', context)
