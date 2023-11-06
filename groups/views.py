from django.shortcuts import render, redirect,reverse
from .models import CommonGroups, User
from groups.forms import CommonGroupsForm
from django.contrib import messages
from my_messages.forms import MessageForm
from receipts.models import Expense, Receipt
from my_messages.models import Message
from profile_mangement.models import ProfileInfo
from django.template.defaultfilters import slugify
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import Http404


def groups(request):
    your_groups = CommonGroups.objects.filter(owner=request.user)
    member_of_groups = CommonGroups.objects.filter(members=request.user).order_by("-date_created")

    page_number = request.GET.get('page',1)
    p = Paginator(member_of_groups, 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'your_groups': your_groups, "member_of_groups":member_of_groups, 'pages': pages}
    return render(request, 'groups/your_groups.html', context)


def group_site(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    members = group.members.all().order_by("id")
    profiles = ProfileInfo.objects.filter(user__in=members).order_by("user_id")
    pam = zip(profiles, members)
    user = request.user

    if user not in members:
        return redirect('groups:not_member_of_group', group_id=group_id)

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
    context = {"group": group, "members": members, "user": user, "amount_per_member": "{:.2f}".format(amount_per_member),
               "suma": "{:.2f}".format(suma), "profile_and_members": pam}
    return render(request, 'groups/group_site.html', context)


def invite_page(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0

    if request.method == 'POST':
            new_message = Message.objects.create(receiver = User.objects.get(username=request.POST["user_to_invite"]),
                                                 sender = request.user, title = "Zaproszenie do grupy " + group.group_name,
                                                 message_type="invitation", group = group
                                                 )
            new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Zapraszam Cię do dołączenia do grupy " + group.group_name + "."
            new_message.save()
            messages.success(request, 'Wiadomość została wysłana.')
            return redirect('groups:group_site', group_id=group_id)


    context = {"group": group, "code": group.password}
    return render(request, 'groups/invite_page.html', context)


def search(request, group_id):
    text = 'noOne'
    group = get_object_or_404(CommonGroups, id=group_id)
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


def leaving_group_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    if group.members.count() > 1:
        member = group.members.exclude(id=group.owner.id).order_by("date_joined")[0]
    else:
        member = None

    context = {"group": group, "user": request.user, "new_owner": member}
    return render(request, 'groups/leaving_group_page.html', context)


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


def group_deletion(request,group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    if request.user != group.owner:
        return Http404
    context = {'group':group}
    return render(request,'groups/group_deletion.html',context)


def delete_group(request,group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    group.delete()
    return redirect('groups:groups')


def left_group(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    user = request.user
    if request.method == "POST":
        try:
            group.owner = group.members.get(username=request.POST["new_owner"])
            group.members.remove(user)
            group.number_of_members -= 1
            group.save()
        except:
            if len(request.POST["new_owner"]) > 0:
                messages.error(request, "Brak użytkownika")
                return redirect('groups:leaving_group_page', group_id=group.id)
            else:
                group.members.remove(user)
                group.number_of_members -= 1
                group.owner = group.members.all().order_by("date_joined")[0]
                group.save()
    return redirect('groups:groups')


def manage_group(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    members = [group.owner] + list(group.members.all().order_by("date_joined")[1:])
    context = {"group": group, "user": request.user, 'members': members}
    return render(request, 'groups/manage_group.html', context)


def search_group(request):
    number = 0
    exists = False
    if request.method == 'POST':
        group_name = request.POST.get('q', '')

        try:
            groups_searched = CommonGroups.objects.filter(group_name__icontains=group_name)
            number = CommonGroups.objects.filter(group_name__icontains=group_name).count()
            exists = True
        except :
            groups_searched = None
    else:
        group_name = request.GET.get('q', '')

        try:
            groups_searched = CommonGroups.objects.filter(group_name__icontains=group_name)
            number = CommonGroups.objects.filter(group_name__icontains=group_name).count()
            exists = True
        except :
            groups_searched = None

    if number == 0:
        text = "Brak wyników."
    elif number == 1:
        text = "Znaleziono 1 wynik"
    elif number in [2,3,4]:
        text = f"Znaleziono {number} wyniki"
    else:
        text = f"Znaleziono {number} wyników"

    page_number = request.GET.get('page',1)
    p = Paginator(groups_searched, 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {"pages": pages, "text": text, "user": request.user, 'exists': exists, 'groups': groups_searched,
               'number': number, 'query': group_name}
    return render(request, 'groups/search_group.html', context)


def group_receipts_and_expenses(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
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

    page_number = request.GET.get('page',1)
    p = Paginator(group_expenses, 1)

    try:
        page_obj = p.page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    context = {'group': group, 'group_expenses': group_expenses, 'suma': suma, 'number_of_members': number_of_members,
               'group_receipts': group_receipts, 'suma_wydatki': "{:.2f}".format(suma_wydatki),'suma_paragony': "{:.2f}".format(suma_paragony),
               'amount_per_member':"{:.2f}".format(amount_per_member),'page_obj': page_obj}
    return render(request, 'groups/group_receipts_and_expenses.html', context)


def not_member_of_group(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)

    if request.method == 'POST':
        try:
            new_message = Message.objects.create(sender=request.user,
                                                 receiver=group.owner,
                                                 title="Prośba o przyjęcie do grupy  " + group.group_name,
                                                 message_type="request",
                                                 group=group)
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Proszę o przyjęcie do grupy  " + group.group_name + "."
            new_message.save()
            messages.success(request, 'Wiadomość została wysłana.')
        except:
            messages.error(request, 'Nie udało się wysłać wiadomości.')

        return redirect('groups:groups')

    context = {"group": group, "code": group.password}
    return render(request, "groups/not_member_of_group.html", context)


def password_check(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    if request.method == "POST":
        pswd = request.POST['Hasło']
        if pswd == group.password:
            group.members.add(request.user)
            group.number_of_members += 1
            group.save()
            messages.success(request, "Zostałeś dodany do grupy.")
            return redirect("groups:group_site", group_id=group.id)
        else:
            messages.error(request, "Złe hasło.")
            return redirect("groups:not_member_of_group", group_id=group.id)


def profile_not_public(request):
    context = {}
    return render(request, "groups/profile_not_public.html", context)


def remove_member(request, group_id, member_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        member = group.members.get(id=member_id)
        group.members.remove(member)
        messages.success(request, f"Usunięto użytkownika {member.username} z grupy.")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:manage_group", group_id=group.id)

