from django.shortcuts import render, redirect, reverse
from .models import ShoppingList, Product
from receipts.models import Expense
from .forms import ShoppingListForm, ProductForm
from django.http import Http404
from django.contrib.auth.decorators import login_required
from my_messages.models import Message
from categories.models import BaseCategories
from django.http import HttpResponseRedirect,Http404
import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse


def homepage(request):
    """ Homepage of application"""
    return render(request, 'shopping_lists/homepage.html')


def contact(request):
    return render(request, 'shopping_lists/contact.html')


@login_required
def your_lists(request):
    """ Your shopping lists page"""
    your_shopping_lists = ShoppingList.objects.filter(owner=request.user).order_by('-date_added')
    form = ShoppingListForm()

    page_number = request.GET.get('page', 1)
    p = Paginator(your_shopping_lists, 4)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'your_lists': your_shopping_lists, 'form': form, 'pages': pages}
    return render(request, 'shopping_lists/your_lists.html', context)


@login_required
def add_shopping_list(request):
    if request.method == 'POST':
        form = ShoppingListForm(data=request.POST)
        if form.is_valid():
            new_l = form.save(commit=False)
            new_l.owner = request.user
            new_l.save()
            if 'is_from_web_checkbox' in request.POST:
                # Webscraping for products
                url = request.POST['page_url']
                data = requests.get(url)
                html = BeautifulSoup(data.text, 'html.parser')

                if "www.kwestiasmaku.com" in url:
                    ingredients = html.find("div", {"class": "field field-name-field-skladniki field-type-text-long field-label-hidden"})
                    starter = 7
                elif "aniagotuje.pl" in url:
                    ingredients = html.find("ul", {"class": "recipe-ing-list"})
                    starter = 32
                else:
                    return JsonResponse({'error': 'Strona nie jest obsługiwana.'})
                try:
                    unordered_list = (ingredients.find_all("li"))
                    for ing in list(unordered_list):
                        new_prod = Product.objects.create(selected_list=new_l, product=str(ing)[starter:len(ing)-6])
                        new_prod.save()
                except:
                    return JsonResponse({'error': 'Something went wrong.'})

            return JsonResponse({'message': f'Successfully saved: {new_l.text}'})
        else:
            return JsonResponse({'error': 'Form is not valid'})
    return JsonResponse({'error': 'Invalid request method'})


@login_required
def del_shopping_lists(request):
    if request.method == 'POST':
        fruits = request.POST.getlist('fruits')
        return JsonResponse({'message': f'Successfully saved.{fruits}'})
    return JsonResponse({'error': 'Something went wrong'})


@login_required
def edit_shopping_lists(request, list_id):
    current_list = ShoppingList.objects.get(id=list_id)

    if request.method == 'POST':
        form = ShoppingListForm(instance=current_list, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': f'Successfully saved.'})
        else:
            return JsonResponse({'error': 'Form is not valid'})

    return JsonResponse({'error': 'Something went wrong'})


@login_required
def single_list(request, list_id):
    """ Your shopping lists page"""
    sh_list = ShoppingList.objects.get(id=list_id) # This get me my current list name

    if sh_list.owner != request.user:
        return Http404
    # Minus changes way of displaying elements
    products = sh_list.product_set.order_by('-date_added')

    context = {'current_list': sh_list, 'products': products}
    return render(request, 'shopping_lists/shopping_list_page.html', context)


@login_required
def new_product(request, list_id):
    current_list = ShoppingList.objects.get(id=list_id)
    if request.method == 'POST':
        form = ProductForm(data=request.POST)
        if form.is_valid():
            new_prod = form.save(commit=False)
            new_prod.selected_list = current_list
            new_prod.save()
            return redirect('single_list', list_id=list_id)
    else:
        form = ProductForm()

    context = {'current_list': current_list, 'form': form}
    return render(request, 'shopping_lists/new_product.html', context)


@login_required
def edit_product(request, product_id):
    current_product = Product.objects.get(id=product_id)
    current_list = current_product.selected_list

    if request.method == 'POST':
        form = ProductForm(instance=current_product, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('single_list', list_id=current_list.id)
    else:
        form = ProductForm(instance=current_product)

    context = {'current_product': current_product, 'form': form}
    return render(request, 'shopping_lists/edit_product.html',context)


import plotly.express as px
from django.shortcuts import render
from datetime import datetime

@login_required
def main_panel(request):
    expenses = Expense.objects.filter(owner=request.user).values_list("category","amount")
    dates_added = Expense.objects.filter(owner=request.user).values_list( "date_added")
    new_messages_number = Message.objects.filter(receiver=request.user, new=True).count()
    categories = BaseCategories.objects.values_list("id","category_name")

    if request.method == 'POST' and 'run_script' in request.POST:
        now = datetime.today()
        uk = now - dates_added[3][0].replace(tzinfo=None)
        # return user to required page
        return redirect(reverse("main_panel"))



    # Pie Chart
    try:
        df = pd.DataFrame(list(expenses))
        df.columns = ['category','amount']
        df_temp = pd.DataFrame(list(categories))
        df_temp.columns = ['category', 'category_name']
        df2 = pd.merge(df, df_temp, on=['category'])
        fig_pie = px.pie(df2, values='amount', names='category_name', height=300,title="Wydatki stałe")

        pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)

        labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]


    except:
        pie_chart = "None"
        labels = "None"

    context = {"pie_chart": pie_chart, 'labels': labels, 'new_messages_number': new_messages_number}
    return render(request, 'shopping_lists/main_panel.html', context)


def removed(request, product_id):
        current_product = Product.objects.get(id=product_id)
        sh_list = current_product.selected_list
        current_product.delete()

        return HttpResponseRedirect(reverse('single_list', kwargs={'list_id': sh_list.id}))


def list_removed(request, list_id):
    current_list = ShoppingList.objects.get(id=list_id)
    current_list.delete()

    return HttpResponseRedirect(reverse('your_lists'))


@login_required
def share_list(request, list_id):
    context = {}
    return render(request, 'shopping_lists/share_list.html', context)