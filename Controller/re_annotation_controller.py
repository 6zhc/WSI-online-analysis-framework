import os
import numpy
import cv2
import random
from Controller.nuclick.nuclick import gen_mask

annotation_result_root = "/home1/zhc/resnet/annotation_record/whole/"
boundary_result_root = "/home1/zhc/resnet/boundary_record/"
region_image_root = "/home1/zhc/resnet/anno_data/"

result_root = "Data/re_annotation_data/" + "results/"
points_root = "Data/re_annotation_data/" + "points/"
grades_root = "Data/re_annotation_data/" + "grades/"

color = [[0, 128, 0, 0], [255, 0, 209, 255], [0, 255, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255],
         [255, 191, 0, 255], [0, 0, 0, 255], [0, 0, 0, 0]]

import colorsys
import random


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


def boundary_2_point(anno, annotator_id):
    anno_name = anno.split('.')[0]
    boundary_file_name = boundary_result_root + anno_name + '.txt'
    annotation_file_name = annotation_result_root + anno_name + '.txt'

    if not os.path.exists(points_root + 'a' + annotator_id + '/'):
        os.mkdir(points_root + 'a' + annotator_id + '/')
    if not os.path.exists(grades_root + 'a' + annotator_id + '/'):
        os.mkdir(grades_root + 'a' + annotator_id + '/')
    if not os.path.exists(result_root + 'a' + annotator_id + '/'):
        os.mkdir(result_root + 'a' + annotator_id + '/')

    points_file_name = points_root + 'a' + annotator_id + '/' + anno_name + '.txt'
    grades_file_name = grades_root + 'a' + annotator_id + '/' + anno_name + '.txt'

    boundary_file = numpy.loadtxt(boundary_file_name, dtype=int, delimiter=',')
    annotation_file = numpy.loadtxt(annotation_file_name, dtype=int, delimiter=',')

    points_file = open(points_file_name, 'w')
    grades_file = open(grades_file_name, 'w')

    points = []
    grades = []

    for i in range(numpy.max(boundary_file)):
        if i == 0 or i == 1 or annotation_file[i] == 0 or annotation_file[i] > 6:
            continue
        temp = numpy.argwhere(boundary_file == i)

        if temp.size == 0:
            continue

        x = temp[:, 1]
        y = temp[:, 0]
        cx = int(numpy.mean(x))
        cy = int(numpy.mean(y))

        if boundary_file[cy, cx] == i:
            points_file.write(str(cx) + ' ' + str(cy) + '\n')
            grades_file.write(str(annotation_file[i]) + '\n')
        else:
            cy = y[len(y) // 2]
            cx = x[len(x) // 2]
            points_file.write(str(cx) + ' ' + str(cy) + '\n')
            grades_file.write(str(annotation_file[i]) + '\n')

    grades_file.close()
    points_file.close()


def point_2_boundary(anno, mask_name, annotator_id):
    anno_name = anno.split('.')[0]
    region_image_file_name = region_image_root + anno_name + '.png'

    if not os.path.exists(points_root + 'a' + annotator_id + '/'):
        os.mkdir(points_root + 'a' + annotator_id + '/')
    if not os.path.exists(grades_root + 'a' + annotator_id + '/'):
        os.mkdir(grades_root + 'a' + annotator_id + '/')
    if not os.path.exists(result_root + 'a' + annotator_id + '/'):
        os.mkdir(result_root + 'a' + annotator_id + '/')

    points_file_name = points_root + 'a' + annotator_id + '/' + anno_name + '.txt'
    grades_file_name = grades_root + 'a' + annotator_id + '/' + anno_name + '.txt'
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
    dot = numpy.array(points)
    result = gen_mask(dot, region_image_file)

    ret, binary = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(cv2.convertScaleAbs(binary), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    result.astype(numpy.int8)
    result = cv2.drawContours(result, contours, -1, 255, 1)
    result = result.astype(numpy.int8)
    result[result == 255] = -1

    numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt",
                  result, fmt='%d', delimiter=",")

    grades.insert(0, 0)
    grades = numpy.array(grades, dtype=int)
    numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt",
                  grades, fmt='%d', delimiter=",")


def boundary_2_mask(anno, mask_name, annotator_id):
    anno_name = anno.split('.')[0]

    if not os.path.exists(points_root + 'a' + annotator_id + '/'):
        os.mkdir(points_root + 'a' + annotator_id + '/')
    if not os.path.exists(grades_root + 'a' + annotator_id + '/'):
        os.mkdir(grades_root + 'a' + annotator_id + '/')
    if not os.path.exists(result_root + 'a' + annotator_id + '/'):
        os.mkdir(result_root + 'a' + annotator_id + '/')

    boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt"
    annotation_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt"

    boundary_file = numpy.loadtxt(boundary_file_name, dtype=int, delimiter=',')
    annotation_file = numpy.loadtxt(annotation_file_name, dtype=int, delimiter=',')

    mask = numpy.zeros([512, 512, 4])

    for i in range(len(annotation_file)):
        mask[boundary_file == i] = color[annotation_file[i]]
    mask[boundary_file == -1] = [0, 255, 0, 255]

    cv2.imwrite(result_root + 'a' + annotator_id + '/' + 'mask_' + anno_name + '_' + mask_name + '.png', mask)


def boundary_2_mask_u_net(anno, annotator_id):
    if not os.path.exists(points_root + 'a' + annotator_id + '/'):
        os.mkdir(points_root + 'a' + annotator_id + '/')
    if not os.path.exists(grades_root + 'a' + annotator_id + '/'):
        os.mkdir(grades_root + 'a' + annotator_id + '/')
    if not os.path.exists(result_root + 'a' + annotator_id + '/'):
        os.mkdir(result_root + 'a' + annotator_id + '/')

    anno_name = anno.split('.')[0]
    boundary_file_name = boundary_result_root + anno_name + '.txt'
    annotation_file_name = annotation_result_root + anno_name + '.txt'

    boundary_file = numpy.loadtxt(boundary_file_name, dtype=int, delimiter=',')
    annotation_file = numpy.loadtxt(annotation_file_name, dtype=int, delimiter=',')

    mask = numpy.zeros([512, 512, 4])

    for i in range(len(annotation_file)):
        try:
            mask[boundary_file == i] = color[annotation_file[i]]
        except:
            pass
    mask[boundary_file == -1] = [0, 255, 0, 255]

    cv2.imwrite(result_root + 'a' + annotator_id + '/' + 'mask_' + anno_name + '_U-net.png', mask)


def boundary_2_mask_separate_nuclei(anno, mask_name, annotator_id):
    anno_name = anno.split('.')[0]

    if not os.path.exists(points_root + 'a' + annotator_id + '/'):
        os.mkdir(points_root + 'a' + annotator_id + '/')
    if not os.path.exists(grades_root + 'a' + annotator_id + '/'):
        os.mkdir(grades_root + 'a' + annotator_id + '/')
    if not os.path.exists(result_root + 'a' + annotator_id + '/'):
        os.mkdir(result_root + 'a' + annotator_id + '/')

    boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt"
    annotation_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt"

    boundary_file = numpy.loadtxt(boundary_file_name, dtype=int, delimiter=',')
    annotation_file = numpy.loadtxt(annotation_file_name, dtype=int, delimiter=',')

    mask = numpy.zeros([512, 512, 4])

    region_color = ncolors(len(annotation_file))
    random.shuffle(region_color)

    for i in range(1, len(annotation_file)):
        mask[boundary_file == i] = region_color[i]
    mask[boundary_file == -1] = [0, 255, 0, 255]

    cv2.imwrite(result_root + 'a' + annotator_id + '/' + 'mask_' + anno_name + '_' + mask_name + '_separate_nuclei.png',
                mask)
