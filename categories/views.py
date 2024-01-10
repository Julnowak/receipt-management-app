from django.shortcuts import render, redirect
from .models import BaseCategories, SubCategories, Product
from .forms import NewCategoryForm, NewSubCategoryForm, NewProductForm
from groups.models import CommonGroups
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404


@login_required
def categories(request):
    base_main_categories = BaseCategories.objects.all().order_by("category_name")
    cat_public = base_main_categories.filter(owner=None)
    cat_private = base_main_categories.filter(owner=request.user)

    page_number = request.GET.get('page', 1)
    p = Paginator(cat_public, 6)

    try:
        pages_public = p.page(page_number)
    except PageNotAnInteger:
        pages_public = p.page(1)
    except EmptyPage:
        pages_public = p.page(p.num_pages)

    page_number_priv = request.GET.get('page', 1)
    p_priv = Paginator(cat_private, 6)

    try:
        pages_private = p_priv.page(page_number_priv)
    except PageNotAnInteger:
        pages_private = p_priv.page(1)
    except EmptyPage:
        pages_private = p_priv.page(p_priv.num_pages)

    context = {'main_categories': base_main_categories, "cat_public": cat_public, "cat_private":cat_private,
               'pages_public': pages_public, 'pages_private': pages_private}
    return render(request, 'categories/categories.html', context)


@login_required
def new_category(request):
    if request.method == 'POST':
        form = NewCategoryForm(data=request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            if 'public' not in request.POST:
                cat.owner = request.user
            cat.color = request.POST["color"]
            cat.save()
            messages.success(request, "Dodano nową kategorię.")
            return redirect('categories:categories')
        else:
            messages.error(request, "Coś poszło nie tak.")
    else:
        form = NewCategoryForm()
    context = {'form':form, 'user': request.user}
    return render(request, 'categories/new_category.html', context)


@login_required
def edit_category(request, category_id):
    cat = BaseCategories.objects.get(id=category_id)

    if request.user != cat.owner:
        return Http404

    if request.method == 'POST':
        form = NewCategoryForm(instance=cat, data=request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.color = request.POST['color']
            cat.save()
            messages.success(request, "Kategoria została edytowana.")
            return redirect('categories:subcategories', category_id=cat.id)
        else:
            messages.error(request, "Dodano nową kategorię.")
    else:
        form = NewCategoryForm(instance=cat)
    context = {'form': form, 'category': cat}
    return render(request, 'categories/edit_category.html', context)


@login_required
def subcategories(request, category_id):
    category = get_object_or_404(BaseCategories, id=category_id)
    subcats = SubCategories.objects.filter(category=category).order_by("subcategory_name")

    page_number_priv = request.GET.get('page', 1)
    p_priv = Paginator(subcats, 10)

    try:
        pages = p_priv.page(page_number_priv)
    except PageNotAnInteger:
        pages = p_priv.page(1)
    except EmptyPage:
        pages = p_priv.page(p_priv.num_pages)

    context = {"category": category, "subcategories": subcats, "pages": pages,
               "user": request.user}

    return render(request, 'categories/sub_categories.html', context)


@login_required
def new_subcategory(request, category_id):
    category = BaseCategories.objects.get(id=category_id)
    if request.method == "POST":
        form = NewSubCategoryForm(data=request.POST)
        if form.is_valid():
            new_subcat = form.save(commit=False)
            new_subcat.owner = request.user
            new_subcat.category = category
            new_subcat.color = request.POST['color']
            new_subcat.save()
            messages.success(request, "Dodano nową podkategorię.")
            return redirect('categories:subcategories', category_id=category_id)
        else:
            print(form.errors.as_data())
            messages.error(request, "Coś poszło nie tak.")
    else:
        form = NewSubCategoryForm()
    context = {'form': form, 'category': category}
    return render(request, 'categories/new_subcategory.html', context)


@login_required
def edit_subcategory(request, subcategory_id):
    subcat = SubCategories.objects.get(id=subcategory_id)
    cat = subcat.category
    if request.user != subcat.owner:
        return Http404

    if request.method == 'POST':
        form = NewSubCategoryForm(instance=subcat, data=request.POST)
        if form.is_valid():
            new_subcat = form.save(commit=False)
            new_subcat.color = request.POST['color']
            new_subcat.save()
            messages.success(request, "Kategoria została edytowana.")
            return redirect('categories:subcategories', category_id=cat.id)
        else:
            messages.error(request, "Dodano nową kategorię.")
    else:
        form = NewSubCategoryForm(instance=subcat)
    context = {'form': form, 'subcategory': subcat, 'category': cat}
    return render(request, 'categories/edit_subcategory.html', context)


@login_required
def products_in_subcategory(request, subcategory_id):
    subcat = SubCategories.objects.get(id=subcategory_id)
    category = subcat.category
    sub_products = Product.objects.filter(subcategory=subcat)
    user = request.user
    page_number_priv = request.GET.get('page', 1)
    p_priv = Paginator(sub_products, 10)

    try:
        pages = p_priv.page(page_number_priv)
    except PageNotAnInteger:
        pages = p_priv.page(1)
    except EmptyPage:
        pages = p_priv.page(p_priv.num_pages)

    context = {"subcategory": subcat, 'category': category, 'sub_products': sub_products,
               'pages':pages, "user": user}
    return render(request, 'categories/products_in_subcategory.html', context)


@login_required
def delete_category(request, category_id):
    category = BaseCategories.objects.get(id=category_id)
    category.delete()
    return redirect("categories:categories")


@login_required
def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategories, id=subcategory_id)
    category = subcategory.category
    subcategory.delete()
    return redirect("categories:subcategories", category_id=category.id)


@login_required
def delete_product(request, product_id):
    prod = get_object_or_404(Product, id=product_id)
    subcat = prod.subcategory
    prod.delete()
    return redirect("categories:products_in_subcategory", subcategory_id=subcat.id)


@login_required
def new_product(request, subcategory_id):
    subcat = get_object_or_404(SubCategories, id=subcategory_id)
    cat = subcat.category
    if request.method == "POST":
        form = NewProductForm(data=request.POST)
        if form.is_valid():
            new_prod = form.save(commit=False)
            new_prod.subcategory = subcat
            new_prod.save()
            messages.success(request, "Poprawnie dodano produkt do kategorii.")
            return redirect('categories:products_in_subcategory', subcategory_id=subcategory_id)
        else:
            messages.error(request, "Coś poszło nie tak.")
    else:
        form = NewProductForm()

    context = {'subcategory': subcat, 'category': cat,'form': form}
    return render(request,"categories/new_product.html", context)


@login_required
def edit_product(request, product_id):
    prod = get_object_or_404(Product, id=product_id)
    subcat = prod.subcategory
    category = prod.subcategory.category
    if request.method == "POST":
        form = NewProductForm(instance=prod, data=request.POST)
        if form.is_valid():
            new_prod = form.save(commit=False)
            new_prod.save()
            messages.success(request, "Poprawnie dodano produkt do kategorii.")
            return redirect('categories:products_in_subcategory', subcategory_id=subcat.id)
        else:
            messages.error(request, "Coś poszło nie tak.")
    else:
        form = NewProductForm(instance=prod)

    context = {'form': form, "prod": prod,'subcategory': subcat, 'category': category}
    return render(request, "categories/edit_product.html", context)

