import os, sys

# sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/")
# sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/nuclick/")
sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/nuclick/nuclick_test.py")
import numpy
import cv2
# import Controller.nuclick.nuclick

from nuclick_test import gen_mask

gpus = "7"
n_gpus = len(gpus.split(','))
os.environ['CUDA_VISIBLE_DEVICES'] = gpus

annotation_result_root = "/home5/sort/annotation/"
boundary_result_root = "/home5/sort/masks/"
region_image_root = "/home5/sort/images_small/"

result_root = "static/data/re_annotation_data/" + "results/"
points_root = "static/data/re_annotation_data/" + "points/"
grades_root = "static/data/re_annotation_data/" + "grades/"

image_type = '.jpg'

if __name__ == "__main__":
    print(sys.argv)
    region_image_file_name = sys.argv[1]
    points_file_name = sys.argv[2]
    grades_file_name = sys.argv[3]
    anno_name = sys.argv[4]
    annotator_id = sys.argv[5]
    mask_name = sys.argv[6]

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
    if len(dot) == 0:
        result = numpy.zeros([region_image_file.shape[0], region_image_file.shape[1]])
    else:
        result = gen_mask(dot, region_image_file)

    ret, binary = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(cv2.convertScaleAbs(binary), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    result = cv2.drawContours(result, contours, -1, 255, 1)
    result = result.astype(numpy.int16)
    result[result == 255] = -1

    numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt",
                  result, fmt='%d', delimiter=",")

    grades.insert(0, 0)
    grades = numpy.array(grades, dtype=numpy.int16)
    numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt",
                  grades, fmt='%d', delimiter=",")
