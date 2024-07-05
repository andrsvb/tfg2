from pdf2image import convert_from_path
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np


def split_pages(file, base_name, dpi=300):
    pages = convert_from_path(file, dpi)
    # create the directory png
    if not os.path.exists('png'):
        os.mkdir('png')
    for i, page in enumerate(pages):
        # save each page in a png file
        im_file = 'png/' + base_name + '_page' + str(i) + '.png'
        page.save(im_file)


def show_example(img, title):
    example = img[1350:2350, 350:1350]
    plt.figure(figsize=(6,6))
    plt.title(title)
    plt.imshow(example, cmap='gray')



def show_example_comparison(imgs1, imgs2, imgs3, imgs4, titles):
    fig, axs = plt.subplots(4, 3, figsize=(18, 18))
    count = 0

    for img in imgs1:
        example = img[1350:2350, 350:1350]
        axs[0][count].set_title(titles[count])
        axs[0][count].imshow(example, cmap='gray')
        count += 1

    for img in imgs2:
        example = img[1350:2350, 350:1350]
        axs[1][count - 3].set_title("SHARPEN - " + titles[count - 3])
        axs[1][count - 3].imshow(example, cmap='gray')
        count += 1
        
    for img in imgs3:
        example = img[1350:2350, 350:1350]
        axs[2][count - 6].set_title("LINES - " + titles[count - 6])
        axs[2][count - 6].imshow(example, cmap='gray')
        count += 1
        
    for img in imgs4:
        example = img[1350:2350, 350:1350]
        axs[3][count - 9].set_title("BOXES - " + titles[count - 9])
        axs[3][count - 9].imshow(example, cmap='gray')
        count += 1
    plt.show()




def preprocess_img(file, dpi=300):
    img = cv2.imread(file)
    line_min_width = int(dpi * 0.14)

    title = ("IMAGEN BASE")
    show_example(img, title)

    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    title = ("IMAGEN EN BLACO Y NEGRO")
    show_example(gray_scale, title)

    kernel_sizes = [[3,3], [5,5], [7,7]]
    sharpen_k = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

    blurs, sharpens, lines, final, titles = [], [], [], [], []
    for (kx, ky) in kernel_sizes:
        img_copy = img
        titles.append("REGULAR BLUR - %s" % (kx))
        blur = cv2.blur(gray_scale, (kx, ky))
        blurs.append(blur)
        
        sharpen = cv2.filter2D(blur, -1, sharpen_k)
        sharpens.append(sharpen)

        _, img_bin = cv2.threshold(sharpen, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_bin = ~img_bin

        kernel_h = np.ones((1, line_min_width), np.uint8)
        kernel_v = np.ones((line_min_width, 1), np.uint8)
        img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
        img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
        img_bin_final = img_bin_h | img_bin_v
        lines.append(~img_bin_final)

        contours, hierarchy = cv2.findContours(~img_bin_final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[::-1]
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x,y), (x+w,y+h), (0,255,0), 1)
        final.append(img_copy)

    show_example_comparison(blurs, sharpens, lines, final, titles)

    blurs, sharpens, lines, final, titles = [], [], [], [], []
    for (kx, ky) in kernel_sizes:
        img_copy = img
        titles.append("GAUSSIAN BLUR - %s" % (kx))
        blur = cv2.GaussianBlur(gray_scale, (kx, ky), 0)
        blurs.append(blur)
        
        sharpen = cv2.filter2D(blur, -1, sharpen_k)
        sharpens.append(sharpen)

        _, img_bin = cv2.threshold(sharpen, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_bin = ~img_bin

        kernel_h = np.ones((1, line_min_width), np.uint8)
        kernel_v = np.ones((line_min_width, 1), np.uint8)
        img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
        img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
        img_bin_final = img_bin_h | img_bin_v
        lines.append(~img_bin_final)

        contours, hierarchy = cv2.findContours(~img_bin_final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[::-1]
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x,y), (x+w,y+h), (0,255,0), 1)
        final.append(img_copy)

    show_example_comparison(blurs, sharpens, lines, final, titles)
        
    blurs, sharpens, lines, final, titles = [], [], [], [], []
    for (kx, ky) in kernel_sizes:
        img_copy = img
        titles.append("MEDIAN BLUR - %s" % (kx))
        blur = cv2.medianBlur(gray_scale, kx)
        blurs.append(blur)
        
        sharpen = cv2.filter2D(blur, -1, sharpen_k)
        sharpens.append(sharpen)

        _, img_bin = cv2.threshold(sharpen, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_bin = ~img_bin

        kernel_h = np.ones((1, line_min_width), np.uint8)
        kernel_v = np.ones((line_min_width, 1), np.uint8)
        img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
        img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
        img_bin_final = img_bin_h | img_bin_v
        lines.append(~img_bin_final)

        contours, hierarchy = cv2.findContours(~img_bin_final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[::-1]
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img_copy, (x,y), (x+w,y+h), (0,255,0), 1)
        final.append(img_copy)
        
    show_example_comparison(blurs, sharpens, lines, final, titles)




def find_cboxes_img(file, dpi=300):
    img = cv2.imread(file)
    line_min_width = int(dpi * 0.14)
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray_scale, (5, 5), 0)
    sharpen = cv2.filter2D(blur, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))

    _, img_bin = cv2.threshold(sharpen, 0, 225, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_bin = ~img_bin

    kernel_h = np.ones((1, line_min_width), np.uint8)
    kernel_v = np.ones((line_min_width, 1), np.uint8)
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
    img_bin_final = img_bin_h | img_bin_v

    stats = []
    contours, hierarchy = cv2.findContours(~img_bin_final, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[::-1]
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        stats.append([x, y, w, h])
    
    return stats



def draw_boxes(file, stats):
    img = cv2.imread(file)

    ncols = 5
    nrows = int(stats.__len__() / ncols) + 1
    fig, axs = plt.subplots(nrows, ncols, figsize=(20, nrows*4))

    count = 0
    for (box) in stats:
        x, y, w, h = box
        i, j = int(count/5), count%5
        count += 1

        inner_box = img[y:y+h, x:x+w]

        axs[i,j].imshow(inner_box)

    plt.show()



def is_valid_box(x, y, w, h, stats, dpi=300):
    line_min_width = int(dpi * 0.14)
    a_height, a_width = dpi * 11.6, dpi * 8.3
    qr_points = np.array([6.4, 7, 10.2, 10.7]) * dpi

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


