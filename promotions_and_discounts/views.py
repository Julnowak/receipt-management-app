from django.shortcuts import render, redirect
from .models import Shop
import requests
from bs4 import BeautifulSoup
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time


@login_required
def shop_selection(request):
    shops = Shop.objects.filter(promos_available=True)
    context = {'shops': shops}
    return render(request, "promotions_and_discounts/shop_selection.html", context)


@login_required
def shop_site(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    page_number = request.GET.get('page', 1)
    PriceFrom = request.GET.get('PriceFrom', '')
    PriceTo = request.GET.get('PriceTo', '')
    addon = ''

    list_of_products_labels = []
    list_of_discounts = []
    list_of_old_prices = []
    list_of_new_prices = []

    if shop.shop_name == "Rossman":
        try:
            if request.POST['range_price_min'] and request.POST['range_price_max']:
                addon = f'&PriceFrom={int(request.POST["range_price_min"])}&PriceTo={int(request.POST["range_price_max"])}'
                PriceFrom = int(request.POST["range_price_min"])
                PriceTo = int(request.POST["range_price_max"])
            else:
                PriceFrom = request.GET.get('PriceFrom', '')
                PriceTo = request.GET.get('PriceTo', '')
        except:
            PriceFrom = request.GET.get('PriceFrom', '')
            PriceTo = request.GET.get('PriceTo', '')
        if addon == '' and PriceFrom == '' and PriceTo == '':
            addon = ''
        elif addon == '':
            addon = f'&PriceFrom={PriceFrom}&PriceTo={PriceTo}'
        url = shop.link[:38] + str(page_number) + shop.link[39:] + addon
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options)
        driver.get(url)
        time.sleep(5)
        htmlSource = driver.page_source
        html = BeautifulSoup(htmlSource, 'html.parser')
        text = html.find_all("div", {"class", "tile-product"})
        for t in text:
            products_reg = re.findall(r'<a class="tile-product__name"(.+?)</a>', str(t))
            products_reg = re.findall(r'<strong>.*?</strong>|<span>.*?</span>|<span class="text-nowrap">.*?</span>',''.join(products_reg))
            product_label = [re.sub(r'(<.*?>)', '', ' '.join(products_reg))]
            new = re.findall(r'\d+,\d+', ''.join(re.findall(r'<span class="tile-product__current-price">.*?</span>', str(t))))
            old = re.findall(r'\d+,\d+', ''.join(re.findall(r'regularna:\xa0 (.+?)</span?', str(t))))
            if old and new and product_label:
                list_of_products_labels += product_label
                list_of_old_prices += old
                list_of_new_prices += new
                list_of_discounts += [100 - round(float(new[x].replace(',', '.')) / float(old[x].replace(',', '.')) * 100) for x in range(len(old))]
        max_web_pages = html.find_all("a", {"class", "pages__last"})

    elif shop.shop_name == "House":
        pass

    colors_list = []
    for i in list_of_discounts:
        if int(i) > 95:
            colors_list.append('#fa2b43')
        elif int(i) > 85:
            colors_list.append('#fc2756')
        elif int(i) > 80:
            colors_list.append('#fb2867')
        elif int(i) > 75:
            colors_list.append('#f92e79')
        elif int(i) > 70:
            colors_list.append('#f53689')
        elif int(i) > 65:
            colors_list.append('#ee4099')
        elif int(i) > 60:
            colors_list.append('#e64aa8')
        elif int(i) > 55:
            colors_list.append('#dc54b5')
        elif int(i) > 50:
            colors_list.append('#d05ec1')
        elif int(i) > 45:
            colors_list.append('#c367cb')
        elif int(i) > 40:
            colors_list.append('#b56fd4')
        elif int(i) > 35:
            colors_list.append('#a577da')
        elif int(i) > 30:
            colors_list.append('#967edf')
        elif int(i) > 25:
            colors_list.append('#8584e2')
        elif int(i) > 20:
            colors_list.append('#7589e4')
        elif int(i) > 15:
            colors_list.append('#648ee3')
        elif int(i) > 10:
            colors_list.append('#4696de')
        elif int(i) > 5:
            colors_list.append('#3a99da')
        else:
            colors_list.append('#319cd5')

    some_promos = list(
        zip(list_of_products_labels, list_of_discounts, list_of_old_prices, list_of_new_prices, colors_list))
    some_promos = sorted(list(some_promos), key=lambda x: x[1], reverse=True)

    p = Paginator(some_promos, 24)

    try:
        page_obj = p.page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(24)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    list_of_pages = re.findall('\d+', str(max_web_pages))

    context = {'shop': shop, 'some_promos': some_promos, 'page_obj': page_obj,
               'max': int(list_of_pages[0]), 'curr': int(page_number), 'next': str(int(page_number) + 1),
               'previous': str(int(page_number) - 1), 'PriceFrom': PriceFrom, 'PriceTo': PriceTo}
    return render(request, "promotions_and_discounts/shop_site.html", context)


@login_required
def shop_settings(request, shop_id):
    shop = Shop.objects.get(promos_available=True, id=shop_id)
    if request.POST:
        return redirect('promotions_and_discounts:shop_site', shop_id=shop.id)
    context = {'shop': shop}
    return render(request, "promotions_and_discounts/shop_settings.html", context)
