from django.shortcuts import render
from .models import Shop
import requests
from bs4 import BeautifulSoup
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


def shop_selection(request):
    shops = Shop.objects.all()
    context = {'shops': shops}
    return render(request, "promotions_and_discounts/shop_selection.html", context)


def shop_site(request, shop_slug):
    shop = Shop.objects.get(slug=shop_slug)

    # lidl
    url = shop.link
    print(url)
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    some_promos = []
    if shop.shop_name == "Lidl":
        product_name = html.find_all("h2", {"class", "grid-box__headline grid-box__text--dense"})
        discounts = html.find_all("div", {"class", "m-price__label"})
        old_price = html.find_all("div", {"class", "m-price__top"})
        new_price = html.find_all("div", {"class", "m-price__bottom"})

        products_reg = re.sub(r"(\s*<.*?>\s*)", '=', str(product_name))
        list_of_products_labels = re.findall("=([A-z]+.*?)=", products_reg)

        disc = re.sub(r"(<.*?>)", '', str(discounts))
        list_of_discounts = re.findall("(-\d\d%)", disc)

        olpri = re.sub(r"(<.*?>)", '', str(old_price))
        list_of_old_prices = re.findall("(\d+,\d+)", olpri)

        newpri = re.sub(r"(<.*?>)", '', str(new_price))
        list_of_new_prices = re.findall("(\d+,\d+)", newpri)

        colors_list = []
        for i in list_of_discounts:
            if int(i[1:-1]) > 95:
                colors_list.append('#fa2b43')
            elif int(i[1:-1]) > 85:
                colors_list.append('#fc2756')
            elif int(i[1:-1]) > 80:
                colors_list.append('#fb2867')
            elif int(i[1:-1]) > 75:
                colors_list.append('#f92e79')
            elif int(i[1:-1]) > 70:
                colors_list.append('#f53689')
            elif int(i[1:-1]) > 65:
                colors_list.append('#ee4099')
            elif int(i[1:-1]) > 60:
                colors_list.append('#e64aa8')
            elif int(i[1:-1]) > 55:
                colors_list.append('#dc54b5')
            elif int(i[1:-1]) > 50:
                colors_list.append('#d05ec1')
            elif int(i[1:-1]) > 45:
                colors_list.append('#c367cb')
            elif int(i[1:-1]) > 40:
                colors_list.append('#b56fd4')
            elif int(i[1:-1]) > 35:
                colors_list.append('#a577da')
            elif int(i[1:-1]) > 30:
                colors_list.append('#967edf')
            elif int(i[1:-1]) > 25:
                colors_list.append('#8584e2')
            elif int(i[1:-1]) > 20:
                colors_list.append('#7589e4')
            elif int(i[1:-1]) > 15:
                colors_list.append('#648ee3')
            elif int(i[1:-1]) > 10:
                colors_list.append('#4696de')
            elif int(i[1:-1]) > 5:
                colors_list.append('#3a99da')
            else:
                colors_list.append('#319cd5')

        max_web_pages = str(html.find_all("a", {"class", "s-pagination__link"}))
        list_of_pages = re.findall('=\d+', max_web_pages)

        some_promos = zip(list_of_products_labels,list_of_discounts,list_of_old_prices,list_of_new_prices, colors_list)


    # for pages in list_of_pages:
    #
    #     new_url = url + f"?offset{pages}"
    #     print(new_url)
    #     new_data = requests.get(new_url)
    #     new_html = BeautifulSoup(new_data.text, 'html.parser')
    #     new = new_html.find_all("div", {"class","m-price__price m-price__price--small"})
    #
    #     print(len(new))

    context = {'shop': shop, 'some_promos': some_promos}
    return render(request, "promotions_and_discounts/shop_site.html", context)