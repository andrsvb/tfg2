import cv2
import numpy as np
import json


def find_checkboxes(file):
    img = cv2.imread(file)
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th1, img_bin = cv2.threshold(gray_scale, 150, 225, cv2.THRESH_BINARY)
    img_bin = ~img_bin

    # set min width of lines for the rectangle: 20 pixels
    line_min_width = 20
    kernal_h = np.ones((1, line_min_width), np.uint8)
    kernal_v = np.ones((line_min_width, 1), np.uint8)

    # find horizontal and vertical lines and join them
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v)
    img_bin_final = img_bin_h | img_bin_v

    # find conected lines that form a box
    _, labels, stats, _ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)

    # for x, y, w, h, area in stats[2:]:
    #    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return stats[2:]


def check_marked(file, stats):
    # would check the boxes in 'stats' on the png 'file' to see if marked
    # stats: [ x, y, width, height, area ] * number of checboxes. area appears to be the blank area inside the square
    # for now: check if the inside area is smaller than 80% of the square's area
    # if ( stats[area] < ( stats[width] * stats[height] ) * 0.8 )
    is_checked = {'checkboxes': []}
    for row in stats:
        sq_area = row[2] * row[3]
        is_checked['checkboxes'].append(
            {
                'x': int(row[0]),
                'y': int(row[1]),
                'w': int(row[2]),
                'h': int(row[3]),
                'a': int(row[4]),
                'is_checked': str(row[4] < sq_area * 0.8)
            }
        )
    return is_checked


def match(data_sol, data_scan):
    comparacion = {'examen': []}

    i = 0  # to iterate the exercises
    j = 0  # to iterate the boxes in each exercise
    # read the data from the solutions
    for box in data_sol['checkboxes']:

        # if it is the first box to be read (i, j already = 0)
        if not comparacion['examen']:
            comparacion['examen'].append(
                {
                    'ejercicio': box['checkbox'].split()[0],
                    'num_boxes': 0,
                    'marked_sol': [],
                    'marked_scan': []
                }
            )

        # if it is a box that is from the same exercise as the previous box read (i =, j ++)
        elif comparacion['examen'][i]['ejercicio'] == box['checkbox'].split()[0]:
            j = j + 1

        # if it is a box that is from a different exercise than the previous box read (i ++, j = 0)
        else:
            j = 0
            i = i + 1
            comparacion['examen'].append(
                {
                    'ejercicio': box['checkbox'].split()[0],
                    'num_boxes': 0,
                    'marked_sol': [],
                    'marked_scan': []
                }
            )

        # update the number of boxes in the current exercise
        comparacion['examen'][i]['num_boxes'] = j + 1

        # check if the box is marked on the solution, and append to the dict if so
        if box['state'] == '/Yes':
            comparacion['examen'][i]['marked_sol'].append(j + 1)

    i = 0
    j = 0
    j_max = 0
    # read the data from the scans
    for box in data_scan['checkboxes']:
        # if it is the first box to be read
        if j_max == 0:
            j_max = comparacion['examen'][i]['num_boxes']

        # if all the boxes for the exercise 'i' have already been read
        if j == j_max:
            j = 0
            i = i + 1
            j_max = comparacion['examen'][i]['num_boxes']

        # check if the box is marked on the scan, and append to the dict if so
        if box['is_checked'] == 'True':
            comparacion['examen'][i]['marked_scan'].append(j + 1)

        # update j to next box
        j = j + 1

    return comparacion

# %%
