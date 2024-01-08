import itertools
import pandas as pd
from difflib import get_close_matches
import cv2
import numpy as np
import imutils
from deskew import determine_skew
import pytesseract
from pytesseract import Output
from datetime import date
import re
from collections import Counter
import datetime
from promotions_and_discounts.models import Shop
from categories.models import BaseCategories


sklepy = Shop.objects.all().values_list("shop_name", flat=True)
sklepy = [s.lower() for s in sklepy]

sklepy_map = dict()
for mapped, shop_name in list(set(Shop.objects.values_list("map_names", "shop_name"))):
    if mapped is not None:
        words = mapped.split(',')
        for w in words:
            w = w.strip()
            sklepy.append(w)
            sklepy_map[w] = shop_name.lower()

categories = BaseCategories.objects.values_list('category_name', flat=True)
categories = [c.lower() for c in categories]

my_set = list(set(Shop.objects.values_list("nip", flat=True)))
my_set = [x for x in my_set if x is not None]
NIP = [x for x in my_set if x is not None]

nip_to_shop = dict()
for n, name in Shop.objects.values_list("nip", "shop_name"):
    if n is not None:
        nip_to_shop[n] = name

# from kaggle
products_base = pd.read_csv('receipts/BASE.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
a = products_base['Pname'].dropna().drop_duplicates().str.replace('\d+', '', regex=True)
a = list(a.str.lower().str.split()[1:])
df = pd.DataFrame({'words': list(itertools.chain.from_iterable(a))})
df = df.drop_duplicates()
base_prods = df['words'].str.replace('\\+', '', regex=True).loc[df['words'].str.len() >= 3]

category_shop_dict = dict()
for cat, name in Shop.objects.values_list("category__category_name", "shop_name"):
    if name is not None:
        category_shop_dict[name.lower()] = cat

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def median_blur(image):
    return cv2.medianBlur(image, 7)


def remove_noise(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def dilate(image, iter_num=1, ker=(7, 7)):
    kernel = np.ones(ker, np.uint8)
    return cv2.dilate(image, kernel, iterations=iter_num)


def erode(image, iter_num=1):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=iter_num)


def opening(image, ker=(5, 5)):
    kernel = np.ones(ker, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def canny(image):
    return cv2.Canny(image, 100, 200)


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\path\to\poppler-xx\bin"


def rotation(img, angle):
    height, width = img.shape[0], img.shape[1]
    center = (width / 2, height / 2)

    rotation_mat = cv2.getRotationMatrix2D(center, angle, 2)

    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w / 2 - center[0]
    rotation_mat[1, 2] += bound_h / 2 - center[1]

    rotated_mat = cv2.warpAffine(img, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def cropping(rotated_img, max_num):
    height = int(rotated_img.shape[0])
    crop_output = []
    p = 0
    i = int(height / max_num)
    num = 0

    while num != max_num:
        if num == max_num-1:
            cropped_image = rotated_img[p:, :]
        else:
            cropped_image = rotated_img[p:i, :]
        p = i
        i += int(height / max_num)
        num += 1
        crop_output += triple_OCR_text(cropped_image)
    return crop_output


def triple_OCR_text(img):
    text = []
    custom_config = r'--oem 1 --psm 6 -l pol -c tessedit_char_blacklist=)!?(%'  # konfiguracja tesseract

    try:
        text.append(pytesseract.image_to_string(img, config=custom_config))
    except:
        pass

    try:
        text.append(pytesseract.image_to_string(erode(img), config=custom_config))
    except:
        pass

    try:
        text.append(pytesseract.image_to_string(dilate(img), config=custom_config))
    except:
        pass
    return text


def algo(img):
    output = []
    contrast = 1  # kontrast
    brightness = 0.1  # jasność
    out = cv2.addWeighted(img, contrast, img, 0, brightness)
    output += triple_OCR_text(out)

    angle = determine_skew(out)
    rotated = rotation(out, angle)
    rotated = imutils.resize(rotated, height=2000)

    output += cropping(rotated,3)
    output += cropping(rotated,2)

    # gradientowe przekształcenie morfologiczne z kernelem w postaci elipsy
    k_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, k_ellipse)

    # Binaryzacja
    after_bin = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[0]
    k_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(after_bin, cv2.MORPH_CLOSE, k_rect)

    output += triple_OCR_text(closed)
    return output


def possible_date(date_poss):
    flag_date_make = False
    date_poss = date_poss.replace('-', ' ')
    d = date_poss[:2]
    m = date_poss[3:5]
    y_first = date_poss[6:11]
    poss_dates = []

    try:
        if 2000 <= int(y_first) <= date.today().year:
            if int(m) <= 12 and int(d) <= 31:
                poss_dates += [date(int(y_first), int(m), int(d))]
            else:
                flag_date_make = True

        if flag_date_make:
            print('p')
            poss_d = []
            poss_m = []
            poss_y = []
            for i in [d, m, y_first]:
                new = i.replace('9', '0')
                new_new = i.replace('7', '2')

                new_2 = new_new.replace('9', '0')
                new_new_2 = new.replace('7', '2')
                if i == d:
                    poss_d += list({new, new_new, new_2, new_new_2})
                elif i == m:
                    poss_m += list({new, new_new, new_2, new_new_2})
                elif i == y_first:
                    poss_y += list({new, new_new, new_2, new_new_2})

            if d[0] not in ['0', '1', '2', '3']:
                if d[0] == '7':
                    d = '2' + d[1]
                elif d[0] == '9' or d[0] == '6':
                    d = '0' + d[1]
                poss_d += [d]

            if m[0] not in ['0', '1']:
                if m[0] == '9' or m[0] == '6':
                    m = '0' + d[1]
                poss_m += [m]

            if m[0] == '1' and m[1] not in ['0', '1', '2']:
                if m[1] == '9' or m[1] == '6' or m[1] == '8':
                    m = m[0] + '0'
                if m[1] == '4':
                    m = m[0] + '1'
                if m[1] == '5' or m[1] == '7':
                    m = m[0] + '2'
                poss_m += [m]

            for di in poss_d:
                for mi in poss_m:
                    for yi in poss_y:
                        try:
                            n_date = date(int(yi), int(mi), int(di))
                            if n_date <= date.today():
                                poss_dates += [n_date]
                        except:
                            pass
    except:
        pass

    return poss_dates


def possible_date_reverse(date_poss):
    date_poss = date_poss.replace('-', ' ')
    d = date_poss[8:]
    m = date_poss[5:7]
    y_first = date_poss[:4]
    poss_dates = []
    flag_date_make = False

    try:
        if 2000 <= int(y_first) <= date.today().year:
            if int(m) <= 12 and int(d) <= 31:
                poss_dates += [date(int(y_first), int(m), int(d))]
            else:
                flag_date_make = True

        if flag_date_make:
            poss_d = []
            poss_m = []
            poss_y = []
            for i in [d, m, y_first]:
                new = i.replace('9', '0')
                new_new = i.replace('7', '2')

                new_2 = new_new.replace('9', '0')
                new_new_2 = new.replace('7', '2')
                if i == d:
                    poss_d += list({new, new_new, new_2, new_new_2})
                elif i == m:
                    poss_m += list({new, new_new, new_2, new_new_2})
                elif i == y_first:
                    poss_y += list({new, new_new, new_2, new_new_2})

            if d[0] not in ['0', '1', '2', '3']:
                if d[0] == '7':
                    d = '2' + d[1]
                elif d[0] == '9' or d[0] == '6':
                    d = '0' + d[1]
                poss_d += [d]

            if m[0] not in ['0', '1']:
                if m[0] == '9' or m[0] == '6':
                    m = '0' + m[1]
                poss_m += [m]

            if m[0] == '1' and m[1] not in ['0', '1', '2']:
                if m[1] == '9' or m[1] == '6' or m[1] == '8':
                    m = m[0] + '0'
                if m[1] == '4':
                    m = m[0] + '1'
                if m[1] == '5' or m[1] == '7':
                    m = m[0] + '2'
                poss_m += [m]

            for di in poss_d:
                for mi in poss_m:
                    for yi in poss_y:
                        try:
                            n_date = date(int(yi), int(mi), int(di))
                            if n_date <= date.today():
                                poss_dates += [n_date]
                        except:
                            pass
    except:
        pass
    return poss_dates


def read_normal(data_string):
    m = int(data_string[3:5])
    d = int(data_string[:2])
    y_first = data_string[6:11]
    if y_first[0] == '0':
        y_first = '2' + y_first[1:]

    y = int(y_first)
    if m == 14:
        m = 11

    if d == 77:
        d = 22

    if y < 2000:
        y = int('20' + str(y)[2:])
    return y, m, d


def read_reverse(date_string):
    d = int(date_string[8:11])
    m = int(date_string[5:7])
    y_first = date_string[:4]
    if y_first[0] == '0':
        y_first = '2' + y_first[1:]

    y = int(y_first)

    if m == 14:
        m = 11

    if d == 77:
        d = 22

    if y < 2000:
        y = int('20' + str(y)[2:])
    return y, m, d


def postprocessing(text):
    cats = []
    suma = ""
    potencjalne_produkty = []
    list_of_dates = []
    amo = []
    shop_list = []
    occurence_count = 0

    for t in text:
        suma_z_prod = 0
        flag_main = False
        for elem in t.split("\n"):
            elem_list = elem.lower().split(" ")
            if get_close_matches("fiskalny", elem_list) or get_close_matches("paragon", elem_list):
                flag_main = True
            if get_close_matches("sprzedaż", elem_list) or get_close_matches("suma", elem_list):
                flag_main = False
            if flag_main:
                cena = None
                if re.findall(f"(\d+\s*,\s*\d+)", elem):
                    cena = re.findall(f"(\d+\s*,\s*\d+)", elem)[0]

                if re.findall(f"(\d+\s*\\.\s*\d+)", elem):
                    cena = re.findall(f"(\d+\s*\\.\s*\d+)", elem)[0]
                if cena:
                    try:
                        if "," in cena:
                            cena = re.findall(f"(\d+,\d+)", cena)[0].replace(",", ".")
                        elif "." in cena:
                            cena = re.findall(f"(\d+\\.\d+)", cena)[0]
                    except:
                        pass
                for i in base_prods:
                    if get_close_matches(i, elem_list, cutoff=0.9):
                        potencjalne_produkty.append(i)
                # potencjalne_produkty.append(elem)

            if not flag_main:
                for e in elem_list:
                    # Cutoff pomiędzy 0.6 a 0.7
                    shp = get_close_matches(e.lower(), sklepy, cutoff=0.85)
                    if shp:
                        for shpshp in shp:
                            if len(e.lower()) <= 4 and e.lower() in sklepy:
                                shop_list.append(shpshp)
                            else:
                                shop_list.append(shpshp)
                                shop_list.append(shpshp)
                    if e.lower() in sklepy:
                        if len(e.lower()) <= 4:
                            shop_list.append(e)
                        else:
                            shop_list.append(e)
                            shop_list.append(e)

                for ems in sklepy:
                    if len(ems) <= 4:
                        shp = re.findall(ems, elem.lower())
                        if shp:
                            for shpshp in shp:
                                newi = get_close_matches(shpshp, sklepy, cutoff=0.85)
                                for inewi in newi:
                                    shop_list.append(inewi)
                    else:
                        shp = get_close_matches(ems, elem_list, cutoff=0.85)
                        shp += re.findall(ems, elem.lower())
                        shp += re.findall(ems, elem.lower())
                        if shp:
                            for shpshp in shp:
                                newi = get_close_matches(shpshp, sklepy, cutoff=0.85)
                                for inewi in newi:
                                    shop_list.append(inewi)

            nip_match = re.findall(r'\d+[- ]*\d+[- ]*\d+', elem)
            for np in nip_match:
                try:
                    shop_list += [nip_to_shop[np]] * 5
                except:
                    pass

            # Wykrycie daty - konkretne wykrycie
            d_match = re.findall(r'\d+[-/\. ]*\d+[-/\., ]*\d+', elem)
            d_match_mist = re.findall(r'\d+[-/\. ]*\d+[-/\., ]*\d+', elem.replace('/', '7'))
            if d_match or d_match_mist:
                if d_match:
                    elem = elem
                else:
                    elem = elem.replace('/', '7')
                print(d_match)
                print(d_match_mist)

                date_string_shortyear = re.findall(r'\d{2}[-/\. ]\d{2}[-/\. ]\d{2}', elem)
                date_string_normal = re.findall(r'\d{2}[-/\.]\d{2}[-/\.]\d{4}', elem)
                date_string_other = re.findall(r'\d{4}[-/\.]\d{2}[-/\.]\d{2}', elem)
                try:
                    if date_string_normal:
                        for i in date_string_normal:
                            list_of_dates += possible_date(i)
                            y, m, d = read_normal(i)

                            if 2000 <= y <= datetime.date.today().year and m <= 12 and d <= 31:
                                try:
                                    date_bought = datetime.date(y, m, d)
                                    list_of_dates += date_bought
                                except:
                                    pass

                    if date_string_other:
                        for date_string in date_string_other:
                            list_of_dates += possible_date_reverse(date_string)
                            y, m, d = read_reverse(date_string)

                            flag = False
                            if 2000 <= y <= datetime.date.today().year and m <= 12 and d <= 31:
                                try:
                                    date_bought = datetime.date(y, m, d)
                                    list_of_dates += date_bought
                                except:
                                    flag = True

                                if flag:
                                    try:
                                        date_bought = datetime.date(y, d, m)
                                        list_of_dates += date_bought
                                    except:
                                        flag = True

                except:
                    pass

            d_match_second = re.findall(r'\d+[-/]\d+[-/]\d+', elem)

            if d_match_second:
                print("GGGGGGGGGGGGGGGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGGGGGGGGGGGGG")
                print(d_match_second)
                print("GGGGGGGGGGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGGGGG")
                for v in d_match_second:
                    try:
                        list_of_dates += possible_date_reverse(v)
                        y, m, d = read_reverse(v)
                        if 2000 <= y <= datetime.date.today().year and m <= 12 and d <= 31:
                            date_bought = datetime.date(y, m, d)
                            list_of_dates += date_bought
                    except:
                        pass

                    try:
                        list_of_dates += possible_date(v)
                        y, m, d = read_normal(v)
                        if 2000 <= y <= datetime.date.today().year and m <= 12 and d <= 31:
                            date_bought = datetime.date(y, m, d)
                            list_of_dates += date_bought
                    except:
                        pass
            # #match new dn.22r03.09
            new_match_uncommon = re.findall(r'\d+[-/\.,r ]\d+[-/\., ]+\d+', elem)
            if new_match_uncommon:
                for i in new_match_uncommon:
                    i = i.replace(' ', '').replace('r', '').replace('.', '')
                    y = '20' + i[:2]
                    m = i[2:4]
                    d = i[4:6]
                try:
                    if 2000 <= int(y) <= datetime.date.today().year and int(m) <= 12 and int(d) <= 31:
                        list_of_dates += [datetime.date(int(y), int(m), int(d))]
                except:
                    pass

            if "suma" in elem.lower() or "kwota" in elem.lower() or get_close_matches("pln", elem_list) or \
                    "karta" in elem.lower() or get_close_matches("suma", elem_list) or "do zapłaty" in elem.lower() \
                    or "gotówka" in elem.lower() or "karta" in elem.lower() or get_close_matches("kwota", elem_list) \
                    or "cena" in elem.lower() or "sprzedaż" in elem.lower():

                if get_close_matches("reszta", elem_list):
                    print("YRYRYRYRYRYRYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                else:
                    suma = elem
                    try:
                        print("++++++++++++++++++++++++++++++++++")
                        print(suma)
                        print("++++++++++++++++++++++++++++++++++")

                        flag = False
                        if re.findall(f"(\d+\s*,\s*\d+)", elem):
                            sm = re.findall(f"(\d+\s*,\s*\d+)", elem)[0]
                            flag = True

                        if re.findall(f"(\d+\s*\\.\s*\d+)", elem):
                            sm = re.findall(f"(\d+\s*\\.\s*\d+)", elem)[0]
                            flag = True

                        if flag:
                            sm = ''.join(sm.split(' '))
                            print(f"++++++++++++++{sm}+++++++++++++++")
                            if "suma pln" in suma.lower() and not "ptu" in suma.lower():
                                amo += [sm] * 3

                            if "pln" in suma.lower() and not "ptu" in suma.lower() \
                                    and not get_close_matches('reszta', suma.lower()):
                                amo += [sm] * 3

                            if "karta visa debit" in suma.lower() and "pln" in suma.lower():
                                amo += [sm] * 3

                            if "karta visa" in suma.lower():
                                amo += [sm] * 3

                            if not "ptu" in suma.lower():
                                try:
                                    amo.append(sm)
                                except:
                                    pass
                    except IndexError:
                        pass
        print("############################################################")
        print(amo)
        first_part = []
        second_part = []
        for imk in amo:
            first_part.append(str(imk)[:2])
            second_part.append(str(imk)[3:])
        print(shop_list)
        print(list_of_dates)
        print("############################################################")

    for shop_i in shop_list:
        if shop_i.lower() in sklepy_map.keys():
            cats += [category_shop_dict[sklepy_map[shop_i.lower()]]]
        elif shop_i in [ss.lower() for ss in sklepy]:
            try:
                cats += [category_shop_dict[shop_i.lower()]]
            except:
                pass

    category = cats
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(Counter(amo).most_common())
    print(Counter(shop_list).most_common())
    print(Counter(list_of_dates).most_common())
    print(potencjalne_produkty)
    return amo, list_of_dates, shop_list, category


def triple_check(img_to_check):
    custom_config = r'--oem 1 --psm 6 -l pol -c tessedit_char_blacklist=)!?(%'
    text = []
    text += [pytesseract.image_to_string(img_to_check, config=custom_config)]
    text += [pytesseract.image_to_string(erode(img_to_check), config=custom_config)]
    text += [pytesseract.image_to_string(dilate(img_to_check), config=custom_config)]
    return text


def make_OCR(img):
    angles = [0, 90, 180, 270]
    custom_config = r'--oem 1 --psm 4 -l pol'

    main_price_list = []
    dat_dat_list = []
    shop_shop_list = []
    category_list = []
    text = []
    cases = []
    confs = dict()
    ret_shop_shop = ''
    ret_main_price = ''
    ret_dat_dat = ''

    gray = get_grayscale(erode(img, 1))
    n = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text += triple_check(n)

    img_array = np.array(gray)
    # Przycięcie
    if np.mean(img_array[:, :]) < 200:
        blurred_img = cv2.GaussianBlur(gray, (3, 3), 0)
        edged_img = cv2.Canny(blurred_img, 80, 200)
        points = np.argwhere(edged_img > 0)

        # Finding the min and max points
        y0, x0 = points.min(axis=0)
        y1, x1 = points.max(axis=0)

        # Crop ROI from the givn image
        org = img[y0:y1, x0:x1]
    else:
        org = img

    # Rotacja obrazu w głównych kątach - wybór prawidłowej orientacji
    for angle in angles:
        print('----OK----')
        corrected_img = get_grayscale(org)
        data_orig = np.array(corrected_img)
        data_rot = rotation(data_orig, angle)
        after_img = cv2.threshold(data_rot, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        train_text = pytesseract.image_to_data(after_img, output_type=Output.DICT, config=custom_config)
        conf = sum(train_text['conf']) / len(train_text['conf'])
        confs[conf] = angle

    s = sorted(confs, reverse=True)
    s_angles = []
    for si in s:
        s_angles.append(confs[si])

    for ang in s_angles:
        # Obraz po korekcji orientacji
        corrected = rotation(org, ang)

        # Obraz szary
        gray = get_grayscale(corrected)

        text += triple_check(gray)

        # Remove shadows
        dilated_img = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(gray, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255,
                                 norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        ada = cv2.adaptiveThreshold(norm_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ada = opening(median_blur(ada))

        text += triple_check(ada)

        work_img = cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        text += triple_check(work_img)
        result = text + algo(work_img) + algo(ada)

        main_price, dat_dat, shop_shop, category = postprocessing(result)

        cases += [(main_price, dat_dat, shop_shop)]
        main_price_list += main_price
        dat_dat_list += dat_dat
        shop_shop_list += shop_shop
        category_list += category

        if main_price_list and dat_dat_list and shop_shop_list and category_list:
            break

    # CHOICE
    try:
        ret_shop_shop = Counter(shop_shop_list).most_common(1)[0][0]
        if ret_shop_shop.capitalize() not in Shop.objects.values_list("shop_name", flat=True):
            ret_shop_shop = sklepy_map[ret_shop_shop]
    except:
        ret_shop_shop = ''

    try:
        ret_main_price = Counter(main_price_list).most_common(1)[0][0]
    except:
        ret_main_price = ''

    try:
        ret_dat_dat = Counter(dat_dat_list).most_common(1)[0][0]
    except:
        ret_dat_dat = ''
    try:
        ret_category = Counter(category_list).most_common(1)[0][0]
    except:
        ret_category = ''

    return ret_main_price, ret_dat_dat, ret_shop_shop, ret_category, cases
