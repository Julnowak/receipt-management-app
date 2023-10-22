from django.shortcuts import render
from .models import Shop
import requests
from bs4 import BeautifulSoup
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import itertools
# Create your views here.


def shop_selection(request):
    shops = Shop.objects.all()
    context = {'shops': shops}
    return render(request, "promotions_and_discounts/shop_selection.html", context)


def shop_site(request, shop_slug):
    shop = Shop.objects.get(slug=shop_slug)

    # lidl
    url = shop.link
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')

    some_promos = []
    list_of_products_labels = []
    list_of_discounts = []
    list_of_old_prices = []
    list_of_new_prices = []
    if shop.shop_name == "Lidl":
        max_web_pages = str(html.find_all("a", {"class", "s-pagination__link"}))
        list_of_pages = re.findall('=\d+', max_web_pages)

        for i in range(len(list_of_pages)+1):
            if i == 0:
                url = shop.link
            else:
                url = shop.link + f"?offset{i-1}"
            data = requests.get(url)
            html = BeautifulSoup(data.text, 'html.parser')

            product_name = html.find_all("h2", {"class", "grid-box__headline grid-box__text--dense"})
            discounts = html.find_all("div", {"class", "m-price__label"})
            old_price = html.find_all("div", {"class", "m-price__top"})
            new_price = html.find_all("div", {"class", "m-price__bottom"})

            products_reg = re.sub(r"(\s*<.*?>\s*)", '=', str(product_name))
            list_of_products_labels.append(re.findall("=([A-z]+.*?)=", products_reg))

            disc = re.sub(r"(<.*?>)", '', str(discounts))
            list_of_discounts.append(re.findall("(-\d\d%)", disc))

            olpri = re.sub(r"(<.*?>)", '', str(old_price))
            list_of_old_prices.append(re.findall("(\d+,\d+)", olpri))

            newpri = re.sub(r"(<.*?>)", '', str(new_price))
            list_of_new_prices.append(re.findall("(\d+,\d+)", newpri))

        list_of_products_labels = list(itertools.chain.from_iterable(list_of_products_labels))
        list_of_discounts = list(itertools.chain.from_iterable(list_of_discounts))
        list_of_old_prices = list(itertools.chain.from_iterable(list_of_old_prices))
        list_of_new_prices = list(itertools.chain.from_iterable(list_of_new_prices))
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

        some_promos = zip(list_of_products_labels,list_of_discounts,list_of_old_prices,list_of_new_prices, colors_list)
        some_promos = sorted(list(some_promos), key=lambda x: x[1],reverse=True)

    elif shop.shop_name == "Rossman":
        pass
    elif shop.shop_name == "House":
        print(url)
        print(html.find_all("a", {"class", "es-product-photo"}))
        # max_web_pages = str(html.find_all("a", {"class", "s-pagination__link"}))
        # list_of_pages = re.findall('=\d+', max_web_pages)
        #
        # for i in range(len(list_of_pages)+1):
        #     if i == 0:
        #         url = shop.link
        #     else:
        #         url = shop.link + f"?offset{i-1}"
        #     data = requests.get(url)
        #     html = BeautifulSoup(data.text, 'html.parser')
        #
        #     product_name = html.find_all("h2", {"class", "grid-box__headline grid-box__text--dense"})
        #     discounts = html.find_all("div", {"class", "m-price__label"})
        #     old_price = html.find_all("div", {"class", "m-price__top"})
        #     new_price = html.find_all("div", {"class", "m-price__bottom"})
        #
        #     products_reg = re.sub(r"(\s*<.*?>\s*)", '=', str(product_name))
        #     list_of_products_labels.append(re.findall("=([A-z]+.*?)=", products_reg))
        #
        #     disc = re.sub(r"(<.*?>)", '', str(discounts))
        #     list_of_discounts.append(re.findall("(-\d\d%)", disc))
        #
        #     olpri = re.sub(r"(<.*?>)", '', str(old_price))
        #     list_of_old_prices.append(re.findall("(\d+,\d+)", olpri))
        #
        #     newpri = re.sub(r"(<.*?>)", '', str(new_price))
        #     list_of_new_prices.append(re.findall("(\d+,\d+)", newpri))
        #
        # list_of_products_labels = list(itertools.chain.from_iterable(list_of_products_labels))
        # list_of_discounts = list(itertools.chain.from_iterable(list_of_discounts))
        # list_of_old_prices = list(itertools.chain.from_iterable(list_of_old_prices))
        # list_of_new_prices = list(itertools.chain.from_iterable(list_of_new_prices))
        # colors_list = []
        # for i in list_of_discounts:
        #     if int(i[1:-1]) > 95:
        #         colors_list.append('#fa2b43')
        #     elif int(i[1:-1]) > 85:
        #         colors_list.append('#fc2756')
        #     elif int(i[1:-1]) > 80:
        #         colors_list.append('#fb2867')
        #     elif int(i[1:-1]) > 75:
        #         colors_list.append('#f92e79')
        #     elif int(i[1:-1]) > 70:
        #         colors_list.append('#f53689')
        #     elif int(i[1:-1]) > 65:
        #         colors_list.append('#ee4099')
        #     elif int(i[1:-1]) > 60:
        #         colors_list.append('#e64aa8')
        #     elif int(i[1:-1]) > 55:
        #         colors_list.append('#dc54b5')
        #     elif int(i[1:-1]) > 50:
        #         colors_list.append('#d05ec1')
        #     elif int(i[1:-1]) > 45:
        #         colors_list.append('#c367cb')
        #     elif int(i[1:-1]) > 40:
        #         colors_list.append('#b56fd4')
        #     elif int(i[1:-1]) > 35:
        #         colors_list.append('#a577da')
        #     elif int(i[1:-1]) > 30:
        #         colors_list.append('#967edf')
        #     elif int(i[1:-1]) > 25:
        #         colors_list.append('#8584e2')
        #     elif int(i[1:-1]) > 20:
        #         colors_list.append('#7589e4')
        #     elif int(i[1:-1]) > 15:
        #         colors_list.append('#648ee3')
        #     elif int(i[1:-1]) > 10:
        #         colors_list.append('#4696de')
        #     elif int(i[1:-1]) > 5:
        #         colors_list.append('#3a99da')
        #     else:
        #         colors_list.append('#319cd5')
        #
        # some_promos = zip(list_of_products_labels,list_of_discounts,list_of_old_prices,list_of_new_prices, colors_list)
        # some_promos = sorted(list(some_promos), key=lambda x: x[1],reverse=True)
    context = {'shop': shop, 'some_promos': some_promos}
    return render(request, "promotions_and_discounts/shop_site.html", context)