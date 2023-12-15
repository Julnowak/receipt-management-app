from difflib import get_close_matches
import cv2
import numpy as np
import imutils
from deskew import determine_skew
import pytesseract
from pytesseract import Output
from datetime import date
from promotions_and_discounts.models import Shop
from receipts.models import Product
import re
from collections import Counter
import datetime


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def median_blur(image):
    return cv2.medianBlur(image, 7)


def remove_noise(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# dilation
def dilate(image, iter_num=1, ker=(7, 7)):
    kernel = np.ones(ker, np.uint8)
    return cv2.dilate(image, kernel, iterations=iter_num)


# erosion
def erode(image, iter_num=1):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=iter_num)


# opening - erosion followed by dilation
def opening(image, ker=(5, 5)):
    kernel = np.ones(ker, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\path\to\poppler-xx\bin"


def rotation(img, angle):
    # angle in degrees

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


def algo(img):
    text = []
    custom_config = r'--oem 1 --psm 6 -l pol -c tessedit_char_blacklist=)!?(%'
    contrast = 1  # Contrast control ( 0 to 127)
    brightness = 0.1  # Brightness control (0-100)

    out = cv2.addWeighted(img, contrast, img, 0, brightness)

    gray_image = out
    text.append(pytesseract.image_to_string(gray_image, config=custom_config))
    text.append(pytesseract.image_to_string(erode(gray_image), config=custom_config))
    text.append(pytesseract.image_to_string(dilate(gray_image), config=custom_config))
    angle = determine_skew(gray_image)
    rotated = rotation(gray_image, angle)
    rotated = imutils.resize(rotated, height=2000)

    img = rotated
    height = int(img.shape[0])
    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=custom_config)

    p = 0
    i = int(height / 3)
    num = 0

    while num != 3:
        if num == 2:
            cropped_image = img[p:, :]
        else:
            cropped_image = img[p:i, :]
        p = i
        i += int(height / 3)
        num += 1
        try:
            text.append(pytesseract.image_to_string(cropped_image, config=custom_config))
        except:
            pass

        try:
            text.append(pytesseract.image_to_string(erode(cropped_image), config=custom_config))
        except:
            pass

        try:
            text.append(pytesseract.image_to_string(dilate(cropped_image), config=custom_config))
        except:
            pass

    p = 0
    i = int(height / 2)
    num = 0

    while num != 2:
        if num == 1:
            cropped_image = img[p:, :]
        else:
            cropped_image = img[p:i, :]
        p = i
        i += int(height / 2)
        num += 1
        try:
            text.append(pytesseract.image_to_string(cropped_image, config=custom_config))
        except:
            pass

        try:
            text.append(pytesseract.image_to_string(erode(cropped_image), config=custom_config))
        except:
            pass

        try:
            text.append(pytesseract.image_to_string(dilate(cropped_image), config=custom_config))
        except:
            pass

    # find the gradient map
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    grad = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

    # Binarize the gradient image
    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # #connect horizontally oriented regions
    # #kernal value (9,1) can be changed to improved the text detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    text.append(pytesseract.image_to_string(connected, config=custom_config))
    text.append(pytesseract.image_to_string(erode(connected), config=custom_config))
    text.append(pytesseract.image_to_string(dilate(connected), config=custom_config))

    return text


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


products = Product.objects.values_list('product_name')
products_list = list(map(lambda x: x[0], products))

shops = Shop.objects.values_list('shop_name', 'nip', 'map_names')
sklepy = list(map(lambda x: x[0], shops.values_list('shop_name')))
shop_nip = shops.values_list('shop_name','nip')


def postprocessing(text):
    estimated_sum = []
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
                print("PSPSPSPPSPSPSPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", flag_main)

            if get_close_matches("sprzedaż", elem_list) or get_close_matches("suma", elem_list):
                flag_main = False
                print("PSPSPSPPSPSPSPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", flag_main)

            print(elem)
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
                        print("========")
                        print(cena)
                        suma_z_prod += float(cena)
                        print("========")
                    except:
                        pass
                # for i in base_prods:
                #     if get_close_matches(i, elem_list, cutoff=0.9):
                #         potencjalne_produkty.append(i)

            if not flag_main:
                for e in elem_list:
                    # Cutoff pomiędzy 0.6 a 0.7
                    shp = get_close_matches(e.lower(), sklepy, cutoff=0.85)
                    if shp:
                        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
                        print(shp)
                        for shpshp in shp:
                            if len(e.lower()) <= 4:
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
                shp = re.findall(ems, elem.lower())
                for shpshp in shp:
                    shop_list.append(shpshp)

            nip_match = re.findall(r'\d+[- ]*\d+[- ]*\d+', elem)
            for np in nip_match:
                print("GGGGhddddddddddddddddddddddddddddddddddGGGGGGGGGGGGG")
                print(nip_match)
                print("GGGGGGjdffjjdfffffffffffffffffffffGGGGGGGGGG")
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
                print("========")
                print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                print(d_match)
                print(d_match_mist)
                print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                print("========")
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

                        if date_string_shortyear:
                            pass
                except:
                    pass

            d_match_second = re.findall(r'\d+[-/]\d+[-/]\d+', elem)
            # d_match_second_lines = re.findall(r'\d+[-/]*\d+[-/]*\d+', elem)
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
            new_match_uncommon = re.findall(r'dn\.\d+[-/\.,r ]\d+[-/\., ]\d+', elem)
            if new_match_uncommon:
                for i in new_match_uncommon:
                    y = '20' + i[3:5]
                    m = i[6:8]
                    d = i[9:11]
                try:
                    list_of_dates += [datetime.date(int(y), int(m), int(d))]
                except:
                    pass

            if "suma" in elem.lower() or "kwota" in elem.lower() or get_close_matches("pln", elem_list) or \
                    "karta" in elem.lower() or get_close_matches("suma", elem_list) or "do zapłaty" in elem.lower() \
                    or "gotówka" in elem.lower() or "karta" in elem.lower() or get_close_matches("kwota", elem_list) \
                    or "cena" in elem.lower():

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

                            if "pln" in suma.lower() and not "ptu" in suma.lower() and not get_close_matches('reszta',
                                                                                                             suma.lower()):
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

        first_part = []
        second_part = []
        for imk in amo:
            first_part.append(str(imk)[:2])
            second_part.append(str(imk)[3:])

    category = ''
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(Counter(amo).most_common())
    print(Counter(shop_list).most_common())
    print(Counter(list_of_dates).most_common())
    return amo, list_of_dates, shop_list, category


def make_OCR(img):
    angles = [0, 90, 180, 270]
    main_price_list = []
    dat_dat_list = []
    shop_shop_list = []
    ret_shop_shop = ''
    ret_main_price = ''
    ret_dat_dat = ''
    text = []
    custom_config = r'--oem 1 --psm 4 -l pol'
    cases = []
    confs = dict()
    gray = get_grayscale(erode(remove_noise(img), 1))
    num = 0

    n = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text.append(pytesseract.image_to_string(n, config=custom_config))
    text.append(pytesseract.image_to_string(erode(n), config=custom_config))
    img_array = np.array(gray)
    # Przycięcie
    if np.mean(img_array[:, :]) < 200:
        blurred_image = cv2.GaussianBlur(gray, (3, 3), 0)
        edged_img = cv2.Canny(blurred_image, 80, 200)
        pts = np.argwhere(edged_img > 0)

        # Finding the min and max points
        y1, x1 = pts.min(axis=0)
        y2, x2 = pts.max(axis=0)

        # Crop ROI from the givn image
        output_image = img[y1:y2, x1:x2]
        org = output_image
    else:
        org = img

    # Rotacja obrazu w głównych kątach - wybór prawidłowej orientacji
    for angle in [0]:
        print('----OK----')
        corrected_img = get_grayscale(org)
        data_orig = np.array(corrected_img)
        data_rot = rotation(data_orig, angle)
        _, after_img = cv2.threshold(data_rot, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

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

        text.append(pytesseract.image_to_string(gray, config=custom_config))
        text.append(pytesseract.image_to_string(erode(gray), config=custom_config))
        text.append(pytesseract.image_to_string(dilate(gray), config=custom_config))

        # Remove shadows
        dilated_img = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(gray, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255,
                                 norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        ada = cv2.adaptiveThreshold(norm_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                    cv2.THRESH_BINARY, 11, 2)
        ada = (opening(median_blur(ada)))

        text.append(pytesseract.image_to_string(ada, config=custom_config))
        text.append(pytesseract.image_to_string(erode(ada), config=custom_config))
        text.append(pytesseract.image_to_string(dilate(ada), config=custom_config))

        work_img = cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        text.append(pytesseract.image_to_string(work_img, config=custom_config))
        text.append(pytesseract.image_to_string(erode(work_img), config=custom_config))
        text.append(pytesseract.image_to_string(dilate(work_img), config=custom_config))
        result = text + algo(work_img) + algo(ada)

        main_price, dat_dat, shop_shop, category = postprocessing(result)

        cases += [(main_price, dat_dat, shop_shop)]
        main_price_list += main_price
        dat_dat_list += dat_dat
        shop_shop_list += shop_shop

        if main_price and dat_dat and shop_shop:
            break
        num += 1

    if not ret_shop_shop and not ret_main_price and not ret_dat_dat:
        try:
            ret_shop_shop = Counter(shop_shop_list).most_common(1)[0][0]
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

    return ret_main_price, ret_dat_dat, ret_shop_shop, category, cases
