import os
import numpy
import cv2
import random
import colorsys
from Controller.nuclick.nuclick import gen_mask

nuclei_annotation_data_root = "static/data/nuclei_annotation_data/"

color = [[0, 128, 0, 0], [255, 0, 209, 128], [0, 255, 255, 128], [0, 0, 255, 128], [0, 0, 255, 128],
         [255, 191, 0, 128], [0, 0, 0, 128], [0, 0, 0, 0]]


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step

    return hls_colors


def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append([r, g, b, 255])

    return rgb_colors


def point_2_boundary(region_inform):
    annotator_id = region_inform["annotator_id"]
    annotation_project = region_inform["annotation_project"]
    slide_uuid = region_inform["slide_uuid"]
    region_id = region_inform["region_id"]

    annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

    points_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                       str(region_id) + '_points' + '.txt'
    grades_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                       str(region_id) + '_grades' + '.txt'
    region_image_file_name = annotation_root_folder + 'r' + str(region_id) + '.png'

    points_file = open(points_file_name).readlines()
    grades_file = open(grades_file_name).readlines()

    points = []
    grades = []

    for item in points_file:
        points.append([int(item.split(' ')[0]), int(item.split(' ')[1])])
    print(points)

    for item in grades_file:
        grades.append(int(item))
    region_image_file = cv2.imread(region_image_file_name)
    if len(grades) > 0:
        dot = numpy.array(points)
        result = gen_mask(dot, region_image_file)

        ret, binary = cv2.threshold(result, 0, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(cv2.convertScaleAbs(binary), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        result = cv2.drawContours(result, contours, -1, 255, 1)
        result = result.astype(numpy.int16)
        result[result == 255] = -2
        result += 1
    else:
        result = numpy.zeros(region_image_file.shape[:2])
        result += 1

    boundary_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                         str(region_id) + '_boundary' + '.txt'
    numpy.savetxt(boundary_file_name, result, fmt='%d', delimiter=",")

    grades.insert(0, 0)
    grades.insert(0, 0)
    grades = numpy.array(grades, dtype=numpy.int16)
    annotation_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                           str(region_id) + '_annotation' + '.txt'
    numpy.savetxt(annotation_file_name, grades, fmt='%d', delimiter=",")


def boundary_2_mask(region_inform):
    annotator_id = region_inform["annotator_id"]
    annotation_project = region_inform["annotation_project"]
    slide_uuid = region_inform["slide_uuid"]
    region_id = region_inform["region_id"]

    annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

    boundary_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                         str(region_id) + '_boundary' + '.txt'
    annotation_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                           str(region_id) + '_annotation' + '.txt'

    if not os.path.exists(boundary_file_name):
        point_2_boundary(region_inform)
    boundary_file = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')
    annotation_file = numpy.loadtxt(annotation_file_name, dtype=numpy.int16, delimiter=',')

    mask = numpy.zeros([512, 512, 4])

    for i in range(len(annotation_file)):
        mask[boundary_file == i] = color[annotation_file[i]]
    mask[boundary_file == -1] = [0, 255, 0, 255]
    mask[:, -3:] = [255, 0, 0, 255]
    mask[-3:, :] = [255, 0, 0, 255]
    mask[:3, :] = [255, 0, 0, 255]
    mask[:, :3] = [255, 0, 0, 255]

    mask_file_name = annotation_root_folder + '/' + 'a' + str(annotator_id) + '_r' + \
                     str(region_id) + '_mask' + '.png'
    cv2.imwrite(mask_file_name, mask)
    return mask_file_name


def update_grade(region_inform, data):
    annotator_id = region_inform["annotator_id"]
    annotation_project = region_inform["annotation_project"]
    slide_uuid = region_inform["slide_uuid"]
    region_id = region_inform["region_id"]

    annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

    points_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                       str(region_id) + '_points' + '.txt'
    grades_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                       str(region_id) + '_grades' + '.txt'
    boundary_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                         str(region_id) + '_boundary' + '.txt'

    if not os.path.exists(boundary_file_name):
        point_2_boundary(region_inform)

    boundary_file = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')
    boundary_file += len(data['grade'])
    boundary_file[boundary_file == len(data['grade']) - 1] -= len(data['grade'])
    boundary_file[boundary_file == len(data['grade']) + 1] -= len(data['grade'])


    points_file = open(points_file_name, 'w')
    grades_file = open(grades_file_name, 'w')

    for i in range(len(data['grade'])):
        nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i])])
        if nuclei_id == -1:
            try:
                nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i]) - 1])
            except:
                pass
            if nuclei_id == 1:
                try:
                    nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i]) + 1])
                except:
                    pass

        if nuclei_id != 1 and nuclei_id != -1:
            boundary_file[boundary_file == nuclei_id] = i + 2
            if nuclei_id < len(data['grade']):
                data['grade'][nuclei_id - 2] = 0
        if data['grade'][i] == 0:
            boundary_file[boundary_file == i + 2] = 0
        # if nuclei_id != i + 2 and nuclei_id != 1:
        #     if nuclei_id != -1:
        #         try:
        #             data['grade'][nuclei_id - 2] = data['grade'][i]
        #             if int(data['grade'][i]) == 0:
        #                 boundary_file[boundary_file == nuclei_id] = 0
        #         except:
        #             print("------------- error: " + nuclei_id + "++++++++++++")
        #     data['grade'][i] = 0

    current_nuclei_id = 0
    for i in range(len(data['grade'])):
        try:
            if int(data['grade'][i]) != 0:
                points_file.write(str(data['points_x'][i]) + ' ' + str(data['points_y'][i]) + '\n')
                grades_file.write(str(data['grade'][i]) + '\n')
                old_nuclei_id = boundary_file[int(data['points_y'][i]), int(data['points_x'][i])]
                current_nuclei_id += 1
                if old_nuclei_id > 0:
                    boundary_file[boundary_file == old_nuclei_id] = current_nuclei_id

        except:
            pass

    numpy.savetxt(boundary_file_name, boundary_file, fmt='%d', delimiter=",")
    grades_file.close()
    points_file.close()
