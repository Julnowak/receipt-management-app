from django.shortcuts import render, redirect
from .models import CommonGroups, User
from groups.forms import CommonGroupsForm
from django.contrib import messages
from my_messages.models import Message
from profile_mangement.models import ProfileInfo
import math
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required


@login_required
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


import pandas as pd
from receipts.models import Receipt, Expense
from categories.models import BaseCategories
import plotly.express as px
import plotly.graph_objects as go


@login_required
def group_site(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    members = group.members.all().order_by("id")

    profiles = ProfileInfo.objects.filter(user__in=members).order_by("user_id")
    pam = zip(profiles, members)

    page_number = request.GET.get('page', 1)
    p = Paginator(list(pam), 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    user = request.user

    exps = Expense.objects.filter(group=group).values_list('amount','owner')
    receipts = Receipt.objects.filter(group=group).values_list('amount','owner')

    df = pd.DataFrame({'owner': list(exps.values_list("owner")) + list(receipts.values_list("owner")),
                       'amount': list(exps.values_list("amount")) + list(receipts.values_list("amount"))})
    df['owner'] = df['owner'].apply(lambda x: x[0])
    df['amount'] = df['amount'].apply(lambda x: x[0])

    users = User.objects.values_list("id", "username")
    df_temp = pd.DataFrame({'owner': users.values_list("id"),
                            'username': users.values_list("username")})
    df_temp['owner'] = df_temp['owner'].apply(lambda x: x[0])
    df_temp['username'] = df_temp['username'].apply(lambda x: x[0])
    df2 = pd.merge(df, df_temp, on=['owner'])
    df2 = df2.sort_values('amount')
    df2 = df2[['username', 'amount']]

    df_rank = df2.copy()
    try:
        df2 = df2[['amount', 'username']].groupby('username', as_index=False).sum().sort_values(
                by=['amount'], ascending=False)
        new = df2[:3]
        if len(new) >= 3:
            new.loc[len(new)] = ["Inni", df2['amount'][3:].sum()]
            df2 = new
        if group.limit:
            df2.loc[len(df2)] = ['Pozostało', round(group.limit - float(df2['amount'].sum()), 2)]
        if df2.empty:
            pie_chart = "Brak danych"
        else:
            fig_pie = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df2['amount'],
                labels=df2['username'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51','lightgray']))
            fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                  autosize=False,
                                  height=500,
                                  width=400,
                                  legend=dict(orientation="h"))
            pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart= "None"

    if user not in members:
        return redirect('groups:not_member_of_group', group_id=group_id)

    try:
        df_rank = df_rank[['amount', 'username']].groupby('username', as_index=False).sum().sort_values(
            by=['amount'], ascending=False)
        new = df_rank[:3]
        df_rank = new

        if df_rank.empty:
            bars_chart = "Brak danych"
        else:

            fig_bars = go.Figure(data=[
                go.Bar(name='SF Zoo',
                       x=df_rank['username'],
                       y=df_rank['amount'],
                       text=df_rank['amount'],
                       textposition="outside",
                       marker_color=['#4f000b', '#720026', '#ce4257', '#ff7f51'],
                       texttemplate=" %{y:.2} zł", )
            ])
            # marker_color = ["#d4af37", '#c0c0c0', '#cd7f32'],
            fig_bars.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=500,width=400,)

            fig_bars.update_layout(barmode='group')
            bars_chart = fig_bars.to_html(full_html=False, include_plotlyjs=False)

    except:
        bars_chart = "None"

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

    group_sh_list = group.shoppinglist_set.all()
    pg_num = request.GET.get('page', 1)
    ppag = Paginator(group_sh_list, 3)

    try:
        pag = ppag.page(pg_num)
    except PageNotAnInteger:
        pag = ppag.page(1)
    except EmptyPage:
        pag = ppag.page(ppag.num_pages)

    context = {"group": group, "members": members, "user": user, 'amount_per_member': str("{:.2f}".format(amount_per_member)).replace(".", ','),
               "suma": str("{:.2f}".format(suma)).replace(".", ','), "pages": pages, 'pag': pag,
               "pie": pie_chart, "group_sh_list": group_sh_list, 'bars_chart': bars_chart}
    return render(request, 'groups/group_site.html', context)


@login_required
def invite_page(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)

    if request.method == 'POST':
            new_message = Message.objects.create(receiver = User.objects.get(username=request.POST["user_to_invite"]),
                                                 sender = request.user, title = "Zaproszenie do grupy " + group.group_name,
                                                 message_type="invitation", group = group
                                                 )
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Zapraszam Cię do dołączenia do grupy " + group.group_name + "."
            new_message.save()
            messages.success(request, 'Wiadomość została wysłana.')
            return redirect('groups:group_site', group_id=group_id)


    context = {"group": group, "code": group.password}
    return render(request, 'groups/invite_page.html', context)


@login_required
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


@login_required
def leaving_group_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    if group.members.count() > 1:
        member = group.members.exclude(id=group.owner.id).order_by("date_joined")[0]
    else:
        member = None

    context = {"group": group, "user": request.user, "new_owner": member}
    return render(request, 'groups/leaving_group_page.html', context)


@login_required
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


@login_required
def group_deletion(request,group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    if request.user != group.owner:
        return Http404
    context = {'group':group}
    return render(request,'groups/group_deletion.html',context)


@login_required
def delete_group(request,group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    group.delete()
    return redirect('groups:groups')


@login_required
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


@login_required
def manage_group(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    members = [group.owner] + list(group.members.all().order_by("date_joined")[1:])

    page_number = request.GET.get('page', 1)
    p = Paginator(list(members), 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    if group.limit:
        flag = True
    else:
        flag = False

    group_sh_list = group.shoppinglist_set.all()
    pg_num = request.GET.get('page', 1)
    ppag = Paginator(group_sh_list, 3)

    try:
        pag = ppag.page(pg_num)
    except PageNotAnInteger:
        pag = ppag.page(1)
    except EmptyPage:
        pag = ppag.page(ppag.num_pages)
    context = {"group": group, 'pages': pages, "user": request.user, 'members': members, 'flag': flag,
               'pag': pag}
    return render(request, 'groups/manage_group.html', context)


@login_required
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
        text = "Znaleziono 1 wynik:"
    elif number in [2,3,4]:
        text = f"Znaleziono {number} wyniki:"
    else:
        text = f"Znaleziono {number} wyników:"

    page_number = request.GET.get('page',1)
    p = Paginator(groups_searched, 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {"pages": pages, "text": text, "user": request.user, 'exists': exists, 'groups': groups_searched,
               'number': number, 'query': group_name,}
    return render(request, 'groups/search_group.html', context)


@login_required
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

    pn= request.GET.get('page',1)
    p = Paginator(group_receipts, 3)

    try:
        p_rec = p.page(pn)
    except PageNotAnInteger:
        p_rec = p.page(1)
    except EmptyPage:
        p_rec = p.page(p.num_pages)

    page_number = request.GET.get('page', 1)
    p = Paginator(group_expenses, 3)

    try:
        page_obj = p.page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    context = {'group': group, 'group_expenses': group_expenses, 'suma': suma, 'number_of_members': number_of_members,
               'group_receipts': group_receipts, 'suma_wydatki': str("{:.2f}".format(suma_wydatki)).replace(".", ','),
               'suma_paragony': str("{:.2f}".format(suma_paragony)).replace(".", ','), 'page_obj': page_obj,
               'p_rec': p_rec}
    return render(request, 'groups/group_receipts_and_expenses.html', context)


@login_required
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


@login_required
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


@login_required
def profile_not_public(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    context = { 'group': group }
    return render(request, "groups/profile_not_public.html",context)


@login_required
def remove_member(request, group_id, member_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        member = group.members.get(id=member_id)
        group.members.remove(member)
        group.number_of_members -= 1
        messages.success(request, f"Usunięto użytkownika {member.username} z grupy.")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:manage_group", group_id=group.id)


@login_required
def change_invite_possibility(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    if group.allow_invitations:
        group.allow_invitations = False
    else:
        group.allow_invitations = True
    messages.success(request, f"Zmieniono możliwość dodawania wydatków.")
    group.save()
    return redirect("groups:manage_group", group_id=group.id)


@login_required
def del_from_group_expenses(request, group_id, expense_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        expense = group.expense_set.get(id=expense_id)
        group.expense_set.remove(expense)
        messages.success(request, f"Usunięto wydatek {expense.expense_name} z grupy.")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:group_receipts_and_expenses", group_id=group.id)


@login_required
def del_from_group_receipts(request, group_id, receipt_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        receipt = group.receipt_set.get(id=receipt_id)
        group.receipt_set.remove(receipt)
        messages.success(request, f"Usunięto paragon {receipt.receipt_name} z grupy.")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:group_receipts_and_expenses", group_id=group.id)


from shopping_lists.models import ShoppingList
@login_required
def del_list_from_group(request, group_id, list_id):
    lis = get_object_or_404(ShoppingList, id=list_id)
    group = CommonGroups.objects.get(id=group_id)

    try:
        group.shoppinglist_set.remove(lis)
        messages.success(request, f"Odczepiono listę {lis.text} z grupy.")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:manage_group", group_id=group.id)


@login_required
def change_adding_possibility(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    try:
        if group.can_receipts_be_added:
            group.can_receipts_be_added = False
        else:
            group.can_receipts_be_added = True
        messages.success(request, "Zmieniono możliwość dodawania wydatków")
        group.save()
    except:
        messages.error(request, "Wystąpił błąd.")
    return redirect("groups:manage_group", group_id=group.id)


@login_required
def change_limit(request, group_id):
    group = get_object_or_404(CommonGroups, id=group_id)
    if request.method == "POST":
        if request.POST['is_limit_set'] == "True":
            text = request.POST['limit']
            if ',' in text:
                text = request.POST['limit'].replace(',', '.')
            try:
                num = float(text)
                suma = sum(list(i[0] for i in group.expense_set.values_list('amount'))) + sum(list(i[0] for i in group.receipt_set.values_list('amount')))
                if suma <= num:
                    group.limit = num
                    messages.success(request, f"Zmieniono limit wydatków grupy.")
                else:
                    messages.error(request, f"Limit został już przekroczony.")
            except:
                group.limit = None
                messages.error(request, f"Nie udało się zmienić limitu wydatków.")
        else:
            group.limit = None
            messages.success(request, f"Zmieniono limit wydatków grupy.")
        group.save()
    return redirect("groups:manage_group", group_id=group.id)
