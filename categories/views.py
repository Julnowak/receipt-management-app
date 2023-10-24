from django.shortcuts import render, redirect
from .models import BaseCategories, SubCategories
from .forms import NewCategoryForm,NewSubCategoryForm
from groups.models import CommonGroups
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

# Create your views here.


def categories(request):
    base_main_categories = BaseCategories.objects.all()
    cat_public = base_main_categories.filter(owner=None)
    cat_private = base_main_categories.filter(owner=request.user)

    context = {'main_categories': base_main_categories, "cat_public": cat_public, "cat_private":cat_private}
    return render(request, 'categories/categories.html', context)


def new_category(request):
    if request.method == 'POST':

        form = NewCategoryForm(data=request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            if 'public' not in request.POST:
                cat.owner = request.user
            cat.color = request.POST["color"]
            cat.slug = slugify(cat.category_name)
            cat.save()
            return redirect('categories:categories')
    else:
        form = NewCategoryForm()
    context = {'form':form, 'user': request.user}
    return render(request, 'categories/new_category.html', context)


def edit_category(request):
    return render(request, 'categories/edit_category.html')


def subcategories(request, category_slug):
    category = BaseCategories.objects.get(slug=category_slug)
    subcats = SubCategories.objects.filter(category=category)


    context = {"category": category, "subcategories": subcats}

    return render(request, 'categories/sub_categories.html', context)


def new_subcategory(request, category_slug):
    category = BaseCategories.objects.get(slug=category_slug)
    if request.method == "POST":
        form = NewSubCategoryForm()
        if form.is_valid():
            new_subcat = form.save(commit=False)
            new_subcat.owner = request.user
            new_subcat.category = category
            new_subcat.slug = slugify(new_subcat.subcategory_name)
            new_subcat.save()
            return redirect('categories:subcategories', category_slug=category_slug)
    else:
        form = NewSubCategoryForm()
    context = {'form': form, 'category': category}
    return render(request, 'categories/new_subcategory.html', context)


def edit_subcategory(request, category_slug):
    category = BaseCategories.objects.get(slug=category_slug)
    return render(request, 'categories/edit_subcategory.html')


