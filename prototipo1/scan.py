
import PyPDF2 as pypdf
import json
import os
from pdf2image import convert_from_path
import numpy as np
import cv2



def detect_st(st_file, id_exam):
    # open the pdf file with the exam statement ?- check whether file exists
    # get the checkboxes from the modified pyPDF2 version
    var = pypdf.PdfFileReader(st_file).getFields()

    # process and store the checkbox information on the json files
    #   data stores the information to be stored
    #   count_ex iterates the exercises
    #   count_box iterates the checkboxes for each exercise
    data = {'exam': id_exam,
            'num_boxes': var.__len__(),
            'exercises' : []}

    count_ex = -1
    count_box = -1
    for box in var:                 # example of content in box: 1:case:basic-adittion:1,1
        exercise = box.split(sep=':')[2]
        # if it is the first box to be read, or if the new box being read is from a next exercise --> append exercise
        if not data['exercises'] or (data['exercises'][count_ex]['exercise'] != exercise):
            count_ex = count_ex + 1
            count_box = 0
            data['exercises'].append(
                {
                    'exercise': exercise,
                    'checkboxes': []
                }
            )
        # append checkbox
        count_box = count_box + 1
        data['exercises'][count_ex]['checkboxes'].append(
            {
                'checkbox' : str(count_ex) + ',' + str(count_box),
                'cords' : [ float(var[box]['/Rect'][0]),
                            float(var[box]['/Rect'][1]),
                            round(float(var[box]['/Rect'][2]) - float(var[box]['/Rect'][0]), 3),
                            round(float(var[box]['/Rect'][3]) - float(var[box]['/Rect'][1]), 3) ]
            })
    # write the JSON file
    jf_name = 'json/st_' + id_exam + '.json'
    os.makedirs(os.path.dirname(jf_name), exist_ok=True)
    with open(jf_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)




def detect_sol(sol_file, st_json, id_variant):
    # open the pdf file with the exam solution ?- check whether file exists
    # get the checkboxes from the modified pyPDF2 version
    var = pypdf.PdfFileReader(sol_file).getFields()

    # open and read the statement JSON
    with open(st_json) as json_file:
        data = json.load(json_file)

    # process the solution pdf into the dictionary
    # check if it has the same number of checkboxes? or assume correct?
    data['variant'] = id_variant
    count_ex = -1
    count_box = -1
    st_exercise = ''
    for box in var:                 # example of content in box: 1:case:basic-adittion:1,1
        sol_exercise = box.split(sep=':')[2]
        # if it is the first box to be read, or if the current box is in a new exercise --> update st_exercise and add 'sol_marked' key to dict
        # check if the current box is in the same exercise. assumes the exercise names are the same and in the same order
        if not sol_exercise == st_exercise:
            count_ex = count_ex + 1
            count_box = -1
            st_exercise = data['exercises'][count_ex]['exercise']
            data['exercises'][count_ex]['sol_marked'] = []
        # check if the current box is marked. appends if marked
        count_box = count_box + 1
        data['exercises'][count_ex][count_box]['is_marked'] = var[box]['/V'] == '/Yes'
        if var[box]['/V'] == '/Yes':
            data['exercises'][count_ex]['sol_marked'].append(str(count_ex) + ',' + str(count_box))

    # write the JSON file
    jf_name = 'json/sol_' + id_variant+ '.json'
    os.makedirs(os.path.dirname(jf_name), exist_ok=True)
    with open(jf_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)



def detect_fill(filled_file, st_json, id_variant):
    # open the pdf file with the exam solution ?- check whether file exists
    # get the checkboxes from the modified pyPDF2 version
    var = pypdf.PdfFileReader(filled_file).getFields()

    # open and read the statement JSON
    with open(st_json) as json_file:
        data = json.load(json_file)

    # process the solution pdf into the dictionary
    # check if it has the same number of checkboxes? or assume correct?
    data['variant'] = id_variant
    count_ex = -1
    count_box = -1
    st_exercise = ''
    for box in var:                 # example of content in box: 1:case:basic-adittion:1,1
        filled_exercise = box.split(sep=':')[2]
        # if it is the first box to be read, or if the current box is in a new exercise --> update st_exercise and add 'student_marked' key to dict
        # check if the current box is in the same exercise. assumes the exercise names are the same and in the same order
        if not filled_exercise == st_exercise:
            count_ex = count_ex + 1
            count_box = -1
            st_exercise = data['exercises'][count_ex]['exercise']
            data['exercises'][count_ex]['student_marked'] = []
        # check if the current box is marked. appends if marked
        count_box = count_box + 1
        data['exercises'][count_ex][count_box]['is_marked'] = var[box]['/V'] == '/Yes'
        if var[box]['/V'] == '/Yes':
            data['exercises'][count_ex]['student_marked'].append(str(count_ex) + ',' + str(count_box))

    # write the JSON file
    jf_name = 'json/sol_' + id_variant+ '.json'
    os.makedirs(os.path.dirname(jf_name), exist_ok=True)
    with open(jf_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)






def find_cboxes_img(png_file):
    img = cv2.imread(png_file)
    gray_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th1, img_bin = cv2.threshold(gray_scale, 150, 225, cv2.THRESH_BINARY)
    img_bin = ~img_bin

    # set min width of lines for the rectangle: 20 pixels
    line_min_width = 20
    kernel_h = np.ones((1, line_min_width), np.uint8)
    kernel_v = np.ones((line_min_width, 1), np.uint8)

    # find horizontal and vertical lines and join them
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
    img_bin_final = img_bin_h | img_bin_v

    # find conected lines that form a box
    _, labels, stats, _ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)
    # stats: (x, y, w, h, a) * num_boxes
    # first two rows of stats are the background and residue pixel bounding boxes, which we dont need
    return stats[2:]





def find_cboxes(pdf_file, id_student):
    boxes = []
    # export the pdf's pages to png with 250 dots per inch (dpi)
    pages = convert_from_path(pdf_file, 250)
    # create the directory png
    if not os.path.exists('png'):
        os.mkdir('png')
    # iterate the pages
    for i, page in enumerate(pages):
        # save each page in a png file
        im_file = 'png/' + id_student + '_page' + str(i) + '.png'
        page.save(im_file)

        # add the checkboxes to the list
        boxes.append(find_cboxes_img(im_file))
    return boxes




def is_marked(box):
    x, y, w, h, a = box
    # for now, checks if the area extracted is smaller than 80% of the rectangle's area
    return a < (w * h) * 0.8



def is_same_exercise(st_checkboxes, scan_checkboxes):       # assumes st_checkboxes and scan_checkboxes of same length
    st_init_x = st_checkboxes[0]['cords'][0]
    st_init_y = st_checkboxes[0]['cords'][1]
    st_init_w = st_checkboxes[0]['cords'][2]
    scan_init_x = scan_checkboxes[0][0]
    scan_init_y = scan_checkboxes[0][1]
    scan_init_w = scan_checkboxes[0][2]
    factor = scan_init_w / st_init_w                        # different scale between the coordinates
    is_same = True
    for i in range(1, st_checkboxes.__len__()):
        st_x = st_checkboxes[i]['cords'][0]
        st_y = st_checkboxes[i]['cords'][1]
        st_dx_t = abs(st_x - st_init_x) * factor
        st_dy_t = abs(st_y - st_init_y) * factor
        scan_x = scan_checkboxes[i][0]
        scan_y = scan_checkboxes[i][1]
        scan_dx_t = abs(scan_x - scan_init_x)
        scan_dy_t = abs(scan_y - scan_init_y)
        # the difference in distance gets bigger as the distance grows, so increase the range proportionally to distance
        # also, to avoid issues with alignment, increase by flat amount relative to box size
        d_range = (scan_dx_t + scan_dy_t) * 0.2 + scan_init_w
        if st_dx_t < scan_dx_t - d_range or st_dx_t > scan_dx_t + d_range or st_dy_t < scan_dy_t - d_range or st_dy_t > scan_dy_t + d_range:
            is_same = False
            # print('st_dx_t: ', st_dx_t, 'scan_dx_t: ', scan_dx_t, 'st_dy_t: ', st_dy_t, 'scan_dy_t: ', scan_dy_t)
    return is_same





def analyse(scan_file, st_json, id_student):
    # get the checkbox data
    scan_boxes = find_cboxes(scan_file, id_student)
    # open and read the statement JSON
    with open(st_json) as json_file:
        data = json.load(json_file)
    # check if the same exam: check number of boxes
    if data['num_boxes'] != scan_boxes[0].__len__():
        print(data['num_boxes'], scan_boxes[0].__len__())
        print("Error, numero de casillas distinto")
    else:
        # modify st_json with the data from the checkboxes
        data['student'] = id_student
        # to group the boxes from the scanned pdf into exercises
        count_boxes1 = 0
        count_boxes2 = 0
        # iterate through the exercises in the statement dict
        for i, exercise in enumerate(data['exercises']):
            count_boxes2 = count_boxes2 + exercise['checkboxes'].__len__()
            # check if the same exam: check structure of boxes within exercises
            if not is_same_exercise(exercise['checkboxes'], scan_boxes[0][count_boxes1:count_boxes2]):
                print("Error, estructura de casillas no encaja")
            # check each box in the exercise for if they're marked
            data['exercises'][i]['scan_marked'] = []
            for j in range(count_boxes1, count_boxes2):
                if is_marked(scan_boxes[0][j]):
                    data['exercises'][i]['scan_marked'].append(str(i) + ',' + str(j-count_boxes1))
            count_boxes1 = count_boxes2

    # write the JSON file
    jf_name = 'json/scan_' + id_student+ '.json'
    os.makedirs(os.path.dirname(jf_name), exist_ok=True)
    with open(jf_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)






def match(sol_json, scan_json):
    # open solution json
    with open(sol_json) as json_file:
        data_sol = json.load(json_file)
    # open scan json
    with open(scan_json) as json_file:
        data_scan = json.load(json_file)
    # check if same exam
    if data_scan['exam'] != data_sol['exam'] or data_scan['num_boxes'] != data_sol['num_boxes'] or data_scan['exercises'].__len__() != data_sol['exercises'].__len__():
        print('Error, solution y scanned no coinciden')
    count = 0
    for i, exercise in enumerate(data_sol['exercises']):
        if exercise['sol_marked'] == data_scan['exercises'][i]['scan_marked']:
            count = count + 1

    # print('Grade: ', 10*count/data_scan['exercises'].__len__())
    return {'num_correct': count, 'total_exercises': data_scan['exercises'].__len__()}





