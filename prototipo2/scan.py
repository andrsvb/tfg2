import PyPDF2 as pypdf
import json
import os
from pdf2image import convert_from_path
import numpy as np
import cv2
from functools import reduce
import sys
import matplotlib.pyplot as plt



def detect_filled(boxes, exam, variant):
    data = {'exam': exam,
            'variant': variant,
            'num_boxes': boxes.__len__(),
            'exercises': []}
    count_ex = -1
    count_box = -1
    count_page = 1
    last_y = sys.float_info.max
    for box in boxes:
        exercise = box.split(sep=':')[2]
        if not data['exercises'] or (data['exercises'][count_ex]['exercise'] != exercise):
            count_ex = count_ex + 1
            count_box = -1
            data['exercises'].append(
                {
                    'exercise': exercise,
                    'checkboxes': []
                }
            )
            data['exercises'][count_ex]['student_marked'] = []
        x1, y1, x2, y2 = [float(i) for i in boxes[box]['/Rect']]
        if y1 > last_y:
            count_page = count_page + 1
        last_y = y1
        count_box = count_box + 1
        data['exercises'][count_ex]['checkboxes'].append(
            {
                'checkbox': str(count_ex) + ',' + str(count_box),
                'cords': [x1, y1, round(x2 - x1, 3), round(y2 - y1, 3)],
                'page': count_page
            })
        if boxes[box]['/V'] == '/Yes':
            data['exercises'][count_ex]['student_marked'].append(str(count_ex) + ',' + str(count_box))
    return data




def find_qrs(file, dpi):
    # TODO: improve qr detection
    pages = convert_from_path(file, dpi=dpi, thread_count=1, fmt='png')
    img_file = 'img_temp.png'
    qrs = []
    for page in pages:
        page.save(img_file)
        img = cv2.imread(img_file)
        qr_detect = cv2.QRCodeDetector()
        # process the image
        _, img_th = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
        # keep only black pixels
        hsv_img = cv2.cvtColor(img_th, cv2.COLOR_BGR2HSV)
        lower_values = np.array([0,0,0])
        upper_values = np.array([180,255,30])
        black_mask = cv2.inRange(hsv_img, lower_values, upper_values)
        # blur, sharpen and recognize the qr
        blur = cv2.GaussianBlur(black_mask, (3, 3), 0)
        sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
        value, coordinates, qr = qr_detect.detectAndDecode(~sharpen)
        # if it doesn't find the qr, loop blur and sharpen until it does, up to 5 times
        count = 0
        while qr is None:
            if count == 5:
                print('Error: QR not found')
                break
            blur = cv2.GaussianBlur(sharpen, (3, 3), 0)
            sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))
            value, coordinates, qr = qr_detect.detectAndDecode(~sharpen)
            count = count + 1
        exam, variant, page = '', '', ''
        if value:
            exam, variant, page = value.split(sep=',')
        qrs.append({'exam': exam, 'variant': variant, 'page': page, 'coordinates': coordinates})
    if os.path.exists(img_file):
        os.remove(img_file)
    return qrs




def analyse(file, sol_json="", dpi=300):
    # TODO: check if all qrs are from the same exam and variant
    # TODO: deal with the JSON file parameter
    # check if pyPDF2 can detect the boxes
    boxes = pypdf.PdfFileReader(file).getFields()
    # find qrs in the pdf
    qr_codes = find_qrs(file, dpi)
    exam, variant = qr_codes[0]['exam'], qr_codes[0]['variant']
    if boxes:
        # extract marked boxes with pyPDF2
        data = detect_filled(boxes, exam, variant)
    else:
        # extract marked boxes with OpenCV
        data = analyse_scanned(file, dpi, qr_codes)
    # TODO: open JSON file
    # TODO: compare with the data extracted from the pdf
    # TODO: grade the exam and export the grade
    return data






def analyse_scanned(file, dpi, qr_codes):
    img_file = 'img_temp.png'
    data = {'exam': qr_codes[0]['exam'], 'variant': qr_codes[0]['variant'], 'num_boxes': 0, 'boxes': []}
    pages_data = []
    pages = convert_from_path(file, dpi)
    for i, page in enumerate(pages):
        page.save(img_file)
        pages_data.append(analyse_page(img_file, dpi, qr_codes[i]['page'], qr_codes[i]['coordinates']))
    pages_data.sort(key=lambda k: k['page'])
    # TODO: add 'num_boxes' value to dict
    count = 0
    for page in pages_data:
        count = count + page['boxes'].__len__()
        for box in page['boxes']:
            data['boxes'].append(box)
    data['num_boxes'] = count
    if os.path.exists(img_file):
        os.remove(img_file)
    return data






def is_valid_box(x, y, w, h, qr_points, line_min_width, a_height, stats):
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






def analyse_page(file, dpi, page, qr_coordinates, debug=False):
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
    contours = contours[::-1]   # [::-1] because the order is reversed
    stats = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if is_valid_box(x,y,w,h,qr_points,line_min_width,a_height,stats):
            stats.append([x, y, w, h])
    if debug:
        for x,y,w,h in stats:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
        plt.figure(figsize=(20,20))
        plt.imshow(img)
    # check if the boxes are marked and store the data
    for x, y, w, h in stats:
        # get the inside of the box from the inverted grayscale image and check if it is marked
        x2, y2 = x + w, y + h
        box = {'stats': [x, y, w, h], 'page': page}
        inner_box = img_bin[y:y2, x:x2]
        box['is_marked'] = is_marked(inner_box, w, h)
        data['boxes'].append(box)
    return data



def is_marked(inner_box, width, height, b_th=0.1, validation_th = 0.1):
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





def format_scan(sol_data, scan_data):
    if not sol_data['num_boxes'] == scan_data['num_boxes']:
        error = 'Number of boxes incorrect'
        return {}
    data = {'exam': scan_data['exam'],
            'variant': scan_data['variant'],
            'num_boxes': scan_data['num_boxes'],
            'exercises': []
            }
    comparison = []
    count_ex = 0
    count_box = -1
    for scan_box in scan_data['boxes']:
        count_box = count_box + 1
        if sol_data['exercises'][count_ex]['checkboxes'].__len__() == count_box:
            count_box = 0
            count_ex = count_ex + 1
        if count_box == 0:
            data['exercises'].append({'exercise': sol_data['exercises'][count_ex]['exercise'],
                                      'checkboxes': [],
                                      'student_marked': []
                                      })
        sol_box = sol_data['exercises'][count_ex]['checkboxes'][count_box]
        data['exercises'][count_ex]['checkboxes'].append({'checkbox': sol_box['checkbox'],
                                                         'stats': scan_box['stats'],
                                                         'page': scan_box['page'],
                                                         'is_marked': scan_box['is_marked'],
                                                         })
        if scan_box['is_marked']:
            data['exercises'][count_ex]['student_marked'].append(sol_box['checkbox'])
        st_x = sol_box['cords'][0]
        st_y = sol_box['cords'][1]
        sc_x = scan_box['stats'][0]
        sc_y= scan_box['stats'][1]
        factor_x = sc_x / st_x
        factor_y = sc_y / st_y
        comparison.append({'cords_st': (st_x, st_y),
                           'cords_scan': (sc_x, sc_y),
                           'factors': (factor_x, factor_y)
                           })
    return comparison, data