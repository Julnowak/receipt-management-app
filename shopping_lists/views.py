from django.shortcuts import render, redirect, reverse
from .models import ShoppingList, Product
from receipts.models import Expense
from .forms import ShoppingListForm, ProductForm
from django.http import Http404
from django.contrib.auth.decorators import login_required
from my_messages.models import Message

import pandas as pd
# Create your views here.


def homepage(request):
    """ Homepage of application"""
    return render(request, 'shopping_lists/homepage.html')


@login_required
def your_lists(request):
    """ Your shopping lists page"""
    your_shopping_lists = ShoppingList.objects.filter(owner=request.user).order_by('-date_added')
    context = {'your_lists': your_shopping_lists}
    return render(request, 'shopping_lists/your_lists.html', context)


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
def new_list(request):
    if request.method == 'POST':
        form = ShoppingListForm(data=request.POST)
        if form.is_valid():
            new_l = form.save(commit=False)
            new_l.owner = request.user
            new_l.save()
            return redirect('your_lists')
    else:
        form = ShoppingListForm()

    context = {'form': form}
    return render(request, 'shopping_lists/new_list.html', context)


@login_required
def new_product(request, list_id):
    current_list = ShoppingList.objects.get(id=list_id)
    if request.method == 'POST':
        form = ProductForm(data=request.POST)
        if form.is_valid():
            new_prod = form.save(commit=False)
            new_prod.selected_list = current_list
            print(new_prod.selected_list)
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

@login_required
def main_panel(request):

    expenses = Expense.objects.filter(owner=request.user).values_list("category","amount")
    new_messages_number = Message.objects.filter(receiver=request.user, new=True).count()

    # Pie Chart
    df = pd.DataFrame(list(expenses))
    df.columns = ['category','amount']
    print(df)
    fig_pie = px.pie(df, values='amount', names='category', height=300,title="Wydatki stałe")

    pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)

    labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]

    context = {"pie_chart": pie_chart, 'labels': labels, 'new_messages_number': new_messages_number}

    return render(request, 'shopping_lists/main_panel.html', context)


def removed(request, product_id):
        current_product = Product.objects.get(id=product_id)
        current_product.delete()
        return render(request, 'shopping_lists/shopping_list_page.html')