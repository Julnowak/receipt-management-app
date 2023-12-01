from scipy.ndimage import rotate as roto
import math
from typing import Tuple, Union
from difflib import get_close_matches
import cv2
import numpy as np
import imutils
from django.db.models import CharField
from django.db.models.functions import Lower
import matplotlib.pyplot as plt
from deskew import determine_skew
import pytesseract
from pytesseract import Output


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def median_blur(image):
    return cv2.medianBlur(image, 5)


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

CharField.register_lookup(Lower)


def main(img):
    # find the gradient map
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    grad = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

    # Binarize the gradient image
    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # #connect horizontally oriented regions
    # #kernal value (9,1) can be changed to improved the text detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    # display(connected)

    custom_config = r'--oem 1 --psm 6 -l pol -c tessedit_char_blacklist=/)!?(%'
    text = [pytesseract.image_to_string(connected, config=custom_config),
            pytesseract.image_to_string(cv2.bitwise_not(bw), config=custom_config)]

    return text


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
    custom_config = r'--oem 1 --psm 6 -l pol -c tessedit_char_blacklist=/)!?(%'
    contrast = 1  # Contrast control ( 0 to 127)
    brightness = 0.1  # Brightness control (0-100)

    out = cv2.addWeighted(img, contrast, img, 0, brightness)

    scale_percent = 100
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)

    dim = (width, height)
    img = cv2.resize(out, dim, interpolation=cv2.INTER_AREA)

    ratio = img.shape[0] / 2000.0
    img_resize = imutils.resize(img, height=2000)
    gray_image = img_resize

    text.append(pytesseract.image_to_string(gray_image, config=custom_config))
    img_array = np.array(gray_image)

    if np.mean(img_array[:, :]) < 200:
        blurred_image = cv2.GaussianBlur(erode(gray_image), (3, 3), 0)
        edged_img = cv2.Canny(blurred_image, 80, 200)
        pts = np.argwhere(edged_img > 0)

        # Finding the min and max points
        y1, x1 = pts.min(axis=0)
        y2, x2 = pts.max(axis=0)

        # Crop ROI from the givn image
        output_image = img_resize[y1:y2, x1:x2]
        org = output_image
    else:
        org = gray_image

    angle = determine_skew(org)
    rotated = rotation(org, angle)
    rotated = imutils.resize(rotated, height=2000)

    p = 0
    i = int(height / 3)
    num = 0

    img = rotated

    best = []
    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=custom_config)
    conf = d['conf']
    t = d['text']
    for i in range(len(conf)):
        if conf[i] > 70:
            best.append(t[i])
    while num != 3:
        if num == 2:
            cropped_image = img[p:, :]
        else:
            cropped_image = img[p:i, :]
        p = i
        i += height // 3
        num += 1
        try:
            text.append(pytesseract.image_to_string(cropped_image, config=custom_config))
            # print(pytesseract.image_to_data(cropped_image, config=custom_config))
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
        i += height // 2
        num += 1
        try:
            text.append(pytesseract.image_to_string(cropped_image, config=custom_config))
            # print(pytesseract.image_to_data(cropped_image, config=custom_config))
        except:
            pass

    text_from_m = main(rotated)

    return text + text_from_m, best


def make_OCR(img):
    angles = [0, 90, 180, 270]

    custom_config = r'--oem 1 --psm 4 -l pol'

    max_conf = 0
    second_conf = 0
    gray = get_grayscale(img)
    corrected_img = gray
    # Rotacja obrazu w głównych kątach - wybór prawidłowej orientacji
    for angle in angles:
        print('afsf')
        data_orig = np.array(corrected_img)
        data_rot = rotation(data_orig, angle)
        _, after_img = cv2.threshold(data_rot, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        text = pytesseract.image_to_data(after_img, output_type=Output.DICT, config=custom_config)
        conf = sum(text['conf']) / len(text['conf'])
        if conf > max_conf:
            second_conf = max_conf
            print(second_conf)
            max_conf = conf
            corrected_img_second = corrected_img
            corrected_img = after_img

    if abs(conf -max_conf) > 6:
        result = algo(corrected_img)

        return result[0], result[1]
    else:
        result = algo(corrected_img)
        result2 = algo(corrected_img_second)
        return result[0] + result2[0], result[1] + result2[1]


