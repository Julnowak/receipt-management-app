from django.shortcuts import render, redirect
from .models import CommonGroups, User
from groups.forms import CommonGroupsForm
from django.contrib import messages
from my_messages.forms import MessageForm,HiddenMessageForm
from receipts.models import Expense, Receipt
from my_messages.models import Message
from django.template.defaultfilters import slugify
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


def groups(request):
    your_groups = CommonGroups.objects.filter(owner=request.user)
    member_of_groups = CommonGroups.objects.filter(members=request.user)
    context = {'your_groups': your_groups, "member_of_groups":member_of_groups}
    return render(request, 'groups/your_groups.html', context)


def group_site(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    members = group.members.all()
    user = request.user
    group_expenses = Expense.objects.filter(group=group_id)
    group_receipts = Receipt.objects.filter(group=group_id)

    suma_wydatki = 0
    suma_paragony = 0
    for expense in group_expenses.values_list('amount'):
        suma_wydatki += float(expense[0])

    for receipt in group_receipts.values_list('amount'):
        suma_paragony += float(receipt[0])

    suma_wydatki = round(float(suma_wydatki), 2)
    suma_paragony = round(float(suma_paragony), 2)
    suma = suma_wydatki + suma_paragony
    amount_per_member = math.ceil(suma/group.number_of_members * 100)/100
    context = {"group": group, "members": members, "user": user, "amount_per_member": amount_per_member, "suma":suma}
    return render(request, 'groups/group_site.html', context)


def invite_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0

    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user, members=group.members)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.title = "Zaproszenie do grupy " + group.group_name
            new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Zapraszam Cię do dołączenia do grupy " + group.group_name + "."
            new_message.message_type = "invitation"
            new_message.group = group
            new_message.save()
            messages.success(request, 'Wiadomość została wysłana.')
            return redirect('groups:group_site', group_id=group_id)
    else:
        form = MessageForm(user=request.user, members=group.members)

    context = {"group": group, "code": group.password, "form": form}
    return render(request, 'groups/invite_page.html', context)


def search(request, group_id):
    text = 'noOne'
    group = CommonGroups.objects.get(id=group_id)
    if request.method == 'POST':
        name = request.POST.get('textfield', None)
        try:
            user = User.objects.get(username=name)
            #do something with user

            if group.number_of_members >= group.max_number_of_members:
                text = "Osiągnięto limit członków grupy"
            else:
                text = user
                group.number_of_members = group.number_of_members + 1
                group.members.add(user)
                group.save()

        except User.DoesNotExist:
            text = "Nie ma takiego użytkownika"

    context = {'text': text, 'group': group}
    return render(request, 'groups/search.html', context)

    # context = {"group": group, "code": group.password,'form': form}
    # return render(request, 'groups/invite_page.html', context)


def leaving_group_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    if request.method == 'POST':
        name = request.POST.get('textfield', None)

    context = {"group": group, "user": request.user}
    return render(request, 'groups/leaving_group_page.html', context)


# TO DO
def add_group(request):
    if request.method == 'POST':
        form = CommonGroupsForm(request.POST)

        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.owner = request.user
            new_group.save()
            new_group.members.add(request.user)
            messages.success(request, 'Grupa została utworzona')
            return redirect('groups:groups')
    else:
        form = CommonGroupsForm()

    names = list(form._meta.labels.values())
    group_name = names[0]
    max_members = names[1]
    pswd = names[2]
    context = {'form': form, 'group_name': group_name, 'max_members': max_members, 'password': pswd}
    return render(request, 'groups/add_group.html', context)


def delete_group(request,group_id):
    deletion(group_id)
    return redirect('groups:groups')


def deletion(group_id):
    group = CommonGroups.objects.get(id=group_id)
    group.delete()


def left_group(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    user = request.user
    if group.number_of_members == 1:
        deletion(group_id)
    else:
        group.members.remove(user)
        group.number_of_members -= 1
        group.save()

    return redirect('groups:groups')


def manage_group(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    delete_member_fun = delete_member_from_group
    context = {"group": group, "user": request.user, 'members': group.members.all(), "delete_member_fun": delete_member_fun}
    return render(request, 'groups/manage_group.html', context)


def search_group(request):
    groups_searched = 'None'
    number = 0
    exists = False
    if request.method == 'POST':
        group_name = request.POST.get('q')

        try:
            groups_searched = CommonGroups.objects.filter(group_name__icontains=group_name)
            number = CommonGroups.objects.filter(group_name__icontains=group_name).count()
            exists = True
        except :
            groups_searched = "Nie ma takiej grupy"


    if number == 0:
        text = "Brak wyników."
    elif number == 1:
        text = "Znaleziono 1 wynik"
    elif number in [2,3,4]:
        text = f"Znaleziono {number} wyniki"
    else:
        text = f"Znaleziono {number} wyników"

    context = {"text":text,"user": request.user, 'exists': exists, 'groups': groups_searched, 'number': number}
    return render(request, 'groups/search_group.html', context)


def delete_member_from_group(member,group_id):
    group = CommonGroups.objects.get(id=group_id)
    group.members.remove(member)
    group.number_of_members -= 1
    group.save()


def group_receipts_and_expenses(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    number_of_members = group.number_of_members
    group_expenses = Expense.objects.filter(group=group_id).order_by("-date_added")
    group_receipts = Receipt.objects.filter(group=group_id).order_by("-date_added")

    suma_wydatki = 0
    suma_paragony = 0
    for expense in group_expenses.values_list('amount'):
        suma_wydatki += float(expense[0])

    for receipt in group_receipts.values_list('amount'):
        suma_paragony += float(receipt[0])

    suma_wydatki = round(float(suma_wydatki), 2)
    suma_paragony = round(float(suma_paragony), 2)
    suma = suma_wydatki + suma_paragony
    amount_per_member = math.ceil(suma/group.number_of_members * 100)/100

    p = Paginator(group_expenses, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)

    context = {'group': group, 'group_expenses': group_expenses, 'suma': suma, 'number_of_members': number_of_members,
               'group_receipts': group_receipts, 'suma_wydatki': suma_wydatki,'suma_paragony': suma_paragony,
               'amount_per_member':amount_per_member,'page_obj': page_obj}
    return render(request, 'groups/group_receipts_and_expenses.html', context)


def not_member_of_group(request,group_id):
    group = CommonGroups.objects.get(id=group_id)
    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0
    if request.method == 'POST':
        req_temp = request.POST.copy()
        req_temp.update({'receiver': User.objects.get(username=group.owner)})
        form = HiddenMessageForm(req_temp, user=request.user, members=group.members)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.receiver = group.owner

            new_message.title = "Prośba o przyjęcie do grupy  " + group.group_name
            new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Proszę o przyjęcie do grupy  " + group.group_name + "."
            new_message.message_type = "request"
            new_message.group = group
            new_message.save()
            messages.success(request, 'Wiadomość została wysłana.')
            return redirect('groups:groups', group_id=group_id)
    else:
        form = MessageForm(user=request.user, members=group.members)

    context = {"group": group, "code": group.password, "form": form}
    return render(request, "groups/not_member_of_group.html", context)


def password_check(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    if request.method == "POST":
        pswd = "csvvdscsvvdve"
        print(request.POST)
        if pswd == group.password:
            messages.success(request, "Zostałeś dodany do grupy.")
        else:
            messages.error(request, "Złe hasło.")
    context = {"group": group, "code": group.password}
    return redirect("groups:groups")