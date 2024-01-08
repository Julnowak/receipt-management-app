from .models import ShoppingList, ListProduct
from receipts.models import Expense, Receipt,Guarantee
from .forms import ShoppingListForm, ProductForm, DetailsForm
from django.shortcuts import render, redirect, reverse
from datetime import datetime,date
from calendar import monthrange
import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required
from my_messages.models import Message, User
from categories.models import BaseCategories
from django.http import HttpResponseRedirect,Http404
import pandas as pd
import requests
from groups.models import CommonGroups
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404


def homepage(request):
    """ Homepage of application"""
    context = {'user':request.user}
    return render(request, 'shopping_lists/homepage.html', context)


def contact(request):
    return render(request, 'shopping_lists/contact.html')


@login_required
def your_lists(request):
    """ Your shopping lists page"""
    your_shopping_lists = ShoppingList.objects.filter(realizators__username=request.user.username).order_by('-date_added')
    form = ShoppingListForm()

    num_of_prods = []
    bought_num_of_prods = []
    for sh_list in your_shopping_lists:
        prods = ListProduct.objects.filter(shopping_list=sh_list)
        nop = 0
        bnop = 0
        flaga = True
        if prods:
            for prod in prods:
                nop += 1
                if not prod.is_bought:
                    flaga = False
                else:
                    bnop += 1
        else:
            flaga = False
        sh_list.is_completed = flaga
        sh_list.save()
        num_of_prods += [nop]
        bought_num_of_prods += [bnop]

    merged_sh_list = list(zip(your_shopping_lists,num_of_prods,bought_num_of_prods))

    page_number = request.GET.get('page', 1)
    p = Paginator(merged_sh_list, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'your_lists': your_shopping_lists, 'form': form, 'pages': pages, 'user': request.user}
    return render(request, 'shopping_lists/your_lists.html', context)


@login_required
def edit_list(request, list_id):
    current_list = get_object_or_404(ShoppingList, id=list_id)
    old = str(current_list.text)
    if request.method == 'POST':
        form = ShoppingListForm(instance=current_list, data=request.POST)
        if form.is_valid():
            form.save()
            if current_list.is_shared:
                current_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + \
                                    str(request.user.username) + " edytował nazwę listy " + old + " na " + current_list.text + ".;" + current_list.logs
                current_list.save()
                for real in current_list.realizators.exclude(request.user):
                    new_message = Message.objects.create(sender=request.user,
                                                         receiver=real,
                                                         title="Zmieniono nazwę grupy",
                                                         message_type="normal")
                    new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                                       f"Użytkownik {request.user} zmienił nazwę listy {old} na {current_list.text}."
                    new_message.save()
            return redirect("your_lists")
    else:
        form = ShoppingListForm(instance=current_list)
    context = {"form": form, "list": current_list}
    return render(request,"shopping_lists/edit_list.html", context)


@login_required
def single_list(request, list_id):
    sh_list = get_object_or_404(ShoppingList, pk=list_id)
    list_shared = False
    if sh_list.owner != request.user:
        list_shared = True

    if request.user not in sh_list.realizators.all():
        raise Http404

    nop = 0
    bnop = 0

    products = sh_list.listproduct_set.all().order_by('-date_added')

    flaga = True
    if products:
        for prod in products:
            nop += 1
            if not prod.is_bought:
                flaga = False
            else:
                bnop += 1
    else:
        flaga = False
    sh_list.is_completed = flaga
    if sh_list.realizators.count() == 1 and sh_list.realizators.first() == request.user:
        sh_list.is_shared = False
        sh_list.logs = ""
    sh_list.save()
    page_number = request.GET.get('page', 1)
    p = Paginator(products, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'current_list': sh_list, 'products': products,'list_shared':list_shared,
               'user':request.user, 'num_of_prods': nop, 'bought_num_of_prods': bnop, 'pages': pages,
               'flag': None}
    return render(request, 'shopping_lists/shopping_list_page.html', context)


## TO DO
@login_required
def single_list_redirected(request, list_id, group_id):
    """ Your shopping lists page"""
    try:
        group = get_object_or_404(CommonGroups, id=group_id)
        sh_list = get_object_or_404(ShoppingList, id=list_id)
    except:
        raise Http404

    if request.user in group.members.all() and sh_list.group == group:
        if request.user not in sh_list.realizators.all():
            sh_list.realizators.add(request.user)
    else:
        raise Http404

    nop = 0
    bnop = 0

    products = sh_list.listproduct_set.all().order_by('-date_added')

    flaga = True
    if products:
        for prod in products:
            nop += 1
            if not prod.is_bought:
                flaga = False
            else:
                bnop += 1
    else:
        flaga = False
    sh_list.is_completed = flaga
    if sh_list.realizators.count() == 1 and sh_list.realizators.first() == request.user:
        sh_list.is_shared = False
        sh_list.logs = ""
    sh_list.save()
    page_number = request.GET.get('page', 1)
    p = Paginator(products, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'current_list': sh_list, 'products': products, 'list_shared': sh_list.is_shared,
               'user': request.user, 'num_of_prods': nop, 'bought_num_of_prods': bnop, 'pages': pages,
               'flag': 'group', 'group': group}
    return render(request, 'shopping_lists/shopping_list_page.html', context)


@login_required
def new_product(request, list_id):
    current_list = get_object_or_404(ShoppingList, id=list_id)
    if request.method == 'POST':
        form = ProductForm(data=request.POST)
        if form.is_valid():
            new_prod = form.save(commit=False)
            new_prod.shopping_list = current_list
            new_prod.by_who = request.user
            new_prod.save()
            if current_list.is_shared:
                current_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(
                    request.user.username) + " dodał produkt " + str(new_prod.product) + ".;" + current_list.logs
                current_list.save()
            return redirect('single_list', list_id=list_id)
    else:
        form = ProductForm()

    context = {'current_list': current_list, 'form': form}
    return render(request, 'shopping_lists/new_product.html', context)


@login_required
def edit_product(request, product_id):
    current_product = get_object_or_404(ListProduct, id=product_id)
    current_list = current_product.shopping_list
    before = str(current_product.product)
    if request.method == 'POST':
        form = ProductForm(instance=current_product, data=request.POST)
        if form.is_valid():
            form.save()
            if current_list.is_shared:
                current_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(
                    request.user.username) + " edytował produkt " + before + " i obecnie posiada on nazwę " + str(current_product.product) + ".;" + current_list.logs
                current_list.save()
            return redirect('single_list', list_id=current_list.id)
    else:
        form = ProductForm(instance=current_product)

    context = {'current_product': current_product, 'form': form, 'list':current_list}
    return render(request, 'shopping_lists/edit_product.html', context)


@login_required
def main_panel(request):
    expenses = Expense.objects.filter(owner=request.user).values_list("category","amount","date_added")
    receipts = Receipt.objects.filter(owner=request.user).values_list("receipt_categories", "amount", "date_added")
    new_messages_number = Message.objects.filter(receiver=request.user, new=True).count()
    categories = BaseCategories.objects.values_list("id","category_name")
    guarantees = Guarantee.objects.filter(owner=request.user, is_deleted=False)

    year_sum = 0
    month_sum = 0
    week_sum = 0
    day_sum = 0

    #### DEADLINES ####
    guar_list = []
    left = []
    for guar in guarantees:
        days_left = (guar.end_date - date.today()).days
        if days_left < 3:
            guar_list.append(guar)
            left.append(days_left)

    deadlines = zip(left,guar_list)

    page_number = request.GET.get('page', 1)
    p = Paginator(sorted(list(deadlines), key=lambda x: x[0]), 3)

    #### CHARTS ####
    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)


    try:
        df = pd.DataFrame(list(expenses))
        df_rec = pd.DataFrame(list(receipts))
        df.columns = ['category', 'amount', "date_added"]
        df_rec.columns = ['category', 'amount', "date_added"]
        new = pd.concat([df, df_rec])

        # Pie Chart
        df_temp = pd.DataFrame(list(categories))
        df_temp.columns = ['category', 'category_name']
        df2 = pd.merge(new, df_temp, on=['category'])
        # print(df2)
        for i in range(len(df2)):
            df2.loc[i, 'date_added'] = date(int(str(df2.loc[i, 'date_added'])[:4]),
                                            int(str(df2.loc[i, 'date_added'])[5:7]),
                                            int(str(df2.loc[i, 'date_added'])[8:10]))

        df2_year = df2[(df2["date_added"] >= date(datetime.today().year, 1, 1))]
        df2_year = df2_year[['amount', 'category_name']].groupby('category_name', as_index=False).sum().sort_values(
            by=['amount'], ascending=False)

        year_sum = df2_year['amount'].sum()
        new = df2_year[:3]
        if len(df2_year) >= 3:
            new.loc[len(new)] = ["Inne", df2_year['amount'][3:].sum()]
            df2_year = new

        if df2_year.empty:
            pie_chart_year = "Brak danych z tego roku"
        else:
            fig_pie_year = go.Figure(go.Pie(
                name="",
                hole= 0.5,
                values=df2_year['amount'],
                labels=df2_year['category_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_year.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_year.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                       legend=dict(
                                           orientation="h",  # Set legend orientation to horizontal
                                       )
                                       )

            pie_chart_year = fig_pie_year.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart_year = "None"

    try:
        df2_month = df2[(df2["date_added"] >= date(datetime.today().year, datetime.today().month, 1))]
        df2_month = df2_month[['amount', 'category_name']].groupby('category_name', as_index=False).sum().sort_values(
            by=['amount'], ascending=False)
        month_sum = df2_month['amount'].sum()
        new = df2_month[:3]
        if len(df2_month) >= 3:
            new.loc[len(new)] = ["Inne", df2_month['amount'][3:].sum()]
            df2_month = new

        if df2_month.empty:
            pie_chart_month = "Brak danych z tego miesiąca"
        else:
            fig_pie_month = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df2_month['amount'],
                labels=df2_month['category_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_month.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_month.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                        autosize=False,
                                        width=300,
                                        height=300,
                                        legend=dict(orientation="h"))
            pie_chart_month = fig_pie_month.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart_month = "None"

    try:
        list_of_weeks = [8, 15, 22, 29, monthrange(datetime.today().year, datetime.today().month)[1]]
        day = datetime.today().day
        weekday = 0

        for i in list_of_weeks:
            if day <= i:
                weekday = i
                break
        nk = df2[date(datetime.today().year, datetime.today().month, 1) <= df2["date_added"]]
        nk = nk[nk["date_added"] <= date(datetime.today().year, datetime.today().month, weekday)]

        df2_week = nk
        df2_week = df2_week[['amount', 'category_name']].groupby('category_name', as_index=False).sum().sort_values(
            by=['amount'], ascending=False)
        week_sum = df2_week['amount'].sum()
        new = df2_week[:3]
        if len(df2_week) >= 3:
            new.loc[len(new)] = ["Inne", df2_week['amount'][3:].sum()]
            df2_week = new

        if df2_week.empty:
            pie_chart_week = "Brak danych z tego tygodnia"
        else:
            fig_pie_week = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df2_week['amount'],
                labels=df2_week['category_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_week.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_week.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                        autosize=False,
                                        width=300,
                                        height=300,
                                        legend=dict(orientation="h"))
            pie_chart_week = fig_pie_week.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart_week = "None"


    try:
        df2_day = df2[(df2["date_added"] == date(datetime.today().year, datetime.today().month, datetime.today().day))]
        df2_day = df2_day[['amount', 'category_name']].groupby('category_name', as_index=False).sum().sort_values(
            by=['amount'], ascending=False)

        day_sum = df2_day['amount'].sum()
        new = df2_day[:3]
        if len(df2_day) >= 3:
            new.loc[len(new)] = ["Inne", df2_day['amount'][3:].sum()]
            df2_day = new

        if df2_day.empty:
            pie_chart_day = "Brak danych z tego dnia"
        else:
            fig_pie_day = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df2_day['amount'],
                labels=df2_day['category_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_day.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_day.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                        autosize=False,
                                        width=300,
                                        height=300,
                                        legend=dict(orientation="h"))
            pie_chart_day = fig_pie_day.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart_day = "None"

    context = {"pie_chart_year": pie_chart_year, 'pie_chart_month': pie_chart_month,
               'new_messages_number': new_messages_number,'pie_chart_day': pie_chart_day,
               'pie_chart_week': pie_chart_week, 'year_sum':year_sum, 'month_sum':month_sum,
               'deadlines': deadlines, 'pages': pages, 'week_sum':week_sum, 'day_sum':day_sum,}
    return render(request, 'shopping_lists/main_panel.html', context)


@login_required
def removed(request, product_id):
        current_product = get_object_or_404(ListProduct, id=product_id)
        current_list = current_product.shopping_list
        if current_list.is_shared:
            current_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(
                request.user.username) + " usunął produkt " + str(current_product) + ".;" + current_list.logs
            current_list.save()
        current_product.delete()

        return HttpResponseRedirect(reverse('single_list', kwargs={'list_id': current_list.id}))


@login_required
def list_removed(request, list_id):
    current_list = get_object_or_404(ShoppingList, id=list_id)
    if request.user == current_list.owner:
        current_list.delete()
    else:
        current_list.realizators.remove(request.user)
        current_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(
                request.user.username) + " usunął u siebie listę.;"
        addition = ''
        if current_list.is_shared and current_list.realizators.count() == 1:
            newline = "\n"
            addition = f"Dodatkowo, użytkownik ten był ostatnim, który należał do realizatorów. Otrzymujesz więc pełny wykaz logów listy:\n" + f"{current_list.regards.replace(';',newline)}"
        new_message = Message.objects.create(sender=request.user,
                                             receiver=current_list.owner,
                                             title="Użytkownik usunął udostępnioną listę.",
                                             message_type="normal")
        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                           f"Użytkownik {request.user} usunął u siebie udostępnioną mu listę {current_list.text}. " \
                           f"Tym samym został on usunięty z listy realizatorów." + "\n" + addition
        new_message.save()
        current_list.save()
    return HttpResponseRedirect(reverse('your_lists'))


@login_required
def share_list(request, list_id):
    lista = get_object_or_404(ShoppingList, id=list_id)
    users = User.objects.exclude(username__in=lista.realizators.all().values_list('username'))
    groups = CommonGroups.objects.filter(members__username=request.user.username)

    if request.method == "POST":
        if lista.is_shared:
            users_chosen = request.POST.getlist("users_chosen")
            if list(users_chosen):
                for user_id in users_chosen:
                    user_receiver = User.objects.get(id=int(user_id))
                    lista.realizators.add(user_receiver)
                    new_message = Message.objects.create(sender=request.user,
                                                         receiver=user_receiver,
                                                         title="Przekazano Ci nową listę!",
                                                         message_type="normal")
                    new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                                       f"Użytkownik {request.user} przekazuje Ci listę zakupową {lista.text}. Jeśli doszło do pomyłki, skontaktuj się z nadawcą" \
                                       f"w celu wyjaśnienia sprawy."
                    new_message.save()
                return redirect('single_list', list_id=lista.id)
            else:
                messages.error(request, "Nie wybrano użytkownika")
                return redirect('share_list', list_id=list_id)
        else:
            if request.POST["chosen_users_or_whole_group"] == "chosen_users":
                users_chosen = request.POST.getlist("users_chosen")
                if list(users_chosen):
                    for user_id in users_chosen:
                        user_receiver = User.objects.get(id=int(user_id))
                        lista.realizators.add(user_receiver)
                        new_message = Message.objects.create(sender=request.user,
                                                             receiver=user_receiver,
                                                             title="Przekazano Ci nową listę!",
                                                             message_type="normal")
                        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                                           f"Użytkownik {request.user} przekazuje Ci listę zakupową {lista.text}. Jeśli doszło do pomyłki, skontaktuj się z nadawcą" \
                                           f"w celu wyjaśnienia sprawy."
                        new_message.save()
                else:
                    messages.error(request, "Nie wybrano użytkownika")
                    return redirect('share_list', list_id=list_id)

            elif request.POST["chosen_users_or_whole_group"] == "whole_group":
                grp = groups.get(id=int(request.POST["group"]))
                for member in grp.members.values_list():
                    user_receiver = User.objects.get(id=int(member[0]))
                    lista.realizators.add(user_receiver)
                    new_message = Message.objects.create(sender=request.user,
                                                         receiver=user_receiver,
                                                         title="Przekazano Ci nową listę!",
                                                         message_type="normal")
                    new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                                       f"Użytkownik {request.user} przekazuje Ci listę zakupową {lista.text}. Jeśli doszło do pomyłki, skontaktuj się z nadawcą" \
                                       f"w celu wyjaśnienia sprawy."
                    new_message.save()
            if request.POST['copy_or_display_only'] == "copy":
                lista.display_only = False
            elif request.POST['copy_or_display_only'] == 'display_only':
                lista.display_only = True

            if request.POST.get("are_regards_added"):
                lista.regards = request.POST.get("regards")

            lista.is_shared = True
            lista.save()

            messages.success(request,"Lista została przekazana")
            return redirect("single_list", list_id=lista.id)

    context = {'list': lista, 'users': users, 'groups':groups, 'user': request.user}
    return render(request, 'shopping_lists/share_list.html', context)


@login_required
def update_is_bought(request, list_id):
    if request.method == 'POST':
        sh_list = get_object_or_404(ShoppingList, id=list_id)

        prods = ListProduct.objects.filter(shopping_list=sh_list).order_by('-date_added')
        prod = prods.get(id=request.POST.get("product_id"))

        if prod:
            if prod.is_bought:
                prod.is_bought = False
                if sh_list.is_shared:
                    sh_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(request.user.username) + " odznaczył produkt " + str(prod.product) + ".;" + sh_list.logs
            else:
                prod.is_bought = True
                if sh_list.is_shared:
                    sh_list.logs = str(datetime.now().strftime("%Y-%m-%d %H:%M")) + " Użytkownik " + str(request.user.username) + " oznaczył produkt " + str(prod.product) + " jako kupiony.;" + sh_list.logs
            prod.save()
            sh_list.save()

            return JsonResponse({'message': f'{prod.is_bought}'})
        else:
            return JsonResponse({'message': 'Wystąpił błąd'})
    else:
        return JsonResponse({'message': 'Wystąpił błąd'})


@login_required
def new_list(request):
    if request.method == 'POST':
        form = ShoppingListForm(data=request.POST)
        if form.is_valid():
            new_l = form.save(commit=False)
            new_l.owner = request.user
            new_l.save()
            new_l.realizators.add(request.user)
            if 'is_from_web_checkbox' in request.POST:
                url = request.POST['page_url']
                if url != '':
                    if "www.kwestiasmaku.com" in url:
                        data = requests.get(url)
                        html = BeautifulSoup(data.text, 'html.parser')
                        ingredients = html.find("div", {"class": "field field-name-field-skladniki field-type-text-long field-label-hidden"})
                        starter = 7
                        cuter = 6
                    elif "aniagotuje.pl" in url:
                        data = requests.get(url)
                        html = BeautifulSoup(data.text, 'html.parser')
                        ingredients = html.find("ul", {"class": "recipe-ing-list"})
                        cuter = 13
                        starter = 38
                    else:
                        messages.error(request,'Wprowadzony link jest błędny.')
                        ShoppingList.objects.get(id=new_l.id).delete()
                        form = ShoppingListForm(data=request.POST)
                        context = {"form": form}
                        return render(request, 'shopping_lists/new_shopping_list.html', context)
                    unordered_list = (ingredients.find_all("li"))
                    for ing in list(unordered_list):
                        new_ing = str(ing)[starter:len(ing)-cuter]
                        if ":" in new_ing:
                            new_ing = new_ing[new_ing.find(':')+2:]
                            ing_after = new_ing.split(';')
                            for ia in ing_after:
                                new_ia = ia.split(',')
                                for nia in new_ia:
                                    new_prod = ListProduct.objects.create(product=nia)
                                    new_prod.shopping_list = new_l
                                    new_prod.save()
                        else:
                            new_prod = ListProduct.objects.create(product=new_ing)
                            new_prod.shopping_list = new_l
                            new_prod.save()
            new_l.save()
            return redirect("your_lists")
    else:
         form = ShoppingListForm()
    context = {"form": form}
    return render(request, 'shopping_lists/new_shopping_list.html', context)


@login_required
def details(request, list_id):
    sh_list = get_object_or_404(ShoppingList, id=list_id)
    realizers = sh_list.realizators.exclude(id=request.user.id).order_by("username")
    page_number = request.GET.get('page', 1)
    p = Paginator(realizers, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    text_list = []
    text = sh_list.logs
    if text:
        text_list = text.split(';')

    pn = request.GET.get('page', 1)
    p2 = Paginator(text_list, 5)

    try:
        pag_log = p2.page(pn)
    except PageNotAnInteger:
        pag_log = p2.page(1)
    except EmptyPage:
        pag_log = p2.page(p.num_pages)

    context = {'sh_list': sh_list, 'pages': pages, 'pag_log': pag_log}
    return render(request, 'shopping_lists/details.html', context)


@login_required
def details_edit(request, list_id):
    sh_list = get_object_or_404(ShoppingList, id=list_id)

    if request.method == "POST":
        form = DetailsForm( data=request.POST, instance=sh_list)
        if form.is_valid():
            form.save()
            return redirect('details', list_id=sh_list.id)
    else:
        form = DetailsForm(instance=sh_list)
    context = {'sh_list': sh_list, 'form' : form}
    return render(request, 'shopping_lists/details_edit.html', context)


def current_number(request, list_id):
    sh_list = ShoppingList.objects.get(id=list_id)
    count = 0
    for prod in sh_list.listproduct_set.all():
        if prod.is_bought:
            count += 1
    ans = str(count) + "/" + str(sh_list.listproduct_set.count())
    data = {'message': ans}
    return JsonResponse(data)


@login_required
def delete_realizator(request, list_id, realizator_id):
    sh_list = get_object_or_404(ShoppingList, id=list_id)
    rez = get_object_or_404(User, id=realizator_id)
    sh_list.realizators.remove(rez)
    sh_list.save()
    if sh_list.realizators.count() == 1:
        return redirect("single_list", list_id=sh_list.id)
    return redirect("details", list_id=sh_list.id)

