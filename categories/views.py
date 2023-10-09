from django.shortcuts import render, redirect
from .models import BaseCategories, SubCategories
from .forms import NewCategoryForm
from groups.models import CommonGroups
from django.utils.text import slugify

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
        cat = form.save(commit=False)

        ########################
        if request.user.is_superuser:
            cat.public = True

        cat.owner = request.user
        cat.slug = slugify(cat.category_name)
        cat.save()
        return redirect('categories:categories')
    else:
        form = NewCategoryForm()
    context = {'form':form}
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
    return render(request, 'categories/new_subcategory.html')


def edit_subcategory(request, category_slug):
    category = BaseCategories.objects.get(slug=category_slug)
    return render(request, 'categories/edit_subcategory.html')


