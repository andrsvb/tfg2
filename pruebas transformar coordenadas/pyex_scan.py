import PyPDF2 as pypdf
import json
import os
from pdf2image import convert_from_path
import numpy as np
import math
import cv2
from functools import reduce
import sys
import matplotlib.pyplot as plt


def find_qrs_v1(file, dpi=400, verbose=True):
    pages = convert_from_path(file, dpi=dpi, thread_count=1, fmt='png')
    img_file = 'img_temp.png'
    qrs = []
    if verbose:
        nrows, ncols = 1, 3
        size = 6 * nrows
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18, size))
        count_draw_i = 0
    for i, page in enumerate(pages):
        page.save(img_file)
        img = cv2.imread(img_file)
        qr_detect = cv2.QRCodeDetector()
        # process the image
        _, img_th = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
        # keep only black pixels
        hsv_img = cv2.cvtColor(img_th, cv2.COLOR_BGR2HSV)
        lower_values = np.array([0, 0, 0])
        upper_values = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv_img, lower_values, upper_values)
        # blur, sharpen and recognize the qr
        blur = cv2.GaussianBlur(black_mask, (3, 3), 0)
        sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
        value, coordinates, qr = qr_detect.detectAndDecode(~sharpen)
        # if it doesn't find the qr, loop blur and sharpen until it does, up to 5 times
        count = 0
        while qr is None:
            if count == 5:
                e = 'QR not found in page %i of file %s' % (i, file)
                print(e)
                if os.path.exists(img_file):
                    os.remove(img_file)
                sys.exit(1)
            blur = cv2.GaussianBlur(sharpen, (3, 3), 0)
            sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
            value, coordinates, qr = qr_detect.detectAndDecode(~sharpen)
            count = count + 1
        exam, variant, page = '', '', ''
        if value:
            exam, variant, page = value.split(sep=',')
            if verbose:
                x_min, x_max, y_min, y_max = float("inf"), 0, float("inf"), 0
                for x, y in coordinates[0]:
                    if x < x_min:
                        x_min = x
                    if x > x_max:
                        x_max = x
                    if y < y_min:
                        y_min = y
                    if y > y_max:
                        y_max = y
                qr_zone = sharpen[int(y_min - 2):int(y_max + 2), int(x_min - 2):int(x_max + 2)]
                axs[count_draw_i].set_title("QR: %s" % value)
                axs[count_draw_i].imshow(~qr_zone, cmap='gray')
                count_draw_i = count_draw_i + 1
        qrs.append({'exam': exam, 'variant': variant, 'page': page, 'coordinates': coordinates})
    if verbose:
        plt.show()
    if os.path.exists(img_file):
        os.remove(img_file)
    return qrs


def is_valid_box_v0(x, y, w, h, qr_points, line_min_width, a_height, stats):
    inside_qr = (qr_points[0] - line_min_width < x < qr_points[1] + line_min_width and
                 qr_points[2] - line_min_width < y < qr_points[3] + line_min_width)
    if inside_qr:
        return False
    inside_header = (y < a_height * 0.1)
    if inside_header:
        return False
    wrong_size = (w > line_min_width * 1.4 or h > line_min_width * 1.4 or
                  w < line_min_width * 0.6 or h < line_min_width * 0.6)
    if wrong_size:
        return False
    is_new = True
    for box in stats:
        if box[0] < x < (box[0] + box[2]) and box[1] < y < (box[1] + box[3]):
            is_new = False
        elif x < box[0] < (x + w) and y < box[1] < (y + h):
            is_new = False
    return is_new


def is_marked_v0(inner_box, width, height, b_th=0.1, validation_th=0.1):
    # ignore the pixels closest to the border, to avoid noise
    x_min = int(width * b_th)
    y_min = int(height * b_th)
    x_max = width - x_min
    y_max = height - y_min
    area = x_max * y_max
    inner_box = inner_box[y_min:y_max, x_min:x_max]
    # get sum of colored pixels, box is considered full if sum is greater than 10% of area
    bits_filled = [[(0 if i < 100 else 1) for i in j] for j in inner_box]
    add = reduce(lambda a, b: a + b, [reduce(lambda c, d: c + d, row) for row in bits_filled])
    return add > (area * validation_th)


def analyse_page_v0(file, dpi, page, qr_coordinates):
    img = cv2.imread(file)
    line_min_width = int(dpi * 0.14)
    a_height, a_width = dpi * 11.6, dpi * 8.3
    data = {'page': page, 'boxes': []}
    qr_points = [qr_coordinates[0][0][0], qr_coordinates[0][1][0], qr_coordinates[0][0][1], qr_coordinates[0][2][1]]
    # grayscale, blur and sharpen
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_scale, (5, 5), 0)
    sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
    _, img_bin = cv2.threshold(sharpen, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_bin = ~img_bin
    # filter the image to keep only horizontal and vertical lines of at least line_min_width
    kernel_h = np.ones((1, line_min_width), np.uint8)
    kernel_v = np.ones((line_min_width, 1), np.uint8)
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
    img_bin_final = img_bin_h | img_bin_v
    # find contours in the filtered image
    contours, hierarchy = cv2.findContours(~img_bin_final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[::-1]  # [::-1] because the order is reversed
    stats = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if is_valid_box_v0(x, y, w, h, qr_points, line_min_width, a_height, stats):
            stats.append([x, y, w, h])
    # check if the boxes are marked and store the data
    for x, y, w, h in stats:
        # get the inside of the box from the inverted grayscale image and check if it is marked
        x2, y2 = x + w, y + h
        box = {'stats': [x, y, w, h], 'page': page}
        inner_box = img_bin[y:y2, x:x2]
        box['is_marked'] = is_marked_v0(inner_box, w, h)
        data['boxes'].append(box)
    return data

def analyse_scanned_v0(file, dpi, qr_codes):
    img_file = 'img_temp.png'
    data = {'exam': qr_codes[0]['exam'], 'variant': qr_codes[0]['variant'], 'num_boxes': 0, 'boxes': []}
    pages_data = []
    pages = convert_from_path(file, dpi)
    for i, page in enumerate(pages):
        page.save(img_file)
        pages_data.append(
            analyse_page_v0(img_file, dpi, qr_codes[i]['page'], qr_codes[i]['coordinates'])
        )
    pages_data.sort(key=lambda k: k['page'])
    count = 0
    for page in pages_data:
        count = count + page['boxes'].__len__()
        for box in page['boxes']:
            data['boxes'].append(box)
    data['num_boxes'] = count
    return data


def preprocess_img_v1(img, line_min_width, circle_min_width):
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(~gray_scale, cv2.MORPH_CLOSE, kernel)
    _, thresh = cv2.threshold(~morph, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_bin = ~thresh

    # filter the image to keep only horizontal and vertical lines of at least line_min_width
    kernel_h = np.ones((1, line_min_width), np.uint8)
    kernel_v = np.ones((line_min_width, 1), np.uint8)
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
    img_bin_squares = img_bin_h | img_bin_v

    # filter the image to keep only circles
    kernel_circle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (circle_min_width, circle_min_width))
    img_bin_circles = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_circle)

    return img_bin, img_bin_squares, img_bin_circles




def find_amc_circles_v1(amc_circles_expect, circle_min_width, img_bin_circle, verbose):
    amc_circles = []
    if verbose:
        nrows, ncols = 1, 4
        size = 5 * nrows
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12,size))
        count_draw_i = 0
    for circle in amc_circles_expect:
        # get area where the circle should be
        x_min, y_min = max(int(circle[0] - circle_min_width * 3), 1), max(int(circle[1] - circle_min_width * 3), 1)
        x_max, y_max = min(int(circle[0] + circle_min_width * 3), 3600), min(int(circle[1] + circle_min_width * 3), 3600)
        outer_box = img_bin_circle[y_min:y_max, x_min:x_max]
        print("y_min (%s) y_max (%s) x_min (%s) x_max(%s)" % (y_min,y_max, x_min,x_max))
        if verbose:
            axs[count_draw_i].set_title("AMC Circle %i" % count_draw_i)
            axs[count_draw_i].imshow(~outer_box, cmap='gray')
            count_draw_i = count_draw_i + 1
        contours, _ = cv2.findContours(~outer_box, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = ()
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            x = x_min + x
            y = y_min + y
            if (circle_min_width < w < circle_min_width * 1.4) and (circle_min_width < h < circle_min_width * 1.4):
                contour = (x, y, w, h)
        if contour:
            x, y, w, h = contour
            amc_circles.append((x + w / 2, y + h / 2))
    if verbose:
        plt.show()
    return amc_circles